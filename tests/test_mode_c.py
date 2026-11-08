import importlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from common import load_items
from mode_c import decide
run = importlib.import_module("04_run_llm")

EV = {it["item_id"]: it["evidence"] for it in load_items()}
EV["dup"] = "t | 2025\nA | 5\nA | 7"


def cell(row, col, role):
    return {"row": row, "column": col, "role": role}


def fact(text, kind, cells, direction="none", relation="equal", found=True):
    return {"claimed_text": text, "relation": relation, "type": kind, "direction": direction, "found": found, "cells": cells}


LOC = "Scope 2 location-based"
CASES = [
    ("adyen_01", [fact("47%", "change", [cell(LOC, "2024", "old"), cell(LOC, "2025", "new")], "up"),
                  fact("17628 tCO2e", "value", [cell(LOC, "2025", "value")])], "CONSISTENT"),
    ("adyen_01", [fact("57%", "change", [cell(LOC, "2024", "old"), cell(LOC, "2025", "new")], "up")], "INCONSISTENT"),
    ("adyen_01", [fact("47%", "change", [cell(LOC, "2024", "old"), cell(LOC, "2025", "new")], "down")], "INCONSISTENT"),
    ("heineken_01", [fact("14.9 million tonnes", "value", [cell("Total GHG emissions (market-based)", "2025", "value")])], "CONSISTENT"),
    ("heineken_01", [fact("14.9 thousand tonnes", "value", [cell("Total GHG emissions (market-based)", "2025", "value")])], "INCONSISTENT"),
    ("zalando_01", [fact("1.0%", "share", [cell("Gross scope 1", "2025", "part"), cell("Gross scope 2 (market-based)", "2025", "part"),
                                           cell("Total GHG (market-based)", "2025", "total")], relation="less_than")], "CONSISTENT"),
    ("kpn_04", [fact("~4 GWh", "difference", [cell("Electricity consumption (MWh)", "2024", "old"),
                                              cell("Electricity consumption (MWh)", "2025", "new")], "down", "about")], "CONSISTENT"),
    ("kpn_04", [fact("~4 MWh", "difference", [cell("Electricity consumption (MWh)", "2024", "old"),
                                              cell("Electricity consumption (MWh)", "2025", "new")], "down", "about")], "INCONSISTENT"),
    ("heineken_02", [fact("38%", "change", [cell("Scope 1", "2022 baseline", "old"), cell("Scope 2 market-based", "2022 baseline", "old"),
                                            cell("Scope 1", "2025", "new"), cell("Scope 2 market-based", "2025", "new")], "down")], "CONSISTENT"),
    ("kpn_02", [fact("", "direction_only", [cell("Scope 1", "2024", "old"), cell("Scope 1", "2025", "new")], "down")], "CONSISTENT"),
    ("aholddelhaize_03", [fact("5.2%", "value", [cell("% reduction/(increase) FLAG vs baseline", "2025", "value")])], "INVALID"),
    ("signify_03", [fact("31%", "value", [cell("Category 6: Business travel", "% change 25/24", "value")])], "INVALID"),
    ("heineken_03", [fact("", "direction_only", [cell("Scope 3 FLAG", "2024", "old"), cell("Scope 3 FLAG", "2025", "new")], "same")], "CONSISTENT"),
    ("heineken_02", [fact("", "direction_only", [cell("Scope 1", "2024", "old"), cell("Scope 1", "2025", "new")], "same")], "INCONSISTENT"),
    ("prosus_01", [fact("zero", "value", [cell("Scope 1 (corporate)", "FY25", "value")])], "CONSISTENT"),
    ("prosus_01", [fact("", "direction_only", [cell("Scope 1 (corporate)", "FY24", "old"), cell("Scope 1 (corporate)", "FY25", "new")], "same")], "CONSISTENT"),
    ("adyen_02", [fact("2024: 3,748 tCO2e", "value", [cell("Scope 2 market-based", "2024", "value")])], "CONSISTENT"),
    ("adyen_01", [fact("17628 ktCO2e", "value", [cell(LOC, "2025", "value")])], "INCONSISTENT"),
    ("adyen_01", [fact("17628 tCO2e per million EUR", "value", [cell(LOC, "2025", "value")])], "CONSISTENT"),
    ("dup", [fact("5 t", "value", [cell("A", "2025", "value")])], "INVALID"),
    ("heineken_01", [fact("14.9 million tCO2e", "value", [cell("Total GHG emissions (market-based)", "2025", "value")])], "CONSISTENT"),
    ("heineken_01", [fact("14,924 thousand metric tons", "value", [cell("Total GHG emissions (market-based)", "2025", "value")])], "CONSISTENT"),
    ("heineken_01", [fact("14.9 million tonnes", "value", [cell("Total GHG emissions (market-based)", "2025", "value")])], "CONSISTENT"),
    ("adyen_01", [fact("17.628 ktCO2e", "value", [cell(LOC, "2025", "value")])], "CONSISTENT"),
    ("heineken_01", [fact("in 2025 was 14.9 million tonnes", "value", [cell("Total GHG emissions (market-based)", "2025", "value")])], "CONSISTENT"),
    ("adyen_01", [fact("47%", "change", [], "none", found=False)], "CANNOT_VERIFY"),
    ("adyen_01", [fact("47%", "change", [cell(LOC, "2024", "old"), cell(LOC, "2025", "new")], "none")], "INVALID"),
    ("adyen_01", [fact("47%", "change", [cell(LOC, "2024", "old"), cell(LOC, "2025", "new")], "increase")], "INVALID"),
    ("adyen_01", [fact("47%", "change", [cell("Scope 2", "2024", "old"), cell("Scope 2", "2025", "new")], "up")], "INVALID"),
    ("akzonobel_02", [fact("10%", "change", [cell("Total energy consumption per ton of production (KWh/t)", "2018 baseline", "old"),
                                             cell("Total energy consumption per ton of production (KWh/t)", "2025", "new")], "down")], "CONSISTENT"),
    ("adyen_03", [fact("82%", "value", [cell("Scope 3 share of total GHG (%)", "2025", "value")])], "CONSISTENT"),
    ("kpn_04", [fact("4 GWh", "difference", [cell("Electricity consumption (MWh)", "Base 2015", "old"),
                                             cell("Electricity consumption (MWh)", "2025", "new")], "down")], "CANNOT_VERIFY"),
    ("adyen_01", [fact("47%", "change", [], "up", found=False)], "CANNOT_VERIFY"),
    ("adyen_01", [fact("47%", "change", [cell("Scope 9", "2024", "old"), cell(LOC, "2025", "new")], "up")], "INVALID"),
    ("adyen_01", [], "CANNOT_VERIFY"),
]

