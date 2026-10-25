"""Frozen historical benchmark. No retrospective result is promoted to betting."""
import argparse
import hashlib
import importlib.metadata
import json
import math
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from .core import load_history, score_predictions, temporal_folds
from .models import predict_fold

PRIMARY_MODELS = ['frequency_long', 'frequency_recent', 'logistic', 'transformer']


def holm(p_values):
    p = np.asarray(p_values, dtype=float)
    order = np.argsort(p)
    adjusted = np.empty(len(p))
    adjusted[order] = np.minimum(1, np.maximum.accumulate(p[order]*(len(p)-np.arange(len(p)))))
    return adjusted


def bootstrap_summary(deltas, replicates=9999, block=25, seed=20261024):
    """Positive delta = improvement. Circular moving-block, centered null.

    This is exploratory inference under temporal stability assumptions, not an
    exact test for an adaptively selected lottery strategy.
    """
    x = np.asarray(deltas, dtype=float)
    if x.ndim != 1 or len(x) == 0 or not np.isfinite(x).all():
        raise ValueError('Invalid paired differences')
    if block < 1 or block > len(x) or replicates < 1:
        raise ValueError('Invalid bootstrap configuration')
    rng = np.random.default_rng(seed)
    blocks = int(math.ceil(len(x)/block))
    means = np.empty(replicates)
    for start in range(0, replicates, 128):
        size = min(128, replicates-start)
        begins = rng.integers(0, len(x), size=(size, blocks))
        indices = (begins[:, :, None]+np.arange(block)[None, None, :]) % len(x)
        indices = indices.reshape(size, -1)[:, :len(x)]
        means[start:start+size] = x[indices].mean(1)
    observed = float(x.mean())
    centered = means-observed
    p = (1+np.sum(centered >= observed-1e-15))/(replicates+1)
    return dict(mean=observed, ci95=np.quantile(means, [0.025, 0.975]).tolist(),
                p_one_sided=float(p), block=block, replicates=replicates)


def prepare_output(path):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=False)
    return path


def code_hashes():
    root = Path(__file__).parent
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.glob('*.py'))}


def run(config, history, output):
    frame, matrix = load_history(history)
    output = prepare_output(output)
    (output/'config.json').write_text(json.dumps(config, indent=2)+'\n')
    folds = temporal_folds(len(matrix), config['outer_start'], config['outer_block'])
    records, fit_metadata = [], []
    for fold, (train_end, stop) in enumerate(folds, 1):
        print(f'Fold {fold}/{len(folds)}: treino até {train_end}, alvos {train_end+1}..{stop}', flush=True)
        probabilities, metadata = predict_fold(matrix, train_end, stop, config)
        metadata['fold'] = fold
        fit_metadata.append(metadata)
        for name, p in probabilities.items():
            scores = score_predictions(p, matrix[train_end:stop], frame.contest.iloc[train_end:stop])
            for i, target in enumerate(range(train_end, stop)):
                row = dict(contest=int(frame.contest.iloc[target]),date=frame.date.iloc[target],
                           fold=fold,model=name,brier=float(scores['brier'][i]),
                           log_loss=float(scores['log_loss'][i]),hits=int(scores['hits'][i]),
                           selected=' '.join(f'{j+1:02}' for j in np.flatnonzero(scores['selected'][i])))
                row.update({f'p{j+1:02}': float(p[i,j]) for j in range(25)})
                records.append(row)
    table = pd.DataFrame(records)
    table.to_csv(output/'predictions.csv.gz', index=False, compression={'method':'gzip','mtime':0})
    fold_scores = table.groupby(['fold','model'])[['brier','log_loss','hits']].mean().reset_index()
    fold_scores.to_csv(output/'fold_scores.csv', index=False)
    baseline = table[table.model=='uniform'].sort_values('contest')
    models = {}
    for name, part in table.groupby('model', sort=False):
        part = part.sort_values('contest')
        models[name] = dict(brier=float(part.brier.mean()),log_loss=float(part.log_loss.mean()),
                            mean_hits=float(part.hits.mean()),ge11=int((part.hits>=11).sum()),
                            ge12=int((part.hits>=12).sum()),ge13=int((part.hits>=13).sum()),
                            ge14=int((part.hits>=14).sum()),ge15=int((part.hits>=15).sum()))
        if name in PRIMARY_MODELS:
            gain = baseline.brier.to_numpy()-part.brier.to_numpy()
            models[name]['brier_gain_vs_uniform'] = bootstrap_summary(
                gain,config['bootstrap_replicates'],min(config['bootstrap_block'],len(gain)),config['bootstrap_seed'])
    adjusted = holm([models[n]['brier_gain_vs_uniform']['p_one_sided'] for n in PRIMARY_MODELS])
    for name, value in zip(PRIMARY_MODELS, adjusted):
        models[name]['brier_gain_vs_uniform']['p_holm'] = float(value)
    ordered = table[table.model=='transformer'].sort_values('contest')
    shuffled = table[table.model=='transformer_shuffled_context'].sort_values('contest')
    sensitivity = bootstrap_summary(shuffled.brier.to_numpy()-ordered.brier.to_numpy(),
                                   config['bootstrap_replicates'],min(config['bootstrap_block'],len(ordered)),
                                   config['bootstrap_seed'])
    summary = dict(experiment=config.get('experiment','test'),evaluation_draws=len(baseline),
                   first_target=int(baseline.contest.min()),last_target=int(baseline.contest.max()),
                   prospective=False,promoted_to_betting=False,models=models,
                   context_order_sensitivity=sensitivity,
                   interpretation='Retrospectiva exploratória em histórico já acessível ao projeto. Nenhuma promoção operacional.')
    (output/'summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False)+'\n')
    (output/'fit_metadata.json').write_text(json.dumps(fit_metadata, indent=2)+'\n')
    try:
        git_commit = subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
        dirty = bool(subprocess.check_output(['git','status','--porcelain'],text=True).strip())
    except (OSError, subprocess.CalledProcessError):
        git_commit, dirty = None, None
    manifest = dict(created_at_utc=datetime.now(timezone.utc).isoformat(),config=config,
                    data_sha256=hashlib.sha256(Path(history).read_bytes()).hexdigest(),
                    code_sha256=code_hashes(),git_commit_at_run=git_commit,git_dirty_at_manifest=dirty,
                    python=platform.python_version(),platform=platform.platform(),
                    libraries={n:importlib.metadata.version(n) for n in ['numpy','scipy','pandas','scikit-learn','torch']},
                    evaluation='historical_exploratory',source_reconciled_with_caixa=False,
                    model_promotion=False)
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    root=Path(__file__).parent
    parser.add_argument('--config',type=Path,default=root/'config.json')
    parser.add_argument('--history',type=Path,default=root/'data/lotofacil_history_checked.csv')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    run(json.loads(args.config.read_text()),args.history,args.output)
