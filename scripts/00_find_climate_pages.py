import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TERMS = [r"scope 1", r"scope 2", r"ghg emissions", r"tco2e?", r"\bE1\b", r"climate change mitigation", r"renewable electricity"]


def page_texts(pdf):
    out = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True).stdout
    return out.split("\f")


def score(text):
    t = text.lower()
    return sum(len(re.findall(p, t if p != r"\bE1\b" else text)) for p in TERMS)


def ranges(pages):
    if not pages:
        return []
    out, start, prev = [], pages[0], pages[0]
    for p in pages[1:]:
        if p - prev > 2:
            out.append((start, prev))
            start = p
        prev = p
    out.append((start, prev))
    return out


lines = ["# Climate pages per report", "", "Pages (as numbered in the PDF viewer) with many climate terms.", ""]
for pdf in sorted((ROOT / "reports").glob("*.pdf")):
    texts = page_texts(pdf)
    scores = [score(t) for t in texts]
    hot = [i + 1 for i, s in enumerate(scores) if s >= 4]
    top = sorted(range(len(scores)), key=lambda i: -scores[i])[:5]
    r = ", ".join(f"{a}-{b}" if a != b else f"{a}" for a, b in ranges(hot))
    lines.append(f"## {pdf.stem}")
    lines.append(f"- total pages: {len(texts) - 1}")
    lines.append(f"- climate-heavy ranges: {r or 'none found'}")
    lines.append(f"- top pages: {', '.join(str(i + 1) for i in sorted(top))}")
    lines.append("")

out = ROOT / "notes" / "00_climate_pages.md"
out.write_text("\n".join(lines))
print("\n".join(lines))
