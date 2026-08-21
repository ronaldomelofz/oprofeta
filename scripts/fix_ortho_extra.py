# -*- coding: utf-8 -*-
"""Extra orthography pass over commentaries and UI text."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(r"e:\PROJETOS-CURSOR\OPROFETA")

# (pattern, replacement) — applied to authored commentary/UI, not blindly to book paragraphs
EXTRA = [
    ("missivas", "cartas"),
    ("Não destinavam-se", "Não se destinavam"),
    ("julgo de gratidão", "jugo de gratidão"),
    ("melhor vivera o animal", "melhor teria vivido o animal"),
    ("não pelo espondere", "não pelo espondê"),
    ("intellegere", "intelligere"),  # forma latina usual
]

# European ó that should be ô in BR (word boundaries careful)
CIRCUMFLEX = [
    (r"\bplatónicos\b", "platônicos"),
    (r"\bplatónico\b", "platônico"),
    (r"\bplatónicas\b", "platônicas"),
    (r"\bplatónica\b", "platônica"),
    (r"\beconómico\b", "econômico"),
    (r"\beconómica\b", "econômica"),
    (r"\bcrónica\b", "crônica"),
    (r"\bmatrimónio\b", "matrimônio"),
    (r"\bcerimónia\b", "cerimônia"),
    (r"\bpatrimónio\b", "patrimônio"),
    (r"\bacadémico\b", "acadêmico"),
    (r"\bfenómeno\b", "fenômeno"),
    (r"\bgénero\b", "gênero"),
    (r"\banónimo\b", "anônimo"),
    (r"\bautónomo\b", "autônomo"),
    (r"\bóbvio\b", "óbvio"),  # same
]


def fix(s: str) -> str:
    for a, b in EXTRA:
        s = s.replace(a, b)
    for pat, repl in CIRCUMFLEX:
        s = re.sub(pat, repl, s)
    return s


def walk(o):
    if isinstance(o, dict):
        return {k: walk(v) for k, v in o.items()}
    if isinstance(o, list):
        return [walk(x) for x in o]
    if isinstance(o, str):
        return fix(o)
    return o


def main() -> None:
    files = [
        ROOT / "scripts" / "commentaries_elaborated.py",
        ROOT / "src" / "pages" / "Home.tsx",
        ROOT / "src" / "pages" / "About.tsx",
        ROOT / "src" / "pages" / "Journey.tsx",
        ROOT / "src" / "pages" / "ChapterPage.tsx",
        ROOT / "src" / "components" / "Layout.tsx",
        ROOT / "README.md",
        ROOT / "videos" / "README.md",
        ROOT / "index.html",
    ]
    for p in (ROOT / "scripts" / "commentaries_dense").glob("part*.json"):
        files.append(p)

    for f in files:
        if not f.exists():
            continue
        old = f.read_text(encoding="utf-8")
        new = fix(old)
        if new != old:
            f.write_text(new, encoding="utf-8")
            print("updated", f.relative_to(ROOT))
        else:
            print("ok", f.relative_to(ROOT))

    path = ROOT / "src" / "data" / "chapters.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    # Only fix commentary/explanation/meta — keep book paragraphs unless clear typo in EXTRA
    data["meta"] = walk(data["meta"])
    for ch in data["chapters"]:
        if "commentary" in ch:
            ch["commentary"] = walk(ch["commentary"])
        if "explanation" in ch:
            ch["explanation"] = walk(ch["explanation"])
        if "quote" in ch and isinstance(ch["quote"], str):
            ch["quote"] = fix(ch["quote"])
        # book text: only safe global typos
        ch["paragraphs"] = [fix(p) if isinstance(p, str) else p for p in ch.get("paragraphs") or []]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("chapters.json rewritten")

    # verify
    t = path.read_text(encoding="utf-8")
    for bad in ["missivas", "destinavam-se", "julgo de gratidão", "vivera o animal", "espondere"]:
        if bad in t:
            print("STILL", bad)
        else:
            print("gone", bad)


if __name__ == "__main__":
    main()
