from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import locator_synthetic as ls  # noqa: E402
import locator_tiers as lt  # noqa: E402

TIER_NAMES = ("find_folded_quote", "unique_ellipsis_pieces", "find_relaxed_quote", "find_format_only_quote")
ABLATION = ("exact only", "+ NFKC fold", "+ ellipsis pieces", "+ markup and whitespace", "+ format tier (production)")
THRESHOLDS = [round(0.50 + step / 100, 2) for step in range(51)]
FIXED = (0.60, 0.80, 0.90)
EDGE_MARKS = "\"'“”‘’«»„‚`´"


def ablation(text: str, quote: str) -> list[bool]:
    import app.trace.quotes as quotes
    from app.trace.bind import located_quote

    kept = {name: getattr(quotes, name) for name in TIER_NAMES}
    verdicts = []
    try:
        for level in range(len(ABLATION)):
            for at, name in enumerate(TIER_NAMES):
                setattr(quotes, name, kept[name] if at < level else (lambda *args: None))
            verdicts.append(located_quote(text, quote) is not None)
    finally:
        for name, function in kept.items():
            setattr(quotes, name, function)
    return verdicts


def windisch(text: str, quote: str) -> bool:
    trimmed = quote.strip().strip(EDGE_MARKS).strip()
    collapsed = re.sub(r"\s+", " ", trimmed)
    return bool(collapsed) and collapsed in re.sub(r"\s+", " ", text)


def score(text: str, quote: str) -> float:
    from rapidfuzz import fuzz

    return fuzz.partial_ratio(quote, text) / 100


def normalised(text: str) -> str:
    return re.sub(r"\s+", " ", text.casefold()).strip()


def judged(text: str, quote: str) -> dict:
    return {"ablation": ablation(text, quote), "windisch": windisch(text, quote), "score": score(text, quote),
            "folded": score(normalised(text), normalised(quote))}


def casie_samples(split: str) -> list[dict]:
    texts: dict[str, str] = {}
    samples = []
    log = HERE / "results" / f"locator_synthetic_{split}_edits.jsonl"
    for line in log.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row.get("unchanged") or (row["kind"] == "N2" and row["verified_by"]) or row["kind"] == "N1":
            continue
        group = "format" if row["kind"] in ls.FORMAT_EDITS else "N2" if row["kind"] == "N2" else "content"
        if row["article"] not in texts:
            texts[row["article"]] = json.loads((ls.CASIE / f"{row['article']}.json").read_text(encoding="utf-8"))[
                "content"]
        samples.append({"article": row["article"], "kind": row["kind"], "group": group, "quote": row["quote"],
                        "pointer": bool(row.get("pointer"))})
    for sample in samples:
        sample.update(judged(texts[sample["article"]], sample["quote"]))
    return samples


def real_quotes(backend: str) -> dict[str, list[dict]]:
    exported = HERE / "results" / "locator_baselines_export.json"
    subprocess.run([sys.executable, str(HERE / "locator_tiers.py"), "--backend", backend, "--export-only",
                    str(exported)], check=True, cwd=HERE)
    english = json.loads(exported.read_text(encoding="utf-8"))
    exported.unlink()
    thai_texts, thai = lt.thai_items()
    out: dict[str, list[dict]] = {}
    for language, texts, items in (("English", english["texts"], english["items"]), ("Thai", thai_texts, thai)):
        for item in items:
            text = texts[item["case"]]
            out.setdefault(f"{language} {item['split']}", []).append(
                {"case": item["case"], "quote": item["quote"], **judged(text, item["quote"])})
    return out


def rate(samples: list[dict], accepted, group: str, kind: str | None = None) -> list:
    rows = [{**sample, "accepted": accepted(sample)} for sample in samples]
    return ls.interval(rows, lambda r: r["accepted"],
                       lambda r: r["group"] == group and (kind is None or r["kind"] == kind))


def methods(tau: float, folded_tau: float) -> list[tuple[str, object]]:
    rows: list[tuple[str, object]] = [(name, lambda s, at=at: s["ablation"][at]) for at, name in enumerate(ABLATION)]
    rows.append(("Windisch-like", lambda s: s["windisch"]))
    for key, name, chosen in (("score", "similarity", tau), ("folded", "similarity, case-folded", folded_tau)):
        for value in sorted({*FIXED, chosen}):
            label = f"{name} ≥ {value:.2f}" + (" (chosen on development)" if value == chosen else "")
            rows.append((label, lambda s, value=value, key=key: s[key] >= value))
    return rows


def chosen_tau(samples: list[dict], key: str) -> float:
    def gap(tau: float) -> float:
        fmt = [s[key] >= tau for s in samples if s["group"] == "format"]
        content = [s[key] >= tau for s in samples if s["group"] == "content"]
        return sum(fmt) / len(fmt) - sum(content) / len(content)

    return max(THRESHOLDS, key=lambda tau: (round(gap(tau), 6), tau))


def curve(samples: list[dict], key: str) -> list[dict]:
    points = []
    for tau in THRESHOLDS:
        point = {"tau": tau}
        for group in ("format", "content", "N2"):
            chosen = [s for s in samples if s["group"] == group]
            point[group] = round(sum(s[key] >= tau for s in chosen) / len(chosen), 4) if chosen else None
        points.append(point)
    return points


def shown(cell: list) -> str:
    hits, total, value, low, high = cell
    return "–" if value is None else f"{value:.3f} [{low:.3f}, {high:.3f}] ({hits}/{total})"


