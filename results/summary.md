# Results

174 items: 49 real claims and 125 synthetic items. INVALID counts as wrong. Mode C labels are recomputed from the stored replies with the current mode_c.py. 95% intervals use 2000 bootstrap resamples (seed 0) that draw whole source claims, so a real claim and its synthetic versions stay together. p-values use the exact McNemar test and are not corrected for the number of comparisons. The models reject temperature 0, so they run at their default temperature. Each system was run three times. The main tables use run 1, and the section Repeated runs shows all three.

## Overall

| system | accuracy | macro-F1 | 95% CI | real macro-F1 | 95% CI | synthetic accuracy | INVALID |
|---|---|---|---|---|---|---|---|
| baseline | 66.1 | 65.7 | 59.0 to 72.0 | 62.9 | 46.8 to 77.3 | 62.4 | 0 |
| gpt-6-luna A | 98.3 | 98.0 | 95.4 to 100.0 | 94.7 | 83.9 to 100.0 | 99.2 | 0 |
| gpt-6-luna B | 96.6 | 96.0 | 92.7 to 98.8 | 88.0 | 75.2 to 97.3 | 99.2 | 0 |
| gpt-6-luna C | 96.0 | 96.1 | 92.2 to 98.9 | 89.0 | 73.6 to 99.5 | 97.6 | 1 |
| gpt-6.1-sol A | 100.0 | 100.0 | 100.0 to 100.0 | 100.0 | 100.0 to 100.0 | 100.0 | 0 |
| gpt-6.1-sol B | 100.0 | 100.0 | 100.0 to 100.0 | 100.0 | 100.0 to 100.0 | 100.0 | 0 |
| gpt-6.1-sol C | 98.3 | 98.3 | 95.1 to 100.0 | 93.0 | 80.0 to 100.0 | 99.2 | 0 |

The synthetic items contain no CONSISTENT claims, so only accuracy is shown for them.

## Recall per label, real claims

| system | CONSISTENT (n=33) | INCONSISTENT (n=7) | CANNOT_VERIFY (n=9) |
|---|---|---|---|
| baseline | 28/33 | 6/7 | 3/9 |
| gpt-6-luna A | 32/33 | 6/7 | 9/9 |
| gpt-6-luna B | 29/33 | 6/7 | 9/9 |
| gpt-6-luna C | 31/33 | 5/7 | 9/9 |
| gpt-6.1-sol A | 33/33 | 7/7 | 9/9 |
| gpt-6.1-sol B | 33/33 | 7/7 | 9/9 |
| gpt-6.1-sol C | 32/33 | 6/7 | 9/9 |

## Accuracy per perturbation type

| system | number (n=25) | direction (n=22) | year (n=30) | unit (n=10) | scope (n=6) | drop_row (n=32) |
|---|---|---|---|---|---|---|
| baseline | 19/25 | 15/22 | 30/30 | 0/10 | 1/6 | 13/32 |
| gpt-6-luna A | 25/25 | 22/22 | 29/30 | 10/10 | 6/6 | 32/32 |
| gpt-6-luna B | 25/25 | 22/22 | 29/30 | 10/10 | 6/6 | 32/32 |
| gpt-6-luna C | 24/25 | 22/22 | 28/30 | 10/10 | 6/6 | 32/32 |
| gpt-6.1-sol A | 25/25 | 22/22 | 30/30 | 10/10 | 6/6 | 32/32 |
| gpt-6.1-sol B | 25/25 | 22/22 | 30/30 | 10/10 | 6/6 | 32/32 |
| gpt-6.1-sol C | 25/25 | 22/22 | 29/30 | 10/10 | 6/6 | 32/32 |

## Paired check

A pair is an original CONSISTENT claim and one of its synthetic versions. Both right means the system labels both correctly. All right means the original and all its versions are correct.

