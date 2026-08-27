# -*- coding: utf-8 -*-
"""Deep compare old curated letters vs new Beloved Prophet extraction."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(r"E:\PROJETOS-CURSOR\OPROFETA")
sys.stdout.reconfigure(encoding="utf-8")

OLD = json.loads((ROOT / "cartas" / "letters_selection_62.json").read_text(encoding="utf-8"))
NEW = json.loads((ROOT / "src" / "data" / "letters.json").read_text(encoding="utf-8"))


def toks(s: str) -> set[str]:
    return set(re.findall(r"[a-záéíóúâêôãõçàü0-9]{4,}", (s or "").lower()))


def jaccard(a: str, b: str) -> float:
    A, B = toks(a), toks(b)
    if not A or not B:
        return 0.0
    return len(A & B) / len(A | B)


def eng_score(s: str) -> int:
    return len(
        re.findall(
            r"\b(the|and|with|that|this|from|have|were|would|which|their|your|been|when|what)\b",
            s,
            re.I,
        )
    )


def main() -> None:
    # Content-best match for each old letter against ALL new
    rows = []
    for O in OLD["letters"]:
        op = " ".join(O["paragraphs"])
        best = None
        best_j = -1.0
        for N in NEW["letters"]:
            np_ = " ".join(N["paragraphs"])
            j = jaccard(op, np_)
            if j > best_j:
                best_j = j
                best = N
        assert best is not None
        np_ = " ".join(best["paragraphs"])
        rows.append(
            {
                "old_id": O["id"],
                "old_date": O.get("date"),
                "old_author": O.get("author"),
                "old_title": O.get("title"),
                "new_id": best["id"],
                "new_date": best.get("date"),
                "new_author": best.get("author"),
                "jac": round(best_j, 3),
                "old_chars": len(op),
                "new_chars": len(np_),
                "eng_new": eng_score(np_),
                "eng_old": eng_score(op),
                "old_start": op[:160],
                "new_start": np_[:160],
                "date_match": O.get("date") == best.get("date"),
                "author_match": O.get("author") == best.get("author"),
            }
        )

    rows.sort(key=lambda r: r["jac"])
    strong = [r for r in rows if r["jac"] >= 0.35]
    medium = [r for r in rows if 0.2 <= r["jac"] < 0.35]
    weak = [r for r in rows if r["jac"] < 0.2]

    print(f"content matches: strong>={0.35}:{len(strong)} mid:{len(medium)} weak<{0.2}:{len(weak)}")
    print(f"avg jaccard={sum(r['jac'] for r in rows)/len(rows):.3f}")
    print(f"date_match among best content: {sum(1 for r in rows if r['date_match'])}/{len(rows)}")
    print(f"author_match among best content: {sum(1 for r in rows if r['author_match'])}/{len(rows)}")

    print("\n=== STRONG (likely same letter, compare quality) ===")
    for r in sorted(strong, key=lambda x: -x["jac"])[:8]:
        print(
            f"jac={r['jac']} old#{r['old_id']}({r['old_date']}) <-> new#{r['new_id']}({r['new_date']}) "
            f"eng_old={r['eng_old']} eng_new={r['eng_new']}"
        )
        print(f"  OLD: {r['old_start']}")
        print(f"  NEW: {r['new_start']}")

    print("\n=== WEAKEST content matches ===")
    for r in rows[:8]:
        print(
            f"jac={r['jac']} old#{r['old_id']} {r['old_date']} {r['old_author']} "
            f"-> new#{r['new_id']} {r['new_date']} {r['new_author']}"
        )
        print(f"  OLD: {r['old_start']}")
        print(f"  NEW: {r['new_start']}")

    # New corpus quality scan
    eng_leaks = []
    short = []
    for L in NEW["letters"]:
        t = " ".join(L["paragraphs"])
        e = eng_score(t)
        if e >= 6:
            eng_leaks.append((L["id"], e, L.get("date"), t[:120]))
        if len(t) < 50:
            short.append((L["id"], L.get("date"), t))

    print(f"\nNEW english_leak>={6}: {len(eng_leaks)}")
    for item in eng_leaks[:10]:
        print(" ", item)
    print(f"NEW short<50chars: {len(short)}")
    for item in short[:10]:
        print(" ", item)

    # Sample random new letters for literary quality markers (PT-PT, MT artifacts)
    issues_pt = {"ideia_circ": 0, "facto": 0, "te_": 0, "Maria": 0, "Lovingly": 0, "en_dash_weird": 0}
    for L in NEW["letters"]:
        t = " ".join(L["paragraphs"])
        if "Idéia" in t or "idéia" in t:
            issues_pt["ideia_circ"] += 1
        if re.search(r"\bfacto\b", t):
            issues_pt["facto"] += 1
        if re.search(r"\bQue Deus te |\bpara ti\b|\bcontigo\b", t):
            issues_pt["te_"] += 1
        if re.search(r"(?<![nN])\bMaria\b", t):
            issues_pt["Maria"] += 1
        if "Lovingly" in t:
            issues_pt["Lovingly"] += 1
    print("\nPT issues counts:", issues_pt)

    out = {
        "strong": strong,
        "medium": medium,
        "weak": weak,
        "eng_leaks": eng_leaks,
        "short": short,
        "issues_pt": issues_pt,
        "rows": rows,
    }
    # shrink for file
    slim = {
        "summary": {
            "strong": len(strong),
            "medium": len(medium),
            "weak": len(weak),
            "avg_jac": round(sum(r["jac"] for r in rows) / len(rows), 3),
            "eng_leaks": len(eng_leaks),
            "short": len(short),
            "issues_pt": issues_pt,
        },
        "strong_ids": [(r["old_id"], r["new_id"], r["jac"]) for r in strong],
        "weak_ids": [(r["old_id"], r["new_id"], r["jac"]) for r in weak],
        "eng_leak_ids": [x[0] for x in eng_leaks],
    }
    path = ROOT / "cartas" / "compare_old_new_deep.json"
    path.write_text(json.dumps(slim, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", path)


if __name__ == "__main__":
    main()
