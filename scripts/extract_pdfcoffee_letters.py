# -*- coding: utf-8 -*-
"""Extract all letters from Cartas de Amor - Gibran (pdfcoffee).pdf"""
from __future__ import annotations

import json
import re
from pathlib import Path

import fitz

ROOT = Path(r"E:\PROJETOS-CURSOR\OPROFETA")
PDF = ROOT / "cartas" / "Cartas de Amor - Gibran (pdfcoffee).pdf"
OUT_TXT = ROOT / "cartas" / "_pdfcoffee_extract.txt"
OUT_JSON = ROOT / "src" / "data" / "letters.json"
OUT_RAW = ROOT / "cartas" / "letters_pdfcoffee.json"

MONTHS = (
    "enero|febrero|marzo|abril|mayo|junio|julio|agosto|"
    "septiembre|octubre|noviembre|diciembre"
)
MONTH_MAP = {
    "enero": "janeiro",
    "febrero": "fevereiro",
    "marzo": "março",
    "abril": "abril",
    "mayo": "maio",
    "junio": "junho",
    "julio": "julho",
    "agosto": "agosto",
    "septiembre": "setembro",
    "octubre": "outubro",
    "noviembre": "novembro",
    "diciembre": "dezembro",
}

# OCR often drops leading digit: "0 de Noviembre" -> "10", "3 De Junio" -> "23"
DATE_LINE = re.compile(
    rf"(?im)^\s*("
    rf"(?:\d{{1,2}})\s+[Dd]e\s+(?:{MONTHS})(?:\s+[Dd]e\s+\d{{4}})?"
    rf"|(?:{MONTHS})\s+[Dd]e\s+\d{{4}}"
    rf")\s*$"
)


def fix_ocr_date(s: str) -> str:
    s = re.sub(r"\s+", " ", s.strip())
    s = s.replace(" De ", " de ").replace(" De", " de")
    # common OCR: leading 0 for 10/20/30
    m = re.match(rf"(?i)^(\d{{1,2}})\s+de\s+({MONTHS})(?:\s+de\s+(\d{{4}}))?$", s)
    if m:
        day, month, year = m.group(1), m.group(2).lower(), m.group(3)
        # keep as-is but normalize casing
        day_i = int(day)
        if year:
            return f"{day_i} de {month} de {year}"
        return f"{day_i} de {month}"
    m = re.match(rf"(?i)^({MONTHS})\s+de\s+(\d{{4}})$", s)
    if m:
        return f"{m.group(1).lower()} de {m.group(2)}"
    return s


def date_to_pt(s: str) -> str:
    out = s.lower()
    for es, pt in MONTH_MAP.items():
        out = out.replace(es, pt)
    return out


def slugify(s: str, i: int) -> str:
    base = date_to_pt(s).lower()
    for a, b in (
        ("á", "a"),
        ("à", "a"),
        ("ã", "a"),
        ("â", "a"),
        ("é", "e"),
        ("ê", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ô", "o"),
        ("õ", "o"),
        ("ú", "u"),
        ("ç", "c"),
    ):
        base = base.replace(a, b)
    base = re.sub(r"[^a-z0-9]+", "-", base)
    base = re.sub(r"-+", "-", base).strip("-")
    return f"{i:02d}-{base[:70]}" if base else f"{i:02d}-carta"


def clean_paras(block: str) -> list[str]:
    """Unwrap soft line breaks; keep real paragraph breaks."""
    block = block.replace("\xa0", " ")
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in block.splitlines()]
    paras: list[str] = []
    cur = ""

    def flush() -> None:
        nonlocal cur
        p = re.sub(r"\s+", " ", cur).strip()
        if p and len(p) > 3:
            # drop signature-only lines as separate para but keep if longer
            paras.append(p)
        cur = ""

    for ln in lines:
        if not ln:
            flush()
            continue
        if ln.startswith("QuickTime") or ln.startswith("TIFF"):
            continue
        if re.fullmatch(r"\d+", ln):
            continue
        # standalone signatures
        if re.fullmatch(r"(?i)(kahlil\s+gibran|kaklil\s+gibran|mary\s+haskell|gibran|mary|kahlil|kaklil)", ln):
            flush()
            continue

        if not cur:
            cur = ln
            continue

        # soft wrap: previous line does not end a sentence
        if not re.search(r'[.!?…”"»)\]]$', cur):
            cur = cur + " " + ln
            continue
        # new paragraph when previous ended sentence and this starts like a new one
        if ln[0].isupper() or ln[0] in "«\"“¿¡":
            flush()
            cur = ln
        else:
            cur = cur + " " + ln

    flush()
    return paras


