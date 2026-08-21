# -*- coding: utf-8 -*-
"""Normalize authored project text to Portuguese (Brazil)."""
from __future__ import annotations

import importlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(r"e:\PROJETOS-CURSOR\OPROFETA")

REPLACEMENTS = [
    # ó → ô (PT-PT → PT-BR)
    ("platónicos", "platônicos"),
    ("platónicas", "platônicas"),
    ("platónico", "platônico"),
    ("platónica", "platônica"),
    ("económico", "econômico"),
    ("económica", "econômica"),
    ("económicos", "econômicos"),
    ("económicas", "econômicas"),
    ("académico", "acadêmico"),
    ("académica", "acadêmica"),
    ("académicos", "acadêmicos"),
    ("académicas", "acadêmicas"),
    ("fenómeno", "fenômeno"),
    ("fenómenos", "fenômenos"),
    ("género", "gênero"),
    ("géneros", "gêneros"),
    ("anónimo", "anônimo"),
    ("anónima", "anônima"),
    ("autónomo", "autônomo"),
    ("autónoma", "autônoma"),
    ("António", "Antônio"),
    ("crónica", "crônica"),
    ("crónicas", "crônicas"),
    ("matrimónio", "matrimônio"),
    ("matrimónios", "matrimônios"),
    ("património", "patrimônio"),
    ("cerimónia", "cerimônia"),
    ("cerimónias", "cerimônias"),
    ("harmónico", "harmônico"),
    ("harmónica", "harmônica"),
    ("irónico", "irônico"),
    ("irónica", "irônica"),
    ("tónico", "tônico"),
    ("tónica", "tônica"),
    ("cómodo", "cômodo"),
    ("cómoda", "cômoda"),
    ("abdómen", "abdômen"),
    ("gémeo", "gêmeo"),
    ("gémea", "gêmea"),
    ("óptimo", "ótimo"),
    ("óptima", "ótima"),
    ("óptica", "ótica"),
    # ct / cç europeus
    ("factos", "fatos"),
    ("de facto", "de fato"),
    ("facto ", "fato "),
    ("quotidiano", "cotidiano"),
    ("quotidiana", "cotidiana"),
    ("actuais", "atuais"),
    ("actualmente", "atualmente"),
    ("actualidade", "atualidade"),
    ("actualizar", "atualizar"),
    ("actual", "atual"),
    ("contacto", "contato"),
    ("contactos", "contatos"),
    ("objectivo", "objetivo"),
    ("objectos", "objetos"),
    ("objecto", "objeto"),
    ("projectos", "projetos"),
    ("projecto", "projeto"),
    ("secções", "seções"),
    ("secção", "seção"),
    ("direcção", "direção"),
    ("colecção", "coleção"),
    ("acções", "ações"),
    ("acção", "ação"),
    ("reacção", "reação"),
    ("excepção", "exceção"),
    ("espectáculo", "espetáculo"),
    # até + artigo (preferência BR)
    ("até ao ", "até o "),
    ("até à ", "até a "),
    ("até aos ", "até os "),
    ("até às ", "até as "),
    ("à volta", "ao redor"),
    ("ficheiros", "arquivos"),
    ("ficheiro", "arquivo"),
    ("telemóvel", "celular"),
    ("rasto", "rastro"),
    ("planeiam", "planejam"),
    ("gérmen", "germe"),
    # estar a + infinitivo → gerúndio
    ("Estou a pedir", "Estou pedindo"),
    ("estou a dar", "estou dando"),
    ("estou dando — ou a cortar —", "estou dando — ou cortando —"),
    ("estou a tentar", "estou tentando"),
    ("estou a viver", "estou vivendo"),
    ("estão a realizar", "estão realizando"),
    ("estamos a alimentar", "estamos alimentando"),
    ("está a dizer", "está dizendo"),
    # livro / comentários
    ("não vos pertencem", "não pertencem a vocês"),
    ("Vieram através de vós, não de vós", "Vieram através de vocês, não de vocês"),
    ("através de vós", "através de vocês"),
    ("não de vós", "não de vocês"),
    ("de volta a ilha", "de volta à ilha"),
    ("rumo a cidade santa", "rumo à cidade santa"),
    ("deverão encontra-Lo", "deverão encontrá-Lo"),
    ("deverão meus desejos fluírem", "deverão meus desejos fluir"),
    ("lhes foi assignado", "lhes foi atribuído"),
    ("seu amor a Vida", "seu amor à Vida"),
    ("conheçam aos segredos", "conheçam os segredos"),
    ("serenidade aos invernos", "serenidade os invernos"),
    ("e retornarem com a fragrância", "e retornar com a fragrância"),
    ("adentrem ao templo", "adentrem no templo"),
    ("perante a si", "perante si"),
    ("oferecer aquele que", "oferecer àquele que"),
    ("Encham um ao copo", "Encham um o copo"),
    ("junto a maré", "junto à maré"),
    ("junto a chuva", "junto à chuva"),
    ("conecta a terra", "conecta à terra"),
    ("entalhada a faca", "entalhada à faca"),
    ("contemplam ao mundo", "contemplam o mundo"),
    ("seguindo ao ritmo", "seguindo o ritmo"),
    # citações do comentário alinhadas ao texto BR do site
    (
        "“Quando o amor vos chamar, segui-o.”",
        "“Quando o amor lhes acenar, sigam-no.”",
    ),
    (
        "“Haja espaços na vossa união.”",
        "“Permitam que haja espaços em sua junção.”",
    ),
    (
        "“A vossa alegria é a vossa tristeza sem máscara.”",
        "“Sua alegria é a sua tristeza desmascarada.”",
    ),
    (
        "“A vossa dor é o quebrar da concha que envolve a vossa compreensão.”",
        "“Sua dor é o rompimento da casca que enclausura a sua compreensão.”",
    ),
    (
        "“O vosso amigo é a resposta às vossas necessidades.”",
        "“Seu amigo é a resposta para suas necessidades.”",
    ),
    ("Quando o amor vos chamar, segui-o", "Quando o amor lhes acenar, sigam-no"),
    # correções apontadas / varredura 2026-08
    ("missivas", "cartas"),
    ("Não destinavam-se", "Não se destinavam"),
    ("julgo de gratidão", "jugo de gratidão"),
    ("melhor vivera o animal", "melhor teria vivido o animal"),
    ("não pelo espondere", "não pelo espondê"),
]

