# -*- coding: utf-8 -*-
"""Parse Gibran–Haskell letter selections into structured JSON."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(r"E:\PROJETOS-CURSOR\OPROFETA")
TEXT = (ROOT / "cartas" / "_extract.txt").read_text(encoding="utf-8")
OUT = ROOT / "src" / "data" / "letters.json"

MONTHS = (
    "janeiro|fevereiro|março|marco|abril|maio|junho|julho|agosto|"
    "setembro|outubro|novembro|dezembro"
)
DATE_RE = re.compile(
    rf"(?im)^(?:\s*)("
    rf"(?:\d{{1,2}}\s+de\s+(?:{MONTHS})(?:\s+de\s+\d{{4}})?)|"
    rf"(?:{MONTHS})\s+de\s+\d{{4}}|"
    rf"(?:{MONTHS})\s+\d{{4}}|"
    rf"\d{{1,2}}\s+de\s+(?:{MONTHS})\s+\d{{4}}"
    rf")\s*$"
)


def clean_paras(block: str) -> list[str]:
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in block.splitlines()]
    paras: list[str] = []
    buf: list[str] = []
    for ln in lines:
        if not ln:
            if buf:
                paras.append(" ".join(buf))
                buf = []
            continue
        buf.append(ln)
    if buf:
        paras.append(" ".join(buf))
    # drop very short noise
    return [p for p in paras if len(p) > 2]


def slugify(s: str, i: int) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", s.lower())
    base = re.sub(r"-+", "-", base).strip("-")
    return f"{i:02d}-{base[:60]}" if base else f"{i:02d}-carta"


def main() -> None:
    # split preface / intro / letters body
    # After preface comes "Introdução" then first letter content without date sometimes
    text = TEXT.replace("\r\n", "\n")

    # Find start of correspondence after preface
    intro_idx = text.find("Introdução")
    body = text[intro_idx:] if intro_idx >= 0 else text

    # Split by date headings at line start
    lines = body.splitlines()
    chunks: list[tuple[str | None, list[str]]] = []
    current_date: str | None = "Introdução"
    buf: list[str] = []

    for ln in lines:
        m = DATE_RE.match(ln.strip())
        # also match dates mid-style like "9 de abril de 1916"
        m2 = re.match(
            rf"(?i)^(\d{{1,2}}\s+de\s+(?:{MONTHS})(?:\s+de\s+\d{{4}})?)\s*$",
            ln.strip(),
        )
        m3 = re.match(
            rf"(?i)^((?:{MONTHS})\s+de\s+\d{{4}})\s*$",
            ln.strip(),
        )
        hit = m or m2 or m3
        if hit and len(ln.strip()) < 40:
            if buf:
                chunks.append((current_date, buf))
            current_date = hit.group(1)
            buf = []
        else:
            buf.append(ln)
    if buf:
        chunks.append((current_date, buf))

    letters = []
    for i, (date, raw_lines) in enumerate(chunks, 1):
        paras = clean_paras("\n".join(raw_lines))
        if not paras:
            continue
        # detect author hints
        joined = " ".join(paras[:3]).lower()
        if "minha amada mary" in joined or "minha querida mary" in joined or "mary," in joined[:80]:
            author = "Gibran"
        elif "meu amado" in joined or "kahlil" in joined[:120] or "gibran" in joined[:80]:
            author = "Mary"
        elif date == "Introdução":
            author = "Gibran"
        else:
            # heuristic: many entries alternate; default Gibran for Coelho selection voice
            author = "Gibran" if i % 2 else "Mary"

        title = date if date and date != "Introdução" else (paras[0][:60] + ("…" if len(paras[0]) > 60 else ""))
        quote = paras[0][:180] + ("…" if len(paras[0]) > 180 else "")
        letters.append(
            {
                "id": i,
                "slug": slugify(date or f"carta-{i}", i),
                "date": None if date == "Introdução" else date,
                "title": title if date and date != "Introdução" else f"Carta {i}",
                "author": author,
                "paragraphs": paras,
                "quote": quote,
            }
        )

    # Fix first chunk title
    if letters and letters[0]["date"] is None:
        letters[0]["title"] = "Primeiro encontro"
        letters[0]["slug"] = "01-primeiro-encontro"

    data = {
        "meta": {
            "title": "As cartas de amor de Gibran",
            "subtitle": "Correspondência com Mary Haskell (1908–1924)",
            "sourcePdf": "cartas/As-cartas-de-amor-de-Gibran.pdf",
            "note": "Seleção condensada da correspondência entre Gibran e Mary Haskell.",
            "video": {
                "id": "9QNWeNBJm-U",
                "title": "O Grande Amor do Profeta (2009) — Lúcia Helena Galvão",
                "url": "https://www.youtube.com/watch?v=9QNWeNBJm-U",
                "channel": "Nova Acrópole",
                "host": "Lúcia Helena Galvão",
            },
        },
        "letters": letters,
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("letters", len(letters), "->", OUT)
    for L in letters[:8]:
        print(L["id"], L["slug"], L["author"], (L["date"] or "")[:30], "paras", len(L["paragraphs"]))
    print("...")
    for L in letters[-3:]:
        print(L["id"], L["slug"], L["author"], L["date"])


if __name__ == "__main__":
    main()
