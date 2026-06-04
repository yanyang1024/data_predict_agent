# Etch Multi-Agent Output Schema

## Final Report Structure

```markdown
# Etch Multi-Agent Recommendation Report

## 1. User Objective
[Original user request]

## 2. Input Summary
- Layer type:
- RCP parameters:
- Objectives:
- Constraints:
- APIs available:

## 3. Agents Executed

| Agent | Status | Key Output | Limitation |
|-------|--------|------------|------------|
| etch-mechanism | ✅ | qualitative hints | placeholder only |
| etch-literature | ⚠️ | query plan only | API unavailable |
| ... | | | |

## 4. Recommendation Summary

| Rank | Candidate | Evidence Level | Constraint | Action |
|------|-----------|---------------|------------|--------|
| 1 | ... | A/B/C/D/E | PASS/WARN/FAIL | ... |
| 2 | ... | ... | ... | ... |

## 5. Evidence Level Definitions
- **Level A**: data + constraint + mechanism aligned
- **Level B**: data-supported with constraint warnings
- **Level C**: mechanism/literature supported only
- **Level D**: DOE exploration only
- **Level E**: insufficient evidence

## 6. Constraint Check Results
[PASS / WARNING / FAIL / UNKNOWN per constraint]

## 7. DOE Validation Plan
[If applicable, suggested design + factors + runs]

## 8. Risks
[List of process, equipment, or data risks]

## 9. Next Steps
[Recommended actions]

## 10. Generated Files
[Any files produced by the agents]
```

## Evidence Table Format

```json
{
  "recommendations": [
    {
      "rank": 1,
      "parameter_set": { "pressure": 45, "bias_power": 110 },
      "predicted_metrics": {},
      "evidence_level": "B",
      "constraint_status": "WARNING",
      "supported_by": ["data", "constraint"],
      "notes": "Data supports but constraint shows historical space warning"
    }
  ]
}
```
