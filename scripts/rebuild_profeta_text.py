#!/usr/bin/env python3
"""Rebuild O Profeta chapter texts from Rafael Arrais PDF."""
from __future__ import annotations

import json
import re
from pathlib import Path

import fitz

ROOT = Path(r"E:/PROJETOS-CURSOR/OPROFETA")
PDF = ROOT / "LIVRO" / "O Profeta - Khalil Gibran.pdf"
CHAPTERS_JSON = ROOT / "src" / "data" / "chapters.json"

# (slug, start_marker, end_marker) — end_marker begins the next section.
BOUNDARIES: list[tuple[str, str, str | None]] = [
    ("chegada-do-navio", "ALMUSTAFA, o eleito e amado", "ENTÃO, disse Almitra, “nos fale do Amor”"),
    ("o-amor", "ENTÃO, disse Almitra, “nos fale do Amor”", "ENTÃO Almitra falou novamente e disse"),
    ("o-casamento", "ENTÃO Almitra falou novamente e disse", "E UMA MULHER que amamentava um bebê disse"),
    ("os-filhos", "E UMA MULHER que amamentava um bebê disse", "ENTÃO lhe disse um homem rico"),
    ("a-caridade", "ENTÃO lhe disse um homem rico", "ENTÃO um homem velho, dono de uma estalagem"),
    ("o-comer-e-o-beber", "ENTÃO um homem velho, dono de uma estalagem", "ENTÃO um lavrador disse"),
    ("o-trabalho", "ENTÃO um lavrador disse", "ENTÃO disse uma mulher"),
    ("alegria-e-tristeza", "ENTÃO disse uma mulher", "ENTÃO um construtor se aproximou e lhe disse"),
    ("as-casas", "ENTÃO um construtor se aproximou e lhe disse", "E LHE DISSE um tecelão"),
    ("as-roupas", "E LHE DISSE um tecelão", "E LHE DISSE um mercador"),
    ("comprar-e-vender", "E LHE DISSE um mercador", "ENTÃO um dos juízes da cidade se aproximou e lhe disse"),
    ("crime-e-castigo", "ENTÃO um dos juízes da cidade se aproximou e lhe disse", "ENTÃO um advogado lhe disse"),
    ("as-leis", "ENTÃO um advogado lhe disse", "E LHE DISSE um orador"),
    ("a-liberdade", "E LHE DISSE um orador", "E A SACERDOTISA se manifestou novamente e lhe disse"),
    ("razao-e-paixao", "E A SACERDOTISA se manifestou novamente e lhe disse", "E UMA MULHER lhe disse"),
    ("a-dor", "E UMA MULHER lhe disse", "E UM HOMEM lhe disse"),
    ("o-autoconhecimento", "E UM HOMEM lhe disse", "ENTÃO lhe disse um professor"),
    ("o-ensino", "ENTÃO lhe disse um professor", "E UM JOVEM lhe disse"),
    ("a-amizade", "E UM JOVEM lhe disse", "E UM INTELECTUAL lhe disse"),
    ("a-conversacao", "E UM INTELECTUAL lhe disse", "E UM ASTRÔNOMO lhe disse"),
    ("o-tempo", "E UM ASTRÔNOMO lhe disse", "E UM DOS ANCIÃOS da cidade lhe disse"),
    ("o-bem-e-o-mal", "E UM DOS ANCIÃOS da cidade lhe disse", "ENTÃO uma sacerdotisa lhe disse"),
    ("a-oracao", "ENTÃO uma sacerdotisa lhe disse", "ENTÃO um eremita, que visitava a cidade uma vez por ano"),
    ("o-prazer", "ENTÃO um eremita, que visitava a cidade uma vez por ano", "E UM POETA lhe disse"),
    ("a-beleza", "E UM POETA lhe disse", "E UM VELHO SACERDOTE lhe disse"),
    ("a-religiao", "E UM VELHO SACERDOTE lhe disse", "ENTÃO, Almitra falou e lhe disse"),
    ("a-morte", "ENTÃO, Almitra falou e lhe disse", "ENTÃO, já era noitinha"),
    ("a-despedida", "ENTÃO, já era noitinha", "\nFIM\n"),
]


