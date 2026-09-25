# Incident folder -- read first

What we don't have for last night:

- No logs from 23:04 to 23:24. Log rotation deleted them. Whatever changed
  just before the first error is not recorded anywhere.
- No record of who set DB_POOL_SIZE to 5, or when. The file is edited on the
  host and not tracked. Everyone asked says it wasn't them.
- No order numbers from 23:20 to 00:05. The metrics sidecar died with the
  pod, so we can't say how many customers were affected.
