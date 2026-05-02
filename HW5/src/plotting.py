"""Lightweight plotting helpers for HW5 figures."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def savefig(fig, path: Path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def actual_vs_fitted(dates, actual, fitted, title, path: Path):
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(dates, actual, label="actual", lw=1.2)
    ax.plot(dates, fitted, label="fitted (BF)", lw=1.2, linestyle="--")
    ax.set_title(title)
    ax.set_ylabel("monthly return")
    ax.legend()
    ax.grid(alpha=0.3)
    savefig(fig, path)


def cumulative_returns(dates, returns_df: pd.DataFrame, path: Path, title="Cumulative factor returns"):
    cum = (1.0 + returns_df).cumprod() - 1.0
    fig, ax = plt.subplots(figsize=(10, 5))
    for col in returns_df.columns:
        ax.plot(dates, cum[col], label=col, lw=1.4)
    ax.set_title(title)
    ax.set_ylabel("cumulative return")
    ax.legend()
    ax.grid(alpha=0.3)
    savefig(fig, path)


def corr_heatmap(corr: np.ndarray, labels: list, path: Path, title: str, annot=True):
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(
        corr,
        annot=annot,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        vmin=-1,
        vmax=1,
        xticklabels=labels,
        yticklabels=labels,
        ax=ax,
    )
    ax.set_title(title)
    savefig(fig, path)


def large_corr_heatmap(corr: np.ndarray, path: Path, title: str):
    fig, ax = plt.subplots(figsize=(8, 7))
    sns.heatmap(corr, cmap="coolwarm", center=0, vmin=-1, vmax=1, xticklabels=False, yticklabels=False, ax=ax)
    ax.set_title(title)
    savefig(fig, path)


def weight_plots(weights: np.ndarray, path_sorted: Path, path_hist: Path, title_prefix: str):
    w = np.asarray(weights)
    sorted_w = np.sort(w)
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(sorted_w, lw=1.2)
    ax.axhline(0, color="grey", lw=0.6)
    ax.set_title(f"{title_prefix}: sorted weights")
    ax.set_xlabel("rank")
    ax.set_ylabel("weight")
    ax.grid(alpha=0.3)
    savefig(fig, path_sorted)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(w[w != 0], bins=60, color="#1f77b4", alpha=0.8)
    ax.set_title(f"{title_prefix}: weight distribution")
    ax.set_xlabel("weight")
    ax.set_ylabel("count")
    ax.grid(alpha=0.3)
    savefig(fig, path_hist)
