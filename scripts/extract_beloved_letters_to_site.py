# -*- coding: utf-8 -*-
"""Build site letters.json: EN structure + PT translation of each letter body."""
from __future__ import annotations

import json
import re
import time
import unicodedata
from pathlib import Path

from deep_translator import GoogleTranslator

ROOT = Path(r"E:\PROJETOS-CURSOR\OPROFETA")
PAGES_EN = ROOT / "cartas" / "ocr_cache" / "pages"
OUT = ROOT / "src" / "data" / "letters.json"
BACKUP_OLD = ROOT / "cartas" / "letters_selection_62.json"
CACHE = ROOT / "cartas" / "ocr_cache" / "letters_pt_bodies.json"
EXTRACT_JSON = ROOT / "cartas" / "letters_beloved_extracted.json"

MONTHS_EN = {
    "january": "janeiro",
    "february": "fevereiro",
    "march": "março",
    "april": "abril",
    "may": "maio",
    "june": "junho",
    "july": "julho",
    "august": "agosto",
    "september": "setembro",
    "october": "outubro",
    "november": "novembro",
    "december": "dezembro",
}
WEEKDAYS_EN = {
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
}
CITIES = {"new york", "boston", "paris", "cambridge", "columbia", "maine"}


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text[:60] or "carta"


def strip_header(text: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].startswith("---"):
        return "\n".join(lines[1:])
    return text


def is_div(line: str, who: str) -> bool:
    s = re.sub(r"[\s—\-–−_=~*•❧☙◆◇\[\]]+", "", line.strip())
    return s == who


def load_en_rows() -> list[tuple[int, str]]:
    rows: list[tuple[int, str]] = []
    for n in range(1, 457):
        t = strip_header((PAGES_EN / f"{n:03d}.txt").read_text(encoding="utf-8", errors="ignore"))
        for ln in t.splitlines():
            rows.append((n, ln))
        rows.append((n, ""))
    return rows


def parse_date_en(text: str) -> str | None:
    m = re.search(
        r"(January|February|March|April|May|June|July|August|September|October|November|December)"
        r"\s+(\d{1,2}),?\s+(19[0-3]\d)",
        text,
        re.I,
    )
    if m:
        return f"{int(m.group(2))} de {MONTHS_EN[m.group(1).lower()]} de {m.group(3)}"
    m = re.search(
        r"\b(January|February|March|April|May|June|July|August|September|October|November|December)"
        r"\s+(19[0-3]\d)",
        text,
        re.I,
    )
    if m:
        return f"{MONTHS_EN[m.group(1).lower()]} de {m.group(2)}"
    m = re.search(r"\b(19[0-3]\d)\b", text)
    return m.group(1) if m else None


def looks_like_header(line: str) -> bool:
    s = line.strip().strip("[]")
    if not s or len(s) > 70:
        return False
    low = s.lower()
    if low in WEEKDAYS_EN or any(low.startswith(w) for w in WEEKDAYS_EN):
        return True
    if any(c in low for c in CITIES):
        return True
    if re.search(r"\b19[0-3]\d\b", s):
        return True
    if re.match(
        r"^(january|february|march|april|may|june|july|august|september|october|november|december)\b",
        low,
    ):
        return True
    return False


def split_paragraphs(body_lines: list[str]) -> list[str]:
    cleaned = [ln for ln in body_lines if not re.match(r"^\[JOURNAL\]$", ln.strip(), re.I)]
    i = 0
    while i < len(cleaned) and (not cleaned[i].strip() or looks_like_header(cleaned[i])):
        i += 1
    content = cleaned[i:]
    sig_idx = None
    for j, ln in enumerate(content):
        if re.fullmatch(r"Kahlil|Mary|Lovingly,?", ln.strip()):
            sig_idx = j
            break
    if sig_idx is not None:
        tail = content[sig_idx + 1 :]
        content = content[: sig_idx + 1]
        extra: list[str] = []
        for ln in tail:
            if not ln.strip():
                if extra:
                    break
                continue
            if ln.strip().startswith("*") or ln.strip().startswith("∗"):
                extra.append(ln.strip())
            else:
                break
        content.extend(extra)

    paras: list[str] = []
    buf: list[str] = []
    for ln in content:
        if not ln.strip():
            if buf:
                paras.append(re.sub(r"\s+", " ", " ".join(x.strip() for x in buf)))
                buf = []
            continue
        buf.append(ln)
    if buf:
        paras.append(re.sub(r"\s+", " ", " ".join(x.strip() for x in buf)))
    out = []
    for p in paras:
        p = p.strip()
        if not p:
            continue
        if re.fullmatch(r"[—\-–−\s]*KG[—\-–−\s]*", p) or re.fullmatch(r"[—\-–−\s]*MH[—\-–−\s]*", p):
            continue
        out.append(p)
    return out


