# -*- coding: utf-8 -*-
"""Rejoin broken paragraphs in letters.json (PDF line wraps)."""
from __future__ import annotations

import json
import re
from pathlib import Path

PATH = Path(r"E:\PROJETOS-CURSOR\OPROFETA\src\data\letters.json")


def join_broken(paras: list[str]) -> list[str]:
    out: list[str] = []
    for p in paras:
        p = re.sub(r"\s+", " ", p).strip()
        if not p:
            continue
        if out and not re.search(r'[.!?…”"»)\]]$', out[-1]) and p[0].islower():
            out[-1] = out[-1] + " " + p
        elif out and out[-1].endswith(("por", "de", "do", "da", "que", "e", "em", "com", "para", "ao", "à")):
            out[-1] = out[-1] + " " + p
        else:
            out.append(p)
    return out


def main() -> None:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    for L in data["letters"]:
        before = len(L["paragraphs"])
        L["paragraphs"] = join_broken(L["paragraphs"])
        # quote = first paragraph full (no artificial ellipsis for storage; UI no longer shows truncated quote as body)
        if L["paragraphs"]:
            L["quote"] = L["paragraphs"][0][:220] + ("…" if len(L["paragraphs"][0]) > 220 else "")
        print(L["id"], before, "->", len(L["paragraphs"]), "chars", sum(len(p) for p in L["paragraphs"]))
    PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("ok", PATH)


if __name__ == "__main__":
    main()
