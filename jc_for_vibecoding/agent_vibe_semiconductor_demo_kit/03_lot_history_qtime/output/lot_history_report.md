# Lot History UT/QTime Report

Lot: `LOT1001`
Rows analyzed: 5
Time range: 2026-05-01T08:00:00 to 2026-05-02T05:40:00

## Key Observations
- Calculated UT for 5 route steps.
- Found 3 QTime threshold flag(s).
- QTime flag on `PHOTO->ETCH`: 3.25 h > threshold 2.0 h.
- QTime flag on `ASH->METRO`: 6.5 h > threshold 3.0 h.
- QTime flag on `METRO->IMPLANT`: 3.333 h > threshold 2.0 h.

## Top QTime Segments
- `ASH->METRO`: 6.5 h, equipment `ASH02` / chamber `CH1`.
- `METRO->IMPLANT`: 3.333 h, equipment `MET01` / chamber `NA`.
- `PHOTO->ETCH`: 3.25 h, equipment `PHOTO01` / chamber `CH1`.

## Suggested Next Checks
- Check tool availability, chamber queue, recipe version, and hold history around flagged intervals.
- Compare with peer lots using the same product and route if approved data is available.
- Do not use this report alone for lot hold/release decisions.

## Manifest Warnings
- None

## Safety Note
This report is for engineering observation only; no lot disposition decision is made.
