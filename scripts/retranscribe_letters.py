# -*- coding: utf-8 -*-
"""
Retranscribe all letters from the source PDF with strict cleanup,
then translate carefully to Brazilian Portuguese.
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

import fitz
from deep_translator import GoogleTranslator

ROOT = Path(r"E:\PROJETOS-CURSOR\OPROFETA")
sys.path.insert(0, str(ROOT / "scripts"))
from fix_ptbr import fix_str  # noqa: E402

PDF = ROOT / "cartas" / "Cartas de Amor - Gibran (pdfcoffee).pdf"
OUT_JSON = ROOT / "src" / "data" / "letters.json"
OUT_ES = ROOT / "cartas" / "letters_source_es.json"
OUT_TXT = ROOT / "cartas" / "_pdfcoffee_extract.txt"
COMMENTARY = ROOT / "src" / "data" / "letters_commentary.json"

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
DATE_LINE = re.compile(
    rf"(?im)^\s*("
    rf"(?:\d{{1,2}})\s+[Dd]e\s+(?:{MONTHS})(?:\s+[Dd]e\s+\d{{4}})?"
    rf"|(?:{MONTHS})\s+[Dd]e\s+\d{{4}}"
    rf")\s*$"
)

JUNK_LINE = re.compile(
    r"(?i)^(<?\s*)?(quicktime|tiff|decompressor|are needed to see this picture|"
    r"sin comprimir|needed to see|ver esta foto|são necessários|"
    r"son necesarios|para ver esta (foto|imagen|picture)).*$"
)
JUNK_INLINE = re.compile(
    r"(?is)QuickTime.*?picture\.|"
    r"TIFF\s*\([^)]*\)\s*decompressor|"
    r"are needed to see this picture\.?|"
    r"São necessários para ver esta foto\.?|"
    r"Son necesarios para ver esta (foto|imagen)\.?"
)

CHUNK = 4000


def fix_ocr_date(s: str) -> str:
    s = re.sub(r"\s+", " ", s.strip())
    s = s.replace(" De ", " de ")
    m = re.match(rf"(?i)^(\d{{1,2}})\s+de\s+({MONTHS})(?:\s+de\s+(\d{{4}}))?$", s)
    if m:
        day, month, year = int(m.group(1)), m.group(2).lower(), m.group(3)
        return f"{day} de {month}" + (f" de {year}" if year else "")
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


def fix_spanish_ocr(text: str) -> str:
    text = JUNK_INLINE.sub("", text)
    reps = [
        (r"\benla\b", "en la"),
        (r"\benel\b", "en el"),
        (r"\bdela\b", "de la"),
        (r"\bdelas\b", "de las"),
        (r"\bdelo\b", "de lo"),
        (r"\bael\b", "a el"),
        (r"\bsimimo\b", "sí mismo"),
        (r"\bmimo\b", "mismo"),
        (r"\batravés\b", "a través"),
        (r"\batravés\b", "a través"),
        (r"\bKaklil\b", "Kahlil"),
        (r"\sle dinero\b", "el dinero"),
        (r"\s+", " "),
    ]
    for a, b in reps:
        text = re.sub(a, b, text)
    return text.strip()


def clean_paras(block: str) -> list[str]:
    block = JUNK_INLINE.sub("\n", block)
    block = block.replace("\xa0", " ")
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in block.splitlines()]
    paras: list[str] = []
    cur = ""

    def flush() -> None:
        nonlocal cur
        p = fix_spanish_ocr(re.sub(r"\s+", " ", cur))
        if not p or len(p) < 8:
            cur = ""
            return
        if JUNK_LINE.match(p):
            cur = ""
            return
        if re.search(r"(?i)needed to see|ver esta foto|quicktime|decompressor", p):
            cur = ""
            return
        paras.append(p)
        cur = ""

    for ln in lines:
        if not ln or JUNK_LINE.match(ln):
            flush()
            continue
        if re.fullmatch(r"\d+", ln):
            continue
        if re.fullmatch(
            r"(?i)(kahlil\s+gibran|kaklil\s+gibran|mary\s+haskell|gibran|mary|kahlil|kaklil)",
            ln,
        ):
            flush()
            continue
        if not cur:
            cur = ln
            continue
        if not re.search(r'[.!?…"»)\]]$', cur):
            cur = cur + " " + ln
            continue
        if ln[0].isupper() or ln[0] in "«\"“¿¡":
            flush()
            cur = ln
        else:
            cur = cur + " " + ln
    flush()
    return paras


def detect_author(paras: list[str]) -> str:
    head = " ".join(paras[:2]).lower()
    if re.search(r"\b(mi amado|querido kahlil|amado kahlil)\b", head) and "mary" not in head[:50]:
        return "Mary"
    if re.search(r"\b(mi amada mary|mi adorada mary|querida mary|mary,|mary mi)\b", head):
        return "Gibran"
    if re.search(r"\b(mi amado|querido kahlil|amado kahlil)\b", head):
        return "Mary"
    return "Gibran"


def extract_spanish() -> list[dict]:
    doc = fitz.open(PDF)
    pages = [doc[i].get_text() for i in range(doc.page_count)]
    full = "\n".join(pages)
    OUT_TXT.write_text(full, encoding="utf-8")

    start = full.find("Dedicatoria")
    second_pref = full.find("Prefacio", full.find("Prefacio") + 1)
    end = second_pref if second_pref > start else len(full)
    body = full[start:end] if start >= 0 else full[:end]

    corr = re.search(r"(?i)Correspondencia\s+entre", body)
    if corr:
        dedicatory = body[: corr.start()]
        dated = body[corr.end() :]
    else:
        dedicatory, dated = "", body

    chunks: list[tuple[str, list[str]]] = []
    if dedicatory.strip():
        chunks.append(("Dedicatoria / primer encuentro", dedicatory.splitlines()))

    current, buf = "", []
    for ln in dated.splitlines():
        raw = ln.strip()
        m = DATE_LINE.match(raw)
        if m and len(raw) < 45:
            if current and buf:
                chunks.append((current, buf))
            current = fix_ocr_date(m.group(1))
            buf = []
        elif current:
            buf.append(ln)
    if current and buf:
        chunks.append((current, buf))

    letters: list[dict] = []
    seen: set[str] = set()
    for date, raw_lines in chunks:
        paras = clean_paras("\n".join(raw_lines))
        while paras and re.match(
            r"(?i)^(dedicatoria|correspondencia|kahlil|mary haskell|1908|lucas|bienaventurados|cartas de amor)",
            paras[0],
        ):
            paras = paras[1:]
        while paras and re.match(
            r"(?i)^(bienaventurados|lucas|correspondencia|kahlil|mary|y$|1908|cartas de amor|quicktime|needed)",
            paras[-1],
        ):
            paras = paras[:-1]
        if not paras:
            continue
        fp = paras[0][:160].lower()
        if fp in seen:
            continue
        seen.add(fp)
        is_intro = date.startswith("Dedicatoria")
        title = "Primeiro encontro" if is_intro else date_to_pt(date)
        date_pt = None if is_intro else date_to_pt(date)
        letters.append(
            {
                "id": len(letters) + 1,
                "slug": "01-primeiro-encontro" if is_intro else slugify(date, len(letters) + 1),
                "date": date_pt,
                "title": title,
                "author": detect_author(paras),
                "paragraphs_es": paras,
            }
        )

    # same-day titles
    seen_dates: dict[str, int] = {}
    for L in letters:
        if not L["date"]:
            continue
        n = seen_dates.get(L["date"], 0) + 1
        seen_dates[L["date"]] = n
        if n > 1:
            L["title"] = f"{L['date']} (II)" if n == 2 else f"{L['date']} ({n})"
            L["slug"] = slugify(L["title"], L["id"])
    return letters


def translate_text(translator: GoogleTranslator, text: str) -> str:
    text = text.strip()
    if not text:
        return text
    if len(text) <= CHUNK:
        for attempt in range(6):
            try:
                return translator.translate(text)
            except Exception as e:
                time.sleep(2 + attempt * 2)
                if attempt == 5:
                    print("FAIL:", text[:80], e)
                    return text
        return text
    parts = re.split(r"(?<=[.!?…»\"])\s+", text)
    chunks, buf = [], ""
    for p in parts:
        if len(buf) + len(p) + 1 <= CHUNK:
            buf = f"{buf} {p}".strip()
        else:
            if buf:
                chunks.append(buf)
            buf = p
    if buf:
        chunks.append(buf)
    out = []
    for ch in chunks:
        out.append(translate_text(translator, ch))
        time.sleep(0.3)
    return " ".join(out)


def polish_pt(s: str) -> str:
    s = fix_str(s)
    s = JUNK_INLINE.sub("", s)
    for a, b in (
        ("São necessários para ver esta foto.", ""),
        ("São necessários para ver esta foto", ""),
        ("Sr. Dai", "Sr. Day"),
        ("Minha amada Maria", "Minha amada Mary"),
        ("amada Maria", "amada Mary"),
        ("Amada Maria", "Amada Mary"),
        ("querida Maria", "querida Mary"),
        ("Querida Maria", "Querida Mary"),
        ("adorada Maria", "adorada Mary"),
        ("eu e Maria", "eu e Mary"),
        ("é a Maria que", "é a Mary que"),
        ("Maria se veste", "Mary se veste"),
        ("Maria não considera", "Mary não considera"),
        (", Maria,", ", Mary,"),
        (", Maria.", ", Mary."),
        (", Maria:", ", Mary:"),
        ("Sua carta, Maria", "Sua carta, Mary"),
        ("Você sabe, Maria", "Você sabe, Mary"),
        ("Sempre acreditei, Maria", "Sempre acreditei, Mary"),
        ("Imagine, Maria", "Imagine, Mary"),
        ("Daí a luta eterna, Maria", "Daí a luta eterna, Mary"),
        ("Com o passar dos anos, Maria", "Com o passar dos anos, Mary"),
        ("vida, Maria:", "vida, Mary:"),
        ("contigo", "com você"),
        ("Contigo", "Com você"),
        ("para ti", "para você"),
        ("de ti", "de você"),
        ("em ti", "em você"),
        ("sem ti", "sem você"),
        ("a ti", "a você"),
        ("Tu ", "Você "),
        ("te convidar", "convidá-la"),
        ("primeira vez que te visitei", "primeira vez que a visitei"),
        ("Te amarei", "Amarei você"),
        ("te amei", "amei você"),
        ("antes de te ver", "antes de vê-la"),
        ("de te compreender", "de compreendê-la"),
        ("e te deixar", "e deixá-la"),
        ("que te encontro", "que a encontro"),
        ("Quando te conheci", "Quando a conheci"),
        ("auto-satisfação", "autossatisfação"),
        (" le dinheiro", " o dinheiro"),
        ("Até essa data, ele sempre recusou", "Até então, eu sempre recusara"),
        ("\u00ab", "\u201c"),
        ("\u00bb", "\u201d"),
    ):
        s = s.replace(a, b)
    s = re.sub(r"^Maria,", "Mary,", s)
    s = re.sub(r"[ \t]{2,}", " ", s)
    s = re.sub(r" +([.,;:])", r"\1", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(
        r"([.!?])\s+([a-záéíóúàâêôãõç])",
        lambda m: m.group(1) + " " + m.group(2).upper(),
        s,
    )
    s = re.sub(r";\s+([A-ZÁÉÍÓÚÀÂÊÔÃÕ])", lambda m: "; " + m.group(1).lower(), s)
    s = re.sub(r'(["”])\s+você\b', r"\1 Você", s)
    return s.strip()


def load_commentary_map() -> tuple[dict, dict]:
    overview = None
    by_slug: dict = {}
    if COMMENTARY.exists():
        c = json.loads(COMMENTARY.read_text(encoding="utf-8"))
        overview = c.get("overview")
        raw = c.get("letters") or {}
        if isinstance(raw, dict):
            by_slug = raw
    # also from current letters.json
    if OUT_JSON.exists():
        old = json.loads(OUT_JSON.read_text(encoding="utf-8"))
        if overview is None:
            overview = (old.get("meta") or {}).get("commentary")
        for L in old.get("letters") or []:
            if L.get("slug") and L.get("commentary"):
                by_slug.setdefault(L["slug"], L["commentary"])
            if L.get("date") and L.get("commentary"):
                by_slug.setdefault(L["date"].lower(), L["commentary"])
    stub = {
        "summary": "Carta da correspondência entre Gibran e Mary Haskell — diálogo de almas que revela o amor que dá asas e sustenta a obra.",
        "keys": [
            "Amor verdadeiro eleva e não aprisiona.",
            "A distância pode ser criativa quando o vínculo é profundo.",
            "Revelar-se é a tarefa do artista e do amante.",
        ],
        "reflections": [
            "O que esta carta revela sobre o amor que constrói, em vez de possuir?",
        ],
    }
    return overview or stub, by_slug


def attach_commentary(letter: dict, by_slug: dict, stub: dict) -> dict:
    note = by_slug.get(letter["slug"])
    if note is None:
        suffix = re.sub(r"^\d+-", "", letter["slug"])
        for k, v in by_slug.items():
            if re.sub(r"^\d+-", "", str(k)) == suffix:
                note = v
                break
    if note is None and letter.get("date"):
        note = by_slug.get(letter["date"].lower())
    return note if isinstance(note, dict) and "summary" in note else stub


def main() -> None:
    print("1) Extracting Spanish…", flush=True)
    es_letters = extract_spanish()
    print("  letters", len(es_letters), flush=True)
    # sanity: no junk
    junk = 0
    for L in es_letters:
        for p in L["paragraphs_es"]:
            if re.search(r"(?i)quicktime|needed to see|ver esta foto|decompressor", p):
                junk += 1
                print("  JUNK LEFT", L["id"], p[:80])
    print("  junk paras", junk, flush=True)

    OUT_ES.write_text(
        json.dumps({"letters": es_letters}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("2) Translating to PT-BR…", flush=True)
    translator = GoogleTranslator(source="es", target="pt")
    overview, by_slug = load_commentary_map()
    stub = {
        "summary": "Carta da correspondência entre Gibran e Mary Haskell — diálogo de almas que revela o amor que dá asas e sustenta a obra.",
        "keys": [
            "Amor verdadeiro eleva e não aprisiona.",
            "A distância pode ser criativa quando o vínculo é profundo.",
            "Revelar-se é a tarefa do artista e do amante.",
        ],
        "reflections": [
            "O que esta carta revela sobre o amor que constrói, em vez de possuir?",
        ],
    }

    out_letters = []
    for i, L in enumerate(es_letters, 1):
        print(f"  [{i}/{len(es_letters)}] {L['slug']}", flush=True)
        paras_pt = []
        for p in L["paragraphs_es"]:
            pt = polish_pt(translate_text(translator, p))
            if pt and not re.search(r"(?i)ver esta foto|needed to see|quicktime", pt):
                paras_pt.append(pt)
            time.sleep(0.25)
        if not paras_pt:
            continue
        item = {
            "id": L["id"],
            "slug": L["slug"],
            "date": L["date"],
            "title": L["title"],
            "author": L["author"],
            "paragraphs": paras_pt,
            "quote": paras_pt[0][:220] + ("…" if len(paras_pt[0]) > 220 else ""),
            "commentary": attach_commentary(L, by_slug, stub),
        }
        out_letters.append(item)
        if i % 5 == 0:
            # checkpoint
            data = _pack(overview, out_letters)
            OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    data = _pack(overview, out_letters)
    OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", OUT_JSON, "n=", len(out_letters), flush=True)

    # final junk check
    blob = json.dumps(data, ensure_ascii=False)
    for bad in ["QuickTime", "TIFF", "needed to see", "ver esta foto", "São necessários", "pdfcoffee"]:
        print(f"  contains {bad!r}:", bad in blob)


def _pack(overview, letters):
    return {
        "meta": {
            "title": "Cartas de amor do Profeta",
            "subtitle": "Correspondência entre Kahlil Gibran e Mary Haskell (1908–1924)",
            "language": "pt-BR",
            "note": (
                "Seleção da correspondência entre Kahlil Gibran e Mary Haskell, "
                "com leitura a partir da palestra O Grande Amor do Profeta."
            ),
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


if __name__ == "__main__":
    main()
