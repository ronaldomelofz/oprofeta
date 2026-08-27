# -*- coding: utf-8 -*-
"""Translate Beloved Prophet OCR cache (EN → pt-BR) with deep_translator."""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

from deep_translator import GoogleTranslator

ROOT = Path(r"E:\PROJETOS-CURSOR\OPROFETA")
CACHE = ROOT / "cartas" / "ocr_cache"
PAGES = CACHE / "pages"
OUT_PAGES = CACHE / "pages_pt"
CHUNK = 4200

SKIP_MARKERS = ("[ILUSTRAÇÃO]", "[ILLUSTRATION]", "---PAGE")


def translate_long(translator: GoogleTranslator, text: str) -> str:
    text = text.strip()
    if not text:
        return text
    if len(text) <= CHUNK:
        for attempt in range(6):
            try:
                return translator.translate(text)
            except Exception as e:
                wait = 2 + attempt * 2
                print(f"  retry ({e}); wait {wait}s", flush=True)
                time.sleep(wait)
        return text

    parts = re.split(r"(?<=[.!?…\"»])\s+", text)
    chunks: list[str] = []
    buf = ""
    for p in parts:
        if len(buf) + len(p) + 1 <= CHUNK:
            buf = f"{buf} {p}".strip()
        else:
            if buf:
                chunks.append(buf)
            buf = p
    if buf:
        chunks.append(buf)

    out: list[str] = []
    for c in chunks:
        out.append(translate_long(translator, c))
        time.sleep(0.35)
    return " ".join(out)


def clean_page(raw: str) -> str:
    lines = raw.splitlines()
    if lines and lines[0].startswith("---PAGE"):
        lines = lines[1:]
    return "\n".join(lines).strip()


def main() -> None:
    OUT_PAGES.mkdir(parents=True, exist_ok=True)
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    end = int(sys.argv[2]) if len(sys.argv) > 2 else 456
    translator = GoogleTranslator(source="en", target="pt")

    done = 0
    for n in range(start, end + 1):
        src = PAGES / f"{n:03d}.txt"
        dest = OUT_PAGES / f"{n:03d}.txt"
        if not src.exists():
            continue
        if dest.exists() and dest.stat().st_size > 40:
            done += 1
            continue
        body = clean_page(src.read_text(encoding="utf-8", errors="ignore"))
        if not body:
            continue
        # Keep illustration markers mostly as-is
        if body.startswith("[ILUSTRAÇÃO]") or body.startswith("[ILLUSTRATION]"):
            pt = body.replace("[ILLUSTRATION]", "[ILUSTRAÇÃO]")
            # still translate captions after marker
            parts = pt.split("\n", 1)
            if len(parts) == 2 and parts[1].strip():
                cap = translate_long(translator, parts[1].strip())
                pt = f"{parts[0]}\n{cap}"
        else:
            print(f"translate {n:03d} ({len(body)} chars)…", flush=True)
            pt = translate_long(translator, body)
            time.sleep(0.4)

        dest.write_text(f"---PÁGINA {n}---\n{pt}\n", encoding="utf-8")
        done += 1
        if done % 10 == 0:
            print(f"  progress: {done} pages", flush=True)

    meta = {"translated": done, "range": [start, end]}
    (CACHE / "translate_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(meta)


if __name__ == "__main__":
    main()
