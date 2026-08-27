# -*- coding: utf-8 -*-
"""Revise letters.json PT quality: Mary name, orthography, intimate forms, leaks."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(r"E:\PROJETOS-CURSOR\OPROFETA")
sys.path.insert(0, str(ROOT / "scripts"))
from fix_ptbr import fix_str  # noqa: E402

LETTERS = ROOT / "src" / "data" / "letters.json"
PAGES_PT = ROOT / "cartas" / "ocr_cache" / "pages_pt"
FULL_PT = ROOT / "cartas" / "beloved_prophet_pt_full.txt"
BACKUP62 = ROOT / "cartas" / "letters_selection_62.json"

# Protect biblical / fixed phrases
PROTECT = [
    ("Virgem Mary", "Virgem Maria"),  # undo if wrongly changed — applied after
]


def restore_mary(text: str) -> str:
    """Replace person-name Maria with Mary; keep clear Marian titles."""
    # Temporarily protect Marian titles
    protected: list[str] = []

    def _park(m: re.Match) -> str:
        protected.append(m.group(0))
        return f"⟦P{len(protected)-1}⟧"

    text = re.sub(
        r"\b(Virgem|Santa|Nossa Senhora|Ave)\s+Maria\b",
        _park,
        text,
        flags=re.I,
    )
    # Maria + filho/Jesus nearby kept? park "Maria, mãe de Jesus" etc.
    text = re.sub(
        r"\bMaria\b(?=[^,.]{0,40}\b(Jesus|filho|Cristo)\b)",
        _park,
        text,
        flags=re.I,
    )

    text = re.sub(r"\bMaria\b", "Mary", text)

    for i, orig in enumerate(protected):
        # ensure Marian forms use Maria
        fixed = re.sub(r"\bMary\b", "Maria", orig) if "Maria" in orig or "maria" in orig.lower() else orig
        if re.search(r"Virgem|Santa|Ave|Senhora", orig, re.I):
            fixed = re.sub(r"\bMary\b", "Maria", orig)
        text = text.replace(f"⟦P{i}⟧", fixed)
    return text


def polish_text(text: str) -> str:
    text = fix_str(text)
    text = restore_mary(text)
    repls = [
        ("Idéia", "Ideia"),
        ("idéia", "ideia"),
        ("Idéias", "Ideias"),
        ("idéias", "ideias"),
        ("comité", "comitê"),
        ("Comité", "Comitê"),
        ("Carinhosamente Mary", "Com carinho, Mary"),
        ("Carinhosamente, Mary", "Com carinho, Mary"),
        ("Amor de Mary", "Amor de Mary"),  # noop keep when signature from Mary
        ("Kaklil", "Kahlil"),
        ("Sr. Dai", "Sr. Day"),
        ("senhor Dai", "senhor Day"),
        ("Russelll", "Russell"),
        ("\u00ab", "\u201c"),
        ("\u00bb", "\u201d"),
        (" .", "."),
        (" ,", ","),
    ]
    for a, b in repls:
        text = text.replace(a, b)

    regexes = [
        (r"\bfacto\b", "fato"),
        (r"\bfactos\b", "fatos"),
        (r"\bcontacto\b", "contato"),
        (r"\bactual\b", "atual"),
        (r"\bactualmente\b", "atualmente"),
        (r"\bQue Deus te guarde\b", "Que Deus a guarde"),
        (r"\bque Deus te guarde\b", "que Deus a guarde"),
        (r"\bQue Deus te abençoe\b", "Que Deus a abençoe"),
        (r"\bque Deus te abençoe\b", "que Deus a abençoe"),
        (r"\bQue Deus te ame\b", "Que Deus a ame"),
        (r"\bque Deus te ame\b", "que Deus a ame"),
        (r"\bte mantenha\b", "a mantenha"),
        (r"\bpara ti\b", "para você"),
        (r"\bde ti\b", "de você"),
        (r"\bem ti\b", "em você"),
        (r"\bsem ti\b", "sem você"),
        (r"\bcontigo\b", "com você"),
        (r"\bContigo\b", "Com você"),
        (r"Ó Mary, amada Mary", "Ó Mary, amada Mary"),
        (r"Mary, amada Mary", "Mary, amada Mary"),
        (r"[ \t]{2,}", " "),
        # English leftovers common in MT stubs
        (r"\bDear Mary\b", "Querida Mary"),
        (r"\bMy dear Mary\b", "Minha querida Mary"),
        (r"\bBeloved Mary\b", "Amada Mary"),
        (r"\bGood night\b", "Boa noite"),
    ]
    for pat, rep in regexes:
        text = re.sub(pat, rep, text)
    return text.strip()


def eng_score(s: str) -> int:
    return len(
        re.findall(
            r"\b(the|and|with|that|this|from|have|were|would|which|their|your|been)\b",
            s,
            re.I,
        )
    )


def merge_old_commentaries(letters: list[dict]) -> int:
    if not BACKUP62.exists():
        return 0
    old = json.loads(BACKUP62.read_text(encoding="utf-8"))["letters"]
    n = 0
    by_date_auth = {(L.get("date"), L.get("author")): L for L in old}
    for L in letters:
        key = (L.get("date"), L.get("author"))
        O = by_date_auth.get(key)
        if not O:
            continue
        # Prefer richer old commentary when longer
        oc = O.get("commentary") or {}
        nc = L.get("commentary") or {}
        if len((oc.get("summary") or "")) > len((nc.get("summary") or "")) + 40:
            L["commentary"] = oc
            n += 1
    return n


def prefer_old_body_when_same_date(letters: list[dict]) -> int:
    """When date+author match, if old body is clearly better PT and new has EN leak, restore old."""
    if not BACKUP62.exists():
        return 0
    old = json.loads(BACKUP62.read_text(encoding="utf-8"))["letters"]
    by = {(L.get("date"), L.get("author")): L for L in old}
    n = 0
    for L in letters:
        O = by.get((L.get("date"), L.get("author")))
        if not O:
            continue
        new_t = " ".join(L["paragraphs"])
        old_t = " ".join(O["paragraphs"])
        if eng_score(new_t) >= 5 and eng_score(old_t) <= 2 and len(old_t) > 80:
            L["paragraphs"] = [polish_text(p) for p in O["paragraphs"]]
            L["quote"] = L["paragraphs"][0][:220] + (
                "…" if len(L["paragraphs"][0]) > 220 else ""
            )
            if O.get("commentary"):
                L["commentary"] = O["commentary"]
            # keep title from date if present
            if O.get("title") and L.get("date"):
                L["title"] = O["title"]
            n += 1
    return n


def main() -> None:
    data = json.loads(LETTERS.read_text(encoding="utf-8"))
    changed_paras = 0
    maria_before = 0
    maria_after = 0
    for L in data["letters"]:
        blob = " ".join(L["paragraphs"])
        maria_before += len(re.findall(r"\bMaria\b", blob))
        new_paras = []
        for p in L["paragraphs"]:
            q = polish_text(p)
            if q != p:
                changed_paras += 1
            new_paras.append(q)
        L["paragraphs"] = new_paras
        if new_paras:
            L["quote"] = new_paras[0][:220] + ("…" if len(new_paras[0]) > 220 else "")
        # polish commentary lightly
        c = L.get("commentary") or {}
        if isinstance(c.get("summary"), str):
            c["summary"] = polish_text(c["summary"])
        if isinstance(c.get("keys"), list):
            c["keys"] = [polish_text(x) for x in c["keys"]]
        if isinstance(c.get("reflections"), list):
            c["reflections"] = [polish_text(x) for x in c["reflections"]]
        L["commentary"] = c
        maria_after += len(re.findall(r"\bMaria\b", " ".join(L["paragraphs"])))

    restored_body = prefer_old_body_when_same_date(data["letters"])
    restored_comm = merge_old_commentaries(data["letters"])

    # meta polish
    meta = data["meta"]
    meta["note"] = polish_text(meta.get("note") or "")
    if meta.get("commentary"):
        meta["commentary"]["summary"] = polish_text(meta["commentary"].get("summary") or "")
        for s in meta["commentary"].get("sections") or []:
            s["heading"] = polish_text(s.get("heading") or "")
            s["body"] = polish_text(s.get("body") or "")

    data["meta"]["language"] = "pt-BR"
    LETTERS.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / "cartas" / "letters_beloved_extracted.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Also polish page cache used for PDF
    page_changed = 0
    if PAGES_PT.exists():
        for n in range(1, 457):
            pf = PAGES_PT / f"{n:03d}.txt"
            if not pf.exists():
                continue
            old = pf.read_text(encoding="utf-8")
            # keep header line
            lines = old.splitlines()
            if lines and lines[0].startswith("---"):
                header, body = lines[0] + "\n", "\n".join(lines[1:])
            else:
                header, body = "", old
            new_body = polish_text(body)
            # restore dividers that polish might not touch
            new = header + new_body + ("\n" if not new_body.endswith("\n") else "")
            if new != old:
                pf.write_text(new if new.endswith("\n") else new + "\n", encoding="utf-8")
                page_changed += 1
        parts = [
            (PAGES_PT / f"{n:03d}.txt").read_text(encoding="utf-8").strip()
            for n in range(1, 457)
        ]
        FULL_PT.write_text("\n\n".join(parts) + "\n", encoding="utf-8")

    report = {
        "changed_paras": changed_paras,
        "maria_before": maria_before,
        "maria_after": maria_after,
        "restored_body_from_old62": restored_body,
        "restored_commentary_from_old62": restored_comm,
        "pages_pt_changed": page_changed,
        "letters": len(data["letters"]),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
