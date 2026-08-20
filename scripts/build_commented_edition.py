#!/usr/bin/env python3
"""Build commented edition data from PDF text + Nova Acrópole transcripts."""
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
    "o-ensino": "7yMXE_1ZbVE",  # episódio #10: educação e comércio
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

# Fallback essays when transcript unavailable (from video descriptions + série)
FALLBACK = {
    "a-beleza": {
        "summary": "Gibran convida a olhar além da aparência: a beleza eleva, transforma e desperta a alma. O belo não é só o que agrada aos sentidos — revela a harmonia entre o visível e o invisível.",
        "sections": [
            {
                "heading": "Além da aparência",
                "body": "Na leitura comentada, Lúcia Helena Galvão mostra que Gibran desloca a beleza do gosto superficial para um campo formativo: aquilo que educa o olhar e a conduta. A frase-chave do episódio resume o movimento: “A beleza é a eternidade contemplando a si mesma no espelho.”",
            },
            {
                "heading": "Beleza e elevação moral",
                "body": "A tradição clássica — de Platão a Aristóteles, e ecos contemporâneos como Roger Scruton — trata o belo como caminho espiritual. Cultivar a estética na vida prática é reconhecer o verdadeiro belo no cotidiano, não apenas no ornamento.",
            },
            {
                "heading": "Vocês são o espelho",
                "body": "Gibran devolve a responsabilidade ao leitor: a beleza não é só objeto externo. A vida desvela o rosto sagrado quando a consciência se torna capaz de contemplá-lo — e, nesse espelho, a eternidade se reconhece.",
            },
        ],
        "keys": [
            "A beleza verdadeira eleva e transforma, não apenas agrada.",
            "Estética e moral se encontram no cultivo do olhar.",
            "“A beleza é a eternidade contemplando a si mesma no espelho.”",
        ],
        "reflections": [
            "O que chamo de belo revela o que valorizo?",
            "Há beleza no meu cotidiano que ainda não sei contemplar?",
        ],
    },
    "a-morte": {
        "summary": "A poesia não explica: insinua. Neste capítulo, Gibran une vida e morte como rio e mar — e a série da Nova Acrópole convida a tornar a existência mais válida e profunda diante desse mistério.",
        "sections": [
            {
                "heading": "O segredo no coração da vida",
                "body": "Só se descobre o mistério da morte procurando-o no coração da vida. A coruja feita para a noite não descortina a luz do dia: o medo da morte muitas vezes é cegueira perante o que a vida já ensina.",
            },
            {
                "heading": "Despir-se ao vento",
                "body": "Morrer é expor-se ao vento e fundir-se ao sol; cessar de respirar é libertar o hálito das marés inquietas. A imagem não é niilista: é transição, expansão, busca livre do divino.",
            },
            {
                "heading": "Só então se dança de verdade",
                "body": "Beber do rio do silêncio, atingir o cume e só então começar a subir; quando a terra reivindica o corpo, começa a dança verdadeira. A despedida do ciclo prepara o regresso — “outra mulher me conceberá”.",
            },
        ],
        "keys": [
            "Vida e morte são uma, como o rio e o mar.",
            "O temor da morte é tremor diante de uma honra maior.",
            "A profundidade da vida prepara a compreensão da morte.",
        ],
        "reflections": [
            "Como vivo hoje o que gostaria de ter vivido ao partir?",
            "O meu medo da morte revela o que ainda não amei na vida?",
        ],
    },
    "chegada-do-navio": {
        "summary": "Antes das perguntas, Gibran monta o mito: Almustafa vive doze anos em Orphalese sem ser ouvido. Só a partida desperta a cidade — e a consciência nasce no contraste.",
        "sections": [
            {
                "heading": "Um mito, não um romance",
                "body": "Na abertura da série, Lúcia Helena Galvão insiste: O Profeta é linguagem mítica. O personagem central é você; os demais são fatores internos projetados. Doze anos evocam um ciclo completo — como uma vida — e a ilha natal sugere o regresso ao plano espiritual.",
            },
            {
                "heading": "Consciência pelo contraste",
                "body": "Ninguém valorizou Almustafa até ele decidir partir. Valorizamos o que começa a escapar. Quando o navio surge na névoa, alegria e tristeza se misturam: a maré chama, mas a cidade ainda pede verdade.",
            },
            {
                "heading": "Almitra e o pedido",
                "body": "A vidente Almitra — a primeira a crer — pede que ele fale antes de ir. “Revele-nos a nós mesmos.” Toda a obra nasce desse instante: o diálogo interior torna-se palavra oferecida aos filhos dos filhos.",
            },
        ],
        "keys": [
            "O Profeta é mito: diálogo da consciência consigo mesma.",
            "A consciência se dá pelo contraste entre ter e perder.",
            "A partida é o momento em que a sabedoria finalmente é pedida.",
        ],
        "reflections": [
            "Que sabedoria tenho ignorado à minha volta?",
            "O que só valorizo quando ameaça partir?",
        ],
    },
    "a-despedida": {
        "summary": "Fecha-se o ciclo: o vento convida a partir. O que foi semeado permanece; Almitra fica no quebra-mar — memória fiel — enquanto Almustafa promete regressar com a maré.",
        "sections": [
            {
                "heading": "Sementes ao vento",
                "body": "Os errantes não começam o dia onde terminaram o anterior. Somos sementes: quando amadurecemos, o vento nos espalha. A despedida não apaga o que foi vivido — transforma a sede de viver.",
            },
            {
                "heading": "O capitão espera o silêncio",
                "body": "O capitão do navio é paciente; as velas estão cheias, mas espera o silêncio do profeta. Partir é consentimento interior, não fuga. O rio já atingiu o mar.",
            },
            {
                "heading": "“Outra mulher me conceberá”",
                "body": "A última palavra é renovação: um breve descanso sobre o vento e o regresso. A sabedoria não morre com o corpo do sábio — renasce em cada geração que souber perguntar.",
            },
        ],
        "keys": [
            "Partir é espalhar o que amadureceu.",
            "A memória fiel (Almitra) também é um porto.",
            "A sabedoria promete regresso — ciclo após ciclo.",
        ],
        "reflections": [
            "O que deixo semeado ao partir de uma etapa da vida?",
            "Sei receber a despedida sem negar o que foi dado?",
        ],
    },
}


