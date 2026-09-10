"""AXION-GEO Phase 1: visual exploration of the frozen 5x5 baseline.

The script is descriptive and diagnostic. It does not promote geometric
patterns as predictive evidence. Every cell-level deviation is benchmarked
against the Lotofacil N0 null: a uniform draw of 15 cells among 25.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DEFAULT_WINDOWS = (1000, 500, 250)
CELL_P_N0 = 15 / 25


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_binary(df: pd.DataFrame) -> list[str]:
    dcols = [f"d{i:02d}" for i in range(1, 26)]
    required = ["contest", "date", *dcols]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    if df["contest"].duplicated().any():
        raise ValueError("Duplicate contest identifiers found.")
    m = df[dcols].to_numpy(dtype=float)
    if not np.isin(m, [0, 1]).all():
        raise ValueError("Binary matrix contains values other than 0/1.")
    sums = m.sum(axis=1)
    if not np.all(sums == 15):
        raise ValueError(f"{int(np.sum(sums != 15))} rows do not contain exactly 15 selected cells.")
    return dcols


def grid_counts(df: pd.DataFrame, dcols: list[str]) -> np.ndarray:
    return df[dcols].sum(axis=0).to_numpy(dtype=float).reshape(5, 5)


def cell_stats(df: pd.DataFrame, dcols: list[str]) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    n = len(df)
    obs = grid_counts(df, dcols)
    expected = np.full((5, 5), n * CELL_P_N0, dtype=float)
    sd = np.full((5, 5), np.sqrt(n * CELL_P_N0 * (1 - CELL_P_N0)), dtype=float)
    z = (obs - expected) / sd
    prop = obs / n
    return obs, expected, z, prop


def annotate_heatmap(ax, arr: np.ndarray, fmt: str) -> None:
    for r in range(5):
        for c in range(5):
            ax.text(c, r, format(arr[r, c], fmt), ha="center", va="center", fontsize=8)
    ax.set_xticks(range(5), ["1", "2", "3", "4", "5"])
    ax.set_yticks(range(5), ["1", "2", "3", "4", "5"])
    ax.set_xlabel("Coluna")
    ax.set_ylabel("Linha")


def save_heatmap(arr: np.ndarray, title: str, path: Path, *, residual: bool = False, fmt: str = ".0f", vmin=None, vmax=None) -> None:
    fig, ax = plt.subplots(figsize=(7, 6))
    if residual:
        lim = max(2.5, float(np.nanmax(np.abs(arr)))) if vmax is None else float(vmax)
        im = ax.imshow(arr, cmap="RdBu_r", vmin=-lim, vmax=lim)
    else:
        im = ax.imshow(arr, cmap="viridis", vmin=vmin, vmax=vmax)
    annotate_heatmap(ax, arr, fmt)
    ax.set_title(title)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def save_small_multiples(records: list[dict], path: Path, *, residual: bool) -> None:
    fig, axes = plt.subplots(1, len(records), figsize=(15, 4.2), constrained_layout=True)
    if residual:
        lim = max(2.5, max(float(np.max(np.abs(x["z"]))) for x in records))
    else:
        values = [x["prop"] for x in records]
        vmin = min(float(x.min()) for x in values)
        vmax = max(float(x.max()) for x in values)

    for ax, rec in zip(axes, records):
        if residual:
            im = ax.imshow(rec["z"], cmap="RdBu_r", vmin=-lim, vmax=lim)
        else:
            im = ax.imshow(rec["prop"], cmap="viridis", vmin=vmin, vmax=vmax)
        ax.set_title(rec["label"])
        ax.set_xticks(range(5), ["1", "2", "3", "4", "5"], fontsize=8)
        ax.set_yticks(range(5), ["1", "2", "3", "4", "5"], fontsize=8)

    fig.colorbar(im, ax=axes, fraction=0.025, pad=0.02)
    fig.suptitle("Resíduos padronizados por janela" if residual else "Frequência relativa por janela", fontsize=13)
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def load_phase0_summary(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    needed = {"feature", "z_screen_mc", "q_bh_screen_mc"}
    if not needed.issubset(df.columns):
        raise ValueError(f"Phase-0 summary lacks columns: {sorted(needed - set(df.columns))}")
    return df


def select_macro_features(summary: pd.DataFrame) -> pd.DataFrame:
    preferred = [
        "centroid_x", "centroid_y", "radial_mean", "radial_sd", "moment_xx", "moment_yy",
        "adj_orth", "adj_diag", "components_orth", "largest_component_orth", "perimeter_edges",
        "sym_lr", "sym_ud", "sym_diag_main", "sym_diag_anti", "outer_ring", "inner_ring", "center",
    ]
    found = [f for f in preferred if f in set(summary["feature"])]
    if len(found) < 8:
        fallback = summary.sort_values("q_bh_screen_mc").head(12)["feature"].tolist()
        found = list(dict.fromkeys(found + fallback))[:12]
    out = summary[summary["feature"].isin(found)].copy()
    order = {name: i for i, name in enumerate(found)}
    out["_order"] = out["feature"].map(order)
    return out.sort_values("_order")


def save_macro_barplot(macro: pd.DataFrame, path: Path) -> None:
    plot_df = macro.sort_values("z_screen_mc")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(plot_df["feature"], plot_df["z_screen_mc"])
    ax.axvline(0, linewidth=1)
    ax.axvline(2, linestyle="--", linewidth=0.8)
    ax.axvline(-2, linestyle="--", linewidth=0.8)
    ax.set_xlabel("z de triagem da média, observado vs N0")
    ax.set_title("AXION-GEO - Macrogeometria padronizada")
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def save_dashboard(total: dict, macro: pd.DataFrame, records: list[dict], path: Path) -> None:
    fig = plt.figure(figsize=(15, 11), constrained_layout=True)
    gs = fig.add_gridspec(2, 3, height_ratios=[1, 1.15])

    ax1 = fig.add_subplot(gs[0, 0])
    im1 = ax1.imshow(total["prop"], cmap="viridis")
    annotate_heatmap(ax1, total["prop"], ".3f")
    ax1.set_title("Frequência relativa total")
    fig.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04)

    ax2 = fig.add_subplot(gs[0, 1])
    lim = max(2.5, float(np.max(np.abs(total["z"]))))
    im2 = ax2.imshow(total["z"], cmap="RdBu_r", vmin=-lim, vmax=lim)
    annotate_heatmap(ax2, total["z"], ".2f")
    ax2.set_title("Resíduo padronizado total")
    fig.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)

    ax3 = fig.add_subplot(gs[0, 2])
    recent = records[-1]["z"]
    lim2 = max(2.5, float(np.max(np.abs(recent))))
    im3 = ax3.imshow(recent, cmap="RdBu_r", vmin=-lim2, vmax=lim2)
    annotate_heatmap(ax3, recent, ".2f")
    ax3.set_title(f"Resíduo, {records[-1]['label']}")
    fig.colorbar(im3, ax=ax3, fraction=0.046, pad=0.04)

    ax4 = fig.add_subplot(gs[1, :])
    p = macro.sort_values("z_screen_mc")
    ax4.barh(p["feature"], p["z_screen_mc"])
    ax4.axvline(0, linewidth=1)
    ax4.axvline(2, linestyle="--", linewidth=0.8)
    ax4.axvline(-2, linestyle="--", linewidth=0.8)
    ax4.set_xlabel("z de triagem")
    ax4.set_title("Macrogeometria, Fase 0")

    fig.suptitle("AXION-GEO - Dashboard exploratório da Fase 1", fontsize=16)
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def build_cell_summary(df: pd.DataFrame, dcols: list[str], windows: tuple[int, ...]) -> pd.DataFrame:
    rows = []
    specs = [("total", None), *[(f"last_{w}", w) for w in windows]]
    for label, w in specs:
        sample = df if w is None else df.tail(min(w, len(df)))
        obs, exp, z, prop = cell_stats(sample, dcols)
        for r in range(5):
            for c in range(5):
                n = r * 5 + c + 1
                rows.append({
                    "window": label,
                    "n_contests": len(sample),
                    "dezena": n,
                    "row": r + 1,
                    "col": c + 1,
                    "observed_count": int(obs[r, c]),
                    "observed_rate": float(prop[r, c]),
                    "expected_count_n0": float(exp[r, c]),
                    "expected_rate_n0": CELL_P_N0,
                    "z_n0": float(z[r, c]),
                })
    return pd.DataFrame(rows)


def write_results_readme(outdir: Path, metadata: dict, cell_summary: pd.DataFrame, macro: pd.DataFrame) -> None:
    total = cell_summary[cell_summary["window"] == "total"].copy()
    total["abs_z"] = total["z_n0"].abs()
    top_cells = total.sort_values("abs_z", ascending=False).head(5)
    top_macro = macro.assign(abs_z=macro["z_screen_mc"].abs()).sort_values("abs_z", ascending=False).head(5)

    def table(df: pd.DataFrame, cols: list[str]) -> str:
        header = "| " + " | ".join(cols) + " |\n"
        sep = "|" + "|".join(["---"] * len(cols)) + "|\n"
        body = "".join("| " + " | ".join(str(row[c]) for c in cols) + " |\n" for _, row in df.iterrows())
        return header + sep + body

    tc = top_cells.copy()
    tc["observed_rate"] = tc["observed_rate"].map(lambda x: f"{x:.4f}")
    tc["z_n0"] = tc["z_n0"].map(lambda x: f"{x:.3f}")
    tm = top_macro.copy()
    tm["z_screen_mc"] = tm["z_screen_mc"].map(lambda x: f"{x:.3f}")
    tm["q_bh_screen_mc"] = tm["q_bh_screen_mc"].map(lambda x: f"{x:.4f}")

    text = f"""# AXION-GEO - Resultados visuais da Fase 1

