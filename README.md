# ESG Claim Check: can LLMs check sustainability reports against their own tables?

Sustainability reports of large companies are full of sentences like "Scope 2 emissions fell by 22%", and the same report also has a table with these numbers. Most of the time the text and the table match, but this is not always the case. In this project I wanted to see if a language model can check this automatically, and how much better it does than a simple rule-based check.

## Summary

I built a test set of 49 real claims from the FY2025 reports of 10 European companies, and I added 125 synthetic errors to it, and all of them were labeled by hand. 7 of the real claims look inconsistent with their own tables, and 3 of these are clear. A rule-based baseline gets 66% of the items right, while two OpenAI models get 97 to 100% (mean of three runs). The small model is almost as accurate as the large one at about a twentieth of the cost, but it changes its answer between runs on 3 to 5% of the items. When the small model is run three times and only the 6 of 174 items where the answers differ are sent to a person, only 1 error would be left if the person corrects them (signify_01, which is wrong in all three runs), while a single run makes 3 to 7 errors. I simulated this with the gold labels, so no person actually checked these items.

## What I did

### Data

I used the reports of 10 large European companies, which are Adyen, Ahold Delhaize, AkzoNobel, ASML, Heineken, KPN, PostNL, Prosus, Signify and Zalando. All reports cover fiscal year 2025. For Prosus this means April 2024 to March 2025, and its numbers come from its Environmental Impact Report. For the other companies the numbers come from the sustainability statements in the annual report.

From these reports I made a gold set of 49 real claims. Each claim is a sentence from the text together with the table rows it refers to, and I gave each one a label by hand:

- CONSISTENT: the table supports the claim
- INCONSISTENT: the table says something else
- CANNOT_VERIFY: the table does not have what is needed to check the claim

Before labeling, I wrote down the labeling rules ([notes/01_labeling_guidelines.md](notes/01_labeling_guidelines.md)), and I also kept a list of every decision I made along the way.

7 of the 49 claims look inconsistent with their own table, but only 3 of them are clear. The other four could come from rounding, restated figures or a different calculation method, for example market-based and location-based Scope 2. This is why I treat them as possible inconsistencies and not as proven errors by the companies. The column `inconsistency_type` in `data/gold_set.csv` shows which case is which.

### Synthetic items

49 claims is a small number, so I also made 125 synthetic items. For this, I took each correct claim and changed it with a simple rule, such as a different number, the opposite direction, a year that is not in the table, the wrong unit, the wrong scope, or a removed table row. I used rules instead of an LLM, because this way I know exactly what changed in each item. After that, I checked every item by hand, and this showed that some of the rules were not good. For example, when "less than 1%" is changed to "less than 11%", the claim is still true. I fixed these rules and made the items again, and the five bad items that were removed are listed with their reasons in `data/perturbed_removed.csv`.

### Systems

The first system is a baseline without any AI. It finds the numbers in the claim and tries to match them to the table, and it also tries sums, differences, percentage changes and shares.

The other systems are two OpenAI models from the same model family, gpt-6-luna, which is small and cheap, and gpt-6.1-sol, which is larger and about 20 times the list price per token. I used each model in three modes:

- A: the model gives the label directly
- B: the model reasons briefly and then gives the label
- C: the model only points to the table cells for each number in the claim, and Python does the math and chooses the label

All three modes get the same rules in the prompt. I did not put any worked examples in the prompt, because I wanted the comparison between the modes to stay fair and I did not want any test item to leak into the prompt. The prompts are in [prompts/](prompts/), and each setup was run three times.

## Results

The table below shows the results on all 174 items as the mean of three runs. Macro-F1 is the average F1 over the three labels. For the real claims I give the counts for each run, because with only 49 real claims and 7 real inconsistencies one item can change a percentage a lot.

