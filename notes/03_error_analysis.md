# Error analysis

This covers the 19 wrong answers of the six LLM systems with prompt v2: luna A 3, luna B 6, luna C 7, sol A 0, sol B 0, sol C 3. The full list, with each reply, is in results/errors.csv. The extra tables mentioned below are in results/summary.md. Mode A gives no reasoning, so for mode A errors the cause is a best guess from the claim and the table.

9 of the 19 errors are on the 7 items prompt v2 was aimed at, or on adyen_03_year, which is a synthetic version of one of them. So these items stay hard even after the rules were written down.

## 1. Too cautious (6 errors: luna B 5, luna A 1)

The model mostly did the math right but asked for something the task does not require, and answered CANNOT_VERIFY.

- heineken_01 (B): 14,924 kt rounds to 14.9 Mt, "However, it does not specify that this total covers Scope 1, 2 and 3".
- signify_01 (A, B): in B, the 60.3% reduction matches, but "the table does not identify whether this total includes emissions from the product use phase".
- postnl_05 (B): "It does not state the target, so whether 33% is on target cannot be verified."
- asml_02 (B): "The table does not state the SBTi target, so it cannot verify that the reduction exceeded it."
- aholddelhaize_04 (B): "the table does not identify whether its figures cover those brands". The model also rounded the FLAG change of 2.48% to "about 2.5%", which would hide the real problem (2.48% vs the claimed 2.6%).

Rule 11 says a target remark is not checked when the target is not given, so postnl_05 and asml_02 go against the prompt.

Is this caused by the written reasoning? Only partly. luna A made the same cautious errors in v1 (asml_02, postnl_05, signify_01). In run 1, rule 11 in v2 fixed them in A but not in B, and luna B's v1 and v2 answers are the same on 172 of 174 items. In runs 2 and 3, luna A also answered CANNOT_VERIFY on postnl_05 and asml_02, so rule 11 helps A only some of the time. Without the 7 items v2 was aimed at, luna A and B tie in run 1 (2 against 2, macro-F1 97.9 for both), but not in run 2 (1 against 4) or run 3 (3 against 0). So the A vs B gap is not stable across runs.

## 2. Right number, wrong row (2 errors: luna A, luna C)

akzonobel_03 says renewable electricity was 65% in 2024. The matching row (contractual instruments) shows 63. Another row (own operations) shows exactly 65. Mode C shows the model citing that row. Mode A probably made the same match. In run 1, sol got the right label in all three modes (sol A got it wrong in run 3), but sol C got it for the wrong reason: it also cited the own-operations row, and the 2025 value (67 vs 69) made it INCONSISTENT. The same mistake happens in real reports, when a number is taken from the wrong row, which makes it hard and important to catch.

## 3. Changed year read as a contradiction (3 errors: luna A, luna B, luna C)

adyen_02_year says "(2021: 3,748 tCO2e)", while the table shows 3,748 for 2024. luna B answered INCONSISTENT because "the claim identifies 3,748 as the 2021 value, whereas the table identifies it as 2024". luna A did the same on akzonobel_01_year. In mode C on akzonobel_01_year, the changed year probably led the model to cite 2024 instead of 2025 as the new year for the 47%, which gave a mismatch.

The guidelines say a year that is not in the table gives CANNOT_VERIFY, but reading it as a contradiction is also reasonable: the table does say the number belongs to another year. This is an ambiguity in the label design more than a model error. The labels were not changed. Across the six systems, 175 of 180 year items got the gold label in run 1.

## 4. Vague words (6 errors: luna C 3, sol C 3)

- adyen_03 and adyen_03_year (luna C and sol C, 4 errors): "remained in line" became a "same" fact, although the prompt says vague size words are never facts. The share went from 84% to 82%, which fails the under-1% rule for "same". Even the large model ignored this explicit rule.
- prosus_10 (luna C and sol C, 2 errors): "increased slightly" cannot be written as a fact, and the 23% revenue growth is not in the table, so the result was CANNOT_VERIFY instead of INCONSISTENT. Here the model followed the prompt. This is a limit of the mode C design, not a model mistake.

## 5. Mistakes in filling in the facts (2 errors: luna C)

- asml_01_number: the model marked "78 kt" as not found, instead of citing the 2019 cell (60), which would have shown the mismatch.
- aholddelhaize_02 (INVALID): the model cited the "% reduction" row as a value, and mode_c.py rejects such rows because tables use different sign conventions for them. The prompt only forbids this row for a change or difference, so the model's choice is arguably allowed. sol C used a change fact here and was right.

## Summary

| group | errors | mostly in |
|---|---|---|
| 1. too cautious | 6 | luna B |
| 2. right number, wrong row | 2 | luna |
| 3. changed year read as a contradiction | 3 | luna |
| 4. vague words | 6 | mode C |
| 5. mistakes in filling in the facts | 2 | luna C |

No mode B reasoning shows an arithmetic slip, apart from the early rounding in aholddelhaize_04. The errors are about what to check, which row a claim refers to, and how to read vague words.

## Other findings

- Baseline (59 errors): it fails all 10 unit items, 19 of 32 drop_row items (16 of them by calling a table with other rows INCONSISTENT), 12 real claims, 7 direction, 6 number and 5 scope items, and no year item.
- Hard real claims: no real claim is wrong in every system. akzonobel_03, signify_01, adyen_03 and prosus_10 are each wrong in two LLM systems.
- luna B's caution does not show in its correct answers. None of its correct reasonings on real claims hedges.
- Agreement: no item is wrong in all three luna modes. A majority vote over luna's three modes gives 171/174 correct, the same as luna A alone in run 1.
- Run-to-run variation: each system was run three times with the same prompt. luna gave a different label in at least one run on 6 (A), 5 (B) and 8 (C) of 174 items, sol on 1, 0 and 1. The items that change are mostly the hard ones above: akzonobel_03, the changed-year items, and the target remarks (postnl_05, asml_02). The order of luna's modes is not stable. Mode A is best in run 1, but over three runs the three modes are within about 1 point of each other (mean macro-F1 97.0 for A, 96.3 for B, 97.3 for C, and mean accuracy 97.5, 96.9 and 97.1). So the differences between modes are within run-to-run noise. This analysis reads the errors of run 1 only. Runs 2 and 3 also have a few errors on other items (for example akzonobel_04_year in luna A and prosus_24_number in luna C and sol C).
- From v1 to v2, luna also changed on some items the new rules were not aimed at (for example akzonobel_01_year and akzonobel_03 in mode A), which fits the same noise. In the v1 to v2 table in summary.md, adyen_03_year counts as "not aimed at" but is a synthetic version of adyen_03, and akzonobel_03 in mode C was right for the wrong reason in v1, so its change is not a real regression.
