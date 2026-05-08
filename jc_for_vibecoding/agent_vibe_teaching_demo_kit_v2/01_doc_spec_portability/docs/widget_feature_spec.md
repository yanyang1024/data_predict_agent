# Widget event monitor functional spec v1.2

This is a platform-neutral document. Any platform implementation must preserve these requirements.

## Requirements

- REQ-1 Input: read a CSV file containing `timestamp`, `component`, `severity`, and `message`.
- REQ-2 Normalize: trim whitespace from component names and convert severity to integer.
- REQ-3 Filter: keep events whose severity is greater than or equal to the configured threshold.
- REQ-4 Summarize: count retained events by component and include total retained count.
- REQ-5 Emit: write a JSON report with fields `threshold`, `total_retained`, and `by_component`.

## Portability standard

- Do not mix platform-neutral business logic with platform SDK calls.
- Use an adapter layer for platform-specific input/output APIs.
- Keep requirement IDs in comments or traceability output.
- Use examples only as style references; do not copy unsupported SDK calls.