| system | accuracy | macro-F1 (min to max) | real claims correct, out of 49 | real inconsistencies found, out of 7 | label changed between runs |
|---|---|---|---|---|---|
| baseline | 66.1 | 65.7 | 37 | 6 | |
| luna A | 97.5 | 97.0 (95.3 to 98.0) | 47 / 45 / 46 | 6 / 6 / 7 | 6 items (3.4%) |
| luna B | 96.9 | 96.3 (95.8 to 97.0) | 44 / 46 / 44 | 6 / 7 / 6 | 5 items (2.9%) |
| luna C | 97.1 | 97.3 (96.1 to 98.5) | 45 / 47 / 47 | 5 / 5 / 6 | 8 items (4.6%) |
| sol A | 99.8 | 99.8 (99.5 to 100) | 49 / 49 / 48 | 7 / 7 / 6 | 1 item (0.6%) |
| sol B | 100 | 100 (100 to 100) | 49 / 49 / 49 | 7 / 7 / 7 | 0 items |
| sol C | 98.1 | 98.1 (97.8 to 98.3) | 47 / 47 / 47 | 6 / 6 / 6 | 1 item (0.6%) |

The baseline has no randomness, so it was run only once, and the error analysis further below uses run 1. All other tables, including the confidence intervals, significance tests and confusion matrices, are in [results/summary.md](results/summary.md).

The results show that both models are much better than the baseline, with about 97 to 100% against 66%. The biggest gains are on wrong units (the baseline gets 0 of 10 and both models get 10 of 10), wrong scopes and removed rows, and these are the cases where the system has to understand which row a claim is about.

The small model is almost as accurate as the large one at about a twentieth of the cost, but it is less stable. It changed its answer between runs on 3 to 5% of the items, while the large model did this on less than 1% of them.

The three modes performed about the same. In run 1, mode A looks like the best mode for luna, but over three runs the three modes are within about 1 point of each other (mean macro-F1 of 97.0, 96.3 and 97.3), and this difference is within the normal variation between runs. Also, the task turned out to be easy for these models, so this result does not show that reasoning or the Python step would not help on harder data.

Finally, the real claims are harder than the synthetic ones. In run 1, luna gets 98 to 99% accuracy on the synthetic items but 90 to 96% on the real claims, which means that the synthetic set alone would make the models look better than they are.

## What this could mean for a reporting team

These results come from a small and fairly easy test set, so they are only a starting point. Still, they point to a cheap way of working. First, the small model can be used as a first check, because it is about 97% accurate on this set and it costs well under a cent per claim, even for three runs. Second, the model can be run three times, and the items where the answers differ can be sent to a person. For luna A this flags 6 of 174 items, and if a person corrects them only one error would be left (signify_01, which is wrong in all three runs), while a single run makes 3 to 7 errors. This is a simulation with the gold labels and not a real human check. This works less well for luna B, where 3 errors are wrong in all three runs. Third, a person should still look at vague wording and at definitions, because the hard cases were words like "slightly" or "in line", targets that are not in the table, and possible definition differences such as market-based and location-based Scope 2. The numbers for the second point are in the section "Flagging unstable items for review" in [results/summary.md](results/summary.md).

## Error analysis

I read every wrong answer in run 1, and the full analysis is in [notes/03_error_analysis.md](notes/03_error_analysis.md). None of the 19 errors (prompt v2, run 1) seem to come from a calculation mistake. Mode A does not give any reasoning, so for its 3 errors this is a best guess. I put the errors into five groups:

| group | errors | example |
|---|---|---|
| too cautious | 6 | the math is right, but "the table does not say this total covers Scope 1, 2 and 3" |
| right number, wrong row | 2 | the claim says 65%, the right row says 63, and another row says 65 |
| changed year read as a contradiction | 3 | "(2021: 3,748)" when the table gives 3,748 for 2024 |
| vague words | 6 | "remained in line" turned into "did not change" in mode C |
| mistakes in filling in the facts | 2 | mode C marked a number as missing instead of wrong |

The answers that change between runs are also mostly on these same hard items.

## How the prompt changed

