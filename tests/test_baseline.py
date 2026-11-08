import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
bl = importlib.import_module("03_baseline")

AHOLD = "MtCO2e | 2025 | 2024 | 2020 baseline\nScope 3 FLAG | 17.72 | 18.17 | 16.85"
ASML = "ktCO2e | 2019 | 2024 | 2025\nSubtotal scope 1 and market-based scope 2 | 60 | 33 | 26"
PROSUS = "tCO2e | FY25 | FY24\nTotal scope 3 (corporate) | 14048 | 7797"
ADYEN = "tCO2e | 2025 | 2024\nScope 2 market-based | 2926 | 3748"
POSTNL = "tonnes CO2e | 2021 base | 2024 | 2025 | change\nScope 1 | 41081 | 23925 | 19986 | (16)%"

CASES = [
    ("FLAG emissions were 17.72 Mt, which is higher than 18.17 Mt in 2024.", AHOLD, "INCONSISTENT"),
    ("Emissions from 2019 to 2025: we increased scope 1 and 2 emissions from 60 kt to 26 kt.", ASML, "INCONSISTENT"),
    ("From 60 kt to 26 kt, emissions increased.", ASML, "INCONSISTENT"),
    ("We reduced scope 1 and 2 emissions from 60 kt to 26 kt.", ASML, "CONSISTENT"),
    ("Scope 3 emissions were 7,797 tCO2e in FY23.", PROSUS, "CANNOT_VERIFY"),
    ("In scope 3, 14,048 tCO2e came from suppliers.", PROSUS, "CONSISTENT"),
    ("Scope 1, 2 and 3 emissions were 14,048 tCO2e in FY25.", PROSUS, "CONSISTENT"),
    ("Scope 2 market-based emissions rises 22% to 2,926 tCO2e (2024: 3,748 tCO2e).", ADYEN, "INCONSISTENT"),
    ("Scope 2 market-based emissions decreased by 22% to 2,926 tCO2e (2024: 3,748 tCO2e).", ADYEN, "CONSISTENT"),
    ("Scope 2 market-based emissions decreased by 32%.", ADYEN, "INCONSISTENT"),
    ("Scope 1 emissions increased by 16%.", POSTNL, "INCONSISTENT"),
    ("Scope 1 emissions decreased by 16%.", POSTNL, "CONSISTENT"),
    ("Scope 1 emissions decreased in 2022.", POSTNL, "CANNOT_VERIFY"),
    ("Scope 1 emissions went down.", "tCO2e | 2025", "CANNOT_VERIFY"),
]

if __name__ == "__main__":
    bad = 0
    for claim, ev, want in CASES:
        got = bl.predict({"claim": claim, "evidence": ev})[0]
        if got != want:
            bad += 1
            print(f"FAIL {want} != {got}: {claim}")
    print(f"{len(CASES) - bad}/{len(CASES)} passed")
    sys.exit(1 if bad else 0)