def extract_en_letters() -> list[dict]:
    rows = load_en_rows()
    letters: list[dict] = []
    i = 0
    while i < len(rows):
        _, line = rows[i]
        who = None
        if is_div(line, "KG"):
            who = "KG"
        elif is_div(line, "MH"):
            who = "MH"
        if not who:
            i += 1
            continue
        start_page = rows[i][0]
        i += 1
        body: list[str] = []
        end_page = start_page
        while i < len(rows):
            pn, ln = rows[i]
            if is_div(ln, "KG") or is_div(ln, "MH"):
                break
            body.append(ln)
            end_page = pn
            i += 1
        body_txt = "\n".join(body)
        if re.search(r"\[JOURNAL\]", body_txt, re.I):
            continue
        paragraphs = split_paragraphs(body)
        if not paragraphs:
            continue
        date = parse_date_en(body_txt[:500])
        has_sig = any(re.fullmatch(r"Kahlil|Mary|Lovingly,?", p.strip()) for p in paragraphs[-3:])
        chars = sum(len(p) for p in paragraphs)
        if not date and not has_sig and chars < 100:
            continue
        letters.append(
            {
                "who": who,
                "date": date,
                "paragraphs_en": paragraphs,
                "start_page": start_page,
                "end_page": end_page,
            }
        )
    return letters


def translate_paragraphs(translator: GoogleTranslator, paras: list[str]) -> list[str]:
    out: list[str] = []
    for p in paras:
        # keep signatures
        if re.fullmatch(r"Kahlil|Mary|Lovingly,?", p.strip()):
            out.append(p.strip().replace("Lovingly", "Com carinho"))
            continue
        if len(p) < 2:
            out.append(p)
            continue
        for attempt in range(5):
            try:
                # Google limit ~5000
                if len(p) <= 4200:
                    out.append(translator.translate(p))
                else:
                    # split long para
                    chunks = re.split(r"(?<=[.!?])\s+", p)
                    buf, parts = "", []
                    for c in chunks:
                        if len(buf) + len(c) + 1 <= 4200:
                            buf = f"{buf} {c}".strip()
                        else:
                            if buf:
                                parts.append(translator.translate(buf))
                                time.sleep(0.25)
                            buf = c
                    if buf:
                        parts.append(translator.translate(buf))
                    out.append(" ".join(parts))
                break
            except Exception as e:
                time.sleep(1.5 + attempt)
                if attempt == 4:
                    print("  translate fail:", e, p[:60])
                    out.append(p)
        time.sleep(0.2)
    return out


def polish_pt_paras(paras: list[str]) -> list[str]:
    repl = [
        ("Kaklil", "Kahlil"),
        ("Sr. Dai", "Sr. Day"),
        ("Idéia", "Ideia"),
        ("idéia", "ideia"),
        ("comité", "comitê"),
        ("amada Maria", "amada Mary"),
        ("querida Maria", "querida Mary"),
        ("Amada Maria", "Amada Mary"),
        ("Querida Maria", "Querida Mary"),
        ("Maria Haskell", "Mary Haskell"),
    ]
    out = []
    for p in paras:
        for a, b in repl:
            p = p.replace(a, b)
        p = re.sub(r"\bQue Deus te guarde\b", "Que Deus a guarde", p)
        p = re.sub(r"\bQue Deus te abençoe\b", "Que Deus a abençoe", p)
        p = re.sub(r"\bQue Deus te ame\b", "Que Deus a ame", p)
        out.append(p)
    return out


def make_title(date: str | None, paragraphs: list[str], n: int) -> str:
    if date:
        return date
    if paragraphs:
        snip = re.sub(r"^[—\-–−]+\s*", "", paragraphs[0])[:48].rstrip(" ,;:")
        if len(paragraphs[0]) > 48:
            snip += "…"
        return snip or f"Carta {n}"
    return f"Carta {n}"


