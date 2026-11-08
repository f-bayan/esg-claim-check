# Pilot run

5 items (adyen_01, postnl_01, zalando_03, heineken_01_unit, kpn_04), gpt-6-luna, modes A, B and C, with prompt v0 (prompts/history/v0).

All three modes labeled kpn_04 CANNOT_VERIFY because the table does not show "rising data-driven energy demand". When labeling, causes and background ("due to", "driven by", "despite") were never checked, but this rule was not written down. Rule 12 was added to the prompt and the guidelines after this pilot. No label changed.

The model does not accept temperature 0, so the runs use the default temperature.
