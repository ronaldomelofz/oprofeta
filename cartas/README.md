# Cartas de amor — Gibran

Material de apoio à seção `/cartas` do site.

## Fontes consultadas

- Correspondência Gibran ↔ Mary Haskell (arquivo histórico; edições impressas e digitais)
- **Beloved Prophet** — *The Love Letters of Kahlil Gibran and Mary Haskell and Her Private Journal*, edited and arranged by Virginia Hilu (Alfred A. Knopf). Escaneado em `cartas/LIVRO-PRINT/` (456 páginas)
- Empréstimo Archive.org: *Beloved Prophet* e cartas a May Ziadah (PDFs com DRM ACS, quando disponíveis)
- Seleções publicadas da correspondência em volume condensado

## Edição digital (pt-BR)

- PDF traduzido: `cartas/Beloved-Prophet-Cartas-PTBR.pdf` (também servido em `/Beloved-Prophet-Cartas-PTBR.pdf`)
- Cache OCR: `cartas/ocr_cache/pages/` (inglês) e `cartas/ocr_cache/pages_pt/` (português)
- Textos contínuos: `cartas/beloved_prophet_en_full.txt`, `cartas/beloved_prophet_pt_full.txt`
- Scripts:
  - `scripts/ocr_beloved_prophet.py` — upscale + MinerU pipeline (resumível)
  - `scripts/ocr_tesseract_filler.py` — preenchimento rápido de lacunas
  - `scripts/translate_beloved_prophet.py` — EN → pt-BR
  - `scripts/polish_beloved_prophet.py` — ortografia local (+ `--lt` LanguageTool)
  - `scripts/repair_beloved_prophet_pt.py` / `scripts/final_cleanup_beloved_prophet.py` — nomes próprios e tipografia
  - `scripts/build_beloved_prophet_pdf.py` — PDF A5 tipográfico

### Regenerar a edição

```bash
python scripts/polish_beloved_prophet.py
python scripts/final_cleanup_beloved_prophet.py
python scripts/build_beloved_prophet_pdf.py
copy cartas\Beloved-Prophet-Cartas-PTBR.pdf public\Beloved-Prophet-Cartas-PTBR.pdf
```

## Texto no site

- Dados: `src/data/letters.json`
- Comentário: `src/data/letters_commentary.json`
- Scripts de manutenção em `scripts/` (`extract_*`, `translate_*`, `polish_*`)

## Comentário (YouTube)

- [O Grande Amor do Profeta (2009)](https://www.youtube.com/watch?v=9QNWeNBJm-U) — Lúcia Helena Galvão / Nova Acrópole
- Transcrição local: `cartas/videos/grande-amor-do-profeta.txt`