def clean_transcript(text: str) -> str:
    text = re.sub(r"\[.*?\]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    # cut channel outro boilerplate if present at end
    for marker in [
        "Vocês sabiam que a Nova Acrópole",
        "Assine nossa plataforma",
        "Inscreva-se no canal",
    ]:
        i = text.find(marker)
        if i > 2000:
            text = text[:i]
    return text


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?…])\s+", text)
    out = []
    for p in parts:
        p = p.strip()
        if len(p) < 40:
            continue
        if len(p) > 420:
            # hard wrap long caption blobs
            while len(p) > 420:
                cut = p.rfind(" ", 0, 420)
                if cut < 80:
                    cut = 420
                out.append(p[:cut].strip())
                p = p[cut:].strip()
        if p:
            out.append(p)
    return out


def score_sentence(s: str, title: str) -> float:
    s_low = s.lower()
    score = 0.0
    # philosophical signal words
    for w in [
        "gibran",
        "profeta",
        "amor",
        "alma",
        "consciência",
        "filosof",
        "platão",
        "platão",
        "platão",
        "virtude",
        "fraternidade",
        "egoísmo",
        "simbólico",
        "mito",
        "essência",
        "verdade",
        "sagrado",
        "liberdade",
        "dor",
        "trabalho",
        "amigo",
        "morte",
        "beleza",
        "oração",
        "prece",
        "razão",
        "paixão",
        "lei",
        "crime",
        "castigo",
        "tempo",
        "prazer",
        "religião",
        "filho",
        "casamento",
        "dádiva",
        "caridade",
        "ensino",
        "conversa",
    ]:
        if w in s_low:
            score += 1.2
    for t in re.findall(r"[a-záàãâéêíóôõúç]{4,}", title.lower()):
        if t in s_low:
            score += 2.0
    if s.startswith(("Porque", "Porque", "Ou seja", "Ou seja", "Então", "Portanto", "Assim")):
        score += 0.8
    if "“" in s or "”" in s or '"' in s:
        score += 0.5
    # penalize pure bio repetition if late
    if "mary haskell" in s_low or "tuberculose" in s_low:
        score -= 1.5
    if len(s) < 60:
        score -= 0.5
    return score