| system | both right (pairs) | all right (claims) |
|---|---|---|
| baseline | 55.2 (n=125) | 18.2 (n=33) |
| gpt-6-luna A | 96.0 (n=125) | 93.9 (n=33) |
| gpt-6-luna B | 86.4 (n=125) | 84.8 (n=33) |
| gpt-6-luna C | 92.0 (n=125) | 87.9 (n=33) |
| gpt-6.1-sol A | 100.0 (n=125) | 100.0 (n=33) |
| gpt-6.1-sol B | 100.0 (n=125) | 100.0 (n=33) |
| gpt-6.1-sol C | 96.0 (n=125) | 97.0 (n=33) |

## Items the v2 prompt changes were aimed at

Prompt v2 was written after the v1 run. These 7 items are the ones its changes were aimed at, so they are shown separately and macro-F1 without them is given. The v1 rows use the v1 replies with the current mode_c.py, which fixed a unit bug. Stored v1 labels differ for adyen_01_unit, adyen_02_unit and adyen_04_unit. The 5 pilot items (adyen_01, heineken_01_unit, kpn_04, postnl_01, zalando_03) were also seen during prompt writing and are still scored.

| system | adyen_03 | aholddelhaize_04 | asml_02 | postnl_05 | prosus_10 | prosus_24 | prosus_24_number | macro-F1 without them |
|---|---|---|---|---|---|---|---|---|
| baseline | ok | ok | ok | ok | ok | ok | ok | 63.9 |
| gpt-6-luna A | ok | ok | ok | ok | ok | ok | ok | 97.9 |
| gpt-6-luna B | ok | CANNOT_VERIFY | CANNOT_VERIFY | CANNOT_VERIFY | ok | ok | ok | 97.9 |
| gpt-6-luna C | INCONSISTENT | ok | ok | ok | CANNOT_VERIFY | ok | ok | 97.1 |
| gpt-6.1-sol A | ok | ok | ok | ok | ok | ok | ok | 100.0 |
| gpt-6.1-sol B | ok | ok | ok | ok | ok | ok | ok | 100.0 |
| gpt-6.1-sol C | INCONSISTENT | ok | ok | ok | CANNOT_VERIFY | ok | ok | 99.5 |
| gpt-6-luna A (v1) | ok | CONSISTENT | CANNOT_VERIFY | CANNOT_VERIFY | ok | ok | ok | 98.7 |
| gpt-6-luna B (v1) | ok | CONSISTENT | CANNOT_VERIFY | CANNOT_VERIFY | ok | ok | ok | 98.4 |
| gpt-6-luna C (v1) | INCONSISTENT | ok | ok | ok | CANNOT_VERIFY | INVALID | INVALID | 99.0 |

## Comparisons (all 174 items)

Only first right counts items the first system gets right and the second gets wrong.

| first | second | only first right | only second right | p |
|---|---|---|---|---|
| gpt-6-luna A | baseline | 58 | 2 | 0.000 |
| gpt-6.1-sol A | baseline | 59 | 0 | 0.000 |
| gpt-6-luna A | gpt-6-luna B | 5 | 2 | 0.453 |
| gpt-6-luna A | gpt-6-luna C | 5 | 1 | 0.219 |
| gpt-6-luna B | gpt-6-luna C | 7 | 6 | 1.000 |
| gpt-6.1-sol A | gpt-6.1-sol B | 0 | 0 | 1.000 |
| gpt-6.1-sol A | gpt-6.1-sol C | 3 | 0 | 0.250 |
| gpt-6.1-sol B | gpt-6.1-sol C | 3 | 0 | 0.250 |
| gpt-6.1-sol A | gpt-6-luna A | 3 | 0 | 0.250 |
| gpt-6.1-sol B | gpt-6-luna B | 6 | 0 | 0.031 |
| gpt-6.1-sol C | gpt-6-luna C | 4 | 0 | 0.125 |
| gpt-6-luna A | gpt-6-luna A (v1) | 4 | 2 | 0.688 |
| gpt-6-luna B | gpt-6-luna B (v1) | 0 | 1 | 1.000 |
| gpt-6-luna C | gpt-6-luna C (v1) | 2 | 3 | 1.000 |

