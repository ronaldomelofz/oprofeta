#!/usr/bin/env python3
"""Rebuild rich commentaries anchored on chapter discussion (skip biography)."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(r"e:\PROJETOS-CURSOR\OPROFETA")
TRANS = ROOT / "scripts" / "transcripts"
OUT = ROOT / "src" / "data" / "chapters.json"

VIDEO_IDS = {
    "o-amor": "QWiNKqHn7DA",
    "o-casamento": "6F_wJ95-maw",
    "os-filhos": "p_1-Qzxcu5Y",
    "a-caridade": "cf8gDtjMMEc",
    "o-comer-e-o-beber": "G7U9ZnIs3AA",
    "o-trabalho": "8G8pIIqUKw8",
    "alegria-e-tristeza": "wTvadWGh8Tc",
    "as-casas": "qbJUFRROp9Q",
    "as-roupas": "El2iIv5xmtU",
    "comprar-e-vender": "7yMXE_1ZbVE",
    "o-ensino": "7yMXE_1ZbVE",
    "crime-e-castigo": "EyJNJTI3INc",
    "as-leis": "3XwSsNfVMWA",
    "a-liberdade": "Y-EokChUXO8",
    "razao-e-paixao": "F5WJy_hGnfM",
    "a-dor": "Lc-d64uz6e4",
    "o-autoconhecimento": "GdwnmdAjqMY",
    "a-amizade": "VwVkEC2lYJE",
    "a-conversacao": "9VEIwYU9eP4",
    "o-tempo": "si1UY48X0v4",
    "o-bem-e-o-mal": "eJ8ybMWNYvs",
    "a-oracao": "5JT2rwDCoNk",
    "o-prazer": "2hUpEAbipNc",
    "a-beleza": "6niePYlYtNg",
    "a-religiao": "hx-Hm77AVwA",
    "a-morte": "Zg6JLS7EW1M",
}

FRAME = {
    "chegada-do-navio": {
        "summary": "Antes das perguntas, Gibran monta o mito: Almustafa vive doze anos em Orphalese sem ser ouvido. Só a partida desperta a cidade — a consciência nasce no contraste.",
        "sections": [
            {
                "heading": "Linguagem de mito",
                "body": "Na série da Nova Acrópole, Lúcia Helena Galvão insiste: O Profeta não é romance literal. É mito — o protagonista é a própria consciência; os demais personagens são forças interiores projetadas. Doze anos evocam um ciclo completo de experiência humana.",
            },
            {
                "heading": "Consciência pelo contraste",
                "body": "Ninguém valorizou Almustafa até ele decidir partir. Valorizamos o que começa a escapar. No contraste entre ter e perder, a cidade finalmente pede a verdade que tinha ao lado durante uma vida inteira.",
            },
            {
                "heading": "O pedido de Almitra",
                "body": "A vidente Almitra — a primeira a crer — pede: «Revele-nos a nós mesmos.» Toda a obra nasce desse instante. A despedida torna-se colheita: o que estava em silêncio pede palavra.",
            },
        ],
        "keys": [
            "O Profeta é mito: diálogo interior tornado palavra.",
            "A consciência se dá pelo contraste.",
            "Só na iminência da perda a cidade pergunta.",
        ],
        "reflections": [
            "Que sabedoria tenho ignorado à minha volta?",
            "O que só valorizo quando ameaça partir?",
        ],
    },
    "a-despedida": {
        "summary": "Fecha-se o ciclo: o vento convida a partir. O que foi semeado permanece; Almitra fica no quebra-mar enquanto Almustafa promete regressar com a maré.",
        "sections": [
            {
                "heading": "Sementes ao vento",
                "body": "Os errantes não começam o dia onde terminaram o anterior. Somos sementes: quando amadurecemos, o vento nos espalha. A despedida não apaga o vivido — amplia a sede de viver.",
            },
            {
                "heading": "O capitão espera o silêncio",
                "body": "O capitão é paciente; as velas estão cheias, mas espera o silêncio do profeta. Partir é consentimento interior. O rio já atingiu o mar; a grande mãe aperta o filho ao peito.",
            },
            {
                "heading": "A promessa do regresso",
                "body": "«Mais um curto instante… e outra mulher me conceberá.» A sabedoria não morre com o corpo do sábio — renasce em cada geração capaz de perguntar.",
            },
        ],
        "keys": [
            "Partir é espalhar o que amadureceu.",
            "A memória fiel também é um porto.",
            "A sabedoria promete ciclo após ciclo.",
        ],
        "reflections": [
            "O que deixo semeado ao fechar uma etapa?",
            "Sei partir sem negar o que foi dado?",
        ],
    },
    "a-beleza": {
        "summary": "A beleza eleva e transforma: não é só o que agrada aos sentidos, mas o que revela a harmonia entre o visível e o invisível.",
        "sections": [
            {
                "heading": "Além da aparência",
                "body": "Gibran desloca a beleza do gosto superficial para um campo formativo. A frase-chave da palestra resume o movimento: «A beleza é a eternidade contemplando a si mesma no espelho.»",
            },
            {
                "heading": "Caminho espiritual",
                "body": "Na leitura comentada, a estética aparece como via de elevação moral — eco da tradição clássica. Cultivar o belo é educar o olhar e a conduta no quotidiano.",
            },
            {
                "heading": "Vocês são o espelho",
                "body": "A beleza não é apenas objeto externo. Quando a vida desvela o rosto sagrado, a consciência reconhece-se nele — eternidade e espelho são o mesmo mistério.",
            },
        ],
        "keys": [
            "A beleza verdadeira eleva, não apenas agrada.",
            "Estética e moral se encontram no cultivo do olhar.",
            "«A beleza é a eternidade contemplando a si mesma no espelho.»",
        ],
        "reflections": [
            "O que chamo de belo revela o que valorizo?",
            "Que beleza do quotidiano ainda não sei contemplar?",
        ],
    },
    "a-morte": {
        "summary": "Vida e morte são uma, como o rio e o mar. O segredo da morte só se lê no coração da vida.",
        "sections": [
            {
                "heading": "No coração da vida",
                "body": "A coruja feita para a noite não descortina a luz do dia. O medo da morte muitas vezes é cegueira perante o que a vida já ensina — só se encontra o mistério procurando-o no coração do viver.",
            },
            {
                "heading": "Despir-se ao vento",
                "body": "Morrer é expor-se ao vento e fundir-se ao sol; cessar de respirar é libertar o hálito das marés inquietas. A imagem é transição e expansão, não aniquilação.",
            },
            {
                "heading": "A dança verdadeira",
                "body": "Só depois do silêncio se canta; só no cume se começa a subir; quando a terra reivindica o corpo, começa a dança verdadeira. A despedida prepara o regresso.",
            },
        ],
        "keys": [
            "Vida e morte são uma, como o rio e o mar.",
            "O temor da morte é tremor diante de uma honra maior.",
            "A profundidade da vida prepara a compreensão da morte.",
        ],
        "reflections": [
            "Como vivo hoje o que gostaria de ter vivido ao partir?",
            "O meu medo da morte revela o que ainda não amei?",
        ],
    },
}


def clean(text: str) -> str:
    text = re.sub(r"\[.*?\]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    for marker in ["Vocês sabiam que a Nova Acrópole", "Assine nossa plataforma"]:
        i = text.find(marker)
        if i > 3000:
            text = text[:i]
    return text


def anchor_start(text: str, title: str, paragraphs: list[str]) -> int:
    candidates = []
    for pat in [
        r"Fala-nos d[aoe]",
        r"fale-nos d[aoe]",
        r"nos fale d[aoe]",
        r"Quando o amor",
        r"O vosso amigo",
        r"hoje (nós |a gente )?(vamos|vou) (falar|tratar|comentar)",
    ]:
        m = re.search(pat, text, re.I)
        if m:
            candidates.append(m.start())
    # try fragment from gibran text
    for p in paragraphs[1:8]:
        frag = re.sub(r"\s+", " ", p).strip()
        if len(frag) < 30:
            continue
        needle = frag[8:36]
        if len(needle) < 12:
            continue
        i = text.find(needle)
        if i > 0:
            candidates.append(max(0, i - 80))
    if candidates:
        return min(candidates)
    # fallback: skip first third of long lectures
    return len(text) // 3 if len(text) > 12000 else 0


def sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?…])\s+", text)
    out = []
    for p in parts:
        p = p.strip()
        if len(p) < 55:
            continue
        if re.search(r"mary haskell|tuberculose|inscreva-se|acropoleplay", p, re.I):
            continue
        if len(p) > 380:
            while len(p) > 380:
                cut = p.rfind(" ", 0, 380)
                if cut < 100:
                    cut = 380
                out.append(p[:cut].strip())
                p = p[cut:].strip()
        if len(p) >= 55:
            out.append(p)
    return out


def distill(text: str, title: str, paragraphs: list[str]) -> dict:
    text = clean(text)
    start = anchor_start(text, title, paragraphs)
    body = text[start:]
    sents = sentences(body)
    if len(sents) < 6:
        sents = sentences(text[len(text) // 4 :])

    # score by overlap with chapter lexicon + teaching tone
    title_tokens = set(re.findall(r"[a-záàãâéêíóôõúç]{4,}", title.lower()))
    scored = []
    for i, s in enumerate(sents):
        low = s.lower()
        sc = 0.0
        for t in title_tokens:
            if t in low:
                sc += 2.5
        for w in [
            "significa",
            "ou seja",
            "porque",
            "filosof",
            "alma",
            "consciência",
            "simbol",
            "virtude",
            "egoísmo",
            "fraternidade",
            "platão",
            "gibran",
            "verdade",
            "sagrado",
            "essência",
            "humano",
        ]:
            if w in low:
                sc += 1.0
        if any(frag[:20].lower() in low for frag in paragraphs[:5] if len(frag) > 25):
            sc += 3.0
        if 70 <= len(s) <= 280:
            sc += 0.8
        scored.append((sc, i, s))

    scored.sort(reverse=True)
    picked = []
    used = set()
    for sc, i, s in scored:
        if sc < 2.0 and len(picked) >= 4:
            continue
        key = s[:50]
        if key in used:
            continue
        used.add(key)
        picked.append((i, s))
        if len(picked) >= 12:
            break
    picked.sort()
    chosen = [s for _, s in picked]

    headings = [
        "O texto em foco",
        "Leitura filosófica",
        "Símbolos e exigências",
        "Na vida concreta",
        "O que permanece",
    ]
    sections = []
    for idx in range(0, len(chosen), 2):
        chunk = chosen[idx : idx + 2]
        if not chunk:
            continue
        body_txt = " ".join(chunk)
        body_txt = re.sub(r"\b(\w+)( \1\b){1,3}", r"\1", body_txt)
        sections.append({"heading": headings[len(sections) % len(headings)], "body": body_txt})
        if len(sections) >= 5:
            break

    summary = " ".join(chosen[:2]) if chosen else f"Comentário ao capítulo «{title}»."
    if len(summary) > 340:
        summary = summary[:337].rsplit(" ", 1)[0] + "…"

    keys = []
    for s in chosen:
        if 45 < len(s) < 150:
            keys.append(s.rstrip(". "))
        if len(keys) >= 4:
            break
    if len(keys) < 3:
        keys = [s[:130].rstrip(". ") for s in chosen[:4]]

    reflections = [
        f"Como este capítulo sobre {title.lower()} corrige o meu uso habitual desta palavra?",
        "Que atitude concreta este ensinamento pede de mim agora?",
        "Onde ainda vivo apenas a casca deste poema?",
    ]
    return {
        "summary": summary,
        "sections": sections,
        "keys": keys[:5],
        "reflections": reflections,
    }


def load_transcript(slug: str) -> str | None:
    path = TRANS / f"{slug}.txt"
    if slug == "o-ensino" and not path.exists():
        path = TRANS / "comprar-e-vender.txt"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


def main() -> None:
    data = json.loads(OUT.read_text(encoding="utf-8"))
    data["meta"]["title"] = "O Profeta Comentado"
    data["meta"]["subtitle"] = "Khalil Gibran · leitura filosófica capítulo a capítulo"
    data["meta"]["edition"] = "comentada"
    data["meta"]["note"] = (
        "Edição comentada a partir de «O Profeta - Khalil Gibran.pdf» (trad. Rafael Arrais) "
        "e das palestras de Lúcia Helena Galvão na série O Profeta (Nova Acrópole Brasil). "
        "O PDF Challita (o-profeta-gibran-khalil-gibra.pdf) serviu de contraste tipográfico/editorial."
    )

    for ch in data["chapters"]:
        slug = ch["slug"]
        vid = VIDEO_IDS.get(slug)
        ch["videoId"] = vid
        ch["videoUrl"] = f"https://www.youtube.com/watch?v={vid}" if vid else None

        if slug in FRAME:
            essay = FRAME[slug]
        else:
            raw = load_transcript(slug)
            if raw:
                essay = distill(raw, ch["title"], ch["paragraphs"])
            else:
                essay = {
                    "summary": f"Leitura comentada do capítulo «{ch['title']}».",
                    "sections": [
                        {
                            "heading": "Ler nas entrelinhas",
                            "body": "Gibran sugere mais do que explica. A série da Nova Acrópole convida a abrir a dimensão filosófica do poema.",
                        }
                    ],
                    "keys": ["A poesia não explica: insinua."],
                    "reflections": [f"O que muda se eu levar a sério «{ch['title']}»?"],
                }

        ch["commentary"] = essay
        ch["explanation"] = {"summary": essay["summary"], "keys": essay["keys"]}

    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    for c in data["chapters"]:
        print(f"{c['id']:02d} {c['title']}: {len(c['commentary']['sections'])}s | {c['commentary']['summary'][:90]}…")


if __name__ == "__main__":
    main()
