Exports from the distribution tracker.

distributions_2026.csv   one row per site per month
volunteers.csv           total logged volunteer hours per month

food_weight: pounds up to and including June 2026 (the old warehouse
scales). From July 2026 the new scales record kilograms. The column was not
converted.

Exports run on the 1st of each month for the month before.

KNOWN PROBLEMS (please read before using these numbers)

- The Eastgate row for June 2026 is a copy of May: Eastgate closed on
  31 May (see sites.csv). Ignore it.
- food_weight is in pounds up to June and kilograms from July. Convert
  before adding or comparing across July (1 lb = 0.4536 kg).
- Volunteer hours for March are double-counted by the sign-in app. Halve
  March.
- "households" counts visits, not different households. Don't describe it
  as the number of households or people reached.
