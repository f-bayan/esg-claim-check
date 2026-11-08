import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "gold_set.csv"

NUM = re.compile(r"(?<![Ss]cope )(?<![Ss]copes )(?<![Cc]ategory )(?<![A-Za-z])(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)(\s?%)?")
YEAR = re.compile(r"\b(19\d\d|20[0-4]\d)\b")
BOUND = re.compile(r"(?:\b(?:less than|more than|fewer than|over|below|under|above|at least|up to)|<|>)\s*$", re.I)
TARGET = re.compile(r"\s*targets?\b", re.I)
TARGET_NEAR = re.compile(r"\s*%?\s*(?:[A-Za-z-]+\s+){0,2}targets?\b", re.I)
SCOPE3_PARTS = re.compile(r"\bFLAG\b|E&I|purchased goods|business travel|commuting|categor(?:y|ies) \d|use of sold|financed", re.I)

DIRECTION = [
    ("decreased", "increased"), ("increased", "decreased"),
    ("decrease", "increase"), ("increase", "decrease"),
    ("reduced", "increased"), ("reduction", "increase"),
    ("declined", "rose"), ("dropped", "rose"), ("rose", "fell"), ("fell", "rose"),
    ("lower", "higher"), ("higher", "lower"), ("down", "up"),
]
UNITS = [
    ("million tonnes", "thousand tonnes"), ("kilotonnes", "megatonnes"),
    ("tonnes", "thousand tonnes"), ("tCO2e", "ktCO2e"),
    (" kt", " Mt"), ("GWh", "MWh"), ("MWh", "GWh"),
]
SCOPES = [
    ("Scope 1 and 2", "Scope 3"), ("scope 1 and 2", "scope 3"), ("Scopes 1 and 2", "Scope 3"),
    ("Scope 1 & 2", "Scope 3"), ("Scope 3", "Scope 1"), ("scope 3", "scope 1"),
]


def is_year(s):
    return re.fullmatch(r"(19|20)\d\d", s) is not None


def fmt(new, old):
    if "," in old:
        return f"{int(round(new)):,}"
    if "." in old:
        return f"{new:.{len(old.split('.')[1])}f}"
    return str(int(round(new)))


def p_number(claim, ev):
    for m in NUM.finditer(claim):
        val, pct = m.group(1), m.group(2)
        if is_year(val) or BOUND.search(claim[:m.start(1)]) or TARGET_NEAR.match(claim, m.end()):
            continue
        x = float(val.replace(",", ""))
        if pct:
            new = x + 10 if x <= 85 else x - 10
        else:
            if x < 10:
                continue
            new = x * 1.3
        s = fmt(new, val)
        out = claim[:m.start(1)] + s + claim[m.end(1):]
        return out, ev, "INCONSISTENT", f"{val} -> {s}"
    return None


def p_direction(claim, ev):
    hits = []
    for a, b in DIRECTION:
        for m in re.finditer(rf"\b{a}\b", claim, flags=re.I):
            if not TARGET.match(claim, m.end()):
                hits.append((m.start(), m, b))
                break
    if not hits:
        return None
    _, m, b = min(hits, key=lambda h: h[0])
    w = m.group(0)
    b2 = b.capitalize() if w[0].isupper() else b
    return claim[:m.start()] + b2 + claim[m.end():], ev, "INCONSISTENT", f"{w} -> {b2}"


def p_year(claim, ev):
    years = [y for y in YEAR.findall(claim) if y in ev]
    if not years:
        return None
    old = min(years)
    new = str(int(old) - 3)
    while new in ev:
        new = str(int(new) - 1)
    return claim.replace(old, new, 1), ev, "CANNOT_VERIFY", f"{old} -> {new}"


def p_unit(claim, ev):
    for a, b in UNITS:
        m = re.search(rf"(?<![A-Za-z]){re.escape(a.strip())}(?![A-Za-z])", claim)
        if m and not (a.strip() == "tonnes" and re.search(r"(million|thousand)\s+$", claim[:m.start()])):
            return claim[:m.start()] + b.strip() + claim[m.end():], ev, "INCONSISTENT", f"{a.strip()} -> {b.strip()}"
    return None


def p_scope(claim, ev):
    if SCOPE3_PARTS.search(claim):
        return None
    for a, b in SCOPES:
        if a in claim:
            target = b.split()[-1]
            has = re.search(rf"[Ss]cope {target}\b", ev) is not None
            label = "INCONSISTENT" if has else "CANNOT_VERIFY"
            return claim.replace(a, b, 1), ev, label, f"{a} -> {b} (check)"
    return None


def label_of(line):
    return line.split("|")[0].strip()


def p_drop_row(claim, ev, calc):
    nums = {n.replace(",", "") for n in re.findall(r"\d[\d,]*\.?\d*", calc) if not is_year(n)}
    lines = ev.split("\n")
    head, body = lines[0], lines[1:]
    drop = {i for i, l in enumerate(body) if set(re.findall(r"\d[\d.]*", l.replace(",", ""))) & nums}
    if not drop:
        return None
    drop |= {i for i, l in enumerate(body) if label_of(l).lower().startswith("total") or "non-" in label_of(l).lower()}
    for i, l in enumerate(body):
        if i > 0 and label_of(l).startswith("%") and (i in drop or i - 1 in drop):
            drop |= {i, i - 1}
    keep = [l for i, l in enumerate(body) if i not in drop]
    return claim, "\n".join([head] + keep), "CANNOT_VERIFY", f"dropped {len(drop)} row(s)"


def make(row):
    c, e = row["claim"], row["evidence"]
    out = []
    for name, fn in [("number", p_number), ("direction", p_direction), ("year", p_year),
                     ("unit", p_unit), ("scope", p_scope)]:
        r = fn(c, e)
        if r:
            out.append((name, *r))
    r = p_drop_row(c, e, row["calc"])
    if r:
        out.append(("drop_row", *r))
    return out


def main():
    only = set(sys.argv[1].split(",")) if len(sys.argv) > 1 else None
    out_path = ROOT / "data" / ("perturbed_sample.csv" if only else "perturbed.csv")
    old = {}
    if out_path.exists():
        old = {r["item_id"]: r for r in csv.DictReader(open(out_path, encoding="utf-8"))}
    removed_path = ROOT / "data" / "perturbed_removed.csv"
    removed = {r["item_id"] for r in csv.DictReader(open(removed_path, encoding="utf-8"))} if removed_path.exists() else set()
    rows = [r for r in csv.DictReader(open(SRC, encoding="utf-8")) if r["label"] == "CONSISTENT"]
    if only:
        rows = [r for r in rows if r["claim_id"] in only]
    cols = ["item_id", "source_claim_id", "company", "perturbation", "claim", "context", "evidence", "label", "change_note", "checked"]
    res = []
    for r in rows:
        for name, claim, ev, label, note in make(r):
            iid = f"{r['claim_id']}_{name}"
            if iid in removed:
                continue
            o = old.get(iid)
            same = o and (o["claim"], o["evidence"], o["label"]) == (claim, ev, label)
            res.append({"item_id": iid, "source_claim_id": r["claim_id"], "company": r["company"],
                        "perturbation": name, "claim": claim, "context": r.get("context", ""), "evidence": ev, "label": label,
                        "change_note": note, "checked": o["checked"] if same else ""})
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(res)
    print(f"{len(rows)} claims -> {len(res)} items -> {out_path.name}")


if __name__ == "__main__":
    main()