def extract_pdf_text() -> str:
    doc = fitz.open(PDF)
    return "\n".join(page.get_text("text") for page in doc)


def marker_pattern(text: str) -> str:
    words = re.split(r"\s+", text.strip())
    return r"\s+".join(re.escape(w) for w in words)


def find_pos(full: str, needle: str, start: int = 0) -> int:
    if needle == "\nFIM\n":
        idx = full.find("\nFIM\n", start)
        if idx < 0:
            raise ValueError("Marker not found: '\\nFIM\\n'")
        return idx
    m = re.search(marker_pattern(needle), full[start:])
    if not m:
        raise ValueError(f"Marker not found: {needle!r}")
    return start + m.start()


def normalize_linebreaks(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    return text


def split_paragraphs(body: str) -> list[str]:
    body = body.strip()
    if not body:
        return []

    blocks = re.split(r"\n\s*\n+", body)
    paragraphs: list[str] = []
    for block in blocks:
        lines = [ln.strip() for ln in block.split("\n") if ln.strip()]
        if not lines:
            continue
        para = re.sub(r"\s+", " ", " ".join(lines)).strip()
        if not para or para in {"FIM", "***"}:
            continue
        paragraphs.append(para)

    merged: list[str] = []
    for para in paragraphs:
        if merged and len(merged[-1]) < 45 and not merged[-1].endswith((".", "?", "!", "”", '"')):
            merged[-1] = merged[-1] + " " + para
        else:
            merged.append(para)
    return merged


def trim_chapter_body(slug: str, body: str) -> str:
    if slug in {"chegada-do-navio", "a-despedida"}:
        return body

    markers = [
        r"Com uma voz forte, ele lhes disse:",
        r"E ele respondeu(?: assim)?:",
        r"E ele respondeu, dizendo:",
        r"E ele a respondeu:",
        r"E ele o respondeu(?: assim)?:",
        r"E ele disse(?: assim)?:",
        r"E ele respondeu:",
    ]
    for pat in markers:
        m = re.search(pat, body, flags=re.IGNORECASE)
        if m:
            body = body[m.end() :].strip()
            break
    return body


def pick_quote(paragraphs: list[str]) -> str:
    for p in paragraphs:
        if 50 < len(p) < 190:
            return p.strip("“”\"")
    return paragraphs[0][:170].strip("“”\"") if paragraphs else ""


def looks_complete(paragraphs: list[str]) -> bool:
    if not paragraphs:
        return False
    last = paragraphs[-1].rstrip()
    if last.endswith(("…", "...")):
        return False
    if re.search(r"[.!?][”\"]?$", last):
        return True
    if last.endswith(("”", '"')):
        return True
    return False


def main() -> None:
    raw = normalize_linebreaks(extract_pdf_text())

    positions: dict[str, tuple[int, int | None]] = {}
    for slug, start_needle, end_needle in BOUNDARIES:
        start = find_pos(raw, start_needle)
        end = find_pos(raw, end_needle, start + 1) if end_needle else None
        positions[slug] = (start, end)

    data = json.loads(CHAPTERS_JSON.read_text(encoding="utf-8"))
    chapter_by_slug = {c["slug"]: c for c in data["chapters"]}

    incomplete_after: list[str] = []

    for slug, start_needle, end_needle in BOUNDARIES:
        start, end = positions[slug]
        body = raw[start:end].strip() if end else raw[start:].strip()
        body = trim_chapter_body(slug, body)
        paragraphs = split_paragraphs(body)

        ch = chapter_by_slug[slug]
        ch["paragraphs"] = paragraphs
        ch["quote"] = pick_quote(paragraphs)

        ok = looks_complete(paragraphs)
        if not ok:
            incomplete_after.append(slug)

        print(
            f"{ch['id']:02d} {slug:22s} paras={len(paragraphs):3d} "
            f"chars={sum(len(p) for p in paragraphs):5d} ok={ok}"
        )

    CHAPTERS_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("\nIncomplete AFTER:", incomplete_after)


if __name__ == "__main__":
    main()
