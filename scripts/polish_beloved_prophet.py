# -*- coding: utf-8 -*-
"""Revise Beloved Prophet PT-BR pages: orthography, names, register, typography."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(r"E:\PROJETOS-CURSOR\OPROFETA")
sys.path.insert(0, str(ROOT / "scripts"))
from fix_ptbr import fix_str  # noqa: E402

PAGES_PT = ROOT / "cartas" / "ocr_cache" / "pages_pt"
PAGES_EN = ROOT / "cartas" / "ocr_cache" / "pages"
OUT_EN_FULL = ROOT / "cartas" / "beloved_prophet_en_full.txt"
OUT_PT_FULL = ROOT / "cartas" / "beloved_prophet_pt_full.txt"
REPORT = ROOT / "cartas" / "ocr_cache" / "polish_report.json"

# Ordered string replacements (book-specific + MT leftovers)
REPL: list[tuple[str, str]] = [
    ("\u00ab", "\u201c"),
    ("\u00bb", "\u201d"),
    ("Kaklil", "Kahlil"),
    ("Kahil ", "Kahlil "),
    ("Kahll", "Kahlil"),
    ("Sr. Dai", "Sr. Day"),
    ("senhor Dai", "senhor Day"),
    ("galeria do Sr. Dai", "galeria do Sr. Day"),
    ("Idéia", "Ideia"),
    ("idéia", "ideia"),
    ("Idéias", "Ideias"),
    ("idéias", "ideias"),
    ("comité", "comitê"),
    ("Comité", "Comitê"),
    ("comissão", "comissão"),  # noop keep
    ("Bahá'í", "bahá'í"),
    ("Bahai", "bahá'í"),
    ("Baha'i", "bahá'í"),
    ("Abdul-Baha", "Abdul-Baha"),
    ("Abdu'l-Bahá", "Abdul-Baha"),
    ("Abdu’l-Bahá", "Abdul-Baha"),
    ("auto-satisfação", "autossatisfação"),
    ("anti-humano", "antihumano"),
    ("semi-aberto", "semiaberto"),
    (" .", "."),
    (" ,", ","),
    (" ;", ";"),
    (" :", ":"),
    (" !", "!"),
    (" ?", "?"),
    ("——KG ——", "—— KG ——"),
    ("——MH ——", "—— MH ——"),
    ("-KG-", "—— KG ——"),
    ("-MH-", "—— MH ——"),
    ("--KG--", "—— KG ——"),
    ("--MH--", "—— MH ——"),
    ("—KG —", "—— KG ——"),
    ("—MH —", "—— MH ——"),
    ("[DIARIO]", "[DIÁRIO]"),
    ("[JOURNAL]", "[DIÁRIO]"),
    ("---PAGINA ", "---PÁGINA "),
]

REGEX: list[tuple[str, str]] = [
    (r"[ \t]{2,}", " "),
    (r"\n{3,}", "\n\n"),
    # Mary Haskell — never Maria (except biblical rare; restore Mary)
    (r"\bMinha amada Maria\b", "Minha amada Mary"),
    (r"\bminha amada Maria\b", "minha amada Mary"),
    (r"\bAmada Maria\b", "Amada Mary"),
    (r"\bamada Maria\b", "amada Mary"),
    (r"\bQuerida Maria\b", "Querida Mary"),
    (r"\bquerida Maria\b", "querida Mary"),
    (r"\badorada Maria\b", "adorada Mary"),
    (r"\bAdorada Maria\b", "Adorada Mary"),
    (r"\bquerida e amada Maria\b", "querida e amada Mary"),
    (r"\bMaria Haskell\b", "Mary Haskell"),
    (r"\beu e Maria\b", "eu e Mary"),
    (r"\bé a Maria que\b", "é a Mary que"),
    (r"\bMaria se veste\b", "Mary se veste"),
    (r"\bMaria não\b", "Mary não"),
    (r"\bMaria envia\b", "Mary envia"),
    (r"\bMaria,\b", "Mary,"),
    (r"\bMaria:\b", "Mary:"),
    (r"\bMaria\.\b", "Mary."),
    (r"^Maria,", "Mary,"),
    (r", Maria,", ", Mary,"),
    (r"\bpara Maria\b", "para Mary"),
    (r"\bcom Maria\b", "com Mary"),
    (r"\bde Maria\b", "de Mary"),
    (r"\ba Maria\b", "a Mary"),
    (r"\bque Maria\b", "que Mary"),
    (r"\be Maria\b", "e Mary"),
    (r"\bquando Maria\b", "quando Mary"),
    (r"\bse Maria\b", "se Mary"),
    (r"\bcomo Maria\b", "como Mary"),
    (r"\bMas Maria\b", "Mas Mary"),
    (r"\bPois Maria\b", "Pois Mary"),
    (r"\bEntão Maria\b", "Então Mary"),
    (r"\bMary e Kahlil\b", "Mary e Kahlil"),
    # Intimate 2nd person → você / a (cartas)
    (r"\bQue Deus te guarde\b", "Que Deus a guarde"),
    (r"\bque Deus te guarde\b", "que Deus a guarde"),
    (r"\bQue Deus te abençoe\b", "Que Deus a abençoe"),
    (r"\bque Deus te abençoe\b", "que Deus a abençoe"),
    (r"\bQue Deus te ame\b", "Que Deus a ame"),
    (r"\bque Deus te ame\b", "que Deus a ame"),
    (r"\bDeus te ame\b", "Deus a ame"),
    (r"\bte mantenha\b", "a mantenha"),
    (r"\bte ame e a mantenha\b", "a ame e a mantenha"),
    (r"\bDeus te abençoe\b", "Deus a abençoe"),
    (r"\bDeus te guarde\b", "Deus a guarde"),
    (r"\bte guarde\b", "a guarde"),
    (r"\bte abençoe\b", "a abençoe"),
    (r"\bte ame\b", "a ame"),
    (r"\bTe amarei\b", "Amarei você"),
    (r"\bte amei\b", "amei você"),
    (r"\bantes de te ver\b", "antes de vê-la"),
    (r"\bde te compreender\b", "de compreendê-la"),
    (r"\be te deixar\b", "e deixá-la"),
    (r"\bque te encontro\b", "que a encontro"),
    (r"\bQuando te conheci\b", "Quando a conheci"),
    (r"\bprimeira vez que te visitei\b", "primeira vez que a visitei"),
    (r"\bprimeira vez que te vi\b", "primeira vez que a vi"),
    (r"\bte vi\b", "a vi"),
    (r"\bte convidar\b", "convidá-la"),
    (r"\bcontigo\b", "com você"),
    (r"\bContigo\b", "Com você"),
    (r"\bpara ti\b", "para você"),
    (r"\bde ti\b", "de você"),
    (r"\bem ti\b", "em você"),
    (r"\bsem ti\b", "sem você"),
    (r"(?<![A-Za-zÁ-úÀ-ÿ])a ti\b", "a você"),
    (r"\bTu \b", "Você "),
    (r"(?<![A-Za-zÁ-úÀ-ÿ])tu (?!és\b)", "você "),
    # European → BR
    (r"\bautocarro\b", "ônibus"),
    (r"\bcomboio\b", "trem"),
    (r"\btelemóvel\b", "celular"),
    (r"\bequipa\b", "equipe"),
    (r"\bdesporto\b", "esporte"),
    (r"\brapariga\b", "garota"),
    (r"\bficheiro\b", "arquivo"),
    (r"\bpequeno-almoço\b", "café da manhã"),
    (r"\bactualmente\b", "atualmente"),
    (r"\bactual\b", "atual"),
    (r"\bfacto\b", "fato"),
    (r"\bfactos\b", "fatos"),
    (r"\bcontacto\b", "contato"),
    (r"\bcontactos\b", "contatos"),
    (r"\bobjecto\b", "objeto"),
    (r"\bobjectos\b", "objetos"),
    (r"\bprojecto\b", "projeto"),
    (r"\bprojectos\b", "projetos"),
    (r"\bsecção\b", "seção"),
    (r"\bsecções\b", "seções"),
    (r"\bóptimo\b", "ótimo"),
    (r"\bóptica\b", "ótica"),
    (r"\bplatónico\b", "platônico"),
    (r"\bplatónica\b", "platônica"),
    (r"\beconómico\b", "econômico"),
    (r"\bmatrimónio\b", "matrimônio"),
    (r"\bcerimónia\b", "cerimônia"),
    (r"\bcerimónias\b", "cerimônias"),
    (r"\bacção\b", "ação"),
    (r"\bacções\b", "ações"),
    (r"\bdirecção\b", "direção"),
    (r"\bcolecção\b", "coleção"),
    (r"\bacepção\b", "acepção"),
    # Common season capitalization from EN
    (r"\bneste Verão\b", "neste verão"),
    (r"\bneste Inverno\b", "neste inverno"),
    (r"\bnesta Primavera\b", "nesta primavera"),
    (r"\bneste Outono\b", "neste outono"),
    (r"\bdurante este Verão\b", "durante este verão"),
    (r"\bdurante o Verão\b", "durante o verão"),
    (r"\bdurante o Inverno\b", "durante o inverno"),
    (r"\bno Verão\b", "no verão"),
    (r"\bno Inverno\b", "no inverno"),
    # Spacing around dashes
    (r"[ \t]+—[ \t]+", " — "),
]

# Light EN OCR cleanup (do not rewrite literary content)
EN_REPL = [
    ("Kahll", "Kahlil"),
    ("Kaklil", "Kahlil"),
    ("Chartes Russell", "Charles Russell"),
    ("Massachuseus", "Massachusetts"),
    ("Massachusetss", "Massachusetts"),
    ("Matechusetts", "Massachusetts"),
    ("rejuccnation", "rejuvenation"),
    ("ofj to the West", "off to the West"),
    ("holidayt", "holidays"),
    ("moee money", "more money"),
    ("Near Easr", "Near East"),
    ("talk with hir ", "talk with him "),
]


def polish_pt(text: str) -> str:
    text = fix_str(text)
    for a, b in REPL:
        text = text.replace(a, b)
    for pat, rep in REGEX:
        text = re.sub(pat, rep, text, flags=re.MULTILINE)
    # Normalize header
    text = re.sub(r"^---P[ÁA]GINA\s+(\d+)---", r"---PÁGINA \1---", text, count=1)
    return text.strip() + "\n"


def polish_en(text: str) -> str:
    for a, b in EN_REPL:
        text = text.replace(a, b)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip() + "\n"


def count_hits(blob: str) -> dict:
    keys = [
        "Maria",
        "Idéia",
        "idéia",
        "comité",
        "facto",
        "contacto",
        "contigo",
        "para ti",
        "de ti",
        "em ti",
        "Que Deus te",
        "Sr. Dai",
        "Kaklil",
        "cerimónia",
        "matrimónio",
        "acção",
        "óptimo",
    ]
    return {k: blob.count(k) for k in keys if blob.count(k)}


def main() -> None:
    changed_pt = 0
    changed_en = 0
    for n in range(1, 457):
        pf = PAGES_PT / f"{n:03d}.txt"
        if pf.exists():
            old = pf.read_text(encoding="utf-8")
            new = polish_pt(old)
            if new != old:
                pf.write_text(new, encoding="utf-8")
                changed_pt += 1
        ef = PAGES_EN / f"{n:03d}.txt"
        if ef.exists():
            old = ef.read_text(encoding="utf-8")
            new = polish_en(old)
            if new != old:
                ef.write_text(new, encoding="utf-8")
                changed_en += 1
        if n % 50 == 0:
            print(f"... {n}/456", flush=True)

    # Optional LanguageTool pass (typos / compounding only)
    lt_fixes = 0
    use_lt = "--lt" in sys.argv
    if use_lt:
        import time

        import language_tool_python

        print("LanguageTool pt-BR…", flush=True)
        try:
            tool = language_tool_python.LanguageTool("pt-BR")
        except Exception:
            tool = language_tool_python.LanguageToolPublicAPI("pt-BR")
        skip = {
            "gibran",
            "kahlil",
            "mary",
            "haskell",
            "marianna",
            "abdul-baha",
            "bahá'í",
            "bsharri",
            "orkalis",
            "almustafa",
            "kg",
            "mh",
        }
        for n in range(1, 457):
            pf = PAGES_PT / f"{n:03d}.txt"
            text = pf.read_text(encoding="utf-8")
            body = text
            header = ""
            if text.startswith("---"):
                lines = text.splitlines()
                header = lines[0] + "\n"
                body = "\n".join(lines[1:])
            try:
                matches = tool.check(body)
            except Exception as e:
                print(f"  LT skip page {n}: {e}", flush=True)
                time.sleep(1.2)
                continue
            fixed = 0
            for m in sorted(matches, key=lambda x: x.offset, reverse=True):
                cat = (m.category or "").upper()
                rid = str(m.rule_id or "")
                if cat not in {"TYPOS", "CASING", "PUNCTUATION", "TYPOGRAPHY", "COMPOUNDING"}:
                    if not rid.startswith(
                        (
                            "PT_SIMPLE_REPLACE",
                            "MORFOLOGIK_RULE_PT_BR",
                            "HUNSPELL_RULE",
                            "WHITESPACE_RULE",
                        )
                    ):
                        continue
                if not m.replacements:
                    continue
                start, end = m.offset, m.offset + m.error_length
                if start < 0 or end > len(body):
                    continue
                err = body[start:end]
                if err.lower() in skip:
                    continue
                repl = m.replacements[0]
                if abs(len(repl) - len(err)) > 18:
                    continue
                # Don't rewrite proper names Mary/Kahlil mid-fix
                if err in {"Mary", "Kahlil", "Marianna", "Gibran", "Haskell"}:
                    continue
                body = body[:start] + repl + body[end:]
                fixed += 1
            if fixed:
                pf.write_text(header + body.strip() + "\n", encoding="utf-8")
                lt_fixes += fixed
            if n % 25 == 0:
                print(f"  LT {n}/456 fixes_so_far={lt_fixes}", flush=True)
            time.sleep(0.15)

    # Rebuild full texts
    en_parts, pt_parts = [], []
    for n in range(1, 457):
        en_parts.append((PAGES_EN / f"{n:03d}.txt").read_text(encoding="utf-8").strip())
        en_parts.append("\n\n")
        pt_parts.append((PAGES_PT / f"{n:03d}.txt").read_text(encoding="utf-8").strip())
        pt_parts.append("\n\n")
    OUT_EN_FULL.write_text("".join(en_parts), encoding="utf-8")
    OUT_PT_FULL.write_text("".join(pt_parts), encoding="utf-8")

    blob = OUT_PT_FULL.read_text(encoding="utf-8")
    report = {
        "changed_pt_pages": changed_pt,
        "changed_en_pages": changed_en,
        "lt_fixes": lt_fixes,
        "leftovers": count_hits(blob),
        "pt_full_bytes": OUT_PT_FULL.stat().st_size,
        "en_full_bytes": OUT_EN_FULL.stat().st_size,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
