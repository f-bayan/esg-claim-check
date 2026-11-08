import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LABELS = ["CONSISTENT", "INCONSISTENT", "CANNOT_VERIFY"]


def load_items():
    items = []
    for r in csv.DictReader(open(ROOT / "data" / "gold_set.csv", encoding="utf-8")):
        items.append({"item_id": r["claim_id"], "source": "real", "perturbation": "none", "claim": r["claim"],
                      "context": r["context"], "evidence": r["evidence"], "label": r["label"]})
    for r in csv.DictReader(open(ROOT / "data" / "perturbed.csv", encoding="utf-8")):
        items.append({"item_id": r["item_id"], "source": "synthetic", "perturbation": r["perturbation"], "claim": r["claim"],
                      "context": r["context"], "evidence": r["evidence"], "label": r["label"]})
    return items
