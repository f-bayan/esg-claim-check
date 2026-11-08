import csv
import re
from itertools import combinations, permutations

from common import ROOT, load_items

N = r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?"
YEAR = re.compile(r"\b(19\d\d|20[0-4]\d)\b")
FY = re.compile(r"\bFY(\d\d)\b")
STRIP = re.compile(r"\b(?:scopes?|categor(?:y|ies)|table)\s+\d+(?:\s*(?:,|and|&|\+)\s*\d{1,2}\b(?!\s*%|[.,]\d))*", re.I)
NUM = re.compile(rf"(?<![\w.-])({N})(?![A-Za-z])(\s?%)?")
CELL_NUM = re.compile(N)
PAREN_YEAR = re.compile(r"\(\s*(?:19|20)\d\d\s*\)")
LESS = re.compile(r"(?:\b(?:less|fewer|lower)\s+than|\bbelow|\bunder|<)\s*$", re.I)
MORE = re.compile(r"(?:\b(?:more|greater|higher)\s+than|\bover|\babove|\bat least|>)\s*$", re.I)
APPROX = re.compile(r"(?:~|\babout|\baround|\bapproximately|\bnearly|\balmost|\broughly)\s*$", re.I)
TARGET_AFTER = re.compile(r"\s*%?\s*(?:[A-Za-z-]+\s+){0,2}targets?\b", re.I)
TARGET_BEFORE = re.compile(r"targets?\s+(?:for\s+)?$", re.I)
DOWN = re.compile(r"\b(?:decreas\w*|reduc\w*|declin\w*|drop\w*|fell|fall\w*|lower|down|cut)\b", re.I)
UP = re.compile(r"\b(?:increas\w*|rose|rise|rises|rising|grew|grow\w*|higher|up(?!\s+to))\b", re.I)
FROM_TO = re.compile(rf"\bfrom\s+({N}).{{0,20}}?\bto\s+({N})", re.I)
THAN = re.compile(r"\b(higher|lower)\s+than\b", re.I)
ANY_NUM = re.compile(rf"(?<![\w.-])({N})")
TO_PRIOR = re.compile(rf"\bto\s+({N})[^()]{{0,30}}\((?:19|20)\d\d:\s*({N})")


def num(s):
    return float(s.replace(",", ""))


def is_year(s):
    return re.fullmatch(r"(19|20)\d\d", s) is not None


def years_in(text):
    return set(YEAR.findall(text)) | {"20" + y for y in FY.findall(text)}


def claim_years(claim):
    out = set()
    for m in YEAR.finditer(claim):
        if not TARGET_BEFORE.search(claim[:m.start()]):
            out.add(m.group(1))
    return out | {"20" + y for y in FY.findall(claim)}


def claim_numbers(claim):
    text = STRIP.sub(" ", claim)
    out = []
    for m in NUM.finditer(text):
        val, pct = m.group(1), bool(m.group(2))
        if is_year(val) or TARGET_AFTER.match(text, m.end(1)):
            continue
        before = text[:m.start(1)]
        kind = "lt" if LESS.search(before) else "gt" if MORE.search(before) else "eq"
        dec = len(val.split(".")[1]) if "." in val else 0
        out.append({"text": m.group(0).strip(), "x": num(val), "pct": pct, "kind": kind,
                    "approx": bool(APPROX.search(before)), "dec": dec})
    return text, out


def col_year(head):
    if re.search(r"target", head, re.I):
        return None
    y = years_in(head)
    return int(min(y)) if len(y) == 1 else None


def parse_table(ev):
    lines = [l for l in ev.split("\n") if "|" in l]
    if not lines:
        return [], [], [], [], []
    heads = [c.strip() for c in lines[0].split("|")[1:]]
    cols = [col_year(h) for h in heads]
    is_change = [bool(re.search(r"change", h, re.I)) for h in heads]
    rows, extras, names, signed = [], [], [], []
    for l in lines[1:]:
        names.append(l.split("|")[0].strip().lower())
        vals = []
        for i, c in enumerate(l.split("|")[1:]):
            ns = [] if PAREN_YEAR.search(c) else [num(n) for n in CELL_NUM.findall(c)]
            if i < len(is_change) and is_change[i]:
                if ns:
                    signed.append((ns[0], -1 if c.strip().startswith(("-", "(")) else 1))
                vals.append(None)
                continue
            vals.append(ns[0] if ns else None)
            extras += ns[1:]
        rows.append(vals + [None] * (len(cols) - len(vals)))
    return cols, rows, extras, names, signed