def build_sections_from_transcript(text: str, title: str) -> tuple[str, list[dict], list[str], list[str]]:
    text = clean_transcript(text)
    sents = split_sentences(text)
    if not sents:
        return (
            f"Leitura comentada do capítulo “{title}” na série da Nova Acrópole.",
            [],
            [],
            [],
        )

    # Skip early bio if long lecture: start after ~15% if many mary/gibran bio mentions
    start_idx = 0
    for i, s in enumerate(sents[:25]):
        if title.split()[0].lower() in s.lower() and i > 5:
            start_idx = max(0, i - 2)
            break
    # Prefer content after "fale" / chapter topic engagement
    for i, s in enumerate(sents):
        if re.search(r"fale[- ]nos|capítulo|hoje (nós )?vamos|vamos (falar|tratar|comentar)", s, re.I):
            start_idx = i
            break

    usable = sents[start_idx:]
    ranked = sorted(((score_sentence(s, title), i, s) for i, s in enumerate(usable)), reverse=True)
    picked = []
    used = set()
    for sc, i, s in ranked:
        if sc < 1.5:
            continue
        # diversity: avoid near duplicates
        key = s[:60]
        if key in used:
            continue
        used.add(key)
        picked.append((i, s))
        if len(picked) >= 14:
            break
    picked.sort(key=lambda x: x[0])
    chosen = [s for _, s in picked]

    # group into sections of ~3 sentences
    sections = []
    headings = [
        "O que Gibran está dizendo",
        "Chave filosófica",
        "Imagens e símbolos",
        "Aplicação na vida",
        "O fio que permanece",
    ]
    for idx in range(0, len(chosen), 3):
        chunk = chosen[idx : idx + 3]
        if not chunk:
            continue
        h = headings[len(sections) % len(headings)]
        body = " ".join(chunk)
        # light cleanup of caption artifacts
        body = re.sub(r"\b(\w+)( \1\b)+", r"\1", body)
        sections.append({"heading": h, "body": body})
        if len(sections) >= 5:
            break

    summary_bits = chosen[:2] if chosen else usable[:2]
    summary = " ".join(summary_bits)
    if len(summary) > 320:
        summary = summary[:317].rsplit(" ", 1)[0] + "…"

    keys = []
    for s in chosen:
        if 50 < len(s) < 160:
            keys.append(s.rstrip("."))
        if len(keys) >= 4:
            break
    if len(keys) < 3:
        keys = [s[:140] for s in chosen[:4]]

    reflections = [
        f"Como este capítulo sobre {title.lower()} desafia o que eu costumo entender por essa palavra?",
        "Que gesto concreto este texto pede de mim nesta semana?",
        "Onde estou vivendo só a casca deste ensinamento?",
    ]
    return summary, sections, keys[:5], reflections


def essay_for(slug: str, title: str) -> dict:
    if slug in FALLBACK and not (TRANS / f"{slug}.txt").exists():
        fb = FALLBACK[slug]
        return {
            "summary": fb["summary"],
            "sections": fb["sections"],
            "keys": fb["keys"],
            "reflections": fb["reflections"],
        }

    path = TRANS / f"{slug}.txt"
    # ensino shares comércio transcript — prefer education-focused slice
    if slug == "o-ensino" and not path.exists():
        path = TRANS / "comprar-e-vender.txt"

    if path.exists():
        raw = path.read_text(encoding="utf-8")
        if slug == "o-ensino":
            # keep portion about ensino/educação if present
            m = re.search(r"(ensin|educa|mestre|professor|limiar)", raw, re.I)
            if m:
                raw = raw[max(0, m.start() - 200) :]
        summary, sections, keys, reflections = build_sections_from_transcript(raw, title)
        # if weak extraction, merge fallback frame
        if slug in FALLBACK and len(sections) < 2:
            fb = FALLBACK[slug]
            return {
                "summary": fb["summary"],
                "sections": fb["sections"],
                "keys": fb["keys"],
                "reflections": fb["reflections"],
            }
        return {
            "summary": summary,
            "sections": sections,
            "keys": keys,
            "reflections": reflections,
        }

    if slug in FALLBACK:
        fb = FALLBACK[slug]
        return {
            "summary": fb["summary"],
            "sections": fb["sections"],
            "keys": fb["keys"],
            "reflections": fb["reflections"],
        }

    return {
        "summary": f"Comentário filosófico ao capítulo “{title}”, no espírito da série da Nova Acrópole.",
        "sections": [
            {
                "heading": "Ler nas entrelinhas",
                "body": "Gibran sugere mais do que explica. A leitura comentada da Nova Acrópole convida a abrir a terceira dimensão do poema: símbolos, contrastes e exigências éticas por detrás da beleza da prosa.",
            }
        ],
        "keys": [
            "A poesia não explica: insinua.",
            "Cada capítulo relê uma palavra da vida em chave filosófica.",
        ],
        "reflections": [
            f"O que muda se eu levar a sério este capítulo sobre {title.lower()}?",
        ],
    }


