# -*- coding: utf-8 -*-
"""OCR Beloved Prophet page images (LIVRO-PRINT) via upscale + MinerU pipeline.

Resumable: skips pages that already have a non-empty cache file.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from PIL import Image

ROOT = Path(r"E:\PROJETOS-CURSOR\OPROFETA")
SRC = ROOT / "cartas" / "LIVRO-PRINT"
CACHE = ROOT / "cartas" / "ocr_cache"
PAGES = CACHE / "pages"
UPSCALE = CACHE / "upscaled"
MINERU_OUT = CACHE / "mineru_out"
SCALE = 5
BATCH = 25  # pages per MinerU invocation


def upscale_page(n: int, force: bool = False) -> Path:
    UPSCALE.mkdir(parents=True, exist_ok=True)
    out = UPSCALE / f"{n:03d}.jpg"
    if out.exists() and not force and out.stat().st_size > 10_000:
        return out
    src = SRC / f"{n}.png"
    img = Image.open(src).convert("RGB")
    up = img.resize((img.width * SCALE, img.height * SCALE), Image.Resampling.LANCZOS)
    up.save(out, "JPEG", quality=92, optimize=True)
    return out


def page_cache_path(n: int) -> Path:
    return PAGES / f"{n:03d}.txt"


def has_text(n: int) -> bool:
    p = page_cache_path(n)
    if not p.exists():
        return False
    body = p.read_text(encoding="utf-8", errors="ignore").strip()
    return len(body) > 40


def run_mineru_batch(nums: list[int]) -> None:
    """Run MinerU on a temporary folder of upscaled JPEGs; harvest markdown."""
    with tempfile.TemporaryDirectory(prefix="bp_ocr_") as tmp:
        tmp_path = Path(tmp)
        for n in nums:
            src = upscale_page(n)
            shutil.copy2(src, tmp_path / f"{n:03d}.jpg")

        out_dir = MINERU_OUT / f"batch_{nums[0]:03d}_{nums[-1]:03d}"
        if out_dir.exists():
            shutil.rmtree(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            sys.executable,
            "-m",
            "mineru.cli.client",
            "-p",
            str(tmp_path),
            "-o",
            str(out_dir),
            "-m",
            "ocr",
            "-b",
            "pipeline",
            "--formula",
            "false",
            "--table",
            "false",
        ]
        # Prefer mineru executable if available
        mineru_exe = shutil.which("mineru")
        if mineru_exe:
            cmd = [
                mineru_exe,
                "-p",
                str(tmp_path),
                "-o",
                str(out_dir),
                "-m",
                "ocr",
                "-b",
                "pipeline",
                "--formula",
                "false",
                "--table",
                "false",
            ]

        print(f"[mineru] pages {nums[0]}-{nums[-1]} …", flush=True)
        t0 = time.time()
        proc = subprocess.run(cmd, capture_output=True, text=True)
        elapsed = time.time() - t0
        print(f"[mineru] done in {elapsed:.1f}s exit={proc.returncode}", flush=True)
        if proc.returncode != 0:
            print(proc.stderr[-2000:] if proc.stderr else proc.stdout[-2000:], flush=True)

        # Harvest .md files: out_dir/<stem>/ocr/<stem>.md
        for md in out_dir.rglob("*.md"):
            stem = md.stem.replace("_up", "")
            # stem like 050
            try:
                n = int("".join(c for c in stem if c.isdigit())[:3] or stem[:3])
            except ValueError:
                continue
            text = md.read_text(encoding="utf-8", errors="ignore").strip()
            if not text:
                continue
            dest = page_cache_path(n)
            # Only write if vision agent hasn't already produced better text
            if has_text(n) and dest.stat().st_size > len(text) + 50:
                continue
            dest.write_text(f"---PAGE {n}---\n{text}\n", encoding="utf-8")
            print(f"  wrote {dest.name} ({len(text)} chars)", flush=True)


def list_pending(start: int = 1, end: int = 456) -> list[int]:
    return [n for n in range(start, end + 1) if not has_text(n)]


def main() -> None:
    PAGES.mkdir(parents=True, exist_ok=True)
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    end = int(sys.argv[2]) if len(sys.argv) > 2 else 456
    pending = list_pending(start, end)
    print(f"Pending OCR: {len(pending)} / {end - start + 1}", flush=True)
    if not pending:
        print("Nothing to do.")
        return

    # Pre-upscale pending (parallel would help; sequential is fine)
    for i, n in enumerate(pending, 1):
        upscale_page(n)
        if i % 25 == 0:
            print(f"  upscaled {i}/{len(pending)}", flush=True)

    for i in range(0, len(pending), BATCH):
        chunk = pending[i : i + BATCH]
        # re-check: vision agents may have filled some
        chunk = [n for n in chunk if not has_text(n)]
        if not chunk:
            continue
        run_mineru_batch(chunk)

    meta = {
        "source": str(SRC),
        "pages_done": sum(1 for n in range(1, 457) if has_text(n)),
        "total": 456,
        "engine": "mineru-pipeline + vision-cache",
        "scale": SCALE,
    }
    (CACHE / "ocr_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(meta)


if __name__ == "__main__":
    main()
