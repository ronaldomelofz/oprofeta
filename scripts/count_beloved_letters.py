# -*- coding: utf-8 -*-
"""Count letters vs journal entries in Beloved Prophet OCR cache."""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

EN = Path(r"E:\PROJETOS-CURSOR\OPROFETA\cartas\ocr_cache\pages")


def load_blob() -> str:
    parts: list[str] = []
    for n in range(1, 457):
        t = (EN / f"{n:03d}.txt").read_text(encoding="utf-8", errors="ignore")
        lines = t.splitlines()
        if lines and lines[0].startswith("---PAGE"):
            t = "\n".join(lines[1:])
        parts.append(t)
    return "\n\n".join(parts)


def is_div(line: str, who: str) -> bool:
    s = re.sub(r"[\s—\-–−_=~*•❧☙◆◇\[\]]+", "", line.strip())
    return s == who


def main() -> None:
    blob = load_blob()
    lines = blob.splitlines()

    blocks: list[dict] = []
    i = 0
    while i < len(lines):
        who = None
        if is_div(lines[i], "KG"):
            who = "KG"
        elif is_div(lines[i], "MH"):
            who = "MH"
        if not who:
            i += 1
            continue

        i += 1
        body: list[str] = []
        while i < len(lines) and not is_div(lines[i], "KG") and not is_div(lines[i], "MH"):
            body.append(lines[i])
            i += 1
        body_txt = "\n".join(body).strip()
        is_journal = bool(re.search(r"(\[JOURNAL\])|(^JOURNAL\s*$)", body_txt, re.I | re.M))
        has_date = bool(
            re.search(
                r"(January|February|March|April|May|June|July|August|"
                r"September|October|November|December).{0,40}\d{4}|"
                r"(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)"
                r".{0,50}\d{4}|"
                r"\b19[0-3]\d\b",
                body_txt,
                re.I,
            )
        )
        has_sig = bool(re.search(r"^\s*(Kahlil|Mary|Lovingly,?)\s*$", body_txt, re.M))
        kind = "journal" if is_journal else "letter"
        if who == "MH" and not is_journal and not has_sig and not has_date:
            kind = "editorial_or_fragment"
        if who == "KG" and not has_date and not has_sig and len(body_txt) < 100:
            kind = "editorial_or_fragment"
        blocks.append(
            {
                "who": who,
                "kind": kind,
                "chars": len(body_txt),
                "has_date": has_date,
                "has_sig": has_sig,
            }
        )

    c = Counter((b["who"], b["kind"]) for b in blocks)
    print("Blocks by who/kind:")
    for k, v in sorted(c.items()):
        print(f"  {k}: {v}")

    letters = [b for b in blocks if b["kind"] == "letter"]
    journals = [b for b in blocks if b["kind"] == "journal"]
    frags = [b for b in blocks if b["kind"] == "editorial_or_fragment"]

    print()
    print(f"Cartas (excl. diario): {len(letters)}")
    print(f"  de Gibran (KG): {sum(1 for b in letters if b['who'] == 'KG')}")
    print(f"  de Mary (MH, nao-diario): {sum(1 for b in letters if b['who'] == 'MH')}")
    print(f"Entradas de diario [JOURNAL]: {len(journals)}")
    print(f"Fragmentos/editorial: {len(frags)}")
    print(f"Unidades epistolares (cartas + diarios): {len(letters) + len(journals)}")
    print(f"Blocos com divisor KG/MH: {len(blocks)}")

    # Also count raw dividers for transparency
    kg = sum(1 for ln in lines if is_div(ln, "KG"))
    mh = sum(1 for ln in lines if is_div(ln, "MH"))
    print(f"Divisores brutos KG={kg} MH={mh}")


if __name__ == "__main__":
    main()