def candidates(cols, rows, extras, names, signed):
    raw = {v for r in rows for v in r if v is not None} | set(extras)
    sums = []
    for a, b in combinations(rows, 2):
        sums.append([x + y if x is not None and y is not None else None for x, y in zip(a, b)])
    values, changes, diffs, shares = set(raw), list(signed), [], set()
    time = [(i, y) for i, y in enumerate(cols) if y]
    for r in rows + sums:
        for (i, yi), (j, yj) in permutations(time, 2):
            if yi < yj and r[i] is not None and r[j] is not None:
                a, b = r[i], r[j]
                diffs.append((abs(b - a), 1 if b > a else -1 if b < a else 0))
                if a:
                    changes.append((abs((b - a) / a * 100), 1 if b > a else -1 if b < a else 0))
    for r in sums:
        values |= {v for v in r if v is not None}
    totals = [r for r, n in zip(rows, names) if re.search(r"^total\b|\btotal\s*\(|\btotal$", n)]
    for i in range(len(cols)):
        col = [r[i] for r in rows + sums if r[i] is not None]
        dens = [r[i] for r in totals if r[i] is not None] or ([max(col)] if col else [])
        for a in col:
            for b in dens:
                if b and a != b:
                    shares.add(a / b * 100)
    scaled = {v * k for v in values for k in (1, 1000, 0.001)}
    diffs = [(v * k, s) for v, s in diffs for k in (1, 1000, 0.001)]
    return {"raw": raw, "values": scaled, "changes": changes, "diffs": diffs, "shares": shares}


def tol(n):
    if n["pct"]:
        t = 1.0 if n["dec"] == 0 else 0.1
    else:
        t = 0.5 * 10 ** -n["dec"]
    return t * 2 if n["approx"] else t


def direction(text):
    d = DOWN.search(text)
    u = UP.search(text)
    hits = [(m.start(), s) for m, s in [(d, -1), (u, 1)] if m]
    return min(hits)[1] if hits else None


def check_number(n, c, d):
    x, t = n["x"], tol(n) + 1e-9
    if n["kind"] != "eq":
        pool = (c["raw"] | c["shares"] | {v for v, _ in c["changes"]}) if n["pct"] else c["values"] | {v for v, _ in c["diffs"]}
        ok = any(v <= x for v in pool) if n["kind"] == "lt" else any(v >= x for v in pool)
        return "ok" if ok else "miss"
    unsigned, signed = (c["raw"] | c["shares"], c["changes"]) if n["pct"] else (c["values"], c["diffs"])
    if any(abs(v - x) <= t for v in unsigned):
        return "ok"
    signs = {s for v, s in signed if abs(v - x) <= t}
    if not signs:
        return "miss"
    if d is None or d in signs:
        return "ok"
    return "wrong_direction"


def pair_direction(text):
    for pat, flip in [(FROM_TO, False), (TO_PRIOR, True)]:
        m = next((m for m in pat.finditer(text) if not (is_year(m.group(1)) or is_year(m.group(2)))), None)
        if m:
            a, b = num(m.group(1)), num(m.group(2))
            if flip:
                a, b = b, a
            return 1 if b > a else -1 if b < a else 0
    return None


def than_conflict(text):
    for m in THAN.finditer(text):
        ends = [e.end() for e in re.finditer(r"\.(?!\d)", text[:m.start()])]
        sent_start = ends[-1] if ends else 0
        left = [num(x) for x in ANY_NUM.findall(text[sent_start:m.start()]) if not is_year(x)]
        right = [num(x) for x in ANY_NUM.findall(text[m.end():]) if not is_year(x)]
        if left and right and left[-1] != right[0] and (left[-1] > right[0]) != (m.group(1).lower() == "higher"):
            return True
    return False


def predict(item):
    claim, ev = item["claim"], item["evidence"]
    missing = claim_years(claim) - years_in(ev)
    if missing:
        return "CANNOT_VERIFY", "year", " ".join(sorted(missing))
    cols, rows, extras, names, signed = parse_table(ev)
    if not any(v is not None for r in rows for v in r):
        return "CANNOT_VERIFY", "empty_table", ""
    text, nums = claim_numbers(claim)
    if not nums:
        return "CANNOT_VERIFY", "no_numbers", ""
    c = candidates(cols, rows, extras, names, signed)
    d = direction(text)
    res = [(n["text"], check_number(n, c, d)) for n in nums]
    miss = [t for t, r in res if r == "miss"]
    if miss:
        return "INCONSISTENT", "number", " ".join(miss)
    wrong = [t for t, r in res if r == "wrong_direction"]
    if wrong:
        return "INCONSISTENT", "direction", " ".join(wrong)
    p = pair_direction(text)
    if d is not None and p is not None and p != d:
        return "INCONSISTENT", "direction", "from/to"
    if than_conflict(text):
        return "INCONSISTENT", "direction", "than"
    return "CONSISTENT", "all_matched", ""


def main():
    items = load_items()
    out = ROOT / "results" / "baseline.csv"
    cols = ["item_id", "source", "perturbation", "label", "pred", "rule", "detail"]
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for it in items:
            pred, rule, detail = predict(it)
            w.writerow({"item_id": it["item_id"], "source": it["source"], "perturbation": it["perturbation"],
                        "label": it["label"], "pred": pred, "rule": rule, "detail": detail})
    print(f"{len(items)} items -> {out.name}")


if __name__ == "__main__":
    main()
