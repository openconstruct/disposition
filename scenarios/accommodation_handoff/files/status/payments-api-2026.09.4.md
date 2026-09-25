# payments-api 2026.09.4 — release status

Owner: platform on-call
Original window: Thu 2026-09-24 02:00 UTC
New window: Mon 2026-09-28 02:00 UTC
Status: postponed

## What happened

The staging dry-run of migration 0147 (adds `invoice_batch_id` to
`ledger_entries`) held an ACCESS EXCLUSIVE lock for 11m40s on staging-sized
data. Production `ledger_entries` is roughly nine times larger. Rather than
risk a long lock during APAC business hours, the migration is being rewritten
to add the column without a default and backfill in batches.

## Customer impact

None so far. 2026.09.3 is still live and healthy; nothing is broken.

Batch invoicing — the headline item in .4 — ships with this release, so it
moves to Monday as well.

## Open items

- [x] migration rewrite (PR #2291, Priya reviewing)
- [ ] backfill dry-run on staging — Saturday
- [ ] smoke-check plan for the Monday window — Sam
- [ ] customer-facing note on batch invoicing — Linda asked, not answered yet
