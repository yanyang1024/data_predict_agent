# Template Contract

Required fields in `configs/course_template.yaml`:

- `course_title`
- `duration_minutes`
- `sections[]` with `id`, `title`, `start_min`, `end_min`, `objective`
- `review_questions[]`

Required fields in `data/course_progress.json`:

- `current_minute`
- `current_stage`
- `active_demo`
- `completed[]`
- `user_questions[]`
