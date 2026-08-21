# -*- coding: utf-8 -*-
"""Merge dense commentary JSON parts into commentaries_elaborated.py and chapters.json."""
from __future__ import annotations

import json
import pprint
from pathlib import Path

ROOT = Path(r"e:\PROJETOS-CURSOR\OPROFETA")
DENSE = ROOT / "scripts" / "commentaries_dense"
OUT_PY = ROOT / "scripts" / "commentaries_elaborated.py"
CHAPTERS = ROOT / "src" / "data" / "chapters.json"


def main() -> None:
    merged: dict = {}
    for i in range(1, 5):
        part = json.loads((DENSE / f"part{i}.json").read_text(encoding="utf-8"))
        print(f"part{i}: {len(part)} — {sorted(part.keys())}")
        merged.update(part)

    data = json.loads(CHAPTERS.read_text(encoding="utf-8"))
    slugs = [c["slug"] for c in data["chapters"]]
    missing = [s for s in slugs if s not in merged]
    extra = [s for s in merged if s not in slugs]
    print("merged", len(merged), "missing", missing, "extra", extra)
    if missing:
        raise SystemExit("missing slugs")

    for s in slugs:
        c = merged[s]
        nsec = len(c.get("sections") or [])
        words = len((c.get("summary") or "").split())
        for sec in c.get("sections") or []:
            words += len((sec.get("body") or "").split())
        print(f"  {s}: {nsec} sections, ~{words} words")

    # write Python module
    lines = [
        "# -*- coding: utf-8 -*-",
        '"""Comentários elaborados — prosa filosófica densa (não transcrição oral)."""',
        "",
        "COMMENTARIES = ",
    ]
    # Use json for clean unicode, then convert true/false/null — actually write as Python via pprint
    body = pprint.pformat(merged, width=100, sort_dicts=False)
    # pprint may use single quotes — fine for Python
    OUT_PY.write_text("\n".join(lines) + body + "\n", encoding="utf-8")
    print("wrote", OUT_PY)

    for ch in data["chapters"]:
        essay = merged[ch["slug"]]
        ch["commentary"] = essay
        ch["explanation"] = {"summary": essay["summary"], "keys": essay["keys"]}

    CHAPTERS.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", CHAPTERS)


if __name__ == "__main__":
    main()