**Status:** exploratório, sem uso preditivo  
**Base:** concursos {metadata['first_contest']} a {metadata['last_contest']}  
**Quantidade:** {metadata['n_contests']} concursos  
**Nulo de referência:** seleção uniforme 15/25, expectativa marginal de 0,60 por célula

## Dashboard

![Dashboard](07_dashboard_fase1_resumo.png)

## Heatmaps

| Observado | Resíduo N0 |
|---|---|
| ![Observado](01_heatmap_observado_total.png) | ![Resíduo](03_heatmap_residuo_padronizado_total.png) |

## Estabilidade temporal

![Resíduos por janela](05_small_multiples_residuo_janelas.png)

## Macrogeometria

![Macrogeometria](06_barplot_macrogeometria_zscores.png)

## Células com maior desvio absoluto no histórico total

{table(tc, ['dezena', 'row', 'col', 'observed_rate', 'z_n0'])}

## Features geométricas com maior z absoluto na triagem da Fase 0

{table(tm, ['feature', 'z_screen_mc', 'q_bh_screen_mc'])}

## Leitura metodológica

Os mapas de resíduo comparam cada célula à expectativa N0 de 60%. Um desenho visualmente marcante não é suficiente para caracterizar estrutura morfológica. A interpretação exige persistência temporal e, na etapa seguinte, comparação com um nulo N1 que preserve as margens históricas por dezena.

