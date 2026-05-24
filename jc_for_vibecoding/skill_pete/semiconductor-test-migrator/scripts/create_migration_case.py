#!/usr/bin/env python3
"""
Create or update a migration case folder for semiconductor PETE test-code migration.

This helper does not parse C/C++ semantics. It creates traceability scaffolding,
collects file manifests, and optionally snapshots source files so humans and
agents can compare before/after states.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

DEFAULT_EXTENSIONS = (".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".inc", ".efa")
DEFAULT_EXCLUDE_DIRS = {".git", "build", "dist", "out", "node_modules", ".cache", "__pycache__"}


@dataclass
class FileRecord:
    path: str
    size_bytes: int
    sha256: str
    modified_utc: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def should_skip_dir(path: Path, exclude_dirs: set[str]) -> bool:
    return any(part in exclude_dirs for part in path.parts)


def iter_source_files(repo: Path, extensions: tuple[str, ...], exclude_dirs: set[str]) -> Iterable[Path]:
    for path in sorted(repo.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(repo)
        if should_skip_dir(rel, exclude_dirs):
            continue
        if path.suffix.lower() in extensions or path.name in {"flow.c", "efa"}:
            yield path


def collect_manifest(repo: Path, extensions: tuple[str, ...], exclude_dirs: set[str]) -> list[FileRecord]:
    records: list[FileRecord] = []
    for path in iter_source_files(repo, extensions, exclude_dirs):
        stat = path.stat()
        records.append(
            FileRecord(
                path=str(path.relative_to(repo)),
                size_bytes=stat.st_size,
                sha256=sha256_file(path),
                modified_utc=datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
            )
        )
    return records


def write_manifest(case_dir: Path, phase: str, records: list[FileRecord]) -> None:
    json_path = case_dir / f"{phase}_manifest.json"
    csv_path = case_dir / f"{phase}_manifest.csv"

    json_path.write_text(json.dumps([asdict(record) for record in records], indent=2), encoding="utf-8")

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["path", "size_bytes", "sha256", "modified_utc"])
        writer.writeheader()
        for record in records:
            writer.writerow(asdict(record))


def load_manifest(path: Path) -> dict[str, FileRecord]:
    if not path.exists():
        return {}
    rows = json.loads(path.read_text(encoding="utf-8"))
    return {row["path"]: FileRecord(**row) for row in rows}


def write_diff_summary(case_dir: Path) -> None:
    before = load_manifest(case_dir / "before_manifest.json")
    after = load_manifest(case_dir / "after_manifest.json")
    if not before or not after:
        return

    before_paths = set(before)
    after_paths = set(after)
    added = sorted(after_paths - before_paths)
    removed = sorted(before_paths - after_paths)
    modified = sorted(path for path in before_paths & after_paths if before[path].sha256 != after[path].sha256)

    lines = [
        "# Manifest Diff Summary",
        "",
        f"Generated UTC: {datetime.now(timezone.utc).isoformat()}",
        "",
        f"- added files: {len(added)}",
        f"- removed files: {len(removed)}",
        f"- modified files: {len(modified)}",
        "",
        "## Added",
        *(f"- {path}" for path in added),
        "",
        "## Removed",
        *(f"- {path}" for path in removed),
        "",
        "## Modified",
        *(f"- {path}" for path in modified),
        "",
    ]
    (case_dir / "diff_summary.md").write_text("\n".join(lines), encoding="utf-8")


def copy_snapshot(repo: Path, case_dir: Path, phase: str, files: Iterable[Path]) -> None:
    snapshot_dir = case_dir / "snapshots" / phase
    for source in files:
        rel = source.relative_to(repo)
        target = snapshot_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def write_if_missing(path: Path, content: str) -> None:
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def init_templates(case_dir: Path) -> None:
    write_if_missing(
        case_dir / "change_log.md",
        "# Migration Change Log\n\n"
        "## Case metadata\n\n"
        "- case id:\n- source product/tester:\n- target product/tester:\n"
        "- whitelist source:\n- parameter source:\n\n"
        "## Changes\n\n"
        "### change-001: <title>\n\n"
        "- category: deletion | tester-refactor | parameter-update | validation | review\n"
        "- affected test items:\n- affected files:\n- before reference:\n- after reference:\n"
        "- rationale:\n- evidence:\n- validation:\n- human review required:\n- reviewer decision:\n",
    )
    write_if_missing(
        case_dir / "review_checklist.md",
        "# Migration Review Checklist\n\n"
        "- [ ] whitelist loaded and normalized\n"
        "- [ ] required test items mapped to implementation symbols\n"
        "- [ ] deletion candidates have reverse-call evidence\n"
        "- [ ] shared helpers/classes/callbacks/macros reviewed\n"
        "- [ ] product parameters old/new values logged\n"
        "- [ ] tester-platform idioms reviewed\n"
        "- [ ] build/static/offline checks completed\n"
        "- [ ] final human approval recorded\n",
    )
    (case_dir / "deletion_batches").mkdir(exist_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create traceability scaffolding for a PETE test-code migration case.")
    parser.add_argument("--repo", required=True, help="Path to the source repository.")
    parser.add_argument("--case-dir", required=True, help="Output migration case directory.")
    parser.add_argument("--phase", choices=["before", "after"], default="before", help="Manifest phase to collect.")
    parser.add_argument("--case-id", default="", help="Human-readable migration case id.")
    parser.add_argument("--source-product", default="")
    parser.add_argument("--target-product", default="")
    parser.add_argument("--source-tester", default="")
    parser.add_argument("--target-tester", default="")
    parser.add_argument("--whitelist", default="", help="Path to whitelist file, if known.")
    parser.add_argument("--parameters", default="", help="Path to target product parameter source, if known.")
    parser.add_argument(
        "--extensions",
        default=",".join(DEFAULT_EXTENSIONS),
        help="Comma-separated extensions to include in the manifest.",
    )
    parser.add_argument(
        "--exclude-dirs",
        default=",".join(sorted(DEFAULT_EXCLUDE_DIRS)),
        help="Comma-separated directory names to exclude.",
    )
    parser.add_argument("--snapshot", action="store_true", help="Copy included source files into snapshots/<phase>.")
    args = parser.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    case_dir = Path(args.case_dir).expanduser().resolve()
    if not repo.exists() or not repo.is_dir():
        raise SystemExit(f"repo does not exist or is not a directory: {repo}")

    case_dir.mkdir(parents=True, exist_ok=True)
    init_templates(case_dir)

    extensions = tuple(ext.strip().lower() for ext in args.extensions.split(",") if ext.strip())
    exclude_dirs = {name.strip() for name in args.exclude_dirs.split(",") if name.strip()}
    source_files = list(iter_source_files(repo, extensions, exclude_dirs))
    records = collect_manifest(repo, extensions, exclude_dirs)
    write_manifest(case_dir, args.phase, records)

    metadata_path = case_dir / "case_metadata.json"
    existing_metadata = {}
    if metadata_path.exists():
        existing_metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata = {
        **existing_metadata,
        "case_id": args.case_id or existing_metadata.get("case_id", case_dir.name),
        "repo": str(repo),
        "source_product": args.source_product or existing_metadata.get("source_product", ""),
        "target_product": args.target_product or existing_metadata.get("target_product", ""),
        "source_tester": args.source_tester or existing_metadata.get("source_tester", ""),
        "target_tester": args.target_tester or existing_metadata.get("target_tester", ""),
        "whitelist": args.whitelist or existing_metadata.get("whitelist", ""),
        "parameters": args.parameters or existing_metadata.get("parameters", ""),
        "last_phase": args.phase,
        "last_manifest_utc": datetime.now(timezone.utc).isoformat(),
        "included_extensions": list(extensions),
        "excluded_dirs": sorted(exclude_dirs),
        "manifest_file_count": len(records),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    if args.snapshot:
        copy_snapshot(repo, case_dir, args.phase, source_files)

    if args.phase == "after":
        write_diff_summary(case_dir)

    print(f"case directory: {case_dir}")
    print(f"phase: {args.phase}")
    print(f"files recorded: {len(records)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
