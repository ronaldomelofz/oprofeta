# -*- coding: utf-8 -*-
"""Merge letter commentaries and fix author attribution."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(r"E:\PROJETOS-CURSOR\OPROFETA")
LETTERS = ROOT / "src" / "data" / "letters.json"
COMM = ROOT / "src" / "data" / "letters_commentary.json"


def detect_author(paras: list[str]) -> str:
    head = " ".join(paras[:2]).lower()
    # Gibran writing to Mary
    if re.search(
        r"\b(minha amada mary|minha adorada mary|minha querida mary|adora(?:da)? mary|"
        r"mary, minha|querida mary|amado?\s+mary|mary será|pense mary)\b",
        head,
    ):
        return "Gibran"
    if head.startswith("mary,") or head.startswith("mary "):
        return "Gibran"
    # Mary writing to Gibran
    if re.search(
        r"\b(meu amado|meu querido|kahlil|querido gibran|amado gibran)\b",
        head,
    ):
        return "Mary"
    # Coelho selection is mostly Gibran's voice
    return "Gibran"


def main() -> None:
    letters = json.loads(LETTERS.read_text(encoding="utf-8"))
    comm = json.loads(COMM.read_text(encoding="utf-8"))

    letters["meta"]["commentary"] = comm["overview"]
    by_slug = comm.get("letters") or {}

    for L in letters["letters"]:
        L["author"] = detect_author(L.get("paragraphs") or [])
        # fix março slug
        if L.get("date"):
            L["date"] = L["date"].replace("marco", "março").replace("Marco", "Março")
        if "mar-o" in L["slug"]:
            L["slug"] = L["slug"].replace("mar-o", "marco")
        c = by_slug.get(L["slug"])
        if not c:
            # try remapped slug
            c = by_slug.get(L["slug"].replace("marco", "mar-o"))
        if c:
            L["commentary"] = c
        else:
            L["commentary"] = {
                "summary": "Esta carta integra o diálogo de almas entre Gibran e Mary — o amor que, na leitura de Lúcia Helena Galvão, dá asas e constrói a obra.",
                "keys": [
                    "Amor verdadeiro eleva e não aprisiona.",
                    "A distância pode ser criativa quando o vínculo é profundo.",
                ],
                "reflections": [
                    "O que esta carta revela sobre o amor que constrói, em vez de possuir?",
                ],
            }

    # ensure first letter title
    if letters["letters"]:
        first = letters["letters"][0]
        if first["paragraphs"] and first["paragraphs"][0].lower().startswith("introdução"):
            first["paragraphs"] = first["paragraphs"][1:]
        first["title"] = "Primeiro encontro"
        first["slug"] = "01-primeiro-encontro"

    LETTERS.write_text(json.dumps(letters, ensure_ascii=False, indent=2), encoding="utf-8")
    missing = [L["slug"] for L in letters["letters"] if L["slug"] not in by_slug and L["slug"].replace("marco", "mar-o") not in by_slug]
    print("letters", len(letters["letters"]))
    print("with overview sections", len(comm["overview"]["sections"]))
    print("missing commentary slugs", missing)
    for L in letters["letters"][:5]:
        print(L["id"], L["author"], L["slug"], "comm", bool(L.get("commentary")))


if __name__ == "__main__":
    main()