I changed the prompt two times, and I kept every version in [prompts/history/](prompts/history/). Version v0 was used in a pilot with 5 items. In this pilot, all three modes failed on one claim because of its "despite rising demand" part, and this happened because I had never written down that causes are not checked, so I added this rule in v1. Version v1 was used in the first full run with luna. After this run, an audit found some more rules that I had used while labeling but had never written down, mainly about target remarks, numbers inside cause parts and vague size words, and these rules went into v2. No gold label changed.

Since I wrote v2 after I had seen the v1 results, `results/summary.md` reports the 7 items that v2 was aimed at separately and also gives the scores without them. The v1 results are kept in `results/llm/v1/`. For luna, v1 and v2 differ on only a few items in each mode (exact McNemar p of 0.69, 1.00 and 1.00 for A, B and C), and this is about as many items as change between two runs.

## Limits

This project has some limits. There are only 49 real claims and 7 possible inconsistencies, so one item can change the recall a lot. I labeled everything myself, and there is no second annotator. The large model reaches the ceiling, which means that this set cannot show the differences between strong models. In addition, the right table is given with each claim, while in practice the hard part is finding that table in a report of up to 350 pages, and this is not tested here. The models do not accept temperature 0, so they run at their default temperature. Also, the reports are public, so the models may have seen them during training. More details are in [notes/02_known_limits.md](notes/02_known_limits.md).

## Next step

Because the test set is too easy for the large model, it cannot show real differences between the models or the modes. The most useful next step is to remove the given table and let the system first find the right table in the full report and then check the claim, and to measure how much the accuracy drops. Even 2 or 3 full reports would give a first idea.

## Cost

Each request has about 800 input tokens in modes A and B and about 1,500 in mode C. The replies are under 10 tokens in mode A and up to about 300 in modes B and C. One full run of both models in all three modes costs about $1.20, and luna alone costs about ten cents (based on the bill after the first luna run). All runs together, which are the pilot, v1 and the three runs of v2, were about 3,700 requests and cost $3.72.

## Repository

| path | what it is |
|---|---|
| `data/gold_set.csv` | the 49 real claims with evidence, label, calculation and comments |
| `data/perturbed.csv` | the 125 synthetic items, all checked by hand |
| `data/perturbed_removed.csv` | the 5 synthetic items that were removed after the hand check, with reasons |
| `data/gold_set_extra.csv` | 22 extra Prosus and Signify claims that I collected while learning the task, not used in the evaluation |
| `notes/` | labeling guidelines, climate page index, known limits and error analysis |
| `prompts/` | the current prompts, and the earlier versions in `history/` |
| `scripts/00_find_climate_pages.py` | finds the climate pages in each PDF |
| `scripts/02_make_perturbations.py` | makes the synthetic items |
| `scripts/03_baseline.py` | the rule-based baseline |
| `scripts/04_run_llm.py` | sends the prompts to the OpenAI API and saves the replies |
| `scripts/mode_c.py` | turns the mode C facts into a label |
| `scripts/05_evaluate.py` | computes all scores and writes `results/summary.md` and `results/errors.csv` |
| `results/` | the baseline output, all model replies and the summary |
| `tests/` | tests for the baseline and mode C |

There is no script 01, because I made the gold set by hand.

## Reproduce

You need Python 3.10 or later, and `pdftotext` (poppler) only for script 00.

```
pip install -r requirements.txt
python3 tests/test_baseline.py
python3 tests/test_mode_c.py
python3 scripts/02_make_perturbations.py
python3 scripts/03_baseline.py
python3 scripts/05_evaluate.py
```

The model replies are already in `results/llm/`, so the evaluation runs without an API key. To run a model again, put `OPENAI_API_KEY=...` in a file called `.env` and run, for example:

```
python3 scripts/04_run_llm.py --model gpt-6-luna --mode A --run 4
```

Note that `05_evaluate.py` only reads runs 1 to 3. The report PDFs are not included in this repository, but they are public on the website of each company.

## License

The code and my annotations are under the MIT license (see [LICENSE](LICENSE)). The claim texts and table rows in `data/` and `results/` are short excerpts from the public reports of the companies, and they are included so that the evaluation can be reproduced. They are not covered by the MIT license, and their copyright stays with the companies.
