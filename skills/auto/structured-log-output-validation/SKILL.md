---
name: structured-log-output-validation
description: Use when producing normalized log summaries with per-category counts and ordered error records.
---
- Normalize category labels exactly as specified before grouping or sorting.
- Determine whether counts represent distinct log records or repeated events; use repeat or occurrence metadata when the contract calls for event totals.
- Sort records by the required category and timestamp keys in the specified direction.
- Include all required schema and generator metadata, and validate both metadata values and output structure.
- Reconcile aggregate counts against the records and repeat totals to catch mismatches before saving.
