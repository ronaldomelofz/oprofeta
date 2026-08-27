# O Profeta Comentado

Edição comentada de *O Profeta*, de Khalil Gibran: texto integral capítulo a capítulo com leitura filosófica destilada da série de Lúcia Helena Galvão no canal [Nova Acrópole](https://www.youtube.com/@NovaAcropole/search?query=kalill%20gibran).

## Stack

- Vite + React + TypeScript
- React Router
- Deploy: Netlify (`https://oprofetagibran.netlify.app`)

## Desenvolvimento

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
```

## Conteúdo

- Texto: `O Profeta - Khalil Gibran.pdf` (tradução Rafael Arrais, 2013)
- Contraste editorial: `o-profeta-gibran-khalil-gibra.pdf` (Mansour Challita)
- Comentários: destilados das palestras YouTube Nova Acrópole
- Cartas: seleção em `/cartas` + edição integral **Profeta Amado** (`public/Beloved-Prophet-Cartas-PTBR.pdf`) a partir de *Beloved Prophet* (Virginia Hilu), revisada em pt-BR
- Scripts: `scripts/build_commentaries.py`, `scripts/ocr_beloved_prophet.py`, `scripts/translate_beloved_prophet.py`, `scripts/polish_beloved_prophet.py`, `scripts/final_cleanup_beloved_prophet.py`, `scripts/build_beloved_prophet_pdf.py`
