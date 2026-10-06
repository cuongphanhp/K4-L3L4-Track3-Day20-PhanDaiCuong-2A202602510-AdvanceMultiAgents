---
name: precise-monetary-data-cleaning
description: Use when transforming financial records into structured summaries and cleaned data files.
---
- Parse and calculate monetary values with decimal-safe arithmetic; convert to integer cents wherever the output contract requires cents.
- Deduplicate by the specified entity before calculating distinct-entity outputs, but count input rows before deduplication when metadata asks for the original row total.
- Exclude unknown amounts from outputs that require known amounts, and make the distinct-known-entity count consistent with the cleaned records.
- Normalize timestamps to UTC and the exact required format; map categories to their specified canonical spellings.
- Match every required output schema, field order, and metadata value to the task contract, then validate the serialized files.
