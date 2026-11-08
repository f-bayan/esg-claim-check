# Prompt v1 results

Full run of gpt-6-luna (modes A, B and C, 174 items) with prompt v1 (prompts/history/v1).

After this run, an audit compared the prompts with the labeling guidelines and found rules that were used when labeling but were not written in the prompt. Prompt v2 adds them. No gold label changed after this run (aholddelhaize_04 was changed before it).

- Rule 7: the segment exception now says "the only company named for a segment", as in the guidelines.
- Rule 11: a remark that a target was met is only checked if the target value is given.
- Rule 12: up/down words inside a cause part are not checked, but numbers written there are.
- Rule 13 (new): vague size words need a clear contradiction. Mode C does not list them as facts.
- Mode C: if the table already gives a share as a percentage, use type "value". This caused the two INVALID results here (prosus_24, prosus_24_number).

The evidence of asml_05 was also corrected after this run (the placeholder "see table" was replaced by the real row).

The examples in the new rules use words that are not in the data. The 7 items v2 was aimed at (prosus_10, adyen_03, postnl_05, asml_02, aholddelhaize_04, prosus_24, prosus_24_number) are reported separately.

These results are kept so the effect of the prompt change can be reported.
