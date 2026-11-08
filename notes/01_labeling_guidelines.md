# Labeling guidelines (v2)

## 1. What counts as a claim

A claim is one sentence (or part of a sentence) in the narrative text of the climate section that states something that can be checked against a number in a table of the same report.

Keep:
- Change over time: "Scope 1 and 2 emissions fell by 25% compared to 2019."
- A value: "Renewable electricity was 85% of our total in 2025."
- A direction: "Our air business travel emissions rose in FY25."
- A level: "We maintained our corporate emissions at zero."

Skip:
- Future targets and plans: "We aim to cut emissions by 50% by 2030." (nothing to check yet)
- Claims with no matching table in the report.
- Claims that only repeat a table header or caption.
- Claims whose number is only shown in a chart and not in a table.
- Claims about methods or policies with no number or direction.

Inside a kept claim, explanations of causes or background ("due to ...", "driven by ...", "despite ...") are not checked. Only the numbers and directions of the main statement are checked. Words like rose or fell inside a cause part are not checked, but numbers written there are.

A remark that a target was met ("which is on target") is only checked if the target value is in the claim, the evidence or the context.

Words about size ("slightly", "in line", "significantly") make a claim INCONSISTENT only if the table clearly contradicts them, for example "slightly" for a fivefold rise (prosus_10). A change from 84% to 82% can still be "in line" (adyen_03).

## 2. What counts as evidence

The evidence is the table row (or rows) in the same report that the claim is about. Copy only the rows and columns that are needed, plus the header with years and units.

If two tables could match, use the one in the same section as the claim.

## 3. Labels

- CONSISTENT: the evidence supports the claim, within the tolerance in section 4.
- INCONSISTENT: the evidence contains the needed numbers and they contradict the claim.
- CANNOT_VERIFY: the evidence does not contain the numbers needed to check the claim (missing year, missing scope, missing unit, missing category).

Rule of thumb: INCONSISTENT means the table says something else. CANNOT_VERIFY means the table says nothing about it.

## 4. Numbers and rounding

- Percent change is (old - new) / old for a reduction and (new - old) / old for an increase.
- A claim with a whole percent (30%) is CONSISTENT if the computed value rounds to it, or is within 1 percentage point.
- A claim with a decimal (29.6%) is CONSISTENT if it is within 0.1 percentage point of the computed value, because tables are rounded too.
- "About", "around", "approximately", "almost", "nearly", "roughly" and "~" allow twice the normal margin.
- "Less than X" and "more than X" are bounds: "more than 30%" needs at least 30%, "less than 1%" needs at most 1%.
- A share or value claim (85%, 0 tonnes) must match the table value after the same rounding.
- A direction claim (rose, fell, stayed the same) is CONSISTENT if the table moves in that direction. "Stable", "unchanged" or "stayed the same" means the relative change is less than 1%.

## 5. Tricky cases

- Scope 2 market-based vs location-based: if the claim does not say which, accept either. If it names one, use that one.
- Base year: the claim's base year must match a column in the table. If the column is missing, CANNOT_VERIFY.
- Units: tCO2e vs ktCO2e must be converted before comparing. A claim with the wrong unit is INCONSISTENT if the table has the right number in another unit.
- Scope swap: if the claim names a scope that the table also reports, compare with that row (often INCONSISTENT). If the table has no such row, CANNOT_VERIFY.
- Scope of the company: if the claim is about part of the company (one office, one country) and the table covers the whole company, CANNOT_VERIFY unless the table also breaks it down. Exception: if the whole-company value logically forces the part (for example 100% or 0% for all offices), the claim about the part is CONSISTENT.
- Named company inside a segment: if the report puts a company under a segment heading and it is the only company named for that segment, use the segment row as that company's numbers. If the segment has more than one named company, a claim about just one of them is CANNOT_VERIFY.
- Restated numbers: use the latest numbers in the report. Note it in the comment column.

## 6. Columns in the CSV

| column | meaning |
|---|---|
| claim_id | short id, e.g. prosus_01 |
| company | report name, e.g. prosus |
| page_claim | page of the claim (number printed on the page) |
| page_table | page of the table (number printed on the page) |
| claim | the claim text, copied exactly |
| context | only if the claim alone does not say what it is about: the section heading, what a word like 'these' refers to, or a short annotator note based on the report |
| evidence | the needed table rows, copied as plain text with header, years and units |
| claim_type | change, value, direction, level |
| label | CONSISTENT, INCONSISTENT, CANNOT_VERIFY |
| calc | the calculation you did, e.g. (7390-5818)/7390 = 21.3% |
| comment | anything unclear |

## 7. Worked examples (Prosus FY25)

1. Claim (p. 3): "We maintained our corporate emissions at zero."
   Evidence: Scope 1 FY25 0, FY24 0. Scope 2 market-based FY25 0, FY24 0 (tCO2e).
   Label: CONSISTENT. Type: level.

2. Claim (p. 4): "Our air business travel emissions rose in FY25."
   Evidence: Air travel emissions FY25 5 818, FY24 4 842 (tCO2e).
   Label: CONSISTENT. Type: direction.

3. Claim (p. 3): "We procured 100% renewable energy for our Amsterdam and London offices."
   Evidence: Renewable energy (%) FY25 100, for all corporate offices together.
   Label: CONSISTENT. The table is not split by office, but 100% for all offices means 100% for each office (section 5, exception).

## 8. Decisions

- Part-of-company claims are CONSISTENT when the whole-company value logically forces them (example 3).
- Claims with numbers only in charts are skipped.
- A company named alone under a segment heading uses the segment row (Prosus: PayU, OLX, eMAG, iFood). Edtech has two companies, so single-company claims there are CANNOT_VERIFY.
- Decimal claims get a 0.1 point tolerance for rounding (Ahold Delhaize 1.2% vs 1.28% is fine).
- aholddelhaize_04 changed to INCONSISTENT: FLAG 2.6% vs 2.48% is 0.12 points off, so it fails the 0.1 point rule.
- "About" doubles the margin, and "stable" means a change under 1% (section 4). Both were written down after labeling, to match the labels already given (kpn_04, heineken_03). No label changed.
- After the first full run (prompt v1), three rules that were already used when labeling were written down: numbers inside cause parts are checked, target remarks are only checked when the target is given, and size words need a clear contradiction. No label changed.
- Evidence format fixes, no label changed: the Adyen share of scope 3 (82%, 84%) was moved from inside the total cell to its own row, and the AkzoNobel 2018 baseline (275) was moved from the row name to its own column.
- The 7 INCONSISTENT gold claims are possible inconsistencies, not proven errors by the companies. The column inconsistency_type says how strong each one is: clear (postnl_02, postnl_04, akzonobel_03), small difference that could come from a restatement (postnl_01), possible definition difference (zalando_02, restated prior-year figures, and prosus_10, where a location-based Scope 2 figure, not given in the report, could explain the wording), and rounding (aholddelhaize_04).
