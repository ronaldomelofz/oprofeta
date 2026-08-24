# -*- coding: utf-8 -*-
"""Revise PT-BR orthography across site texts (local rules + LanguageTool public API)."""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

import language_tool_python

ROOT = Path(r"E:\PROJETOS-CURSOR\OPROFETA")
sys.path.insert(0, str(ROOT / "scripts"))
from fix_ptbr import fix_str  # noqa: E402

SKIP_KEYS = {
    "id",
    "slug",
    "url",
    "searchUrl",
    "sourcePdf",
    "channel",
    "host",
    "language",
    "source",
}

SKIP_WORDS = {
    "vós",
    "vos",
    "vosso",
    "vossa",
    "vossos",
    "vossas",
    "convosco",
    "dais",
    "sois",
    "podeis",
    "vivei",
    "amai",
    "enchei",
    "dai",
    "fazei",
    "deixai",
    "acreditai",
    "digais",
    "pudésseis",
    "visitais",
    "possuís",
    "gibran",
    "kahlil",
    "mary",
    "haskell",
    "almustafa",
    "almitra",
    "orkalis",
}

# Extra BR / MT / typography (beyond fix_ptbr)
EXTRA = [
    ("\u00ab", "\u201c"),
    ("\u00bb", "\u201d"),
    ("Kaklil", "Kahlil"),
    ("auto-satisfação", "autossatisfação"),
    ("anti-humano", "antihumano"),
    (" .", "."),
    (" ,", ","),
    (" ;", ";"),
    (" :", ":"),
]

# Regex local fixes
REGEX = [
    (r"[ \t]{2,}", " "),
    (r"\bMinha amada Maria\b", "Minha amada Mary"),
    (r"\bminha amada Maria\b", "minha amada Mary"),
    (r"\bAmada Maria\b", "Amada Mary"),
    (r"\bamada Maria\b", "amada Mary"),
    (r"\bQuerida Maria\b", "Querida Mary"),
    (r"\bquerida Maria\b", "querida Mary"),
    (r"\badorada Maria\b", "adorada Mary"),
    (r"\bAdorada Maria\b", "Adorada Mary"),
    (r"\bMaria, minha\b", "Mary, minha"),
    (r"\bMaria, você\b", "Mary, você"),
    (r"\bMaria, o\b", "Mary, o"),
    (r"\bMaria, uma\b", "Mary, uma"),
    (r"\bMaria, que\b", "Mary, que"),
    (r"\bMaria, gostaria\b", "Mary, gostaria"),
    (r"\bMaria, é\b", "Mary, é"),
    (r"\bMaria:\b", "Mary:"),
    (r"\bMaria se veste\b", "Mary se veste"),
    (r"\bMaria não considera\b", "Mary não considera"),
    (r"\bMaria envia\b", "Mary envia"),
    (r"\beu e Maria\b", "eu e Mary"),
    (r"\bé a Maria que\b", "é a Mary que"),
    (r"\bSua carta, Maria\b", "Sua carta, Mary"),
    (r"\bVocê sabe, Maria\b", "Você sabe, Mary"),
    (r"\bSempre acreditei, Maria\b", "Sempre acreditei, Mary"),
    (r"\bImagine, Maria\b", "Imagine, Mary"),
    (r"\bDaí a luta eterna, Maria\b", "Daí a luta eterna, Mary"),
    (r"\bCom o passar dos anos, Maria\b", "Com o passar dos anos, Mary"),
    (r"\bvida, Maria:\b", "vida, Mary:"),
    (r"\bte convidar\b", "convidá-la"),
    (r"\bcontigo\b", "com você"),
    (r"\bContigo\b", "Com você"),
    (r"\bpara ti\b", "para você"),
    (r"\bde ti\b", "de você"),
    (r"\bem ti\b", "em você"),
    (r"\bsem ti\b", "sem você"),
    (r"(?<![A-Za-zÁ-ú])a ti\b", "a você"),
    (r"\bTu \b", "Você "),
    (r"(?<![A-Za-zÁ-ú])tu (?!és\b)", "você "),
    # European → BR extras
    (r"\bautocarro\b", "ônibus"),
    (r"\bcomboio\b", "trem"),
    (r"\btelemóvel\b", "celular"),
    (r"\bequipa\b", "equipe"),
    (r"\bdesporto\b", "esporte"),
    (r"\brapariga\b", "garota"),
    (r"\bficheiro\b", "arquivo"),
    (r"\bpequeno-almoço\b", "café da manhã"),
]


def local_fix(s: str) -> str:
    s = fix_str(s)
    for a, b in EXTRA:
        s = s.replace(a, b)
    for pat, rep in REGEX:
        s = re.sub(pat, rep, s)
    return s