# Guillemets -> Brazilian quotation style
REPLACEMENTS += [
    ("\u00ab", "\u201c"),  # « -> “
    ("\u00bb", "\u201d"),  # » -> ”
]


def fix_str(s: str) -> str:
    for a, b in REPLACEMENTS:
        s = s.replace(a, b)
    return s


def walk(o):
    if isinstance(o, dict):
        return {k: walk(v) for k, v in o.items()}
    if isinstance(o, list):
        return [walk(x) for x in o]
    if isinstance(o, str):
        return fix_str(o)
    return o


def main() -> None:
    files = [
        ROOT / "scripts" / "commentaries_elaborated.py",
        ROOT / "scripts" / "build_commented_edition.py",
        ROOT / "src" / "pages" / "Home.tsx",
        ROOT / "src" / "pages" / "About.tsx",
        ROOT / "src" / "pages" / "Journey.tsx",
        ROOT / "src" / "pages" / "ChapterPage.tsx",
        ROOT / "src" / "components" / "Layout.tsx",
        ROOT / "README.md",
        ROOT / "videos" / "README.md",
        ROOT / "index.html",
    ]

    for f in files:
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8")
        new = fix_str(text)
        if new != text:
            f.write_text(new, encoding="utf-8")
            print("updated", f.relative_to(ROOT))
        else:
            print("ok", f.relative_to(ROOT))

    sys.path.insert(0, str(ROOT / "scripts"))
    import commentaries_elaborated as ce

    importlib.reload(ce)

    path = ROOT / "src" / "data" / "chapters.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data = walk(data)

    for ch in data["chapters"]:
        slug = ch["slug"]
        if slug in ce.COMMENTARIES:
            essay = walk(ce.COMMENTARIES[slug])
            ch["commentary"] = essay
            ch["explanation"] = {"summary": essay["summary"], "keys": essay["keys"]}

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("chapters.json rewritten")

    pat = re.compile(
        r"platónic|económic|fenómen|género|anónim|autónom|académic|crónica|matrimónio|"
        r"cerimónia|harmónic|irónic|óptimo|quotidiano|de facto|até ao |ficheiro|"
        r"assignado|fluírem|estão a |estou a |\u00ab|\u00bb|\bvossa?\b|\bvosso\b|\bvos\b"
    )
    for f in files + [path]:
        hits = set(pat.findall(f.read_text(encoding="utf-8")))
        if hits:
            print("REMAIN", f.name, hits)


if __name__ == "__main__":
    main()
