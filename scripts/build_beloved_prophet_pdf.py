# -*- coding: utf-8 -*-
"""Build a professional PT-BR PDF of Beloved Prophet from translated page cache."""
from __future__ import annotations

import re
import sys
from pathlib import Path

from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.pagesizes import A5
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    KeepTogether,
)

ROOT = Path(r"E:\PROJETOS-CURSOR\OPROFETA")
CACHE = ROOT / "cartas" / "ocr_cache"
PAGES_PT = CACHE / "pages_pt"
PAGES_EN = CACHE / "pages"
OUT = ROOT / "cartas" / "Beloved-Prophet-Cartas-PTBR.pdf"


def register_fonts() -> tuple[str, str, str]:
    """Prefer elegant serif fonts available on Windows."""
    candidates = [
        (r"C:\Windows\Fonts\georgia.ttf", r"C:\Windows\Fonts\georgiai.ttf", r"C:\Windows\Fonts\georgiab.ttf"),
        (r"C:\Windows\Fonts\times.ttf", r"C:\Windows\Fonts\timesi.ttf", r"C:\Windows\Fonts\timesbd.ttf"),
        (r"C:\Windows\Fonts\palab.ttf", r"C:\Windows\Fonts\palabi.ttf", r"C:\Windows\Fonts\palab.ttf"),
    ]
    for regular, italic, bold in candidates:
        if Path(regular).exists() and Path(italic).exists():
            pdfmetrics.registerFont(TTFont("Body", regular))
            pdfmetrics.registerFont(TTFont("Body-Italic", italic))
            if Path(bold).exists():
                pdfmetrics.registerFont(TTFont("Body-Bold", bold))
            else:
                pdfmetrics.registerFont(TTFont("Body-Bold", regular))
            return "Body", "Body-Italic", "Body-Bold"
    return "Times-Roman", "Times-Italic", "Times-Bold"


def escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def looks_like_date_header(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    # e.g. Boston / Tuesday, May 30, 1911 / New York
    if re.match(r"^(Boston|New York|Paris|Cambridge|Columbia|Marianna|Maine)\b", s, re.I):
        return True
    if re.match(
        r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|"
        r"Segunda|Terça|Quarta|Quinta|Sexta|Sábado|Domingo)\b",
        s,
        re.I,
    ):
        return True
    if re.match(
        r"^(January|February|March|April|May|June|July|August|September|October|November|December|"
        r"Janeiro|Fevereiro|Março|Abril|Maio|Junho|Julho|Agosto|Setembro|Outubro|Novembro|Dezembro)\b",
        s,
        re.I,
    ):
        return True
    return False


def build_styles(body: str, italic: str, bold: str):
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="CoverTitle",
            fontName=italic,
            fontSize=22,
            leading=28,
            alignment=TA_CENTER,
            textColor="#5C1A1A",
            spaceAfter=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CoverSub",
            fontName=body,
            fontSize=11,
            leading=16,
            alignment=TA_CENTER,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodyJust",
            fontName=body,
            fontSize=9.5,
            leading=14,
            alignment=TA_JUSTIFY,
            firstLineIndent=12,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodyFlush",
            fontName=body,
            fontSize=9.5,
            leading=14,
            alignment=TA_JUSTIFY,
            firstLineIndent=0,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="LetterHead",
            fontName=italic,
            fontSize=9.5,
            leading=13,
            alignment=TA_RIGHT,
            spaceBefore=10,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="JournalTag",
            fontName=bold,
            fontSize=9,
            leading=12,
            alignment=TA_CENTER,
            spaceBefore=10,
            spaceAfter=6,
            textColor="#333333",
        )
    )
    styles.add(
        ParagraphStyle(
            name="Signature",
            fontName=italic,
            fontSize=10,
            leading=14,
            alignment=TA_RIGHT,
            spaceBefore=4,
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Editorial",
            fontName=italic,
            fontSize=8.5,
            leading=12,
            alignment=TA_JUSTIFY,
            textColor="#444444",
            spaceBefore=6,
            spaceAfter=6,
            leftIndent=8,
            rightIndent=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Footnote",
            fontName=body,
            fontSize=7.5,
            leading=10,
            alignment=TA_JUSTIFY,
            textColor="#555555",
            spaceBefore=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Illust",
            fontName=italic,
            fontSize=9,
            leading=13,
            alignment=TA_CENTER,
            textColor="#666666",
            spaceBefore=40,
            spaceAfter=40,
        )
    )
    styles.add(
        ParagraphStyle(
            name="PageLabel",
            fontName=body,
            fontSize=7,
            leading=9,
            alignment=TA_CENTER,
            textColor="#999999",
            spaceBefore=4,
            spaceAfter=10,
        )
    )
    return styles


