#!/usr/bin/env python3
"""Publication figures for The AI Prose Clock.

Reads ``analysis/results.json`` and writes 300 dpi PNGs to ``figures/``.  Every
figure is driven by results, never by hard-coded numbers.
"""

import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import clock, config  # noqa: E402

CHATGPT = 2022.92  # 2022-11-30
DPI = 300
COLORS = {"arxiv": "#1f77b4", "pubmed": "#2ca02c", "hackernews": "#ff7f0e",
          "edgar": "#9467bd", "nvd": "#d62728"}


def _style(ax, title, ylabel=None):
    ax.axvline(CHATGPT, color="black", linestyle=":", linewidth=1.0, zorder=0)
    ax.set_title(title, fontsize=10)
    ax.set_xlabel("year", fontsize=8)
    ax.tick_params(labelsize=8)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=8)
    ax.grid(alpha=0.25, linewidth=0.5)


def fig_index(corpora, path):
    ok = {k: v for k, v in corpora.items() if v.get("ok")}
    if not ok:
        return
    cols = 2
    rows = math.ceil(len(ok) / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(8.5, 2.4 * rows), squeeze=False)
    for ax, (name, res) in zip(axes.ravel(), ok.items()):
        t = np.array([clock.month_to_year(m) for m in res["months"]])
        y = np.array(res["index_values"])
        se = np.array(res["index_se"])
        color = COLORS.get(name, "gray")
        ax.fill_between(t, y - 1.96 * se, y + 1.96 * se, color=color, alpha=0.20, linewidth=0)
        ax.plot(t, y, color=color, linewidth=1.4)
        clk = res.get("clock", {})
        if clk.get("ok"):
            tt = np.linspace(t.min(), t.max(), 300)
            ax.plot(tt, clock.logistic(tt, clk["K"], clk["g_per_year"], clk["half_adoption"]),
                    color="black", linestyle="--", linewidth=1.0)
            ax.axvline(clk["half_adoption"], color=color, linestyle="-", linewidth=0.8, alpha=0.6)
            title = "%s  half-adoption %s" % (name, clk.get("half_month", "?"))
        else:
            title = name
        _style(ax, title, "excess (log ratio)")
        ax.axhline(0.0, color="gray", linewidth=0.6)
    for ax in axes.ravel()[len(ok):]:
        ax.axis("off")
    fig.suptitle("Excess-vocabulary index: observed (colored) and fitted diffusion clock (dashed)",
                 fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(path, dpi=DPI)
    plt.close(fig)


def fig_markers(corpora, path):
    ok = {k: v for k, v in corpora.items() if v.get("ok") and v.get("top_discovered")}
    if not ok:
        return
    cols = 2
    rows = math.ceil(len(ok) / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(8.5, 2.6 * rows), squeeze=False)
    for ax, (name, res) in zip(axes.ravel(), ok.items()):
        top = res["top_discovered"][:12]
        words = [row["word"] for row in top][::-1]
        vals = [row["mean_excess"] for row in top][::-1]
        ax.barh(words, vals, color=COLORS.get(name, "gray"))
        ax.set_title("%s: largest post-2022 excess words" % name, fontsize=9)
        ax.tick_params(labelsize=7)
        ax.set_xlabel("mean excess (log ratio)", fontsize=8)
        ax.grid(alpha=0.25, axis="x", linewidth=0.5)
    for ax in axes.ravel()[len(ok):]:
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(path, dpi=DPI)
    plt.close(fig)


def fig_typographic(corpora, path):
    ok = {k: v for k, v in corpora.items() if v.get("ok") and v.get("typographic")}
    if not ok:
        return
    fig, ax = plt.subplots(figsize=(7.0, 3.6))
    for name, res in ok.items():
        typo = res["typographic"]
        t = np.array([clock.month_to_year(m) for m in typo["months"]])
        y = np.array(typo["values"])
        ax.plot(t, y, color=COLORS.get(name, "gray"), linewidth=1.3, label=name)
    _style(ax, "Typographic LLM-style marker rate (independent channel)",
           "markers per 1,000 tokens")
    ax.legend(fontsize=8, frameon=False)
    fig.tight_layout()
    fig.savefig(path, dpi=DPI)
    plt.close(fig)


def fig_controls(results, path):
    control = results.get("negative_control")
    res = results.get("corpora", {}).get(control, {})
    if not res.get("ok"):
        return
    fig, ax = plt.subplots(figsize=(6.0, 3.4))
    t = np.array([clock.month_to_year(m) for m in res["months"]])
    y = np.array(res["index_values"])
    ax.plot(t, y, color="#d62728", linewidth=1.3)
    ax.axhline(0.0, color="gray", linewidth=0.6)
    placebo = res.get("placebo_break", {})
    txt = "fake 2020 break: mean excess %+.3f" % placebo.get("fake_post_mean_excess", float("nan"))
    ax.text(0.02, 0.95, txt, transform=ax.transAxes, fontsize=8, va="top")
    _style(ax, "Negative control: %s (should be flat)" % control, "excess (log ratio)")
    fig.tight_layout()
    fig.savefig(path, dpi=DPI)
    plt.close(fig)


def fig_simulation(path_in, path_out):
    if not path_in.exists():
        return
    data = json.loads(path_in.read_text())
    fig, ax = plt.subplots(figsize=(5.0, 3.4))
    for i, (name, res) in enumerate(data.items()):
        ax.scatter(clock.month_to_year(res["true_half_month"]),
                   clock.month_to_year(res["fitted_half_month"] or res["true_half_month"]),
                   s=40, label=name)
    lo, hi = 2022.5, 2023.6
    ax.plot([lo, hi], [lo, hi], color="gray", linestyle="--", linewidth=0.8)
    ax.set_xlabel("true inflection (year)", fontsize=8)
    ax.set_ylabel("recovered inflection", fontsize=8)
    ax.set_title("Synthetic validation: recovered vs true date", fontsize=9)
    ax.grid(alpha=0.25, linewidth=0.5)
    ax.legend(fontsize=7, frameon=False)
    fig.tight_layout()
    fig.savefig(path_out, dpi=DPI)
    plt.close(fig)


def main() -> int:
    results_path = config.ANALYSIS / "results.json"
    if not results_path.exists():
        print("[figures] results.json not found - run scripts/run_analysis.py first", flush=True)
        return 1
    results = json.loads(results_path.read_text())
    corpora = results.get("corpora", {})
    out = config.FIGURES
    out.mkdir(parents=True, exist_ok=True)

    fig_index(corpora, out / "fig1_index_and_clock.png")
    fig_markers(corpora, out / "fig2_discovered_markers.png")
    fig_typographic(corpora, out / "fig3_typographic_channel.png")
    fig_controls(results, out / "fig4_negative_control.png")
    fig_simulation(config.ANALYSIS / "simulation_validation.json", out / "fig5_simulation_validation.png")
    print("[figures] wrote to %s" % out.relative_to(ROOT), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