def apply_lt(tool, text: str) -> tuple[str, int]:
    if len(text) < 20:
        return text, 0
    try:
        matches = tool.check(text)
    except Exception as e:
        print("  LT skip:", type(e).__name__, str(e)[:80])
        time.sleep(1.5)
        return text, 0
    fixes = 0
    for m in sorted(matches, key=lambda x: x.offset, reverse=True):
        cat = (m.category or "").upper()
        if cat not in {"TYPOS", "CASING", "PUNCTUATION", "TYPOGRAPHY", "COMPOUNDING"}:
            if not str(m.rule_id).startswith(
                ("PT_SIMPLE_REPLACE", "MORFOLOGIK_RULE_PT_BR", "HUNSPELL_RULE", "WHITESPACE_RULE")
            ):
                continue
        if not m.replacements:
            continue
        start, end = m.offset, m.offset + m.error_length
        if start < 0 or end > len(text):
            continue
        err = text[start:end]
        if err.lower() in SKIP_WORDS:
            continue
        repl = m.replacements[0]
        if abs(len(repl) - len(err)) > 18:
            continue
        text = text[:start] + repl + text[end:]
        fixes += 1
    return text, fixes


def walk_local(obj, key=None):
    if isinstance(obj, dict):
        return {k: walk_local(v, k) for k, v in obj.items()}
    if isinstance(obj, list):
        return [walk_local(x, key) for x in obj]
    if isinstance(obj, str):
        if key in SKIP_KEYS or obj.startswith("http"):
            return obj
        return local_fix(obj)
    return obj


def revise_letters_with_lt(tool, data) -> int:
    total = 0
    letters = data["letters"]
    for i, L in enumerate(letters, 1):
        print(f"  letter {i}/{len(letters)} {L.get('slug')}", flush=True)
        new_paras = []
        for p in L.get("paragraphs") or []:
            p2 = local_fix(p)
            p2, n = apply_lt(tool, p2)
            total += n
            new_paras.append(p2)
            time.sleep(0.35)  # be kind to public API
        L["paragraphs"] = new_paras
        if new_paras:
            q = new_paras[0]
            L["quote"] = q[:220] + ("…" if len(q) > 220 else "")
        # commentary stubs
        if isinstance(L.get("commentary"), dict):
            for field in ("summary",):
                if field in L["commentary"]:
                    L["commentary"][field] = local_fix(L["commentary"][field])
            for field in ("keys", "reflections"):
                if field in L["commentary"]:
                    L["commentary"][field] = [local_fix(x) for x in L["commentary"][field]]
    if "meta" in data:
        data["meta"] = walk_local(data["meta"])
        data["meta"]["language"] = "pt-BR"
    return total


def main() -> None:
    print("1) Local orthography on all JSON…", flush=True)
    for name in ("chapters.json", "letters.json", "letters_commentary.json"):
        path = ROOT / "src" / "data" / name
        data = json.loads(path.read_text(encoding="utf-8"))
        data = walk_local(data)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print("  local ok", name, flush=True)

    print("2) LanguageTool public API on letters…", flush=True)
    tool = language_tool_python.LanguageToolPublicAPI("pt-BR")
    path = ROOT / "src" / "data" / "letters.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    n = revise_letters_with_lt(tool, data)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / "cartas" / "letters_pdfcoffee.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("  LT letter fixes:", n, flush=True)

    print("3) Local-only pass again on commentary/chapters (no public API flood)…", flush=True)
    for name in ("letters_commentary.json", "chapters.json"):
        path = ROOT / "src" / "data" / name
        data = json.loads(path.read_text(encoding="utf-8"))
        data = walk_local(data)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print("  ok", name, flush=True)

    print("4) UI pages…", flush=True)
    for f in list((ROOT / "src" / "pages").glob("*.tsx")) + list(
        (ROOT / "src" / "components").glob("*.tsx")
    ) + [ROOT / "index.html"]:
        old = f.read_text(encoding="utf-8")
        new = local_fix(old)
        # don't break JSX with aggressive regex on "tu "
        # re-read safer: only guillemets + fix_str
        new = fix_str(old).replace("\u00ab", "\u201c").replace("\u00bb", "\u201d")
        if new != old:
            f.write_text(new, encoding="utf-8")
            print("  updated", f.name)
        else:
            print("  ok", f.name)

    # report remaining Maria
    data = json.loads((ROOT / "src" / "data" / "letters.json").read_text(encoding="utf-8"))
    rem = []
    for L in data["letters"]:
        for p in L["paragraphs"]:
            if "Maria" in p:
                rem.append((L["id"], p[max(0, p.find("Maria") - 25) : p.find("Maria") + 35]))
    print("remaining Maria:", rem)
    print("done")


if __name__ == "__main__":
    main()