def make_commentary(author: str, date: str | None, paragraphs: list[str]) -> dict:
    who = "Gibran" if author == "Gibran" else "Mary Haskell"
    opener = re.sub(r"\s+", " ", (paragraphs[0] if paragraphs else "")).strip()
    if len(opener) > 280:
        opener = opener[:277].rstrip() + "…"
    when = f", em {date}," if date else ""
    summary = (
        f"Carta de {who}{when} preservada em *Beloved Prophet*. "
        f"{opener if opener else 'Texto integral da correspondência.'}"
    )
    keys = (
        ["Voz de Gibran", "Criação e gratidão", "Distância criativa"]
        if author == "Gibran"
        else ["Voz de Mary", "Mecenato e consciência", "Diálogo exigente"]
    )
    reflections = [
        "O que esta carta revela sobre o vínculo entre liberdade e entrega?",
        "Que imagem ou frase aqui ecoa temas depois publicados em O Profeta?",
    ]
    return {"summary": summary, "keys": keys, "reflections": reflections}


def main() -> None:
    current = json.loads(OUT.read_text(encoding="utf-8"))
    if len(current.get("letters", [])) <= 80 and not BACKUP_OLD.exists():
        BACKUP_OLD.write_text(json.dumps(current, ensure_ascii=False, indent=2), encoding="utf-8")

    meta_src = current["meta"]
    if BACKUP_OLD.exists():
        meta_src = json.loads(BACKUP_OLD.read_text(encoding="utf-8"))["meta"]
    rich = []
    if BACKUP_OLD.exists():
        rich = json.loads(BACKUP_OLD.read_text(encoding="utf-8")).get("letters", [])

    print("Extracting EN letter blocks…", flush=True)
    letters_en = extract_en_letters()
    print(f"EN letters found: {len(letters_en)}", flush=True)

    cache: dict[str, list[str]] = {}
    if CACHE.exists():
        cache = json.loads(CACHE.read_text(encoding="utf-8"))

    translator = GoogleTranslator(source="en", target="pt")
    letters_out: list[dict] = []
    used_slugs: set[str] = set()

    for n, b in enumerate(letters_en, 1):
        key = f"{b['who']}:{b['start_page']}:{b['end_page']}:{b.get('date')}"
        author = "Gibran" if b["who"] == "KG" else "Mary"
        if key in cache and cache[key]:
            paragraphs = cache[key]
        else:
            print(f"translate {n}/{len(letters_en)} {author} {b.get('date')}…", flush=True)
            paragraphs = polish_pt_paras(translate_paragraphs(translator, b["paragraphs_en"]))
            cache[key] = paragraphs
            if n % 10 == 0:
                CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")

        date = b["date"]
        title = make_title(date, paragraphs, n)
        base = slugify(f"{n:03d}-{title}-{author}")
        slug = base
        k = 2
        while slug in used_slugs:
            slug = f"{base}-{k}"
            k += 1
        used_slugs.add(slug)

        commentary = None
        if date:
            for L in rich:
                if L.get("date") == date and L.get("author") == author:
                    commentary = L.get("commentary")
                    break
            if not commentary:
                for L in rich:
                    if L.get("date") == date:
                        commentary = L.get("commentary")
                        break
        if not commentary:
            commentary = make_commentary(author, date, paragraphs)

        quote = paragraphs[0][:220] + ("…" if len(paragraphs[0]) > 220 else "")
        letters_out.append(
            {
                "id": n,
                "slug": slug,
                "date": date,
                "title": title,
                "author": author,
                "paragraphs": paragraphs,
                "quote": quote,
                "commentary": commentary,
            }
        )

    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")

    meta = meta_src
    meta["language"] = "pt-BR"
    meta["note"] = (
        f"Integral da correspondência em *Beloved Prophet* (Virginia Hilu): "
        f"{len(letters_out)} cartas em português do Brasil, com ensaio a partir da palestra "
        f"O Grande Amor do Profeta. PDF completo disponível para download."
    )
    meta["sourcePdf"] = "/Beloved-Prophet-Cartas-PTBR.pdf"
    meta["sourceEdition"] = (
        "Beloved Prophet: The Love Letters of Kahlil Gibran and Mary Haskell "
        "and Her Private Journal, organizado por Virginia Hilu (Alfred A. Knopf)"
    )
    meta["subtitle"] = "Correspondência entre Kahlil Gibran e Mary Haskell (1908–1931)"

    data = {"meta": meta, "letters": letters_out}
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    EXTRACT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"DONE letters={len(letters_out)} gibran={sum(1 for L in letters_out if L['author']=='Gibran')} mary={sum(1 for L in letters_out if L['author']=='Mary')}")
    print(f"size={OUT.stat().st_size/1e6:.2f}MB")


if __name__ == "__main__":
    main()
