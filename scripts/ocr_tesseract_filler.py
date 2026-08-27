# -*- coding: utf-8 -*-
"""Fast Tesseract OCR filler for Beloved Prophet pages missing from cache.

Uses 5× LANCZOS upscale + Tesseract. Skips pages that already have text.
"""
from __future__ import annotations

import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pytesseract
from PIL import Image, ImageOps, ImageEnhance

ROOT = Path(r"E:\PROJETOS-CURSOR\OPROFETA")
SRC = ROOT / "cartas" / "LIVRO-PRINT"
PAGES = ROOT / "cartas" / "ocr_cache" / "pages"
SCALE = 5
WORKERS = 4


def has_text(n: int) -> bool:
    p = PAGES / f"{n:03d}.txt"
    if not p.exists():
        return False
    return len(p.read_text(encoding="utf-8", errors="ignore").strip()) > 40


def ocr_one(n: int) -> tuple[int, int]:
    if has_text(n):
        return n, 0
    img = Image.open(SRC / f"{n}.png").convert("L")
    up = img.resize((img.width * SCALE, img.height * SCALE), Image.Resampling.LANCZOS)
    up = ImageOps.autocontrast(up)
    up = ImageEnhance.Sharpness(up).enhance(1.6)
    text = pytesseract.image_to_string(up, lang="eng", config="--oem 3 --psm 6").strip()
    if not text:
        text = "[ILUSTRAÇÃO]\n(página sem texto reconhecível)"
    dest = PAGES / f"{n:03d}.txt"
    # race-safe: don't overwrite richer vision OCR
    if has_text(n):
        return n, 0
    dest.write_text(f"---PAGE {n}---\n{text}\n", encoding="utf-8")
    return n, len(text)


def main() -> None:
    PAGES.mkdir(parents=True, exist_ok=True)
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    end = int(sys.argv[2]) if len(sys.argv) > 2 else 456
    pending = [n for n in range(start, end + 1) if not has_text(n)]
    print(f"Tesseract filler: {len(pending)} pending", flush=True)
    if not pending:
        return
    done = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(ocr_one, n): n for n in pending}
        for fut in as_completed(futs):
            n, chars = fut.result()
            done += 1
            if chars:
                print(f"  {n:03d} ({chars} chars)  [{done}/{len(pending)}]", flush=True)
            elif done % 20 == 0:
                print(f"  skip/progress {done}/{len(pending)}", flush=True)
    left = sum(1 for n in range(1, 457) if not has_text(n))
    print(f"Done. Still missing: {left}")


if __name__ == "__main__":
    main()
