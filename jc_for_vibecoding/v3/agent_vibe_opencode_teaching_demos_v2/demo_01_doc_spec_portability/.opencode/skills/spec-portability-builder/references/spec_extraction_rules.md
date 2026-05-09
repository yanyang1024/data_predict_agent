# Spec Extraction Rules

Extract only normative statements into the normalized rules file. Keep examples, ambiguity logs, and open questions separate. Do not silently resolve contradictions.

Preferred intermediate shape:

```json
{
  "schema_version": "...",
  "source_spec": "...",
  "rules": {},
  "human_review_required": []
}
```
