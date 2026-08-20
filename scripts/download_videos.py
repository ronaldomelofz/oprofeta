# -*- coding: utf-8 -*-
"""Download YouTube videos for all chapters into videos/."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"e:\PROJETOS-CURSOR\OPROFETA")
OUT = ROOT / "videos"
DATA = ROOT / "src" / "data" / "chapters.json"


def main() -> int:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)

    jobs: list[tuple[str, str, str]] = []
    seen: set[str] = set()
    for i, ch in enumerate(data["chapters"], 1):
        vid = ch.get("videoId")
        if not vid:
            print(f"SKIP {i:02d}-{ch['slug']} (sem vídeo)")
            continue
        name = f"{i:02d}-{ch['slug']}"
        # download once per unique id; copy/link for shared episodes later
        jobs.append((name, vid, ch["title"]))
        seen.add(vid)

    print(f"Capítulos com vídeo: {len(jobs)} | IDs únicos: {len(seen)}")

    ok = 0
    fail = 0
    for name, vid, title in jobs:
        outtmpl = str(OUT / f"{name}.%(ext)s")
        # skip if already downloaded (any common video extension)
        existing = list(OUT.glob(f"{name}.*"))
        existing = [p for p in existing if p.suffix.lower() in {".mp4", ".webm", ".mkv", ".m4a"}]
        if existing:
            print(f"OK  {name} (já existe: {existing[0].name})")
            ok += 1
            continue

        url = f"https://www.youtube.com/watch?v={vid}"
        print(f"DL  {name} — {title} [{vid}]")
        cmd = [
            "yt-dlp",
            "--js-runtimes",
            "node",
            "-f",
            "bv*[height<=720]+ba/b[height<=720]/b",
            "--merge-output-format",
            "mp4",
            "-o",
            outtmpl,
            "--no-playlist",
            "--newline",
            "--retries",
            "5",
            url,
        ]
        r = subprocess.run(cmd, cwd=str(ROOT))
        if r.returncode == 0:
            ok += 1
        else:
            fail += 1
            print(f"FAIL {name}", file=sys.stderr)

    print(f"\nConcluído: {ok} ok, {fail} falhas")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
