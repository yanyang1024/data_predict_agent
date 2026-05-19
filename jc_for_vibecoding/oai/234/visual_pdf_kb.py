#!/usr/bin/env python3
"""
Standalone PDF Visual Sidecar Knowledge Base

This reference implementation creates an independent visual index for PDF files.
It does not modify an existing text RAG knowledge base. It stores rendered pages,
image-region crops, metadata, and a small SQLite FTS index that can be queried by
user question plus optional doc/page filters.

Commands:
  ingest      Ingest one PDF into a visual sidecar directory.
  batch       Ingest all PDFs in a directory.
  search      Search visual assets by query, doc_id, page and asset kind.
  show        Show metadata for one asset_id.
  stats       Print index statistics.

Example:
  python scripts/visual_pdf_kb.py ingest --pdf ./whitepaper.pdf --out ./visual_kb --doc-id kb_doc_123 --title "Whitepaper"
  python scripts/visual_pdf_kb.py search --out ./visual_kb --query "A B performance comparison" --doc-id kb_doc_123 --pages 8,9 --top-k 3
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

try:
    import fitz  # PyMuPDF
except Exception as exc:  # pragma: no cover
    raise SystemExit(
        "PyMuPDF is required. Install with: pip install pymupdf\n"
        f"Original import error: {exc}"
    )

CAPTION_RE = re.compile(
    r"(?i)(fig(?:ure)?\.?\s*\d+|table\s*\d+|chart\s*\d+|diagram\s*\d+|"
    r"图\s*\d+|表\s*\d+|架构图|流程图|示意图|截图)"
)
TOKEN_RE = re.compile(r"[\w\-]+|[\u4e00-\u9fff]+", re.UNICODE)


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def short_hash(value: str, length: int = 16) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:length]


def safe_name(value: str) -> str:
    value = value.strip() or "untitled"
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", value)
    return value[:120].strip("._-") or "untitled"


def default_doc_id(pdf_path: Path) -> str:
    stat = pdf_path.stat()
    raw = f"{pdf_path.resolve()}:{stat.st_size}:{int(stat.st_mtime)}"
    return "doc_" + short_hash(raw, 12)


def clip_text(text: str, limit: int = 4000) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    return text if len(text) <= limit else text[: limit - 3] + "..."


def bbox_to_list(rect: fitz.Rect) -> List[float]:
    return [round(rect.x0, 2), round(rect.y0, 2), round(rect.x1, 2), round(rect.y1, 2)]


def bbox_json(rect: fitz.Rect) -> str:
    return json.dumps(bbox_to_list(rect), ensure_ascii=False)


def expand_rect(rect: fitz.Rect, page_rect: fitz.Rect, padding: float) -> fitz.Rect:
    expanded = fitz.Rect(rect.x0 - padding, rect.y0 - padding, rect.x1 + padding, rect.y1 + padding)
    expanded &= page_rect
    return expanded


def render_rect(page: fitz.Page, rect: fitz.Rect, output: Path, dpi: int) -> Tuple[int, int]:
    output.parent.mkdir(parents=True, exist_ok=True)
    pix = page.get_pixmap(dpi=dpi, clip=rect, alpha=False)
    pix.save(str(output))
    return pix.width, pix.height


def render_page(page: fitz.Page, output: Path, dpi: int) -> Tuple[int, int]:
    output.parent.mkdir(parents=True, exist_ok=True)
    pix = page.get_pixmap(dpi=dpi, alpha=False)
    pix.save(str(output))
    return pix.width, pix.height


def text_blocks(page: fitz.Page) -> List[Dict[str, Any]]:
    data = page.get_text("dict")
    blocks: List[Dict[str, Any]] = []
    for block in data.get("blocks", []):
        if block.get("type") != 0:
            continue
        lines = []
        for line in block.get("lines", []):
            line_text = "".join(span.get("text", "") for span in line.get("spans", []))
            if line_text.strip():
                lines.append(line_text.strip())
        text = " ".join(lines).strip()
        if not text:
            continue
        rect = fitz.Rect(block.get("bbox", (0, 0, 0, 0)))
        blocks.append({"bbox": rect, "text": text})
    return blocks


def image_blocks(page: fitz.Page) -> List[Dict[str, Any]]:
    data = page.get_text("dict")
    blocks: List[Dict[str, Any]] = []
    for index, block in enumerate(data.get("blocks", []), start=1):
        if block.get("type") != 1:
            continue
        rect = fitz.Rect(block.get("bbox", (0, 0, 0, 0)))
        blocks.append(
            {
                "index": index,
                "bbox": rect,
                "ext": block.get("ext"),
                "width": block.get("width"),
                "height": block.get("height"),
                "size": block.get("size"),
            }
        )
    return blocks


def horizontal_overlap_ratio(a: fitz.Rect, b: fitz.Rect) -> float:
    overlap = max(0.0, min(a.x1, b.x1) - max(a.x0, b.x0))
    denom = max(1.0, min(a.width, b.width))
    return overlap / denom


def nearby_caption_and_text(rect: fitz.Rect, blocks: Sequence[Dict[str, Any]], limit: int = 900) -> Tuple[str, str]:
    candidates: List[Tuple[float, str, str]] = []
    for block in blocks:
        tb = block["bbox"]
        text = block["text"]
        overlap = horizontal_overlap_ratio(rect, tb)
        if overlap < 0.15:
            continue

        below_gap = tb.y0 - rect.y1
        above_gap = rect.y0 - tb.y1
        side_gap = min(abs(tb.x0 - rect.x1), abs(rect.x0 - tb.x1))

        relation = "far"
        distance = 9999.0
        if 0 <= below_gap <= 120:
            relation = "below"
            distance = below_gap
        elif 0 <= above_gap <= 90:
            relation = "above"
            distance = above_gap + 25
        elif tb.y0 < rect.y1 and tb.y1 > rect.y0 and side_gap <= 80:
            relation = "side"
            distance = side_gap + 50
        else:
            continue

        caption_bonus = -80.0 if CAPTION_RE.search(text) else 0.0
        below_bonus = -15.0 if relation == "below" else 0.0
        candidates.append((distance + caption_bonus + below_bonus, relation, text))

    if not candidates:
        return "", ""

    candidates.sort(key=lambda item: item[0])
    caption = ""
    for _, _, text in candidates:
        if CAPTION_RE.search(text):
            caption = text
            break
    if not caption:
        caption = candidates[0][2]

    nearby = " | ".join(text for _, _, text in candidates[:5])
    return clip_text(caption, 400), clip_text(nearby, limit)


def tokens_for_search(query: str) -> List[str]:
    tokens = [tok.strip().lower() for tok in TOKEN_RE.findall(query or "") if tok.strip()]
    # Avoid huge queries and duplicate terms while preserving order.
    seen = set()
    unique = []
    for tok in tokens:
        if tok not in seen:
            seen.add(tok)
            unique.append(tok)
    return unique[:12]


def fts_query(query: str) -> Optional[str]:
    tokens = tokens_for_search(query)
    if not tokens:
        return None
    # Quote terms to avoid syntax errors. OR is forgiving for exploratory visual search.
    return " OR ".join('"' + tok.replace('"', '""') + '"' for tok in tokens)


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS documents (
            doc_id TEXT PRIMARY KEY,
            title TEXT,
            source_path TEXT,
            checksum TEXT,
            page_count INTEGER,
            ingested_at TEXT
        );
        CREATE TABLE IF NOT EXISTS visual_assets (
            asset_id TEXT PRIMARY KEY,
            doc_id TEXT NOT NULL,
            doc_title TEXT,
            pdf_path TEXT,
            page_number INTEGER NOT NULL,
            asset_kind TEXT NOT NULL,
            bbox_json TEXT,
            image_path TEXT NOT NULL,
            width INTEGER,
            height INTEGER,
            caption TEXT,
            nearby_text TEXT,
            visual_summary TEXT,
            page_text TEXT,
            content_hash TEXT,
            created_at TEXT,
            FOREIGN KEY(doc_id) REFERENCES documents(doc_id)
        );
        CREATE VIRTUAL TABLE IF NOT EXISTS visual_assets_fts USING fts5(
            asset_id UNINDEXED,
            doc_id UNINDEXED,
            page_number UNINDEXED,
            asset_kind UNINDEXED,
            doc_title,
            caption,
            nearby_text,
            visual_summary,
            page_text
        );
        CREATE INDEX IF NOT EXISTS idx_visual_assets_doc_page ON visual_assets(doc_id, page_number);
        CREATE INDEX IF NOT EXISTS idx_visual_assets_kind ON visual_assets(asset_kind);
        """
    )
    conn.commit()