def page_story(n: int, text: str, styles) -> list:
    flow = [Paragraph(f"— {n} —", styles["PageLabel"])]
    raw = text
    if raw.startswith("---"):
        raw = "\n".join(raw.splitlines()[1:]).strip()

    if raw.startswith("[ILUSTRAÇÃO]") or raw.startswith("[ILLUSTRATION]"):
        cap = raw.split("\n", 1)
        body = cap[1].strip() if len(cap) > 1 else raw
        flow.append(Paragraph(escape(body) or "[Ilustração]", styles["Illust"]))
        return flow

    paragraphs = re.split(r"\n\s*\n", raw)
    for block in paragraphs:
        block = block.strip()
        if not block:
            continue
        lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
        joined = " ".join(lines)

        upper = joined.upper()
        if upper in ("[JOURNAL]", "[DIÁRIO]", "JOURNAL", "DIÁRIO") or "[JOURNAL]" in upper or "[DIÁRIO]" in upper:
            flow.append(Paragraph("[DIÁRIO]", styles["JournalTag"]))
            continue
        if re.fullmatch(r"[—\-–−\s]*KG[—\-–−\s]*", joined) or joined.strip() in {"—— KG ——", "KG"}:
            flow.append(Paragraph("—— KG ——", styles["JournalTag"]))
            continue
        if re.fullmatch(r"[—\-–−\s]*MH[—\-–−\s]*", joined) or joined.strip() in {"—— MH ——", "MH"}:
            flow.append(Paragraph("—— MH ——", styles["JournalTag"]))
            continue
        if joined in ("Kahlil", "Mary", "Kahlil Gibran", "Mary Haskell", "M.", "K."):
            flow.append(Paragraph(escape(joined), styles["Signature"]))
            continue
        if joined.startswith("*") or joined.startswith("∗") or joined.startswith("※"):
            flow.append(Paragraph(escape(joined), styles["Footnote"]))
            continue
        if all(looks_like_date_header(ln) or len(ln) < 40 for ln in lines) and len(lines) <= 3:
            flow.append(Paragraph("<br/>".join(escape(ln) for ln in lines), styles["LetterHead"]))
            continue
        # Editorial italic blocks often shorter / commentary
        if joined.startswith("Mary and") or joined.startswith("Mary e ") or "Virginia Hilu" in joined:
            flow.append(Paragraph(escape(joined), styles["Editorial"]))
            continue

        style = styles["BodyJust"]
        flow.append(Paragraph(escape(joined), style))
    return flow


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Body", 8)
    canvas.setFillColorRGB(0.4, 0.4, 0.4)
    page_w, page_h = A5
    canvas.drawCentredString(page_w / 2, 1.2 * cm, str(doc.page))
    canvas.restoreState()


def load_page(n: int) -> str | None:
    pt = PAGES_PT / f"{n:03d}.txt"
    en = PAGES_EN / f"{n:03d}.txt"
    if pt.exists() and pt.stat().st_size > 20:
        return pt.read_text(encoding="utf-8", errors="ignore")
    if en.exists() and en.stat().st_size > 20:
        return en.read_text(encoding="utf-8", errors="ignore")
    return None


def main() -> None:
    body, italic, bold = register_fonts()
    styles = build_styles(body, italic, bold)

    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A5,
        leftMargin=1.8 * cm,
        rightMargin=1.8 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
        title="Profeta Amado - Cartas de amor de Kahlil Gibran e Mary Haskell",
        author="Organizado por Virginia Hilu / Traducao pt-BR O Profeta Comentado",
        subject="Beloved Prophet - traducao portuguesa (Brasil)",
    )

    story = []
    # Cover
    story.append(Spacer(1, 3 * cm))
    story.append(Paragraph("Profeta Amado", styles["CoverTitle"]))
    story.append(Paragraph("As cartas de amor de", styles["CoverSub"]))
    story.append(Paragraph("<b>KAHLIL GIBRAN E MARY HASKELL</b>", styles["CoverSub"]))
    story.append(Paragraph("e o diário particular dela", styles["CoverSub"]))
    story.append(Spacer(1, 1.2 * cm))
    story.append(
        Paragraph(
            "Organizado e disposto por Virginia Hilu<br/>Tradução para o português do Brasil",
            styles["CoverSub"],
        )
    )
    story.append(Spacer(1, 2 * cm))
    story.append(
        Paragraph(
            "Edição digital do projeto <i>O Profeta Comentado</i><br/>"
            "a partir do volume <i>Beloved Prophet</i> (Alfred A. Knopf).",
            styles["CoverSub"],
        )
    )
    story.append(PageBreak())

    missing = []
    for n in range(1, 457):
        text = load_page(n)
        if not text:
            missing.append(n)
            continue
        story.extend(page_story(n, text, styles))
        story.append(PageBreak())

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(f"PDF written: {OUT}")
    print(f"Missing pages: {len(missing)} -> {missing[:30]}{'...' if len(missing) > 30 else ''}")


if __name__ == "__main__":
    main()
