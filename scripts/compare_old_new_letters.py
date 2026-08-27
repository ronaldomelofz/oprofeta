# -*- coding: utf-8 -*-
"""Compare old 62-letter selection with new Beloved Prophet extraction."""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"E:\PROJETOS-CURSOR\OPROFETA")
OLD = json.loads((ROOT / "cartas" / "letters_selection_62.json").read_text(encoding="utf-8"))
NEW = json.loads((ROOT / "src" / "data" / "letters.json").read_text(encoding="utf-8"))


def tokset(s: str) -> set[str]:
    return set(re.findall(r"[a-záéíóúâêôãõçàü0-9]{4,}", (s or "").lower()))


def jaccard(a: str, b: str) -> float:
    A, B = tokset(a), tokset(b)
    if not A or not B:
        return 0.0
    return len(A & B) / len(A | B)


def main() -> None:
    print(f"old={len(OLD['letters'])} new={len(NEW['letters'])}")
    idx: dict[tuple, list] = defaultdict(list)
    for L in NEW["letters"]:
        idx[(L.get("date"), L.get("author"))].append(L)

    matched = []
    unmatched = []
    for O in OLD["letters"]:
        cands = idx.get((O.get("date"), O.get("author"))) or []
        if not cands:
            cands = [L for L in NEW["letters"] if L.get("date") == O.get("date")]
        if not cands:
            unmatched.append(O)
            continue
        # best jaccard among candidates
        op = " ".join(O["paragraphs"])
        best = max(cands, key=lambda N: jaccard(op, " ".join(N["paragraphs"])))
        np_ = " ".join(best["paragraphs"])
        matched.append(
            {
                "old": O,
                "new": best,
                "jac": round(jaccard(op, np_), 3),
                "old_chars": len(op),
                "new_chars": len(np_),
                "ratio": round(len(np_) / max(len(op), 1), 2),
            }
        )

    print(f"matched={len(matched)} unmatched={len(unmatched)}")
    for O in unmatched[:20]:
        print(f"  UNMATCH old#{O['id']} {O.get('date')} {O.get('author')} | {O['title']}")

    jac_vals = [m["jac"] for m in matched]
    print(
        f"jaccard avg={sum(jac_vals)/len(jac_vals):.3f} "
        f"min={min(jac_vals):.3f} median={sorted(jac_vals)[len(jac_vals)//2]:.3f}"
    )

    weak = sorted(matched, key=lambda m: m["jac"])[:15]
    print("\nWEAKEST matches:")
    for m in weak:
        O, N = m["old"], m["new"]
        print(
            f"  jac={m['jac']} ratio={m['ratio']} old#{O['id']}→new#{N['id']} "
            f"{O.get('date')} {O.get('author')}"
        )
        print(f"    OLD: {' '.join(O['paragraphs'])[:140]}")
        print(f"    NEW: {' '.join(N['paragraphs'])[:140]}")

    # quality issues in NEW corpus
    issues = {"english_leak": [], "maria": [], "te_intimate": [], "empty": [], "short": []}
    for L in NEW["letters"]:
        text = " ".join(L["paragraphs"])
        if not text.strip():
            issues["empty"].append(L["id"])
        if len(text) < 40:
            issues["short"].append(L["id"])
        eng = len(
            re.findall(
                r"\b(the|and|with|that|this|from|have|were|would|which|their|your)\b",
                text,
                re.I,
            )
        )
        if eng >= 8:
            issues["english_leak"].append((L["id"], eng, text[:100]))
        if re.search(r"\bMaria\b", text) and "Marianna" not in text:
            # exclude Marianna false positive handled by word boundary
            if re.search(r"(?<![nN])\bMaria\b", text):
                issues["maria"].append(L["id"])
        if re.search(r"\b(Que Deus te |para ti\b|de ti\b|contigo\b)", text):
            issues["te_intimate"].append(L["id"])

    print("\nNEW CORPUS ISSUES:")
    for k, v in issues.items():
        print(f"  {k}: {len(v)}")
        if v and k == "english_leak":
            for item in v[:8]:
                print(f"    {item}")

    # Prefer old text when match is strong date+author but new is weaker/leak
    prefer_old = []
    for m in matched:
        O, N = m["old"], m["new"]
        op = " ".join(O["paragraphs"])
        np_ = " ".join(N["paragraphs"])
        eng_new = len(
            re.findall(
                r"\b(the|and|with|that|this|from|have|were|would|which)\b",
                np_,
                re.I,
            )
        )
        if m["jac"] < 0.25 or eng_new >= 8 or m["ratio"] < 0.45:
            prefer_old.append((O["id"], N["id"], m["jac"], eng_new, m["ratio"]))
    print(f"\ncandidates to restore from old: {len(prefer_old)}")
    for row in prefer_old[:20]:
        print(" ", row)

    report = {
        "matched": len(matched),
        "unmatched": len(unmatched),
        "jaccard_avg": round(sum(jac_vals) / len(jac_vals), 3) if jac_vals else 0,
        "issues": {k: len(v) for k, v in issues.items()},
        "prefer_old": prefer_old,
        "unmatched_ids": [O["id"] for O in unmatched],
        "weak": [
            {
                "jac": m["jac"],
                "old_id": m["old"]["id"],
                "new_id": m["new"]["id"],
                "date": m["old"].get("date"),
            }
            for m in weak
        ],
    }
    out = ROOT / "cartas" / "ocr_cache" / "compare_old_new_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("report", out)


if __name__ == "__main__":
    main()