RAW = [
    ("A", '{"label": "consistent"}', "CONSISTENT"),
    ("B", '{"reasoning": "x", "label": "CANNOT_VERIFY"}', "CANNOT_VERIFY"),
    ("C", json.dumps({"facts": CASES[0][1]}), "CONSISTENT"),
]
BAD_RAW = [("A", '{"label": "TRUE"}'), ("A", "not json"), ("C", '{"facts": "x"}'), ("A", "[1]")]

if __name__ == "__main__":
    bad = 0
    for iid, facts, want in CASES:
        got = decide(facts, EV[iid])[0]
        if got != want:
            bad += 1
            print(f"FAIL {iid}: {want} != {got}")
    for mode, text, want in RAW:
        got = run.parse(mode, text, {"evidence": EV["adyen_01"]})[0]
        if got != want:
            bad += 1
            print(f"FAIL parse {mode}: {want} != {got}")
    for mode, text in BAD_RAW:
        try:
            run.parse(mode, text, {"evidence": EV["adyen_01"]})
            bad += 1
            print(f"FAIL parse should raise: {text}")
        except ValueError:
            pass
    total = len(CASES) + len(RAW) + len(BAD_RAW)
    print(f"{total - bad}/{total} passed")
    sys.exit(1 if bad else 0)
