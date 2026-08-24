# -*- coding: utf-8 -*-
"""Translate letters.json body text from Spanish to Brazilian Portuguese."""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

from deep_translator import GoogleTranslator

# reuse PT-BR orthography table
sys_path_scripts = Path(__file__).resolve().parent
import sys

sys.path.insert(0, str(sys_path_scripts))
from fix_ptbr import fix_str  # noqa: E402

ROOT = Path(r"E:\PROJETOS-CURSOR\OPROFETA")
SRC = ROOT / "src" / "data" / "letters.json"
OUT = SRC
BACKUP = ROOT / "cartas" / "letters_pdfcoffee_es.json"

# Google limit ~5000 chars; keep margin
CHUNK = 4200


def to_ptbr(text: str) -> str:
    text = fix_str(text)
    text = re.sub(r"\.([A-ZÁÉÍÓÚÀÂÊÔÃÕÇ])", r". \1", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def translate_long(translator: GoogleTranslator, text: str) -> str:
    text = text.strip()
    if not text:
        return text
    if len(text) <= CHUNK:
        for attempt in range(5):
            try:
                return to_ptbr(translator.translate(text))
            except Exception as e:
                wait = 2 + attempt * 2
                print(f"  retry ({e}); wait {wait}s")
                time.sleep(wait)
        raise RuntimeError(f"failed to translate: {text[:80]}")

    # split by sentences
    parts = re.split(r"(?<=[.!?…»\"])\s+", text)
    chunks: list[str] = []
    buf = ""
    for p in parts:
        if len(buf) + len(p) + 1 <= CHUNK:
            buf = f"{buf} {p}".strip()
        else:
            if buf:
                chunks.append(buf)
            buf = p
    if buf:
        chunks.append(buf)

    out: list[str] = []
    for i, ch in enumerate(chunks):
        out.append(translate_long(translator, ch))
        time.sleep(0.35)
    return " ".join(out)


def main() -> None:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    # keep Spanish backup once
    if not BACKUP.exists():
        BACKUP.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print("backup", BACKUP)

    translator = GoogleTranslator(source="es", target="pt")
    letters = data["letters"]
    total = len(letters)
    for i, letter in enumerate(letters, 1):
        print(f"[{i}/{total}] {letter.get('slug')}")
        new_paras = []
        for para in letter.get("paragraphs") or []:
            new_paras.append(translate_long(translator, para))
            time.sleep(0.25)
        letter["paragraphs"] = new_paras
        if new_paras:
            q = new_paras[0]
            letter["quote"] = q[:220] + ("…" if len(q) > 220 else "")
        # title "Primeiro encontro" already PT; dated titles already PT
        letter["source"] = "pdfcoffee-es→pt-BR"
        # checkpoint every 5 letters
        if i % 5 == 0 or i == total:
            data["meta"]["language"] = "pt-BR"
            data["meta"]["note"] = (
                "Texto integral do volume «Cartas de Amor del Profeta» (pdfcoffee), "
                "traduzido do espanhol para português do Brasil. Adaptação condensada "
                "associada a Paulo Coelho — 62 cartas/trechos. Não é o arquivo das 600+ "
                "cartas da University of South Carolina."
            )
            OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            print("  checkpoint saved")

    # also update pdfcoffee copy
    (ROOT / "cartas" / "letters_pdfcoffee.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("done")


if __name__ == "__main__":
    main()