## Hard real claims

Real claims that at least two LLM systems got wrong.

| claim | gold | wrong in |
|---|---|---|
| akzonobel_03 | INCONSISTENT | gpt-6-luna A, gpt-6-luna C |
| signify_01 | CONSISTENT | gpt-6-luna A, gpt-6-luna B |
| adyen_03 | CONSISTENT | gpt-6-luna C, gpt-6.1-sol C |
| prosus_10 | INCONSISTENT | gpt-6-luna C, gpt-6.1-sol C |

## Agreement between modes

| model | A and B | A and C | B and C | wrong in all three | majority vote correct |
|---|---|---|---|---|---|
| gpt-6-luna | 167/174 | 168/174 | 161/174 | 0 | 171/174 |
| gpt-6.1-sol | 174/174 | 171/174 | 171/174 | 0 | 174/174 |

When all three modes disagree, the vote uses mode A.

## v1 to v2 changes for luna

| mode | fixed | broken | fixed items not aimed at by v2 | broken items |
|---|---|---|---|---|
| A | 4 | 2 | adyen_03_year | akzonobel_01_year, akzonobel_03 |
| B | 0 | 1 | - | adyen_02_year |
| C | 2 | 3 | - | aholddelhaize_02, akzonobel_03, asml_01_number |

Items that change without being aimed at show how much a single run varies.

## Repeated runs

Each system was run three times with the same prompts. Changed label means the share of items that did not get the same label in all three runs.

| system | accuracy per run | macro-F1 mean (min to max) | changed label | wrong in at least one run |
|---|---|---|---|---|
| gpt-6-luna A | 98.3 / 96.0 / 98.3 | 97.0 (95.3 to 98.0) | 6/174 (3.4) | 7 |
| gpt-6-luna B | 96.6 / 97.7 / 96.6 | 96.3 (95.8 to 97.0) | 5/174 (2.9) | 8 |
| gpt-6-luna C | 96.0 / 98.3 / 97.1 | 97.3 (96.1 to 98.5) | 8/174 (4.6) | 9 |
| gpt-6.1-sol A | 100.0 / 100.0 / 99.4 | 99.8 (99.5 to 100.0) | 1/174 (0.6) | 1 |
| gpt-6.1-sol B | 100.0 / 100.0 / 100.0 | 100.0 (100.0 to 100.0) | 0/174 (0.0) | 0 |
| gpt-6.1-sol C | 98.3 / 98.3 / 97.7 | 98.1 (97.8 to 98.3) | 1/174 (0.6) | 4 |

## Three-run summary

Means over runs 1 to 3. Real counts are correct answers out of 49 real claims, and found counts are real INCONSISTENT claims found out of 7, given per run.

| system | accuracy mean | macro-F1 mean (min to max) | real correct per run | real INCONSISTENT found per run |
|---|---|---|---|---|
| baseline | 66.1 | 65.7 | 37 | 6 |
| gpt-6-luna A | 97.5 | 97.0 (95.3 to 98.0) | 47 / 45 / 46 | 6 / 6 / 7 |
| gpt-6-luna B | 96.9 | 96.3 (95.8 to 97.0) | 44 / 46 / 44 | 6 / 7 / 6 |
| gpt-6-luna C | 97.1 | 97.3 (96.1 to 98.5) | 45 / 47 / 47 | 5 / 5 / 6 |
| gpt-6.1-sol A | 99.8 | 99.8 (99.5 to 100.0) | 49 / 49 / 48 | 7 / 7 / 6 |
| gpt-6.1-sol B | 100.0 | 100.0 (100.0 to 100.0) | 49 / 49 / 49 | 7 / 7 / 7 |
| gpt-6.1-sol C | 98.1 | 98.1 (97.8 to 98.3) | 47 / 47 / 47 | 6 / 6 / 6 |

