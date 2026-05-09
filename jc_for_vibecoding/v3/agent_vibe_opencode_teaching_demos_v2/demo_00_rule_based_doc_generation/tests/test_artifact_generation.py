#!/usr/bin/env python3
from pathlib import Path
import json
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]

def test_generate_artifacts():
    with tempfile.TemporaryDirectory() as td:
        out = Path(td)
        cmd = [
            "python3", str(ROOT / "scripts" / "generate_training_artifacts.py"),
            "--request", str(ROOT / "sample_request.txt"),
            "--progress", str(ROOT / "data" / "course_progress.json"),
            "--template", str(ROOT / "configs" / "course_template.yaml"),
            "--output-dir", str(out),
        ]
        subprocess.check_call(cmd)
        assert (out / "teaching_brief.md").exists()
        assert (out / "teaching_progress_deck.pptx").exists()
        assert (out / "teaching_dashboard.xlsx").exists()
        manifest = json.loads((out / "generation_manifest.json").read_text(encoding="utf-8"))
        assert manifest["human_review_required"] is True
