# CD Constraint Policy

## Constrained CD Metrics

| Metric | Description | Typical Risk |
|--------|-------------|-------------|
| Bias CD | CD after bias step | CD budget violation |
| Bottom CD | Bottom CD after etch | Profile/taper issue |
| Max CD | Maximum CD on feature | Bridging/merging risk |

## Constraint Rules

1. Each of the three CD metrics must have a min and max defined by the process owner.
2. If min or max is null, the constraint check returns UNKNOWN for that metric.
3. FAIL is returned if any CD metric exceeds its defined range.
4. The constraint agent does not assume default values — UNKNOWN is safer than guessing.

## How CD Constraints Are Checked

The constraint-check tool receives predicted CD values (from Data Agent or user input) and compares them against the defined ranges. If predicted values are missing, the tool returns UNKNOWN for CD checks.
