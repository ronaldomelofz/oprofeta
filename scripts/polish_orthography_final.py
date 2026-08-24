# -*- coding: utf-8 -*-
"""Final PT-BR orthography polish (no external API)."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

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

# Safe global string replacements (order matters)
REPL = [
    ("\u00ab", "\u201c"),
    ("\u00bb", "\u201d"),
    ("Sr. Dai", "Sr. Day"),
    ("senhor Dai", "senhor Day"),
    ("galeria do Sr. Dai", "galeria do Sr. Day"),
    ("Kaklil", "Kahlil"),
    ("auto-satisfação", "autossatisfação"),
    (" .", "."),
    (" ,", ","),
    (" ;", ";"),
    (" :", ":"),
]

REGEX = [
    (r"[ \t]{2,}", " "),
    # Mary Haskell (keep Biblical Maria + filho/Jesus)
    (r"\bvida, Maria:", "vida, Mary:"),
    (r"\bMinha amada Maria\b", "Minha amada Mary"),
    (r"\bamada Maria\b", "amada Mary"),
    (r"\bAmada Maria\b", "Amada Mary"),
    (r"\bquerida Maria\b", "querida Mary"),
    (r"\bQuerida Maria\b", "Querida Mary"),
    (r"\badorada Maria\b", "adorada Mary"),
    (r"\beu e Maria\b", "eu e Mary"),
    (r"\bé a Maria que\b", "é a Mary que"),
    (r"\bMaria se veste\b", "Mary se veste"),
    (r"\bMaria não considera\b", "Mary não considera"),
    (r", Maria,", ", Mary,"),
    (r", Maria\.", ", Mary."),
    (r", Maria:", ", Mary:"),
    (r"^Maria,", "Mary,"),
    # Intimate te → você (letters register)
    (r"\bprimeira vez que te visitei\b", "primeira vez que a visitei"),
    (r"\bTe amarei\b", "Amarei você"),
    (r"\bte amei\b", "amei você"),
    (r"\bantes de te ver\b", "antes de vê-la"),
    (r"\bde te compreender\b", "de compreendê-la"),
    (r"\be te deixar\b", "e deixá-la"),
    (r"\bque te encontro\b", "que a encontro"),
    (r"\bQuando te conheci\b", "Quando a conheci"),
    (r"\bte convidar\b", "convidá-la"),
    (r"\bcontigo\b", "com você"),
    (r"\bContigo\b", "Com você"),
    (r"\bpara ti\b", "para você"),
    (r"\bde ti\b", "de você"),
    (r"\bem ti\b", "em você"),
    (r"\bsem ti\b", "sem você"),
    (r"(?<![A-Za-zÁ-ú])a ti\b", "a você"),
    (r"\bTu \b", "Você "),
    # European leftovers
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
    (r"\bprojecto\b", "projeto"),
    (r"\bsecção\b", "seção"),
    (r"\bóptimo\b", "ótimo"),
    (r"\bóptica\b", "ótica"),
    (r"\bplatónico\b", "platônico"),
    (r"\bplatónica\b", "platônica"),
    (r"\beconómico\b", "econômico"),
    (r"\bmatrimónio\b", "matrimônio"),
    (r"\bcerimónia\b", "cerimônia"),
]


def polish(s: str) -> str:
    s = fix_str(s)
    for a, b in REPL:
        s = s.replace(a, b)
    for pat, rep in REGEX:
        s = re.sub(pat, rep, s)
    return s


def walk(obj, key=None):
    if isinstance(obj, dict):
        return {k: walk(v, k) for k, v in obj.items()}
    if isinstance(obj, list):
        return [walk(x, key) for x in obj]
    if isinstance(obj, str):
        if key in SKIP_KEYS or obj.startswith("http"):
            return obj
        return polish(obj)
    return obj


def main() -> None:
    for name in ("letters.json", "letters_commentary.json", "chapters.json"):
        path = ROOT / "src" / "data" / name
        data = json.loads(path.read_text(encoding="utf-8"))
        data = walk(data)
        if name == "letters.json":
            data["meta"]["language"] = "pt-BR"
            for L in data["letters"]:
                if L.get("paragraphs"):
                    q = L["paragraphs"][0]
                    L["quote"] = q[:220] + ("…" if len(q) > 220 else "")
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print("polished", name)

    (ROOT / "cartas" / "letters_pdfcoffee.json").write_text(
        (ROOT / "src" / "data" / "letters.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    for f in list((ROOT / "src" / "pages").glob("*.tsx")) + list(
        (ROOT / "src" / "components").glob("*.tsx")
    ) + [ROOT / "index.html"]:
        old = f.read_text(encoding="utf-8")
        new = fix_str(old).replace("\u00ab", "\u201c").replace("\u00bb", "\u201d")
        new = new.replace("Sr. Dai", "Sr. Day")
        if new != old:
            f.write_text(new, encoding="utf-8")
            print("UI", f.name)
        else:
            print("ok", f.name)

    # verify
    letters = json.loads((ROOT / "src" / "data" / "letters.json").read_text(encoding="utf-8"))
    blob = json.dumps(letters, ensure_ascii=False)
    print("Sr. Day", "Sr. Day" in blob, "Sr. Dai", "Sr. Dai" in blob)
    print("Maria left:")
    for L in letters["letters"]:
        for p in L["paragraphs"]:
            if "Maria" in p:
                print(" ", L["id"], p[max(0, p.find("Maria") - 20) : p.find("Maria") + 40])
    # te leftovers
    text = "\n".join(p for L in letters["letters"] for p in L["paragraphs"])
    left = re.findall(r".{0,20}\bte\b.{0,20}", text, flags=re.I)
    print("te leftovers", len(left))
    for x in left[:15]:
        print(" ", x.replace("\n", " "))


if __name__ == "__main__":
    main()