A Fase 0 já mostrou que nenhuma das 47 features geométricas foi promovida após controle Benjamini-Hochberg. Portanto, estes gráficos são instrumentos de diagnóstico e formulação de hipóteses, não filtros para seleção de jogos.

## Arquivos

- [Metadados](visuals_metadata.json)
- [Resumo por célula](visuals_summary.csv)
- [Manifesto](visuals_manifest.md)

Autor: Jacson Cruz do Nascimento
"""
    (outdir / "README.md").write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--phase0-summary", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--windows", nargs="*", type=int, default=list(DEFAULT_WINDOWS))
    args = parser.parse_args()

    input_path = Path(args.input)
    phase0_path = Path(args.phase0_summary)
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_path, compression="infer")
    dcols = validate_binary(df)
    df = df.sort_values("contest").reset_index(drop=True)

    obs, exp, z, prop = cell_stats(df, dcols)
    total = {"obs": obs, "expected": exp, "z": z, "prop": prop}

    specs = [("Total", None), *[(f"Últimos {w}", w) for w in args.windows]]
    records = []
    for label, w in specs:
        sample = df if w is None else df.tail(min(w, len(df)))
        o, e, zz, pp = cell_stats(sample, dcols)
        records.append({"label": label, "obs": o, "expected": e, "z": zz, "prop": pp})

    # Keep identical scales for observed and expected count heatmaps.
    count_min = min(float(obs.min()), float(exp.min()))
    count_max = max(float(obs.max()), float(exp.max()))
    save_heatmap(obs, "AXION-GEO - Ocupação observada, histórico total", outdir / "01_heatmap_observado_total.png", vmin=count_min, vmax=count_max)
    save_heatmap(exp, "AXION-GEO - Ocupação esperada sob N0", outdir / "02_heatmap_esperado_n0_total.png", fmt=".1f", vmin=count_min, vmax=count_max)
    save_heatmap(z, "AXION-GEO - Resíduo padronizado por célula", outdir / "03_heatmap_residuo_padronizado_total.png", residual=True, fmt=".2f")
    save_small_multiples(records, outdir / "04_small_multiples_observado_janelas.png", residual=False)
    save_small_multiples(records, outdir / "05_small_multiples_residuo_janelas.png", residual=True)

    phase0 = load_phase0_summary(phase0_path)
    macro = select_macro_features(phase0)
    save_macro_barplot(macro, outdir / "06_barplot_macrogeometria_zscores.png")
    save_dashboard(total, macro, records, outdir / "07_dashboard_fase1_resumo.png")

    cell_summary = build_cell_summary(df, dcols, tuple(args.windows))
    cell_summary.to_csv(outdir / "visuals_summary.csv", index=False)

    metadata = {
        "project": "AXION-GEO",
        "phase": 1,
        "status": "exploratory_visual_diagnostics",
        "author": "Jacson Cruz do Nascimento",
        "input_file": input_path.name,
        "input_sha256": sha256_file(input_path),
        "phase0_summary_file": phase0_path.name,
        "phase0_summary_sha256": sha256_file(phase0_path),
        "n_contests": int(len(df)),
        "first_contest": int(df["contest"].min()),
        "last_contest": int(df["contest"].max()),
        "first_date": str(df.iloc[0]["date"]),
        "last_date": str(df.iloc[-1]["date"]),
        "windows": ["total", *[int(w) for w in args.windows]],
        "null_model": "N0_uniform_without_replacement_15_of_25",
        "cell_expected_rate_n0": CELL_P_N0,
        "phase0_multiple_testing": "Benjamini-Hochberg",
        "interpretation": "diagnostic_only_no_predictive_promotion",
    }
    (outdir / "visuals_metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    manifest = """# AXION-GEO - Manifesto da Fase 1 visual

