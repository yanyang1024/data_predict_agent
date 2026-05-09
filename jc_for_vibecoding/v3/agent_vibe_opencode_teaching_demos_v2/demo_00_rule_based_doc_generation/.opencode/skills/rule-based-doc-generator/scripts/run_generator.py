#!/usr/bin/env python3
import subprocess
subprocess.check_call([
    "python3", "scripts/generate_training_artifacts.py",
    "--request", "sample_request.txt",
    "--progress", "data/course_progress.json",
    "--template", "configs/course_template.yaml",
    "--output-dir", "output",
])
