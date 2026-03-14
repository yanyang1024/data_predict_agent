from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Generator, Iterable, Optional


@dataclass
class ParsedSSEEvent:
    raw_line: str
    sse_event_name: Optional[str]
    data: Optional[Dict[str, Any]]



def parse_sse_lines(lines: Iterable[bytes | str]) -> Generator[ParsedSSEEvent, None, None]:
    current_event_name: Optional[str] = None
    for raw in lines:
        if not raw:
            continue
        line = raw.decode("utf-8") if isinstance(raw, bytes) else str(raw)
        line = line.strip()
        if not line:
            continue

        data_part: Optional[str] = None
        if line.startswith("event:") and "data:" not in line:
            current_event_name = line.split(":", 1)[1].strip() or None
            yield ParsedSSEEvent(raw_line=line, sse_event_name=current_event_name, data=None)
            continue

        if line.startswith("data:"):
            data_part = line.split("data:", 1)[1].strip()
        elif "data:" in line:
            # 兼容 event:text data:{...} 这一类非标准拼接行
            prefix, suffix = line.split("data:", 1)
            if prefix.startswith("event:"):
                current_event_name = prefix.split(":", 1)[1].strip() or None
            data_part = suffix.strip()
        else:
            yield ParsedSSEEvent(raw_line=line, sse_event_name=current_event_name, data=None)
            continue

        if not data_part:
            yield ParsedSSEEvent(raw_line=line, sse_event_name=current_event_name, data=None)
            continue

        if data_part == "[DONE]":
            yield ParsedSSEEvent(raw_line=line, sse_event_name=current_event_name, data={"done": True})
            continue

        try:
            parsed = json.loads(data_part)
        except json.JSONDecodeError:
            parsed = {"raw": data_part}
        yield ParsedSSEEvent(raw_line=line, sse_event_name=current_event_name, data=parsed)
