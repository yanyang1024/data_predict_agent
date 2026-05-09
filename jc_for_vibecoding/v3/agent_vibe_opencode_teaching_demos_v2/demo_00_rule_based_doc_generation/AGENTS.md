# Demo 00 Rules

This demo is about rule-based document generation.

Do not hand-edit files in `output/`. Regenerate them with `scripts/generate_training_artifacts.py`.

When asked to change the generated PPT or Excel:
1. Update `configs/course_template.yaml`, `data/course_progress.json`, or the script.
2. Re-run the generator.
3. Inspect the manifest and review checklist.

Human review is required for:
- final meeting time;
- whether progress status is accurate;
- whether user questions are phrased appropriately;
- whether the deck should be shared externally.
