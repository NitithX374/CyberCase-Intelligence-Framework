"""Comparison figure for the warning-layer evaluation (Fig. results).

Style follows the scientific-figure-making skill of figures4papers
(https://github.com/ChenLiu-1996/figures4papers): top/right spines off,
frameless legends, semantic palette, black bar edges, values printed on bars.

Every number is read from the recorded result files; nothing is typed in:
  nli_grounding_experiment/outputs/canonical/final_metrics.json   (WiCE test)
  research/attribution_benchmark/results/b1_20261007.json         (EN/MT-TH, replay)

Run from the repository root:
  python paper/ubimedia2027/figures/make_results.py
"""

import json
import logging
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "results"

PALETTE = {
    "blue_main": "#0F4D92",
    "blue_secondary": "#3775BA",
    "green_3": "#8BCF8B",
    "red_2": "#E9A6A1",
    "red_strong": "#B64342",
    "neutral": "#CFCECE",
    "teal": "#42949E",
}

plt.rcParams.update(
    {
        "font.family": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
        "font.size": 15,
        "axes.spines.right": False,
        "axes.spines.top": False,
        "axes.linewidth": 1.5,
        "legend.frameon": False,
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "xtick.labelsize": 11.5,
        "ytick.labelsize": 11,
        "axes.labelsize": 12,
    }
)


def load():
    wice = json.loads(
        (ROOT / "nli_grounding_experiment/outputs/canonical/final_metrics.json").read_text()
    )["mdeberta"]
    b1 = json.loads(
        (ROOT / "research/attribution_benchmark/results/b1_20261007.json").read_text()
    )
    return wice, b1["paired_en_mt_th"], b1["downstream"]["overall"]


def bars(ax, categories, series, labels, colors, hatches=None, fmt="{:.1f}", texts=None, fs=11):
    n = len(series)
    width = 0.8 / n
    x = np.arange(len(categories))
    for i, (values, label, color) in enumerate(zip(series, labels, colors)):
        pos = x - 0.4 + width / 2 + i * width
        rects = ax.bar(
            pos,
            values,
            width,
            label=label,
            color=color,
            edgecolor="black",
            linewidth=1.0,
            hatch=None if hatches is None else hatches[i],
        )
        for j, rect in enumerate(rects):
            text = texts[i][j] if texts else fmt.format(values[j])
            ax.text(
                rect.get_x() + rect.get_width() / 2,
                rect.get_height() + 0.8,
                text,
                ha="center",
                va="bottom",
                fontsize=fs,
                rotation=90 if texts is None and n > 2 else 0,
            )
    ax.set_xticks(x)
    ax.set_xticklabels(categories)


def main():
    wice, transfer, replay = load()

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.9), gridspec_kw={"width_ratios": [1.0, 1.12, 1.12]})

    # (a) WiCE test: variants of the warning layer
    ax = axes[0]
    variants = ["B0", "B1", "B1-LR", "B3"]
    names = {
        "B0": "B0: full evidence",
        "B1": "B1: selected units",
        "B1-LR": "B1-LR (deployed)",
        "B3": "B3: + reverse NLI",
    }
    series = [
        [100 * wice[v]["macro_f1"], 100 * wice[v]["supp_f1"], 100 * wice[v]["fsr"]] for v in variants
    ]
    bars(
        ax,
        ["Macro-F1 ↑", "Supp. F1 ↑", "False acc. ↓"],
        series,
        [names[v] for v in variants],
        [PALETTE["neutral"], PALETTE["red_2"], PALETTE["blue_main"], PALETTE["teal"]],
    )
    ax.set_ylim(0, 92)
    ax.set_ylabel("% (WiCE test)")
    ax.set_title("(a) Variants (WiCE)", loc="left", fontweight="bold", fontsize=13)
    ax.legend(loc="upper right", fontsize=10, ncol=1, handlelength=1.2, borderaxespad=0.1)

    # (b) English vs machine-translated Thai (AttributionBench test)
    ax = axes[1]
    cats = ["FAR\nID ↓", "FAR\nOOD ↓", "FRR\nID ↓", "FRR\nOOD ↓"]
    en = [
        100 * transfer["test"]["en"]["false_acceptance_rate"],
        100 * transfer["test_ood"]["en"]["false_acceptance_rate"],
        100 * transfer["test"]["en"]["false_rejection_rate"],
        100 * transfer["test_ood"]["en"]["false_rejection_rate"],
    ]
    th = [
        100 * transfer["test"]["th"]["false_acceptance_rate"],
        100 * transfer["test_ood"]["th"]["false_acceptance_rate"],
        100 * transfer["test"]["th"]["false_rejection_rate"],
        100 * transfer["test_ood"]["th"]["false_rejection_rate"],
    ]
    bars(
        ax,
        cats,
        [en, th],
        ["English (original)", "Thai (Google MT)"],
        [PALETTE["blue_secondary"], PALETTE["red_strong"]],
        hatches=[None, "//"],
    )
    for k, split in enumerate(["test", "test_ood"]):
        lo, hi = transfer[split]["cluster_bootstrap"]["th_minus_en95"]["false_acceptance_rate"]
        delta = th[k] - en[k]
        ax.text(
            k,
            max(en[k], th[k]) + 6,
            f"Δ {delta:+.1f} pp\n[{100 * lo:+.1f}, {100 * hi:+.1f}]",
            ha="center",
            va="bottom",
            fontsize=10.5,
            color=PALETTE["red_strong"],
        )
    ax.set_ylim(0, 82)
    ax.set_ylabel("% (AttributionBench test)")
    ax.set_title("(b) English vs. MT Thai", loc="left", fontweight="bold", fontsize=13)
    ax.legend(loc="upper right", fontsize=10, handlelength=1.2, borderaxespad=0.1)

    # (c) Replay: the warning used as a filter
    ax = axes[2]
    keys = [
        ("unsupported_admission", "Unsupp.\nadmitted ↓"),
        ("supported_retention", "Supp.\nretained ↑"),
        ("paired_unsupported_citation_utilization", "Unsupp.\ncited ↓"),
        ("paired_supported_citation_utilization", "Supp.\ncited ↑"),
    ]
    arms = [("unfiltered", "No filter"), ("verified", "B1-LR filter")]
    series, texts = [], []
    for arm, _ in arms:
        series.append([100 * replay[arm][k]["value"] for k, _ in keys])
        texts.append(
            [f"{replay[arm][k]['numerator']}/{replay[arm][k]['denominator']}" for k, _ in keys]
        )
    bars(
        ax,
        [label for _, label in keys],
        series,
        [label for _, label in arms],
        [PALETTE["neutral"], PALETTE["blue_main"]],
        texts=texts,
    )
    ax.set_ylim(0, 125)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_ylabel("%")
    ax.set_title("(c) Label used as a filter", loc="left", fontweight="bold", fontsize=13)
    ax.legend(loc="upper right", fontsize=10, ncol=2, handlelength=1.2, borderaxespad=0.1, columnspacing=0.8)

    fig.tight_layout(pad=0.6, w_pad=1.2)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(OUT.with_suffix(f".{ext}"), dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    main()
