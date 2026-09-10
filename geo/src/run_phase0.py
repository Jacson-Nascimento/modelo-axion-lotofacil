"""Run AXION-GEO phase 0 on a binary contest x 25 matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from scipy.stats import norm

from geometry import extract_features


DEFAULT_SEED = 20260910
DEFAULT_NULL_DRAWS = 20000


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def benjamini_hochberg(pvalues: Iterable[float]) -> np.ndarray:
    p = np.asarray(list(pvalues), dtype=float)
    order = np.argsort(p)
    q = np.empty_like(p)
    running = 1.0
    m = len(p)
    for rank_index in range(m - 1, -1, -1):
        idx = order[rank_index]
        rank = rank_index + 1
        running = min(running, p[idx] * m / rank)
        q[idx] = min(1.0, running)
    return q


def validate_input(df: pd.DataFrame) -> list[str]:
    dcols = [f"d{i:02d}" for i in range(1, 26)]
    required = ["contest", "date", *dcols]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    if df["contest"].duplicated().any():
        raise ValueError("Duplicate contests found.")
    matrix = df[dcols].to_numpy()
    if not np.isin(matrix, [0, 1]).all():
        raise ValueError("Binary matrix contains values other than 0/1.")
    row_sums = matrix.sum(axis=1)
    if not np.all(row_sums == 15):
        bad = int(np.sum(row_sums != 15))
        raise ValueError(f"{bad} rows do not contain exactly 15 selected cells.")
    return dcols


def build_feature_matrix(df: pd.DataFrame, dcols: list[str]) -> pd.DataFrame:
    records = []
    for row in df.itertuples(index=False):
        values = np.asarray([getattr(row, c) for c in dcols], dtype=np.int8)
        record = {"contest": int(row.contest), "date": str(row.date)}
        record.update(extract_features(values))
        records.append(record)
    return pd.DataFrame(records)


def build_null_features(draws: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    records = []
    for _ in range(draws):
        selected = rng.choice(25, size=15, replace=False)
        flat = np.zeros(25, dtype=np.int8)
        flat[selected] = 1
        records.append(extract_features(flat))
    return pd.DataFrame(records)


def build_screening_summary(
    observed: pd.DataFrame, null: pd.DataFrame, null_draws: int
) -> pd.DataFrame:
    feature_cols = [c for c in observed.columns if c not in ("contest", "date")]
    n_obs = len(observed)
    rows = []

    for feature in feature_cols:
        obs = observed[feature].astype(float)
        nul = null[feature].astype(float)
        obs_mean = float(obs.mean())
        null_mean = float(nul.mean())
        null_sd = float(nul.std(ddof=1))

        # Phase-0 screening only. The denominator includes Monte Carlo
        # uncertainty in the estimated null mean.
        se_diff = null_sd * math.sqrt((1.0 / n_obs) + (1.0 / null_draws))
        z = (obs_mean - null_mean) / se_diff if se_diff > 0 else float("nan")
        p = float(2 * norm.sf(abs(z))) if np.isfinite(z) else float("nan")

        rows.append(
            {
                "feature": feature,
                "obs_mean": obs_mean,
                "obs_sd": float(obs.std(ddof=1)),
                "null_mean": null_mean,
                "null_sd": null_sd,
                "mean_diff": obs_mean - null_mean,
                "z_screen_mc": z,
                "p_screen_mc": p,
                "null_q025": float(nul.quantile(0.025)),
                "null_median": float(nul.quantile(0.5)),
                "null_q975": float(nul.quantile(0.975)),
            }
        )

    summary = pd.DataFrame(rows)
    summary["q_bh_screen_mc"] = benjamini_hochberg(summary["p_screen_mc"])
    return summary.sort_values(["q_bh_screen_mc", "p_screen_mc", "feature"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="binary_matrix.csv")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--null-draws", type=int, default=DEFAULT_NULL_DRAWS)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_path)
    dcols = validate_input(df)
    observed = build_feature_matrix(df, dcols)
    null = build_null_features(args.null_draws, args.seed)
    summary = build_screening_summary(observed, null, args.null_draws)

    observed_path = output_dir / "geo_feature_matrix.csv"
    summary_path = output_dir / f"null_summary_B{args.null_draws}.csv"
    metadata_path = output_dir / f"phase0_metadata_B{args.null_draws}.json"

    observed.to_csv(observed_path, index=False)
    summary.to_csv(summary_path, index=False)

    metadata = {
        "project": "AXION-GEO",
        "version": "0.1.0",
        "phase": 0,
        "status": "screening_only",
        "input_file": input_path.name,
        "input_sha256": sha256_file(input_path),
        "n_contests": int(len(df)),
        "first_contest": int(df["contest"].min()),
        "last_contest": int(df["contest"].max()),
        "first_date": str(df.iloc[0]["date"]),
        "last_date": str(df.iloc[-1]["date"]),
        "feature_count": int(len(observed.columns) - 2),
        "null_model": "uniform_without_replacement_15_of_25",
        "null_draws": int(args.null_draws),
        "seed": int(args.seed),
        "multiple_testing": "Benjamini-Hochberg across phase-0 mean screens",
        "screening_note": (
            "The z/p/q columns are triage statistics, not evidence of prediction. "
            "They account for Monte Carlo uncertainty in the estimated null mean."
        ),
        "holdout_policy": (
            "Phase-0 feature definitions use contests through the supplied baseline only. "
            "Post-baseline contests are not used to tune the feature catalog."
        ),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    checksum_lines = []
    for path in [observed_path, summary_path, metadata_path]:
        checksum_lines.append(f"{sha256_file(path)}  {path.name}")
    (output_dir / "CHECKSUMS.sha256").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")

    print(json.dumps(metadata, indent=2, ensure_ascii=False))
    print("\nTop screening deviations:")
    print(
        summary[
            ["feature", "obs_mean", "null_mean", "z_screen_mc", "p_screen_mc", "q_bh_screen_mc"]
        ].head(10).to_string(index=False)
    )


if __name__ == "__main__":
    main()