def figure(points: list[dict], folded: list[dict], production: dict, path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    taus = [p["tau"] for p in points]
    fig, ax = plt.subplots(figsize=(6, 3.6))
    ax.plot(taus, [p["format"] for p in points], color="black", linewidth=1, label="format edits verified")
    ax.plot(taus, [p["content"] for p in points], color="black", linewidth=1, linestyle="--",
            label="content edits verified")
    ax.plot(taus, [p["format"] for p in folded], color="black", linewidth=1, linestyle=":",
            label="format edits verified, case-folded")
    ax.plot(taus, [p["content"] for p in folded], color="black", linewidth=1, linestyle="-.",
            label="content edits verified, case-folded")
    ax.axhline(production["format"], color="grey", linewidth=0.8)
    ax.axhline(production["content"], color="grey", linewidth=0.8, linestyle="--")
    ax.set_xlabel("similarity threshold τ (partial_ratio)")
    ax.set_ylabel("share verified")
    ax.set_ylim(-0.02, 1.02)
    ax.legend(frameon=False, fontsize=8)
    ax.set_title("Grey: production locator", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=200)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", required=True)
    parser.add_argument("--split", choices=("development", "confirmation"), required=True)
    args = parser.parse_args()
    ls.backend(args.backend)
    samples = casie_samples(args.split)
    development = HERE / "results" / "locator_baselines_development.json"
    if args.split == "development":
        tau, folded_tau = chosen_tau(samples, "score"), chosen_tau(samples, "folded")
    else:
        chosen = json.loads(development.read_text(encoding="utf-8"))
        tau, folded_tau = chosen["chosen tau"], chosen["chosen tau, case-folded"]
    real = real_quotes(args.backend)
    real = {name: quotes for name, quotes in real.items() if name.endswith(args.split)}
    table, report = [], {"split": args.split, "chosen tau": tau,
                         "chosen tau, case-folded": folded_tau, "rows": {}, "real": {}}
    kinds = ls.CONTENT_EDITS
    header = ["Method", "Format edits verified ↑", "Content edits verified ↓", *[f"{k} ↓" for k in kinds],
              "N2 verified ↓", *[f"real {name}" for name in real], "Says where it differs"]
    table += ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    for label, accepted in methods(tau, folded_tau):
        cells = {"format": rate(samples, accepted, "format"), "content": rate(samples, accepted, "content"),
                 "N2": rate(samples, accepted, "N2"),
                 **{kind: rate(samples, accepted, "content", kind) for kind in kinds}}
        counts = {name: sum(1 for q in quotes if accepted(q)) for name, quotes in real.items()}
        report["rows"][label] = {**cells, "real": counts}
        says = "yes" if label == ABLATION[-1] else "no"
        table.append("| " + " | ".join([label, shown(cells["format"]), shown(cells["content"]),
                                        *[shown(cells[k]) for k in kinds], shown(cells["N2"]),
                                        *[f"{counts[name]} / {len(real[name])}" for name in real], says]) + " |")
    pointer = [s for s in samples if s["group"] == "content" and not s["ablation"][-1]]
    report["pointer on unverified content edits"] = [sum(s["pointer"] for s in pointer), len(pointer)]
    points, folded_points = curve(samples, "score"), curve(samples, "folded")
    report["curve"] = points
    report["curve, case-folded"] = folded_points
    production = {group: sum(s["ablation"][-1] for s in samples if s["group"] == group)
                  / max(1, sum(1 for s in samples if s["group"] == group)) for group in ("format", "content")}
    reaching = [(key, p["tau"]) for key, curve_points in (("raw", points), ("case-folded", folded_points))
                for p in curve_points if p["format"] >= production["format"] - 0.01 and p["content"] <= 0.001]
    report["thresholds reaching production"] = reaching
    extra = []
    for name, quotes in real.items():
        for q in quotes:
            if q["score"] >= tau and not q["ablation"][-1]:
                extra.append({"data": name, "case": q["case"], "score": q["score"], "quote": q["quote"]})
    report["real quotes verified by the chosen tau and not by production"] = len(extra)
    figure(points, folded_points, production, HERE / "results" / f"locator_baselines_threshold_{args.split}.png")
    script = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    md = [f"# Locator: ablation and alternatives ({args.split})", "",
          f"Script sha256 `{script}`. Backend `{args.backend}`. Chosen τ (on development): {tau:.2f}; case-folded {folded_tau:.2f}. No model call.",
          "", "CASIE cells: rate [95% article bootstrap] (count). Real cells: quotes verified / written.", "",
          *table, "",
          f"Pointer on content edits production leaves unverified: {report['pointer on unverified content edits']}.",
          f"Thresholds that reach production's point (format within 0.01, content ≤ 0.001): {reaching or 'none'}.",
          "", f"## Real quotes the chosen τ verifies and production does not ({len(extra)})", ""]
    md += [f"- {e['data']} `{e['case']}` score {e['score']:.3f}: «{e['quote'][:200]}»" for e in extra[:60]]
    (HERE / "results" / f"locator_baselines_{args.split}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (HERE / "results" / f"locator_baselines_{args.split}.json").write_text(
        json.dumps({"script": script, **report}, indent=1, ensure_ascii=False), encoding="utf-8")
    print("\n".join(md[:len(table) + 12]))


if __name__ == "__main__":
    main()