Esta execução produz visualizações exploratórias da grade 5x5. Os resíduos por célula usam N0, seleção uniforme de 15 entre 25. Os z-scores de macrogeometria são lidos do sumário congelado da Fase 0. Nenhuma visualização, isoladamente, autoriza alteração de filtros, pesos ou geração de combinações.

Próximo gate metodológico: N1 com preservação das frequências marginais históricas por dezena.
"""
    (outdir / "visuals_manifest.md").write_text(manifest, encoding="utf-8")
    write_results_readme(outdir, metadata, cell_summary, macro)

    files_to_hash = sorted(p for p in outdir.iterdir() if p.is_file() and p.name != "CHECKSUMS.sha256")
    checksums = "\n".join(f"{sha256_file(p)}  {p.name}" for p in files_to_hash) + "\n"
    (outdir / "CHECKSUMS.sha256").write_text(checksums, encoding="utf-8")

    total_cells = cell_summary[cell_summary["window"] == "total"].copy()
    total_cells["abs_z"] = total_cells["z_n0"].abs()
    print("AXION-GEO Phase 1 completed")
    print(json.dumps(metadata, indent=2, ensure_ascii=False))
    print("\nLargest absolute cell residuals:")
    print(total_cells.sort_values("abs_z", ascending=False).head(10)[["dezena", "observed_rate", "z_n0"]].to_string(index=False))
    print("\nPhase-0 macro features with smallest q:")
    print(phase0.sort_values("q_bh_screen_mc").head(10)[["feature", "z_screen_mc", "q_bh_screen_mc"]].to_string(index=False))


if __name__ == "__main__":
    main()
