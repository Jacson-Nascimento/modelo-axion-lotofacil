#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modelo Axion Lotofacil v1.2 - execucao operacional em Python.

Autor: Jacson Cruz do Nascimento
Projeto: Modelo Axion Lotofacil
Local: Brasilia, DF, Brasil

O modelo organiza procedimentos de exploracao estatistica e combinatoria.
Nao constitui recomendacao financeira, garantia de premiacao ou demonstracao
 de vantagem preditiva contra sorteios regulares.
"""

from __future__ import annotations

import hashlib
import math
import re
import unicodedata
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
OUTPUT_DIR = ROOT / "saida_axion_lotofacil_v12"
OUTPUTS = ROOT / "outputs"
FIGURES = ROOT / "figures"
CHECKSUMS = ROOT / "checksums"

CAIXA_URL = "https://servicebus2.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Lotof%C3%A1cil"
CAIXA_PAGE = "https://loterias.caixa.gov.br/Paginas/Lotofacil.aspx"

AUTHOR = "Jacson Cruz do Nascimento"
PROJECT = "Modelo Axion Lotofacil"
VERSION = "v1.2"
SEED = 20260427
N_CANDIDATES = 50000
N_FINAL_GAMES = 25
N_TOP_RESIDUAL_EXPORT = 1000
N_MONTE_CARLO = 1000
MAX_OVERLAP_BETWEEN_FINAL_GAMES = 12
MAX_HISTORICAL_DRAWS_FOR_OVERLAP = 1000

PRIMES = {2, 3, 5, 7, 11, 13, 17, 19, 23}
BORDER = {1, 2, 3, 4, 5, 6, 10, 11, 15, 16, 20, 21, 22, 23, 24, 25}
ALL_NUMBERS = np.arange(1, 26)


def ensure_dirs() -> None:
    for path in [DATA_RAW, DATA_PROCESSED, OUTPUT_DIR, OUTPUTS, FIGURES, CHECKSUMS]:
        path.mkdir(parents=True, exist_ok=True)


def normalize_name(value: object) -> str:
    text = str(value).strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def max_run(values: Sequence[int]) -> int:
    ordered = sorted(int(v) for v in values)
    best = 1
    current = 1
    for previous, actual in zip(ordered, ordered[1:]):
        if actual == previous + 1:
            current += 1
            best = max(best, current)
        else:
            current = 1
    return best


def scale_01(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    vmin = np.nanmin(values)
    vmax = np.nanmax(values)
    if not np.isfinite(vmin) or not np.isfinite(vmax) or math.isclose(vmax, vmin):
        return np.zeros_like(values, dtype=float)
    return (values - vmin) / (vmax - vmin)


def shannon_normalized(counts: Sequence[int]) -> float:
    arr = np.asarray(counts, dtype=float)
    total = arr.sum()
    if total <= 0:
        return 0.0
    p = arr[arr > 0] / total
    if len(p) <= 1:
        return 0.0
    return float(-(p * np.log(p)).sum() / math.log(len(arr)))


def combo_to_binary(combo: Sequence[int]) -> np.ndarray:
    out = np.zeros(25, dtype=np.int8)
    out[np.asarray(combo, dtype=int) - 1] = 1
    return out


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_data_if_needed() -> Path:
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    candidates = [
        DATA_RAW / "lotofacil_historico.xlsx",
        DATA_RAW / "Lotofacil.xlsx",
        DATA_RAW / "Lotofácil.xlsx",
        ROOT / "Lotofácil(1) - estatistica_descritiva.xlsx",
        ROOT / "Lotofacil(1) - estatistica_descritiva.xlsx",
        ROOT / "Lotofácil(1).xlsx",
        ROOT / "Lotofacil(1).xlsx",
    ]
    for candidate in candidates:
        if candidate.exists() and candidate.stat().st_size > 0:
            return candidate

    destination = DATA_RAW / "lotofacil_historico.xlsx"
    print("Baixando base historica oficial da Lotofacil - CAIXA")
    print(f"URL: {CAIXA_URL}")
    request = urllib.request.Request(CAIXA_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=120) as response:
        payload = response.read()
    if not payload:
        raise RuntimeError("Download da base historica retornou arquivo vazio.")
    destination.write_bytes(payload)

    source_note = DATA_RAW / "SOURCE_CAIXA.md"
    source_note.write_text(
        "\n".join(
            [
                "# Fonte dos dados - Lotofacil",
                "",
                f"**Projeto:** {PROJECT}",
                f"**Autor:** {AUTHOR}",
                "**Fonte:** Portal Loterias CAIXA",
                f"**Endpoint de download:** {CAIXA_URL}",
                f"**Pagina institucional:** {CAIXA_PAGE}",
                f"**Arquivo gerado:** `{destination.as_posix()}`",
                f"**Data/hora da execucao:** {datetime.now().isoformat(timespec='seconds')}",
                f"**SHA-256:** {sha256_file(destination)}",
                "",
                "O arquivo deve ser tratado como insumo externo. A reproducao dos resultados depende da versao efetivamente baixada e dos hashes gerados apos a execucao.",
            ]
        ),
        encoding="utf-8",
    )
    return destination


def read_excel_best_sheet(path: Path) -> tuple[pd.DataFrame, str]:
    try:
        sheets = pd.read_excel(path, sheet_name=None, engine="openpyxl")
    except Exception as exc:
        raise RuntimeError(f"Nao foi possivel ler a planilha {path}: {exc}") from exc

    best_name = None
    best_df = None
    best_score = -1
    for sheet_name, df in sheets.items():
        norm = [normalize_name(c) for c in df.columns]
        score = sum(bool(re.match(r"^(bola|dezena)_?[0-9]+$", n)) for n in norm)
        numeric_score = 0
        for col in df.columns:
            values = pd.to_numeric(df[col], errors="coerce")
            ok = ((values >= 1) & (values <= 25)).mean(skipna=True)
            if pd.notna(ok) and ok > 0.80:
                numeric_score += 1
        score = max(score, numeric_score)
        if score > best_score:
            best_name = str(sheet_name)
            best_df = df
            best_score = int(score)
    if best_df is None:
        raise RuntimeError("Nenhuma aba valida encontrada na planilha.")
    return best_df, best_name or "sheet1"


def detect_number_columns(df: pd.DataFrame) -> List[str]:
    names = list(df.columns)
    normalized = [normalize_name(c) for c in names]
    detected = [c for c, n in zip(names, normalized) if re.match(r"^(bola|dezena)_?[0-9]+$", n)]
    if len(detected) >= 15:
        def suffix(col: str) -> int:
            found = re.findall(r"[0-9]+", normalize_name(col))
            return int(found[-1]) if found else 999
        return sorted(detected, key=suffix)[:15]

    candidates = []
    for col in names:
        values = pd.to_numeric(df[col], errors="coerce")
        valid_ratio = ((values >= 1) & (values <= 25)).mean(skipna=True)
        if pd.notna(valid_ratio) and valid_ratio > 0.80:
            candidates.append(col)
    if len(candidates) >= 15:
        return candidates[:15]

    raise RuntimeError(f"Nao foi possivel identificar 15 colunas de dezenas. Detectadas: {detected}")


def import_history(path: Path) -> tuple[np.ndarray, pd.DataFrame, str, List[str]]:
    df, sheet_name = read_excel_best_sheet(path)
    cols = detect_number_columns(df)
    matrix_df = df[cols].apply(pd.to_numeric, errors="coerce")
    valid_rows = matrix_df.notna().all(axis=1)
    matrix_df = matrix_df.loc[valid_rows].astype(int)
    matrix = matrix_df.to_numpy(dtype=int)

    invalid = []
    for i, row in enumerate(matrix, start=1):
        if len(set(row.tolist())) != 15 or np.any(row < 1) or np.any(row > 25):
            invalid.append(i)
    if invalid:
        raise RuntimeError(f"Base contem linhas invalidas. Exemplos: {invalid[:10]}")

    matrix = np.sort(matrix, axis=1)
    processed = pd.DataFrame(matrix, columns=[f"Bola{i:02d}" for i in range(1, 16)])
    processed.insert(0, "linha_base", np.arange(1, len(processed) + 1))
    processed.to_csv(DATA_PROCESSED / "lotofacil_historico_normalizado.csv", index=False)
    return matrix, df, sheet_name, cols


def historical_stats(matrix: np.ndarray) -> pd.DataFrame:
    n_draws = matrix.shape[0]
    rows = []
    for number in range(1, 26):
        present = np.any(matrix == number, axis=1)
        positions = np.where(present)[0]
        freq_abs = int(present.sum())
        freq_rel = freq_abs / n_draws if n_draws else 0.0
        atraso_atual = int(n_draws - 1 - positions[-1]) if len(positions) else int(n_draws)
        if len(positions) <= 1:
            atraso_max = atraso_atual
        else:
            gaps = np.diff(positions) - 1
            atraso_max = int(max(gaps.max(initial=0), positions[0], n_draws - 1 - positions[-1]))
        rows.append(
            {
                "dezena": number,
                "freq_abs": freq_abs,
                "freq_rel": freq_rel,
                "atraso_atual": atraso_atual,
                "atraso_maximo": atraso_max,
            }
        )
    stats = pd.DataFrame(rows)
    stats["freq_score"] = scale_01(stats["freq_rel"].to_numpy())
    stats["atraso_score"] = scale_01(stats["atraso_atual"].to_numpy())
    uniform = np.repeat(1 / 25, 25)
    raw = 0.45 * stats["freq_score"].to_numpy() + 0.20 * stats["atraso_score"].to_numpy() + 0.35 * uniform
    stats["peso_amostragem"] = raw / raw.sum()
    stats.to_csv(OUTPUT_DIR / "estatisticas_dezenas_v12.csv", index=False)
    return stats


def generate_candidates(prob: np.ndarray, rng: np.random.Generator) -> List[Tuple[int, ...]]:
    candidates = set()
    attempts = 0
    max_attempts = N_CANDIDATES * 6
    while len(candidates) < N_CANDIDATES and attempts < max_attempts:
        combo = tuple(sorted(rng.choice(ALL_NUMBERS, size=15, replace=False, p=prob).tolist()))
        candidates.add(combo)
        attempts += 1
    return list(candidates)


def build_candidate_metrics(candidates: List[Tuple[int, ...]], matrix: np.ndarray) -> pd.DataFrame:
    hist_reference = matrix[-min(MAX_HISTORICAL_DRAWS_FOR_OVERLAP, matrix.shape[0]) :]
    hist_binary = np.vstack([combo_to_binary(row) for row in hist_reference])
    cand_binary = np.vstack([combo_to_binary(row) for row in candidates])
    max_overlap_hist = cand_binary @ hist_binary.T
    max_overlap_hist = max_overlap_hist.max(axis=1)

    sums_hist = matrix.sum(axis=1)
    q05, q95 = np.quantile(sums_hist, [0.05, 0.95])
    sum_median = float(np.median(sums_hist))
    sum_range = max(float(q95 - q05), 1.0)
    last_draw = set(matrix[-1].tolist())

    records = []
    for idx, combo in enumerate(candidates, start=1):
        s = set(combo)
        row_counts = [sum(1 for x in combo if 1 + 5 * r <= x <= 5 + 5 * r) for r in range(5)]
        pares = sum(1 for x in combo if x % 2 == 0)
        altas = sum(1 for x in combo if x >= 14)
        primas = sum(1 for x in combo if x in PRIMES)
        borda = sum(1 for x in combo if x in BORDER)
        soma = sum(combo)
        repetidas_ultimo = len(s & last_draw)
        max_consecutivas = max_run(combo)
        entropia = shannon_normalized(row_counts)
        balance = 1.0 - np.mean(
            [
                min(abs(pares - 7.5) / 7.5, 1.0),
                min(abs(altas - 7.5) / 7.5, 1.0),
                min(abs(primas - 5.5) / 5.5, 1.0),
                min(abs(borda - 9.5) / 9.5, 1.0),
            ]
        )
        anti_pop = 1.0 - min(max_consecutivas / 15.0, 1.0)
        diversidade_hist = 1.0 - (float(max_overlap_hist[idx - 1]) / 15.0)
        estabilidade_soma = 1.0 - min(abs(soma - sum_median) / sum_range, 1.0)
        score = (
            0.20 * entropia
            + 0.20 * balance
            + 0.15 * anti_pop
            + 0.18 * diversidade_hist
            + 0.15 * estabilidade_soma
            + 0.12 * (1.0 - min(abs(soma - sum_median) / max(sum_median, 1.0), 1.0))
        )
        record = {f"D{i:02d}": combo[i - 1] for i in range(1, 16)}
        record.update(
            {
                "id_candidato": idx,
                "soma": soma,
                "pares": pares,
                "impares": 15 - pares,
                "altas": altas,
                "baixas": 15 - altas,
                "primas": primas,
                "borda": borda,
                "centro": 15 - borda,
                "max_consecutivas": max_consecutivas,
                "repetidas_ultimo": repetidas_ultimo,
                "max_overlap_historico": int(max_overlap_hist[idx - 1]),
                "entropia_linhas": entropia,
                "score_balanceamento": float(balance),
                "score_antipopularidade": float(anti_pop),
                "score_diversidade_historica": float(diversidade_hist),
                "score_estabilidade_soma": float(estabilidade_soma),
                "score_total": float(score),
                "filtro_soma_min": float(q05),
                "filtro_soma_max": float(q95),
            }
        )
        records.append(record)
    return pd.DataFrame(records)


def apply_filters(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    steps = []
    current = df.copy()

    def step(name: str, mask: pd.Series) -> None:
        nonlocal current
        before = len(current)
        current = current.loc[mask].copy()
        steps.append({"filtro": name, "antes": before, "depois": len(current), "eliminados": before - len(current)})

    step("pares_6_9", current["pares"].between(6, 9))
    step("altas_6_9", current["altas"].between(6, 9))
    step("soma_empirica_5_95", current["soma"].between(current["filtro_soma_min"], current["filtro_soma_max"]))
    step("max_consecutivas_ate_5", current["max_consecutivas"] <= 5)
    step("primas_4_7", current["primas"].between(4, 7))
    step("borda_7_12", current["borda"].between(7, 12))
    step("repetidas_ultimo_6_12", current["repetidas_ultimo"].between(6, 12))

    if current.empty:
        current = df.sort_values("score_total", ascending=False).head(max(N_FINAL_GAMES, N_TOP_RESIDUAL_EXPORT)).copy()
        steps.append(
            {
                "filtro": "fallback_top_score_por_residual_vazio",
                "antes": 0,
                "depois": len(current),
                "eliminados": 0,
            }
        )

    current = current.sort_values("score_total", ascending=False).reset_index(drop=True)
    diag = pd.DataFrame(steps)
    diag.to_csv(OUTPUT_DIR / "diagnostico_filtros_v12.csv", index=False)
    current.head(N_TOP_RESIDUAL_EXPORT).to_csv(OUTPUT_DIR / "top_residual_v12.csv", index=False)
    return current, diag


def select_final_games(residual: pd.DataFrame) -> pd.DataFrame:
    selected_rows = []
    selected_sets: List[set[int]] = []
    number_cols = [f"D{i:02d}" for i in range(1, 16)]
    for _, row in residual.iterrows():
        combo = {int(row[col]) for col in number_cols}
        if all(len(combo & previous) <= MAX_OVERLAP_BETWEEN_FINAL_GAMES for previous in selected_sets):
            selected_rows.append(row)
            selected_sets.append(combo)
        if len(selected_rows) >= N_FINAL_GAMES:
            break
    if len(selected_rows) < N_FINAL_GAMES:
        used = {int(row["id_candidato"]) for row in selected_rows}
        for _, row in residual.iterrows():
            if int(row["id_candidato"]) not in used:
                selected_rows.append(row)
            if len(selected_rows) >= N_FINAL_GAMES:
                break
    final = pd.DataFrame(selected_rows).reset_index(drop=True)
    final.insert(0, "jogo", np.arange(1, len(final) + 1))
    final.to_csv(OUTPUT_DIR / "jogos_final_v12.csv", index=False)
    return final


def final_metrics(final: pd.DataFrame) -> pd.DataFrame:
    number_cols = [f"D{i:02d}" for i in range(1, 16)]
    combos = [set(int(row[col]) for col in number_cols) for _, row in final.iterrows()]
    coverage_numbers = len(set.union(*combos)) if combos else 0
    overlaps = []
    for i in range(len(combos)):
        for j in range(i + 1, len(combos)):
            overlaps.append(len(combos[i] & combos[j]))
    metrics = pd.DataFrame(
        [
            {
                "n_jogos": len(final),
                "cobertura_dezenas": coverage_numbers,
                "overlap_medio_entre_jogos": float(np.mean(overlaps)) if overlaps else 0.0,
                "overlap_maximo_entre_jogos": int(np.max(overlaps)) if overlaps else 0,
                "score_medio": float(final["score_total"].mean()) if len(final) else 0.0,
                "soma_media": float(final["soma"].mean()) if len(final) else 0.0,
                "entropia_media_linhas": float(final["entropia_linhas"].mean()) if len(final) else 0.0,
            }
        ]
    )
    metrics.to_csv(OUTPUT_DIR / "metricas_conjunto_final_v12.csv", index=False)
    return metrics


def monte_carlo_reference(rng: np.random.Generator, matrix: np.ndarray) -> pd.DataFrame:
    last_draw = set(matrix[-1].tolist())
    records = []
    for i in range(1, N_MONTE_CARLO + 1):
        combo = tuple(sorted(rng.choice(ALL_NUMBERS, size=15, replace=False).tolist()))
        row_counts = [sum(1 for x in combo if 1 + 5 * r <= x <= 5 + 5 * r) for r in range(5)]
        records.append(
            {
                "simulacao": i,
                "soma": sum(combo),
                "pares": sum(1 for x in combo if x % 2 == 0),
                "altas": sum(1 for x in combo if x >= 14),
                "primas": sum(1 for x in combo if x in PRIMES),
                "borda": sum(1 for x in combo if x in BORDER),
                "max_consecutivas": max_run(combo),
                "repetidas_ultimo": len(set(combo) & last_draw),
                "entropia_linhas": shannon_normalized(row_counts),
            }
        )
    sim = pd.DataFrame(records)
    sim.to_csv(OUTPUT_DIR / "simulacao_monte_carlo_v12.csv", index=False)
    summary = sim.describe().T.reset_index().rename(columns={"index": "metrica"})
    summary.to_csv(OUTPUT_DIR / "resumo_simulacao_v12.csv", index=False)
    return sim


def make_plots(stats: pd.DataFrame, residual: pd.DataFrame) -> None:
    plt.figure(figsize=(10, 5))
    plt.bar(stats["dezena"].astype(str), stats["freq_abs"])
    plt.title("Frequencia historica das dezenas - Lotofacil")
    plt.xlabel("Dezena")
    plt.ylabel("Frequencia absoluta")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "grafico_frequencia_dezenas_v12.png", dpi=160)
    plt.close()

    plt.figure(figsize=(10, 5))
    top = residual.head(min(100, len(residual))).copy()
    plt.plot(np.arange(1, len(top) + 1), top["score_total"].to_numpy())
    plt.title("Score do espaco residual - top combinacoes")
    plt.xlabel("Ranking residual")
    plt.ylabel("Score total")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "grafico_score_residual_v12.png", dpi=160)
    plt.close()


def write_report(
    data_path: Path,
    sheet_name: str,
    cols: List[str],
    matrix: np.ndarray,
    candidates_count: int,
    residual: pd.DataFrame,
    final: pd.DataFrame,
    metrics: pd.DataFrame,
) -> None:
    report = [
        "Relatorio de execucao - Modelo Axion Lotofacil v1.2",
        "",
        f"Autor: {AUTHOR}",
        f"Projeto: {PROJECT}",
        f"Versao: {VERSION}",
        f"Data/hora da execucao: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "Entrada de dados",
        f"- Arquivo: {data_path}",
        f"- Aba: {sheet_name}",
        f"- Colunas de dezenas: {', '.join(map(str, cols))}",
        f"- Concursos validos: {matrix.shape[0]}",
        "",
        "Parametros",
        f"- seed: {SEED}",
        f"- n_candidatos: {N_CANDIDATES}",
        f"- n_jogos_finais: {N_FINAL_GAMES}",
        f"- n_simulacoes_monte_carlo: {N_MONTE_CARLO}",
        "",
        "Resultados",
        f"- Candidatos unicos gerados: {candidates_count}",
        f"- Tamanho do espaco residual: {len(residual)}",
        f"- Jogos finais selecionados: {len(final)}",
        "",
        "Metricas do conjunto final",
        metrics.to_string(index=False),
        "",
        "Limite de interpretacao",
        "O modelo nao deve ser interpretado como mecanismo de previsao de sorteios. As simulacoes servem para avaliar diversidade, redundancia, aderencia estatistica e comportamento dos filtros.",
    ]
    (OUTPUT_DIR / "relatorio_execucao_v12.txt").write_text("\n".join(report), encoding="utf-8")


def mirror_outputs() -> None:
    for file in OUTPUT_DIR.glob("*.csv"):
        (OUTPUTS / file.name).write_bytes(file.read_bytes())
    for file in OUTPUT_DIR.glob("*.txt"):
        (OUTPUTS / file.name).write_bytes(file.read_bytes())
    for file in OUTPUT_DIR.glob("*.png"):
        (FIGURES / file.name).write_bytes(file.read_bytes())

    checksum_lines = []
    for folder in [DATA_RAW, OUTPUTS, FIGURES]:
        for file in sorted(folder.glob("*")):
            if file.is_file():
                checksum_lines.append(f"{sha256_file(file)}  {file.relative_to(ROOT).as_posix()}")
    (CHECKSUMS / "CHECKSUMS.sha256").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    rng = np.random.default_rng(SEED)
    data_path = download_data_if_needed()
    matrix, _raw_df, sheet_name, cols = import_history(data_path)
    stats = historical_stats(matrix)
    candidates = generate_candidates(stats["peso_amostragem"].to_numpy(), rng)
    candidate_metrics = build_candidate_metrics(candidates, matrix)
    residual, _diag = apply_filters(candidate_metrics)
    final = select_final_games(residual)
    metrics = final_metrics(final)
    monte_carlo_reference(rng, matrix)
    make_plots(stats, residual)
    write_report(data_path, sheet_name, cols, matrix, len(candidates), residual, final, metrics)
    mirror_outputs()

    print("Execucao concluida.")
    print(f"Arquivo de entrada: {data_path}")
    print(f"Concursos importados: {matrix.shape[0]}")
    print(f"Candidatos gerados: {len(candidates)}")
    print(f"Espaco residual: {len(residual)}")
    print(f"Jogos finais: {len(final)}")
    print(f"Saidas: {OUTPUT_DIR}")
    print(f"Checksums: {CHECKSUMS / 'CHECKSUMS.sha256'}")


if __name__ == "__main__":
    main()