def detect_author(paras: list[str]) -> str:
    head = " ".join(paras[:2]).lower()
    if re.search(
        r"\b(mi amada mary|mi adorada mary|querida mary|amado mary|mary,|"
        r"mary mi|pens[eé] mary|amado gibran|kahlil)\b",
        head,
    ):
        # if addressing Mary -> Gibran; if "mi amado" without mary -> Mary
        if re.search(r"\b(mi amado|querido kahlil|amado kahlil)\b", head) and "mary" not in head[:40]:
            return "Mary"
        if "mary" in head[:80]:
            return "Gibran"
    if re.search(r"\b(mi amado|querido kahlil|amado kahlil)\b", head):
        return "Mary"
    return "Gibran"


def main() -> None:
    doc = fitz.open(PDF)
    pages = []
    for i in range(doc.page_count):
        pages.append(doc[i].get_text())
    full = "\n".join(pages)
    OUT_TXT.write_text(full, encoding="utf-8")
    print("extract chars", len(full), "pages", doc.page_count)

    # PDF embeds the book twice — keep only the first copy (cut at 2nd Prefacio)
    start = full.find("Dedicatoria")
    second_pref = full.find("Prefacio", full.find("Prefacio") + 1)
    end = second_pref if second_pref > start else len(full)
    body = full[start:end] if start >= 0 else full[:end]

    # Split dedicatory narrative from dated correspondence
    corr = re.search(r"(?i)Correspondencia\s+entre", body)
    if corr:
        dedicatory = body[: corr.start()]
        dated = body[corr.end() :]
    else:
        dedicatory = ""
        dated = body

    chunks: list[tuple[str, list[str]]] = []
    if dedicatory.strip():
        chunks.append(("Dedicatoria / primer encuentro", dedicatory.splitlines()))

    current = ""
    buf: list[str] = []
    for ln in dated.splitlines():
        raw = ln.strip()
        m = DATE_LINE.match(raw)
        if m and len(raw) < 45:
            if current and buf:
                chunks.append((current, buf))
            elif current and not buf:
                pass
            current = fix_ocr_date(m.group(1))
            buf = []
        else:
            if current:
                buf.append(ln)
            # skip section title lines before first date
    if current and buf:
        chunks.append((current, buf))

    letters = []
    seen: set[str] = set()
    for i, (date, raw_lines) in enumerate(chunks, 1):
        paras = clean_paras("\n".join(raw_lines))
        # drop heading echo / front-matter leftovers
        while paras and re.match(
            r"(?i)^(dedicatoria|correspondencia|kahlil gibran|mary haskell|1908|lucas)",
            paras[0],
        ):
            paras = paras[1:]
        # drop trailing section leftovers
        while paras and re.match(
            r"(?i)^(bienaventurados|lucas|correspondencia|kahlil\s*gibran|kaklil\s*gibran|mary haskell|y$|1908|cartas de amor|quicktime|tiff)",
            paras[-1],
        ):
            paras = paras[:-1]
        # fix common OCR glues
        paras = [re.sub(r"\.([A-ZÁÉÍÓÚÑ¿¡])", r". \1", p) for p in paras]
        if not paras:
            continue
        fingerprint = paras[0][:160].lower()
        if fingerprint in seen:
            continue
        seen.add(fingerprint)

        is_intro = date.startswith("Dedicatoria")
        title = "Primeiro encontro" if is_intro else date_to_pt(date)
        date_pt = None if is_intro else date_to_pt(date)
        author = detect_author(paras)
        quote = paras[0][:220] + ("…" if len(paras[0]) > 220 else "")
        letters.append(
            {
                "id": len(letters) + 1,
                "slug": "01-primeiro-encontro" if is_intro else slugify(date, len(letters) + 1),
                "date": date_pt,
                "title": title,
                "author": author,
                "paragraphs": paras,
                "quote": quote,
                "source": "pdfcoffee-es",
            }
        )

    print("letters found", len(letters))
    for L in letters[:8]:
        print(L["id"], L["slug"], L["date"], "paras", len(L["paragraphs"]), "chars", sum(len(p) for p in L["paragraphs"]))
    print("...")
    total = sum(sum(len(p) for p in L["paragraphs"]) for L in letters)
    print("total letter chars", total)

    stub = {
        "summary": "Carta da correspondência entre Gibran e Mary Haskell — o diálogo de almas que, na leitura de Lúcia Helena Galvão, revela o amor que dá asas e sustenta a obra.",
        "keys": [
            "Amor verdadeiro eleva e não aprisiona.",
            "A distância pode ser criativa quando o vínculo é profundo.",
            "Revelar-se é a tarefa do artista e do amante.",
        ],
        "reflections": [
            "O que esta carta revela sobre o amor que constrói, em vez de possuir?",
        ],
    }
    overview = None
    notes_by_slug: dict = {}
    commentary_path = ROOT / "src" / "data" / "letters_commentary.json"
    if commentary_path.exists():
        cdata = json.loads(commentary_path.read_text(encoding="utf-8"))
        overview = cdata.get("overview")
        raw_notes = cdata.get("letters") or {}
        if isinstance(raw_notes, dict):
            notes_by_slug = raw_notes

    for L in letters:
        note = notes_by_slug.get(L["slug"])
        if note is None:
            # match by date suffix ignoring numeric prefix (01-23-de-junho-...)
            suffix = re.sub(r"^\d+-", "", L["slug"])
            for k, v in notes_by_slug.items():
                if re.sub(r"^\d+-", "", k) == suffix:
                    note = v
                    break
        L["commentary"] = note or stub

    if overview is None:
        overview = {
            "summary": "As cartas entre Khalil Gibran e Mary Haskell revelam um amor profundo, exigente e criativo — a mesma chama que prepara O Profeta.",
            "sections": [],
            "keys": [],
            "reflections": [],
        }

    # disambiguate same-day titles
    seen_dates: dict[str, int] = {}
    for L in letters:
        if not L["date"]:
            continue
        n = seen_dates.get(L["date"], 0) + 1
        seen_dates[L["date"]] = n
        if n > 1:
            L["title"] = f"{L['date']} (II)" if n == 2 else f"{L['date']} ({n})"
            L["slug"] = slugify(L["title"], L["id"])
            L["commentary"] = notes_by_slug.get(L["slug"], stub)

    data = {
        "meta": {
            "title": "Cartas de amor do Profeta",
            "subtitle": "Correspondência entre Kahlil Gibran e Mary Haskell (1908–1924)",
            "sourcePdf": "cartas/Cartas de Amor - Gibran (pdfcoffee).pdf",
            "language": "es",
            "note": "Texto integral deste volume: «Cartas de Amor del Profeta» (pdfcoffee), adaptação condensada em espanhol associada a Paulo Coelho — 62 cartas/trechos. Não é o arquivo das 600+ cartas da University of South Carolina.",
            "video": {
                "id": "9QNWeNBJm-U",
                "title": "O Grande Amor do Profeta (2009) — Lúcia Helena Galvão",
                "url": "https://www.youtube.com/watch?v=9QNWeNBJm-U",
                "channel": "Nova Acrópole",
                "host": "Lúcia Helena Galvão",
            },
            "commentary": overview,
        },
        "letters": letters,
    }

    OUT_RAW.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", OUT_JSON)
    print("wrote", OUT_RAW)


if __name__ == "__main__":
    main()