def upsert_document(
    conn: sqlite3.Connection,
    doc_id: str,
    title: str,
    source_path: str,
    checksum: str,
    page_count: int,
) -> None:
    conn.execute(
        """
        INSERT INTO documents(doc_id, title, source_path, checksum, page_count, ingested_at)
        VALUES(?, ?, ?, ?, ?, ?)
        ON CONFLICT(doc_id) DO UPDATE SET
            title=excluded.title,
            source_path=excluded.source_path,
            checksum=excluded.checksum,
            page_count=excluded.page_count,
            ingested_at=excluded.ingested_at
        """,
        (doc_id, title, source_path, checksum, page_count, utc_now()),
    )


def delete_doc_assets(conn: sqlite3.Connection, doc_id: str) -> None:
    asset_ids = [row[0] for row in conn.execute("SELECT asset_id FROM visual_assets WHERE doc_id = ?", (doc_id,))]
    for asset_id in asset_ids:
        conn.execute("DELETE FROM visual_assets_fts WHERE asset_id = ?", (asset_id,))
    conn.execute("DELETE FROM visual_assets WHERE doc_id = ?", (doc_id,))
    conn.commit()


def upsert_asset(conn: sqlite3.Connection, asset: Dict[str, Any]) -> None:
    values = (
        asset["asset_id"],
        asset["doc_id"],
        asset.get("doc_title", ""),
        asset.get("pdf_path", ""),
        asset["page_number"],
        asset["asset_kind"],
        asset.get("bbox_json", ""),
        asset["image_path"],
        asset.get("width"),
        asset.get("height"),
        asset.get("caption", ""),
        asset.get("nearby_text", ""),
        asset.get("visual_summary", ""),
        asset.get("page_text", ""),
        asset.get("content_hash", ""),
        asset.get("created_at", utc_now()),
    )
    conn.execute(
        """
        INSERT INTO visual_assets(
            asset_id, doc_id, doc_title, pdf_path, page_number, asset_kind, bbox_json,
            image_path, width, height, caption, nearby_text, visual_summary, page_text,
            content_hash, created_at
        ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(asset_id) DO UPDATE SET
            doc_id=excluded.doc_id,
            doc_title=excluded.doc_title,
            pdf_path=excluded.pdf_path,
            page_number=excluded.page_number,
            asset_kind=excluded.asset_kind,
            bbox_json=excluded.bbox_json,
            image_path=excluded.image_path,
            width=excluded.width,
            height=excluded.height,
            caption=excluded.caption,
            nearby_text=excluded.nearby_text,
            visual_summary=excluded.visual_summary,
            page_text=excluded.page_text,
            content_hash=excluded.content_hash,
            created_at=excluded.created_at
        """,
        values,
    )
    conn.execute("DELETE FROM visual_assets_fts WHERE asset_id = ?", (asset["asset_id"],))
    conn.execute(
        """
        INSERT INTO visual_assets_fts(
            asset_id, doc_id, page_number, asset_kind, doc_title, caption,
            nearby_text, visual_summary, page_text
        ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            asset["asset_id"],
            asset["doc_id"],
            str(asset["page_number"]),
            asset["asset_kind"],
            asset.get("doc_title", ""),
            asset.get("caption", ""),
            asset.get("nearby_text", ""),
            asset.get("visual_summary", ""),
            asset.get("page_text", ""),
        ),
    )


def asset_to_jsonable(row: sqlite3.Row, out_dir: Optional[Path] = None, score: Optional[float] = None) -> Dict[str, Any]:
    item = dict(row)
    if item.get("bbox_json"):
        try:
            item["bbox"] = json.loads(item["bbox_json"])
        except json.JSONDecodeError:
            item["bbox"] = None
    item.pop("bbox_json", None)
    if out_dir and item.get("image_path"):
        try:
            item["image_uri"] = str(Path(item["image_path"]).resolve())
        except Exception:
            item["image_uri"] = item["image_path"]
    else:
        item["image_uri"] = item.get("image_path")
    if score is not None:
        item["score"] = round(float(score), 6)
    return item


def append_manifest(out_dir: Path, asset: Dict[str, Any]) -> None:
    manifest = out_dir / "manifest.jsonl"
    with manifest.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asset, ensure_ascii=False) + "\n")


def ingest_pdf(
    pdf_path: Path,
    out_dir: Path,
    doc_id: Optional[str] = None,
    title: Optional[str] = None,
    dpi: int = 144,
    page_dpi: int = 120,
    min_width: float = 45.0,
    min_height: float = 45.0,
    min_area_ratio: float = 0.003,
    overwrite: bool = False,
    render_full_pages: bool = True,
) -> Dict[str, Any]:
    pdf_path = pdf_path.resolve()
    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)
    doc_id = doc_id or default_doc_id(pdf_path)
    title = title or pdf_path.stem

    out_dir.mkdir(parents=True, exist_ok=True)
    asset_root = out_dir / "assets" / safe_name(doc_id)
    db_path = out_dir / "index.sqlite"
    conn = connect(db_path)
    init_db(conn)

    if overwrite:
        delete_doc_assets(conn, doc_id)
        if asset_root.exists():
            shutil.rmtree(asset_root)

    checksum = sha256_file(pdf_path)
    saved_assets = 0
    page_assets = 0
    image_assets = 0

    with fitz.open(str(pdf_path)) as doc:
        upsert_document(conn, doc_id, title, str(pdf_path), checksum, doc.page_count)
        for page_index in range(doc.page_count):
            page = doc.load_page(page_index)
            page_number = page_index + 1
            page_dir = asset_root / f"page_{page_number:04d}"
            page_dir.mkdir(parents=True, exist_ok=True)
            page_text = clip_text(page.get_text("text"), 5000)
            blocks = text_blocks(page)

            if render_full_pages:
                page_image = page_dir / "page.png"
                width, height = render_page(page, page_image, page_dpi)
                rect = page.rect
                asset_id = short_hash(f"{doc_id}:{page_number}:page_render:{bbox_json(rect)}")
                asset = {
                    "asset_id": asset_id,
                    "doc_id": doc_id,
                    "doc_title": title,
                    "pdf_path": str(pdf_path),
                    "page_number": page_number,
                    "asset_kind": "page_render",
                    "bbox_json": bbox_json(rect),
                    "image_path": str(page_image),
                    "width": width,
                    "height": height,
                    "caption": f"Page {page_number} of {title}",
                    "nearby_text": clip_text(page_text, 1200),
                    "visual_summary": "",
                    "page_text": page_text,
                    "content_hash": sha256_file(page_image),
                    "created_at": utc_now(),
                }
                upsert_asset(conn, asset)
                append_manifest(out_dir, asset)
                page_assets += 1
                saved_assets += 1

            page_area = max(1.0, page.rect.width * page.rect.height)
            seen_regions = set()
            for img_num, img in enumerate(image_blocks(page), start=1):
                rect = img["bbox"]
                if rect.width < min_width or rect.height < min_height:
                    continue
                if (rect.width * rect.height) / page_area < min_area_ratio:
                    continue
                region_key = tuple(round(v, 1) for v in bbox_to_list(rect))
                if region_key in seen_regions:
                    continue
                seen_regions.add(region_key)

                crop_rect = expand_rect(rect, page.rect, padding=4)
                crop_file = page_dir / f"image_{img_num:03d}.png"
                width, height = render_rect(page, crop_rect, crop_file, dpi=dpi)
                content_hash = sha256_file(crop_file)
                caption, nearby = nearby_caption_and_text(rect, blocks)
                asset_id = short_hash(f"{doc_id}:{page_number}:embedded_image_region:{bbox_json(rect)}:{content_hash[:12]}")
                asset = {
                    "asset_id": asset_id,
                    "doc_id": doc_id,
                    "doc_title": title,
                    "pdf_path": str(pdf_path),
                    "page_number": page_number,
                    "asset_kind": "embedded_image_region",
                    "bbox_json": bbox_json(rect),
                    "image_path": str(crop_file),
                    "width": width,
                    "height": height,
                    "caption": caption,
                    "nearby_text": nearby,
                    "visual_summary": "",
                    "page_text": page_text,
                    "content_hash": content_hash,
                    "created_at": utc_now(),
                }
                upsert_asset(conn, asset)
                append_manifest(out_dir, asset)
                image_assets += 1
                saved_assets += 1

        conn.commit()

    return {
        "out_dir": str(out_dir.resolve()),
        "index": str(db_path.resolve()),
        "doc_id": doc_id,
        "title": title,
        "pdf_path": str(pdf_path),
        "page_assets": page_assets,
        "image_assets": image_assets,
        "saved_assets": saved_assets,
    }


def build_filter_sql(
    doc_id: Optional[str],
    pages: Optional[Sequence[int]],
    kinds: Optional[Sequence[str]],
    prefix: str = "v",
) -> Tuple[str, List[Any]]:
    clauses: List[str] = []
    params: List[Any] = []
    if doc_id:
        clauses.append(f"{prefix}.doc_id = ?")
        params.append(doc_id)
    if pages:
        placeholders = ",".join("?" for _ in pages)
        clauses.append(f"{prefix}.page_number IN ({placeholders})")
        params.extend(int(p) for p in pages)
    if kinds:
        placeholders = ",".join("?" for _ in kinds)
        clauses.append(f"{prefix}.asset_kind IN ({placeholders})")
        params.extend(kinds)
    return (" AND " + " AND ".join(clauses)) if clauses else "", params


def parse_pages(value: Optional[str], page_window: int = 0) -> Optional[List[int]]:
    if not value:
        return None
    pages = set()
    for part in re.split(r"[,\s]+", value.strip()):
        if not part:
            continue
        if "-" in part:
            left, right = part.split("-", 1)
            start, end = int(left), int(right)
            for p in range(min(start, end), max(start, end) + 1):
                pages.add(p)
        else:
            pages.add(int(part))
    if page_window > 0:
        expanded = set()
        for p in pages:
            for q in range(max(1, p - page_window), p + page_window + 1):
                expanded.add(q)
        pages = expanded
    return sorted(pages)


def kind_bonus(kind: str) -> float:
    if kind in {"embedded_image_region", "figure_crop", "table_crop"}:
        return 0.15
    if kind == "page_render":
        return -0.05
    return 0.0


def search_assets(
    out_dir: Path,
    query: str,
    top_k: int = 5,
    doc_id: Optional[str] = None,
    pages: Optional[Sequence[int]] = None,
    kinds: Optional[Sequence[str]] = None,
) -> List[Dict[str, Any]]:
    db_path = out_dir / "index.sqlite"
    conn = connect(db_path)
    init_db(conn)

    hits: Dict[str, Tuple[sqlite3.Row, float]] = {}
    fq = fts_query(query)
    filter_sql, filter_params = build_filter_sql(doc_id, pages, kinds, prefix="v")

    if fq:
        try:
            sql = f"""
                SELECT v.*, bm25(f) AS rank
                FROM visual_assets_fts f
                JOIN visual_assets v ON v.asset_id = f.asset_id
                WHERE visual_assets_fts MATCH ? {filter_sql}
                ORDER BY rank ASC
                LIMIT ?
            """
            for row in conn.execute(sql, [fq] + filter_params + [max(top_k * 5, 20)]):
                rank = float(row["rank"])
                # FTS bm25 is lower-is-better. Convert to a rough positive score.
                score = 1.0 / (1.0 + max(0.0, rank)) + kind_bonus(row["asset_kind"])
                if row["caption"]:
                    score += 0.08
                hits[row["asset_id"]] = (row, score)
        except sqlite3.OperationalError:
            # FTS tokenization can be fragile for symbols-heavy or CJK queries. Fall back below.
            pass

    tokens = tokens_for_search(query)
    filter_sql2, filter_params2 = build_filter_sql(doc_id, pages, kinds, prefix="visual_assets")
    sql = f"SELECT * FROM visual_assets WHERE 1=1 {filter_sql2}"
    for row in conn.execute(sql, filter_params2):
        haystack = " ".join(
            str(row[key] or "")
            for key in ["doc_title", "asset_kind", "caption", "nearby_text", "visual_summary", "page_text"]
        ).lower()
        if not tokens:
            lexical = 0.0
        else:
            lexical = sum(1.0 for tok in tokens if tok in haystack) / max(1, len(tokens))
        if lexical <= 0 and hits:
            continue
        if lexical <= 0 and tokens:
            continue
        score = lexical + kind_bonus(row["asset_kind"])
        if row["caption"]:
            score += 0.08
        if row["asset_id"] in hits:
            old_row, old_score = hits[row["asset_id"]]
            hits[row["asset_id"]] = (old_row, max(old_score, score))
        else:
            hits[row["asset_id"]] = (row, score)

    ordered = sorted(hits.values(), key=lambda item: item[1], reverse=True)[:top_k]
    return [asset_to_jsonable(row, out_dir=out_dir, score=score) for row, score in ordered]


def show_asset(out_dir: Path, asset_id: str) -> Dict[str, Any]:
    conn = connect(out_dir / "index.sqlite")
    init_db(conn)
    row = conn.execute("SELECT * FROM visual_assets WHERE asset_id = ?", (asset_id,)).fetchone()
    if row is None:
        raise KeyError(f"asset_id not found: {asset_id}")
    return asset_to_jsonable(row, out_dir=out_dir)


def index_stats(out_dir: Path) -> Dict[str, Any]:
    conn = connect(out_dir / "index.sqlite")
    init_db(conn)
    docs = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    assets = conn.execute("SELECT COUNT(*) FROM visual_assets").fetchone()[0]
    by_kind = [dict(row) for row in conn.execute("SELECT asset_kind, COUNT(*) AS count FROM visual_assets GROUP BY asset_kind ORDER BY count DESC")]
    return {"out_dir": str(out_dir.resolve()), "documents": docs, "assets": assets, "by_kind": by_kind}


def print_json(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def cmd_ingest(args: argparse.Namespace) -> None:
    result = ingest_pdf(
        pdf_path=Path(args.pdf),
        out_dir=Path(args.out),
        doc_id=args.doc_id,
        title=args.title,
        dpi=args.dpi,
        page_dpi=args.page_dpi,
        min_width=args.min_width,
        min_height=args.min_height,
        min_area_ratio=args.min_area_ratio,
        overwrite=args.overwrite,
        render_full_pages=not args.no_page_render,
    )
    print_json(result)


def cmd_batch(args: argparse.Namespace) -> None:
    pdf_dir = Path(args.pdf_dir)
    if not pdf_dir.exists():
        raise FileNotFoundError(pdf_dir)
    results = []
    for pdf_path in sorted(pdf_dir.rglob("*.pdf")):
        doc_id = None
        if args.doc_id_prefix:
            doc_id = f"{args.doc_id_prefix}_{short_hash(str(pdf_path.resolve()), 10)}"
        results.append(
            ingest_pdf(
                pdf_path=pdf_path,
                out_dir=Path(args.out),
                doc_id=doc_id,
                title=pdf_path.stem,
                dpi=args.dpi,
                page_dpi=args.page_dpi,
                overwrite=args.overwrite,
                render_full_pages=not args.no_page_render,
            )
        )
    print_json({"count": len(results), "results": results})


def cmd_search(args: argparse.Namespace) -> None:
    pages = parse_pages(args.pages, page_window=args.page_window)
    kinds = [part.strip() for part in args.kinds.split(",") if part.strip()] if args.kinds else None
    hits = search_assets(
        out_dir=Path(args.out),
        query=args.query,
        top_k=args.top_k,
        doc_id=args.doc_id,
        pages=pages,
        kinds=kinds,
    )
    print_json({"query": args.query, "count": len(hits), "visual_hits": hits})


def cmd_show(args: argparse.Namespace) -> None:
    print_json(show_asset(Path(args.out), args.asset_id))


def cmd_stats(args: argparse.Namespace) -> None:
    print_json(index_stats(Path(args.out)))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Independent PDF visual sidecar KB reference implementation")
    sub = parser.add_subparsers(dest="command", required=True)

    ingest = sub.add_parser("ingest", help="ingest one PDF")
    ingest.add_argument("--pdf", required=True, help="PDF file path")
    ingest.add_argument("--out", required=True, help="visual KB output directory")
    ingest.add_argument("--doc-id", help="stable doc_id aligned with the text RAG KB")
    ingest.add_argument("--title", help="document title")
    ingest.add_argument("--dpi", type=int, default=144, help="crop render dpi")
    ingest.add_argument("--page-dpi", type=int, default=120, help="full page render dpi")
    ingest.add_argument("--min-width", type=float, default=45.0, help="minimum image block width in PDF points")
    ingest.add_argument("--min-height", type=float, default=45.0, help="minimum image block height in PDF points")
    ingest.add_argument("--min-area-ratio", type=float, default=0.003, help="minimum image block area divided by page area")
    ingest.add_argument("--overwrite", action="store_true", help="remove existing assets for this doc_id before ingest")
    ingest.add_argument("--no-page-render", action="store_true", help="do not store full page renders")
    ingest.set_defaults(func=cmd_ingest)

    batch = sub.add_parser("batch", help="ingest all PDFs in a directory")
    batch.add_argument("--pdf-dir", required=True, help="directory containing PDFs")
    batch.add_argument("--out", required=True, help="visual KB output directory")
    batch.add_argument("--doc-id-prefix", help="optional doc_id prefix for generated ids")
    batch.add_argument("--dpi", type=int, default=144)
    batch.add_argument("--page-dpi", type=int, default=120)
    batch.add_argument("--overwrite", action="store_true")
    batch.add_argument("--no-page-render", action="store_true")
    batch.set_defaults(func=cmd_batch)

    search = sub.add_parser("search", help="search visual assets")
    search.add_argument("--out", required=True, help="visual KB output directory")
    search.add_argument("--query", required=True, help="user query or text-RAG chunk keywords")
    search.add_argument("--top-k", type=int, default=5)
    search.add_argument("--doc-id", help="filter by doc_id")
    search.add_argument("--pages", help="filter pages, for example 8,9 or 8-10")
    search.add_argument("--page-window", type=int, default=0, help="expand page filter by +/- N pages")
    search.add_argument("--kinds", help="comma separated asset kinds, e.g. embedded_image_region,page_render")
    search.set_defaults(func=cmd_search)

    show = sub.add_parser("show", help="show one visual asset")
    show.add_argument("--out", required=True)
    show.add_argument("--asset-id", required=True)
    show.set_defaults(func=cmd_show)

    stats = sub.add_parser("stats", help="show index statistics")
    stats.add_argument("--out", required=True)
    stats.set_defaults(func=cmd_stats)

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
