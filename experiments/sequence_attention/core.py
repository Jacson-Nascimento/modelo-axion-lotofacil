"""Data integrity, causal representations and proper marginal scores."""
import io
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import expit


def load_history(path):
    frame = pd.read_csv(path)
    required = ['contest', 'date'] + [f'n{i}' for i in range(1, 16)]
    if list(frame.columns) != required or frame.empty:
        raise ValueError('Unexpected history schema or empty history')
    numbers = frame[required[2:]].to_numpy(dtype=float)
    contests = frame.contest.to_numpy(dtype=float)
    if not np.isfinite(numbers).all() or not np.isfinite(contests).all():
        raise ValueError('Non-finite history values')
    if (numbers != np.floor(numbers)).any() or (contests != np.floor(contests)).any():
        raise ValueError('Non-integer lottery values')
    if contests[0] != 1 or (np.diff(contests) != 1).any():
        raise ValueError('History must start at 1 and be consecutive')
    if (numbers < 1).any() or (numbers > 25).any():
        raise ValueError('Numbers out of range')
    if (np.diff(np.sort(numbers, axis=1), axis=1) == 0).any():
        raise ValueError('Repeated number in a draw')
    dates = pd.to_datetime(frame.date, format='%Y-%m-%d', errors='raise')
    if dates.isna().any() or (dates.diff().iloc[1:] < pd.Timedelta(0)).any():
        raise ValueError('Dates must not go backwards; contest order is authoritative')
    matrix = np.zeros((len(frame), 25), dtype=np.float64)
    matrix[np.arange(len(frame))[:, None], numbers.astype(int)-1] = 1
    return frame, matrix


def derive_checked_history(raw, official_checks, output):
    """Create a new date-reconciled snapshot, never edit numbers or raw bytes."""
    output = Path(output)
    if output.exists():
        raise FileExistsError(output)
    frame = pd.read_csv(raw)
    corrections = []
    for check in official_checks:
        contest = check['contest']
        rows = frame.index[frame.contest == contest]
        if len(rows) != 1 or check['provider_contest'] != contest:
            raise ValueError('Official check does not identify exactly one contest')
        expected_url = f'https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil/{contest}'
        if check['source_url'] != expected_url:
            raise ValueError('Unexpected official source URL')
        index = rows[0]
        existing = sorted(int(frame.loc[index, f'n{i}']) for i in range(1, 16))
        if existing != sorted(check['numbers']):
            raise ValueError('Numbers differ from official check; manual reconciliation needed')
        old = frame.loc[index, 'date']
        if old != check['official_date']:
            frame.loc[index, 'date'] = check['official_date']
            corrections.append(dict(contest=int(contest),old_date=old,
                                    new_date=check['official_date'],source_url=expected_url))
    csv = frame.to_csv(index=False)
    load_history(io.StringIO(csv))
    with output.open('x') as stream:
        stream.write(csv)
    return corrections


def causal_features(matrix):
    """Row t is a prediction input made exclusively from rows [0, t)."""
    matrix = np.asarray(matrix, dtype=float)
    cumulative = np.vstack([np.zeros((1, 25)), np.cumsum(matrix, axis=0)])
    target = np.arange(len(matrix)+1)
    pieces = []
    for window in (5, 25, 100, 500):
        start = np.maximum(0, target-window)
        count = target-start
        freq = (cumulative[target]-cumulative[start])/np.maximum(count[:, None], 1)
        freq[count == 0] = 0.6
        pieces.append(freq)
    pieces.append(np.vstack([np.full((1, 25), 0.6), matrix]))
    return np.concatenate(pieces, axis=1)


def project_marginals(logits):
    """Find a shared logit intercept so each 25-vector sums to exactly 15.

    These are marginal probabilities, not independent Bernoulli draws.
    Extreme logits are bounded for finite numerical resolution.
    """
    x = np.asarray(logits, dtype=np.float64)
    if x.ndim != 2 or x.shape[1] != 25 or not np.isfinite(x).all():
        raise ValueError('Expected finite [samples,25] logits')
    x = np.clip(x, -30, 30)
    lo, hi = np.full((len(x), 1), -80.), np.full((len(x), 1), 80.)
    for _ in range(70):
        mid = (lo+hi)/2
        sums = expit(x+mid).sum(1, keepdims=True)
        lo = np.where(sums < 15, mid, lo)
        hi = np.where(sums >= 15, mid, hi)
    return np.clip(expit(x+(lo+hi)/2), 1e-12, 1-1e-12)


def temporal_folds(n, start=2000, block=300):
    if block <= 0 or start <= 0 or start >= n:
        raise ValueError('Invalid temporal split')
    return [(t, min(t+block, n)) for t in range(start, n, block)]


def contexts(matrix, targets, length):
    targets = np.asarray(targets, dtype=int)
    if length < 1 or (targets < length).any() or (targets > len(matrix)).any():
        raise ValueError('Insufficient past context')
    return np.asarray(matrix)[targets[:, None]+np.arange(-length, 0)[None, :]]


def frequency_logits(matrix, targets, window=None, prior=100.):
    cumulative = np.vstack([np.zeros((1, 25)), np.cumsum(matrix, axis=0)])
    t = np.asarray(targets, dtype=int)
    start = np.zeros_like(t) if window is None else np.maximum(0, t-window)
    p = (cumulative[t]-cumulative[start]+prior*0.6)/(t-start+prior)[:, None]
    p = np.clip(p, 1e-12, 1-1e-12)
    return np.log(p/(1-p))


def score_predictions(probabilities, actual, contests):
    p, actual = np.asarray(probabilities), np.asarray(actual)
    if p.shape != actual.shape or p.ndim != 2 or p.shape[1] != 25:
        raise ValueError('Invalid score shapes')
    if not np.isfinite(p).all() or ((p <= 0) | (p >= 1)).any():
        raise ValueError('Invalid probabilities')
    if not np.allclose(p.sum(1), 15, atol=1e-8):
        raise ValueError('Marginals must sum to 15')
    selected = np.zeros_like(actual, dtype=int)
    for i, contest in enumerate(contests):
        tie = np.random.default_rng(20261024+int(contest)).permutation(25)
        order = np.lexsort((tie, -p[i]))
        selected[i, order[:15]] = 1
    return {
        'brier': np.mean((p-actual)**2, axis=1),
        'log_loss': -np.mean(actual*np.log(p)+(1-actual)*np.log1p(-p), axis=1),
        'hits': np.sum(selected*actual, axis=1).astype(int),
        'selected': selected,
    }
