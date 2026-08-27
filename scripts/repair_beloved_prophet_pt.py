# -*- coding: utf-8 -*-
"""Repair LT over-corrections and normalize Beloved Prophet PT typography."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(r"E:\PROJETOS-CURSOR\OPROFETA")
PAGES_PT = ROOT / "cartas" / "ocr_cache" / "pages_pt"
OUT_PT_FULL = ROOT / "cartas" / "beloved_prophet_pt_full.txt"
REPORT = ROOT / "cartas" / "ocr_cache" / "repair_report.json"

# Exact phrase / name restorations (LT damage + MT)
REPL = [
    ("Hitchênia", "Kitchener"),
    ("Hitchenia", "Kitchener"),
    ("Horário Herbert Kitchener", "Horatio Herbert Kitchener"),
    ("Horário Herbert Hitchênia", "Horatio Herbert Kitchener"),
    ("Horario Herbert Kitchener", "Horatio Herbert Kitchener"),
    ("Sr. Dai", "Sr. Day"),
    ("senhor Dai", "senhor Day"),
    ("galeria do Sr. Dai", "galeria do Sr. Day"),
    ("ateliê do Sr. Dai", "ateliê do Sr. Day"),
    ("estúdio do Sr. Dai", "estúdio do Sr. Day"),
    ("Sr. Russel", "Sr. Russell"),
    ("Charles Edward Russel", "Charles Edward Russell"),
    ("Charles Russel", "Charles Russell"),
    ("o Sr. Russel", "o Sr. Russell"),
    ("Mariarna", "Marianna"),
    ("Kaklil", "Kahlil"),
    ("Kahll", "Kahlil"),
    ("Kahlíl", "Kahlil"),
    ("Abdu'l-Bahá", "Abdul-Baha"),
    ("Abdu’l-Bahá", "Abdul-Baha"),
]

REGEX = [
    # Normalize letter dividers to a single house style
    (r"[—\-]{1,3}\s*KG\s*[—\-]{1,3}", "—— KG ——"),
    (r"[—\-]{1,3}\s*MH\s*[—\-]{1,3}", "—— MH ——"),
    (r"—\s+—\s+KG\s+—", "—— KG ——"),
    (r"—\s+—\s+MH\s+—", "—— MH ——"),
    (r"——\s+KG\s+——-?", "—— KG ——"),
    (r"——\s+MH\s+——-?", "—— MH ——"),
    (r"KG\s+——-?", "—— KG ——"),
    (r"MH\s+——-?", "—— MH ——"),
    (r"❧\s*KG\s*☙", "—— KG ——"),
    (r"❧\s*MH\s*☙", "—— MH ——"),
    (r"[ \t]{2,}", " "),
    (r"\n{3,}", "\n\n"),
    # leftover intimate forms
    (r"\bQue Deus te ame\b", "Que Deus a ame"),
    (r"\bque Deus te ame\b", "que Deus a ame"),
    (r"\bte mantenha\b", "a mantenha"),
    (r"\bpara ti\b", "para você"),
    (r"\bde ti\b", "de você"),
    (r"\bem ti\b", "em você"),
    (r"\bsem ti\b", "sem você"),
    (r"\bcontigo\b", "com você"),
]


def repair(text: str) -> str:
    for a, b in REPL:
        text = text.replace(a, b)
    for pat, rep in REGEX:
        text = re.sub(pat, rep, text)
    # collapse accidental double dividers on same line
    text = re.sub(r"(—— KG ——)(?:\s*—— KG ——)+", r"\1", text)
    text = re.sub(r"(—— MH ——)(?:\s*—— MH ——)+", r"\1", text)
    return text.strip() + "\n"


def main() -> None:
    changed = 0
    for n in range(1, 457):
        pf = PAGES_PT / f"{n:03d}.txt"
        old = pf.read_text(encoding="utf-8")
        new = repair(old)
        if new != old:
            pf.write_text(new, encoding="utf-8")
            changed += 1

    parts = []
    for n in range(1, 457):
        parts.append((PAGES_PT / f"{n:03d}.txt").read_text(encoding="utf-8").strip())
        parts.append("\n\n")
    OUT_PT_FULL.write_text("".join(parts), encoding="utf-8")
    blob = OUT_PT_FULL.read_text(encoding="utf-8")
    report = {
        "changed": changed,
        "hitchenia": blob.count("Hitchênia"),
        "russel_wrong": len(re.findall(r"\bRussel\b", blob)),
        "russell_ok": len(re.findall(r"\bRussell\b", blob)),
        "sr_dai": blob.count("Sr. Dai"),
        "sr_day": blob.count("Sr. Day"),
        "kitchener": blob.count("Kitchener"),
        "bad_div_kg": blob.count("— — KG"),
        "good_div_kg": blob.count("—— KG ——"),
        "good_div_mh": blob.count("—— MH ——"),
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