## Flagging unstable items for review

A simple rule for a reporting team: run the cheap model three times and send an item to a person when the three answers differ. An item whose answers differ is always wrong in at least one run, so all flagged items reach a person. Errors left after review counts items that are wrong in all three runs, which flagging cannot catch.

| system | items flagged | errors per single run | errors left after review |
|---|---|---|---|
| gpt-6-luna A | 6 | 3 / 7 / 3 | 1 (signify_01) |
| gpt-6-luna B | 5 | 6 / 4 / 6 | 3 (asml_02, postnl_05, signify_01) |
| gpt-6-luna C | 8 | 7 / 3 / 5 | 1 (prosus_10) |
| gpt-6.1-sol A | 1 | 0 / 0 / 1 | 0 (-) |
| gpt-6.1-sol B | 0 | 0 / 0 / 0 | 0 (-) |
| gpt-6.1-sol C | 1 | 3 / 3 / 4 | 3 (adyen_03, adyen_03_year, prosus_10) |

## Confusion matrices, all items

Rows are gold labels, columns are predictions.

**baseline**

| gold \ pred | CONSISTENT | INCONSISTENT | CANNOT_VERIFY | INVALID |
|---|---|---|---|---|
| CONSISTENT | 28 | 0 | 5 | 0 |
| INCONSISTENT | 24 | 40 | 3 | 0 |
| CANNOT_VERIFY | 5 | 22 | 47 | 0 |

**gpt-6-luna A**

| gold \ pred | CONSISTENT | INCONSISTENT | CANNOT_VERIFY | INVALID |
|---|---|---|---|---|
| CONSISTENT | 32 | 0 | 1 | 0 |
| INCONSISTENT | 1 | 66 | 0 | 0 |
| CANNOT_VERIFY | 0 | 1 | 73 | 0 |

**gpt-6-luna B**

| gold \ pred | CONSISTENT | INCONSISTENT | CANNOT_VERIFY | INVALID |
|---|---|---|---|---|
| CONSISTENT | 29 | 0 | 4 | 0 |
| INCONSISTENT | 0 | 66 | 1 | 0 |
| CANNOT_VERIFY | 0 | 1 | 73 | 0 |

**gpt-6-luna C**

| gold \ pred | CONSISTENT | INCONSISTENT | CANNOT_VERIFY | INVALID |
|---|---|---|---|---|
| CONSISTENT | 31 | 1 | 0 | 1 |
| INCONSISTENT | 1 | 64 | 2 | 0 |
| CANNOT_VERIFY | 0 | 2 | 72 | 0 |

**gpt-6.1-sol A**

| gold \ pred | CONSISTENT | INCONSISTENT | CANNOT_VERIFY | INVALID |
|---|---|---|---|---|
| CONSISTENT | 33 | 0 | 0 | 0 |
| INCONSISTENT | 0 | 67 | 0 | 0 |
| CANNOT_VERIFY | 0 | 0 | 74 | 0 |

**gpt-6.1-sol B**

| gold \ pred | CONSISTENT | INCONSISTENT | CANNOT_VERIFY | INVALID |
|---|---|---|---|---|
| CONSISTENT | 33 | 0 | 0 | 0 |
| INCONSISTENT | 0 | 67 | 0 | 0 |
| CANNOT_VERIFY | 0 | 0 | 74 | 0 |

**gpt-6.1-sol C**

| gold \ pred | CONSISTENT | INCONSISTENT | CANNOT_VERIFY | INVALID |
|---|---|---|---|---|
| CONSISTENT | 32 | 1 | 0 | 0 |
| INCONSISTENT | 0 | 66 | 1 | 0 |
| CANNOT_VERIFY | 0 | 1 | 73 | 0 |
