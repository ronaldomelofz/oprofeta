# Cartas de amor — Gibran

## Internet Archive (empréstimo / DRM)

Itens restritos — baixados como PDF ACS criptografado (Adobe Digital Editions + empréstimo na conta Archive.org):

1. [Beloved Prophet](https://archive.org/details/belovedprophetlo00gibr) — cartas Gibran ↔ Mary Haskell (Knopf, 1972)  
   → `Beloved Prophet - Love Letters of Kahlil Gibran and Mary Haskell (ACS encrypted).pdf`
2. [Gibran Love Letters](https://archive.org/details/gibranloveletter0000gibr) — cartas a May Ziadah  
   → `Gibran Love Letters - to May Ziadah (ACS encrypted).pdf`

Os PDFs “Text PDF” abertos retornam 401/500 sem empréstimo.

## Passei Direto

- `As-cartas-de-amor-de-Gibran.pdf` — seleção condensada (trad./adaptação associada a Paulo Coelho)
- Fonte: https://www.passeidireto.com/arquivo/87684200/as-cartas-de-amor-de-gibran

## pdfcoffee

- `Cartas de Amor - Gibran (pdfcoffee).pdf` (~282 KB, texto extraível, espanhol)
- Fonte: https://pdfcoffee.com/cartas-de-amor-gibran-pdf-free.html
- Extração: `scripts/extract_pdfcoffee_letters.py` → `src/data/letters.json` (**62** cartas/trechos) e cópia em `cartas/letters_pdfcoffee.json`
- Tradução ES→PT-BR: `scripts/translate_letters_ptbr.py` (backup espanhol: `cartas/letters_pdfcoffee_es.json`)
- Texto bruto: `cartas/_pdfcoffee_extract.txt`

## Comentário (YouTube)

Palestra encontrada no canal Nova Acrópole / Lúcia Helena Galvão:

- [O Grande Amor do Profeta (2009)](https://www.youtube.com/watch?v=9QNWeNBJm-U) — homenagem a Khalil Gibran e Mary Haskell
- Transcrição local: `cartas/videos/grande-amor-do-profeta.txt`

Não há série carta a carta no canal; esta palestra é a referência principal para o comentário filosófico no site (`/cartas`).
