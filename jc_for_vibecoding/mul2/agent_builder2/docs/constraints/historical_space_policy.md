# Historical Space Risk Policy

## Purpose
Detect when a candidate parameter set falls outside the range of historical data. Extrapolation beyond known data carries higher risk.

## Policy
1. For each numeric RCP parameter, record the min and max observed in historical data.
2. If a candidate parameter value is outside the historical range, mark it as WARNING.
3. WARNING does not block the candidate but signals that predictions for that region are extrapolations.
4. If no historical range is defined for a parameter, return UNKNOWN.

## Fallback Behavior
When historical data is unavailable:
- All parameters return UNKNOWN for historical space check.
- The constraint summary notes "No historical data for space comparison."
- Candidates are evaluated solely on boundary constraints and CD rules.
