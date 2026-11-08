import re

N = r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?"
NUM = re.compile(rf"(?<![\w.-])({N})(?![A-Za-z])")
YEAR = re.compile(r"(?:19|20)\d\d")
PAREN_YEAR = re.compile(r"\(\s*(?:19|20)\d\d\s*\)")
WORDS = {"zero": "0", "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
         "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10"}
UNITS = [
    (r"million tonnes|megatonnes|\bmt\b|\bmtco2", "mass", 1e6),
    (r"thousand tonnes|kilotonnes|ktonnes|\bkt\b|\bktco2", "mass", 1e3),
    (r"metric tons|tonnes|\btons?\b|\btco2|\bt\b", "mass", 1),
    (r"\bgwh\b", "energy", 1e3),
    (r"\bmwh\b", "energy", 1),
    (r"\bkwh\b", "energy", 1e-3),
]
ROLES = {"value": ["value"], "change": ["old", "new"], "difference": ["old", "new"],
         "direction_only": ["old", "new"], "share": ["part", "total"]}
DIRECTIONS = {"up", "down", "same", "none"}
RELATIONS = {"equal", "about", "less_than", "more_than"}
PRECOMPUTED = re.compile(r"change|reduction|increase", re.I)
MULT = {"billion": 1e9, "million": 1e6, "thousand": 1e3}


def norm(s):
    return re.sub(r"\s+", " ", str(s)).strip().lower()


def unit_of(text):
    m = re.search(r"\b(billion|million|thousand)\b", text, re.I)
    if m and not re.search(r"(\bper|/)\s*$", text[:m.start()], re.I):
        base = unit_of(text[:m.start()] + text[m.end():])
        return (base[0], base[1] * MULT[m.group(1).lower()]) if base else None
    best = None
    for pat, dim, f in UNITS:
        m = re.search(pat, text.lower())
        if m and (best is None or m.start() < best[0]):
            best = (m.start(), dim, f)
    return best[1:] if best else None


def parse_grid(ev):
    lines = [l for l in ev.split("\n") if "|" in l]
    if not lines:
        return [], {}
    heads = [c.strip() for c in lines[0].split("|")]
    grid = {}
    for l in lines[1:]:
        cells = [c.strip() for c in l.split("|")]
        key = norm(cells[0])
        grid[key] = None if key in grid else (cells[0], cells[1:])
    return heads, grid


def find_col(name, heads):
    cols = [norm(h) for h in heads[1:]]
    n = norm(name)
    return cols.index(n) if n in cols else None


def cell_value(text):
    if PAREN_YEAR.search(text):
        return None
    m = re.search(N, text)
    if not m:
        return None
    v = float(m.group(0).replace(",", ""))
    return -v if text.strip().startswith(("-", "(")) else v


def claimed(text):
    text = re.sub(r"\b(" + "|".join(WORDS) + r")\b", lambda m: WORDS[m.group(1).lower()], text or "", flags=re.I)
    for m in NUM.finditer(text):
        s, rest = m.group(1), text[m.end():]
        pct, unit = rest.lstrip().startswith("%"), unit_of(re.match(r"\s*(?:[^\d(:;,]|(?<=[Cc][Oo])2)*", rest).group(0))
        if YEAR.fullmatch(s) and not (pct or unit):
            continue
        dec = len(s.split(".")[1]) if "." in s else 0
        return float(s.replace(",", "")), dec, pct, unit
    return None


def close(x, dec, pct, relation, v):
    t = (1.0 if dec == 0 else 0.1) if pct else 0.5 * 10 ** -dec
    if relation == "about":
        t *= 2
    if relation == "less_than":
        return v <= x + 1e-9
    if relation == "more_than":
        return v >= x - 1e-9
    return abs(v - x) <= t + 1e-9


def check_fact(f, heads, grid):
    kind, d, rel = f.get("type"), f.get("direction", "none"), f.get("relation", "equal")
    if kind not in ROLES or d not in DIRECTIONS or rel not in RELATIONS:
        return "bad_fact"
    if not f.get("found"):
        return "missing"
    if kind in ("change", "difference") and d not in ("up", "down"):
        return "bad_fact"
    sums, units = {}, {}
    for c in f.get("cells") or []:
        if not isinstance(c, dict) or c.get("role") not in ROLES[kind]:
            return "bad_fact"
        row = grid.get(norm(c.get("row", "")))
        col = find_col(c.get("column", ""), heads)
        if row is None or col is None:
            return "lookup_error"
        label, cells = row
        if PRECOMPUTED.search(label) or PRECOMPUTED.search(heads[col + 1]):
            return "bad_fact"
        v = cell_value(cells[col]) if col < len(cells) else None
        if v is None:
            return "missing"
        role = c["role"]
        sums[role] = sums.get(role, 0) + v
        units[role] = unit_of(label) or unit_of(heads[0])
    if any(r not in sums for r in ROLES[kind]):
        return "bad_fact"
    if kind in ("change", "difference", "direction_only"):
        delta = sums["new"] - sums["old"]
        if d == "same":
            stable = delta == 0 or (sums["old"] != 0 and abs(delta) / abs(sums["old"]) < 0.01)
            return "ok" if stable else "mismatch"
        if (d == "up" and delta <= 0) or (d == "down" and delta >= 0):
            return "mismatch"
        if kind == "direction_only":
            return "ok"
    c = claimed(f.get("claimed_text", ""))
    if c is None:
        return "bad_fact"
    x, dec, pct, cunit = c
    if kind == "change":
        if sums["old"] == 0:
            return "missing"
        v = abs(delta) / abs(sums["old"]) * 100
        return "ok" if close(x, dec, True, rel, v) else "mismatch"
    if kind == "share":
        if sums["total"] == 0:
            return "missing"
        v = sums["part"] / sums["total"] * 100
        return "ok" if close(x, dec, True, rel, v) else "mismatch"
    v = abs(delta) if kind == "difference" else abs(sums["value"])
    tunit = units.get("old") if kind == "difference" else units.get("value")
    if not pct and cunit and tunit:
        if cunit[0] != tunit[0]:
            return "mismatch"
        v = v * tunit[1] / cunit[1]
    return "ok" if close(x, dec, pct, rel, v) else "mismatch"


def decide(facts, evidence):
    if not facts:
        return "CANNOT_VERIFY", "no_facts"
    heads, grid = parse_grid(evidence)
    res = [check_fact(f, heads, grid) if isinstance(f, dict) else "bad_fact" for f in facts]
    for bad in ("bad_fact", "lookup_error"):
        if bad in res:
            return "INVALID", bad
    if "mismatch" in res:
        return "INCONSISTENT", "mismatch"
    if "missing" in res:
        return "CANNOT_VERIFY", "missing"
    return "CONSISTENT", "all_ok"