def main() -> None:
    data = json.loads(OUT.read_text(encoding="utf-8"))

    # ensure chegada/despedida fallbacks always apply rich content
    for slug in ("chegada-do-navio", "a-despedida", "a-beleza", "a-morte"):
        # force fallback quality for framing chapters / missing subs
        pass

    for ch in data["chapters"]:
        slug = ch["slug"]
        title = ch["title"]
        essay = essay_for(slug, title)
        # Prefer curated framing for narrative chapters
        if slug in ("chegada-do-navio", "a-despedida", "a-beleza", "a-morte"):
            essay = {
                "summary": FALLBACK[slug]["summary"],
                "sections": FALLBACK[slug]["sections"],
                "keys": FALLBACK[slug]["keys"],
                "reflections": FALLBACK[slug]["reflections"],
            }
            # enrich beleza/morte keys already set; for others with transcript, append a transcript section
            tpath = TRANS / f"{slug}.txt"
            if tpath.exists() and slug not in ("chegada-do-navio", "a-despedida"):
                summary, sections, keys, reflections = build_sections_from_transcript(
                    tpath.read_text(encoding="utf-8"), title
                )
                if sections:
                    essay["sections"] = FALLBACK[slug]["sections"] + sections[:2]
                    essay["keys"] = list(dict.fromkeys(FALLBACK[slug]["keys"] + keys))[:6]

        vid = VIDEO_IDS.get(slug)
        ch["videoId"] = vid
        ch["videoUrl"] = f"https://www.youtube.com/watch?v={vid}" if vid else None
        ch["commentary"] = essay
        # keep backward-compatible explanation field for any leftover UI
        ch["explanation"] = {
            "summary": essay["summary"],
            "keys": essay["keys"],
        }

        # quote pick
        if not ch.get("quote"):
            for p in ch["paragraphs"]:
                if 50 < len(p) < 170:
                    ch["quote"] = p.strip('“”"')
                    break

    data["meta"]["title"] = "O Profeta Comentado"
    data["meta"]["subtitle"] = "Khalil Gibran · leitura filosófica capítulo a capítulo"
    data["meta"]["translator"] = "Rafael Arrais (2013)"
    data["meta"]["note"] = (
        "Edição comentada: texto de O Profeta (PDF “O Profeta - Khalil Gibran.pdf”) "
        "com chaves de leitura destiladas das palestras de Lúcia Helena Galvão na série "
        "“O Profeta” do canal Nova Acrópole Brasil. Os vídeos originais estão embutidos em cada capítulo."
    )
    data["meta"]["edition"] = "comentada"
    data["meta"]["sources"] = {
        "textPdf": "O Profeta - Khalil Gibran.pdf",
        "textPdfAlt": "o-profeta-gibran-khalil-gibra.pdf",
        "series": data["meta"]["series"],
    }

    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("chapters", len(data["chapters"]))
    for c in data["chapters"]:
        nsec = len(c["commentary"]["sections"])
        print(f"{c['id']:02d} {c['title']}: {nsec} seções, video={c['videoId']}")


if __name__ == "__main__":
    main()
