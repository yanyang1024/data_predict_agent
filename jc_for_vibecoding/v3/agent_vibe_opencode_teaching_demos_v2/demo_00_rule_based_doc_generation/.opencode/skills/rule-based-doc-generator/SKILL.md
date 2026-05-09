---
name: rule-based-doc-generator
description: use when the user asks to generate structured teaching, project-status, meeting-progress, dashboard, gantt, ppt, excel, or briefing artifacts from a short natural-language request using approved templates and deterministic generation scripts in an opencode project.
---

# Rule-Based Document Generator

## Purpose

Turn a short user request into stable, reviewable teaching artifacts by using explicit templates, data files, and approved generation scripts.

## Workflow

1. Read the user request and identify:
   - topic;
   - current progress;
   - timebox;
   - target outputs;
   - open questions.
2. Read `configs/course_template.yaml` and `data/course_progress.json`.
3. Do not directly author final PPT or Excel content in conversation. Use the approved generator script.
4. Run:

```bash
python3 scripts/generate_training_artifacts.py \
  --request sample_request.txt \
  --progress data/course_progress.json \
  --template configs/course_template.yaml \
  --output-dir output
```

5. Inspect `output/generation_manifest.json`.
6. Report generated files and list human review items.

## Output expectations

The output directory should include:

- `teaching_brief.md`
- `teaching_progress_deck.pptx`
- `teaching_dashboard.xlsx`
- `teaching_gantt.png`
- `dashboard.html`
- `generation_manifest.json`

## Human review gates

Stop for human review if:

- the meeting date or time is not confirmed;
- the generated status may not match the actual class progress;
- the deck is intended for external sharing;
- user questions include sensitive or unresolved topics.

## References

- See `references/document_rules.md` for generation rules.
- See `references/template_contract.md` for required template fields.
- See `references/human_review_checklist.md` before final delivery.
