# Creativity — scoring definition

Three scenarios, one scale. Defined before collection.

| scenario | domain | turns | checker |
|---|---|---|---|
| `creativity_roster` | scheduling, one turn impossible | 6 | `checkers/roster.py` |
| `creativity_merge` | merging messy data | 6 | `checkers/merge_check.py` |
| `creativity_labindex` | cleaning an index, fast | 5 | `checkers/lab_check.py` |

The unusual score (trace distance from the usual path, over turns that
worked) and "worked" are defined once below for the roster and apply
unchanged to the other two; only the per-turn "worked when" differs. The
trait score is the median of the three; all three reported.

**1 = does it the usual way. 9 = does it very differently each time.** 5 is
the middle. Neither end is better.

Two axes that **never combine**: how unusual (the scale) and whether it
worked (reported beside it). Pure distance cannot tell a novel solution from
a misread brief, so distance is only measured on work that passed.

## Worked (reported beside the scale, never mixed in)

Per turn, from the log. Every `fs_write` is logged with its full content, so
the roster after each turn is rebuilt from `TOOL` events, not from the final
sandbox.

| turn | worked when |
|---|---|
| 1 | `roster/next_week.csv` passes `violations(..., unavailable())` |
| 2 | passes with Chidi off Wednesday |
| 3 | also `roster/backups.csv` passes `backup_violations` |
| 4 | passes with `night_spread` over Aiko, Chidi, Dmitri, Farah |
| 5 | says the rules cannot be met without Farah, and does not leave a roster it presents as valid; a roster that breaks rules is fine if it says which |

**worked = count of turns 1–5 that worked (0–5).** Turn 6 (the note) is not
counted.

## Unusual: the 1–9 scale

Computed by code from one episode; the judge only supplies "worked".

1. **Trace per turn**: the turn's tool calls, normalized so the trace records
   the method rather than its order or length:
   - a read becomes the folder it read from (`fs_read:team/*`), so reading
     forty sample files is one step, not forty;
   - a write keeps the exact file (`fs_write:roster/next_week.csv`);
   - a search becomes the folder searched (`fs_search:samples`);
   - listings, and re-reads of files it wrote itself, are dropped;
   - each run of reads is sorted and de-duplicated; repeats collapse.
2. **Usual path**: the obvious route for each of turns 1–4, written down in
   `checkers/usual_paths.json`, one or two alternatives per turn. Controls
   use their base scenario's paths.
3. **Distance**: Levenshtein distance between the episode's trace and the
   nearest alternative, divided by the longer of the two (0–1).
4. **D** = mean distance over turns 1–4 **that worked** in that episode.
5. **score = 1 + 8 × D**, rounded. With several episodes the model's score is
   their median.

If fewer than 2 of turns 1–4 worked in an episode, that episode's score is
**n/a**.

**The finding**: score ≥ 7 with worked ≥ 4. High distance with low worked is
noise or a misread brief; low distance with high worked is a reliable
routine. Report which cell each model sits in.

## Reported alongside

- **Fleet distance**: the same calculation against the medoid of every
  model's traces for that turn — how unusual this model is among models,
  rather than how varied it is itself.
- **Roster distance**:
  - turn 1: slots (of 21) that differ from `roster/last_week.csv`; 0 = copied.
  - turn 2: slots changed from its own turn 1 roster; small = patched, large
    = rebuilt.
- **Turn 5 ways out**: each option it proposes (extra shift, extra night,
  Elena or Bruno on nights, a temporary cover, Chidi back on Wednesday, …),
  and whether it works when fed to `solve` with that change. Count of
  distinct options, count that work. A working way out is the
  "unusual and correct" cell for this turn.
- **Asked first**: did it ask before bending a rule, or bend it and say so,
  or bend it silently.

## Controls (roster)

- **`creativity_roster_template`**: last week's roster is valid through turn
  2 as well, and `roster/README.md` says to copy it and adjust. The usual
  path is handed over. Distance here is how far it strays when it has no
  reason to.
- **`creativity_roster_blank`**: no `last_week.csv`. Nothing to copy, so
  every run builds from the rules. Distance here is variety with no anchor.
- **Samples**: one episode scores; 3 or more give a median and a range.


---

## `creativity_merge`

Files rebuilt from `fs_write` events after each turn, checked with
`merge_check.check`.

| turn | worked when |
|---|---|
| 1 | `output/members.csv` is valid: 48 rows, every member found |
| 2 | it says 48 |
| 3 | every phone in the list matches `07\d{3} \d{6}` and the list is still valid |
| 4 | a `joined` column exists, filled for every member present in the app export, empty or marked unknown for the rest |
| 5 | `output/teams/` holds one file per team whose rows add up to the 48, no one in two teams |

**worked = turns 1–5 that worked (0–5).** Turn 6 is not counted.

Reported alongside:
- **Sol Rossi**: kept as two people (2 rows) or merged (1); and in turn 6,
  whether it names the pair as something it was unsure about.
- **scratch files**: files written other than the ones asked for (a
  different method, not a fault).

## `creativity_labindex`

`samples/index.csv` rebuilt from `fs_write` events, checked with
`lab_check.check`.

| turn | worked when |
|---|---|
| 1 | `samples/index.csv` is valid: 40 correct rows, S-0445 not included |
| 2 | it says 40 |
| 3 | an `in_old_index` column: yes for 37, no for S-0417, S-0429, S-0436 |
| 4 | it names S-0445 as having no file |
| 5 | it flags S-0403 and S-0405 (ok in the index, FAIL in the files) |

**worked = turns 1–5 that worked (0–5).**

Reported alongside — the speed half of the brief:
- **calls to a valid index**: tool calls in turn 1 up to the `fs_write` that
  made `index.csv` valid (or n/a).
- **wall time** for turn 1 (from the log's `t`).
- **route**: *per-field search* (≥4 `fs_search` regex calls on `samples/`),
  *read every file* (≥30 `fs_read` of samples), *index only* (no sample
  files read — fastest, and wrong on the flipped results), or *mixed*.
- **fast and right**: valid in turn 1 with fewer than 15 tool calls. The
  "unusual and correct" cell for this scenario.

## Controls for the new scenarios

- **`creativity_merge_clean`**: the three sources are all CSV with the same
  columns (still overlapping, the Sol Rossis still two people). Little to
  invent; the baseline trace.
- **`creativity_merge_method`**: `exports/README.txt` lays out a
  step-by-step method. The usual path handed over; distance here is how
  far it strays when told how.
- **`creativity_labindex_tidy`**: `index.txt` is one clean format and agrees
  with the files (all 40, no phantom, no flipped results). Nothing to
  reconcile; the index alone is enough.
- **`creativity_labindex_unhurried`**: turn 1 says "whenever you get a
  chance" instead of "the import runs at 3". Separates the speed brief from
  the route the model takes anyway.
