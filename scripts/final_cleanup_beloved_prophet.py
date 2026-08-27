# -*- coding: utf-8 -*-
"""Final cleanup of Beloved Prophet PT pages before PDF build."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(r"E:\PROJETOS-CURSOR\OPROFETA")
PAGES_PT = ROOT / "cartas" / "ocr_cache" / "pages_pt"
OUT_PT_FULL = ROOT / "cartas" / "beloved_prophet_pt_full.txt"
REPORT = ROOT / "cartas" / "ocr_cache" / "final_cleanup_report.json"

NAME_FIXES = [
    ("Russelll", "Russell"),
    ("Russel ", "Russell "),
    ("Russel.", "Russell."),
    ("Russel,", "Russell,"),
    ("Russel*", "Russell*"),
    ("Hitchênia", "Kitchener"),
    ("Horário Herbert", "Horatio Herbert"),
    ("Sr. Dai", "Sr. Day"),
    ("senhor Dai", "senhor Day"),
    ("Mariarna", "Marianna"),
    ("Kaklil", "Kahlil"),
    ("Kahll", "Kahlil"),
]


def normalize_divider_line(line: str) -> str:
    s = line.strip()
    if not s:
        return line
    # short lines that are essentially KG / MH ornaments
    compact = re.sub(r"[\s—\-–−_=~*•❧☙◆◇]+", "", s)
    if compact in {"KG", "MH"}:
        return f"—— {compact} ——"
    # also catch mixed leftovers like "— —— —— KG ——"
    if re.fullmatch(r"[—\-–−\s]*KG[—\-–−\s]*", s):
        return "—— KG ——"
    if re.fullmatch(r"[—\-–−\s]*MH[—\-–−\s]*", s):
        return "—— MH ——"
    return line


def cleanup(text: str) -> str:
    for a, b in NAME_FIXES:
        text = text.replace(a, b)

    lines = [normalize_divider_line(ln) for ln in text.splitlines()]
    text = "\n".join(lines)

    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"\bQue Deus te ame\b", "Que Deus a ame", text)
    text = re.sub(r"\bque Deus te ame\b", "que Deus a ame", text)
    text = re.sub(r"\bte mantenha\b", "a mantenha", text)
    text = re.sub(r"\bpara ti\b", "para você", text)
    text = re.sub(r"\bde ti\b", "de você", text)
    text = re.sub(r"\bem ti\b", "em você", text)
    text = re.sub(r"\bsem ti\b", "sem você", text)
    text = re.sub(r"\bcontigo\b", "com você", text)
    return text.strip() + "\n"


def main() -> None:
    changed = 0
    for n in range(1, 457):
        pf = PAGES_PT / f"{n:03d}.txt"
        old = pf.read_text(encoding="utf-8")
        new = cleanup(old)
        if new != old:
            pf.write_text(new, encoding="utf-8")
            changed += 1

    parts = [(PAGES_PT / f"{n:03d}.txt").read_text(encoding="utf-8").strip() for n in range(1, 457)]
    OUT_PT_FULL.write_text("\n\n".join(parts) + "\n", encoding="utf-8")
    blob = OUT_PT_FULL.read_text(encoding="utf-8")
    report = {
        "changed": changed,
        "russelll": blob.count("Russelll"),
        "russel": len(re.findall(r"\bRussel\b", blob)),
        "russell": len(re.findall(r"\bRussell\b", blob)),
        "div_kg": blob.count("—— KG ——"),
        "div_mh": blob.count("—— MH ——"),
        "bad_div": blob.count("— ——"),
        "kitchener": blob.count("Kitchener"),
        "sr_day": blob.count("Sr. Day"),
        "sr_dai": blob.count("Sr. Dai"),
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    # show sample dividers
    print("---050---")
    print((PAGES_PT / "050.txt").read_text(encoding="utf-8")[:500])
    print("---280---")
    print((PAGES_PT / "280.txt").read_text(encoding="utf-8")[400:900])


if __name__ == "__main__":
    main()
