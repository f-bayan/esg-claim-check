# Known limits

## Baseline (no AI)
- It does not know which row a claim is about, so scope swaps often pass.
- It only tries x1000 and x0.001 for units, so all 10 unit errors pass.
- Claims without numbers ("significantly lower", "remained stable") get CANNOT_VERIFY.
- It tries many sums, differences and shares, so a wrong number can match by chance.
- Unsigned % rows (for example "% reduction vs baseline") cannot show direction.

## Mode C (LLM reads, Python calculates)
- Vague size words such as "slightly" or "in line" are not listed as facts in mode C, so prosus_10 ("increased slightly" while the market-based Scope 1 and 2 of the PayU segment rose about 5 times) cannot be caught there.
- Rules 11 to 13 of prompt v2 were written after the v1 run. They match how the gold labels were made, but the 7 items they were aimed at (prosus_10, adyen_03, postnl_05, asml_02, aholddelhaize_04, prosus_24, prosus_24_number) are reported separately when comparing v1 and v2.
- asml_05 is hard: the table shows gross business travel (65 -> 32), while the claim is about the SAF reduction (28 kt). A model could call this INCONSISTENT, but none did. Gold is CANNOT_VERIFY.
- If the claim says Scope 2 without the method, mode C uses the market-based row, while modes A and B may accept either. No current item depends on this.
- Facts that cite precomputed % change rows or columns are rejected as INVALID, because tables use different sign conventions.

## Data and design
- "Stable" (under 1%) means relative change in mode_c.py. The prompt does not say relative or percentage points, which matters for shares (adyen_03, 84% to 82%).
- 11 of 32 drop_row items keep only the table header, which makes them easy.
- Year items can be solved by string matching (the baseline gets 30/30).
- The models reject temperature 0, so they run at the default temperature. Each system was run three times. The main tables use run 1. luna changed its label on 3 to 5% of items between runs, sol on less than 1%.
- The reports are public, so the models may have seen them in training.
- The tables are given with the claim. Finding the right table in a long report, which is the harder part in practice, is not tested.

