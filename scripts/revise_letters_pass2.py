# -*- coding: utf-8 -*-
"""Second-pass fixes after revise_letters_quality."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(r"E:\PROJETOS-CURSOR\OPROFETA")
LETTERS = ROOT / "src" / "data" / "letters.json"


def fix_para(p: str) -> str:
    p = p.replace("—E ", "— E ")
    p = p.replace("—And ", "— E ")
    p = re.sub(r"\bEu te amo\b", "Eu a amo", p)
    p = re.sub(r"\beu te amo\b", "eu a amo", p)
    p = re.sub(r"\bTe amo\b", "Amo você", p)
    p = re.sub(r"(?<![A-Za-zÁ-ú])te amo\b", "a amo", p)
    p = re.sub(r"\bque te amo\b", "que a amo", p)
    p = re.sub(r"\bque eu te amo\b", "que eu a amo", p)
    p = re.sub(r"[ \t]{2,}", " ", p)
    return p.strip()


def main() -> None:
    data = json.loads(LETTERS.read_text(encoding="utf-8"))
    n = 0
    te_left = 0
    for L in data["letters"]:
        paras = [fix_para(p) for p in L["paragraphs"]]
        if paras != L["paragraphs"]:
            n += 1
        L["paragraphs"] = paras
        if paras:
            L["quote"] = paras[0][:220] + ("…" if len(paras[0]) > 220 else "")
        blob = " ".join(paras)
        te_left += len(re.findall(r"\bte amo\b|\bTe amo\b|\bEu te amo\b", blob, flags=re.I))
    LETTERS.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / "cartas" / "letters_beloved_extracted.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"letters touched={n} te_amo_left={te_left} total={len(data['letters'])}")


if __name__ == "__main__":
    main()
