"""Small, fixed-capacity predictors. Every fit has an explicit past boundary."""
import copy
import hashlib
import io

import numpy as np
import torch
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from torch import nn

from .core import causal_features, contexts, frequency_logits, project_marginals


class TinyTransformer(nn.Module):
    def __init__(self, config):
        super().__init__()
        d = config['d_model']
        self.input = nn.Linear(25, d)
        self.position = nn.Parameter(torch.randn(config['context'], d)*0.01)
        layer = nn.TransformerEncoderLayer(
            d, config['heads'], config['feedforward'], config['dropout'],
            activation='gelu', batch_first=True, norm_first=True)
        self.encoder = nn.TransformerEncoder(layer, config['layers'], enable_nested_tensor=False)
        self.output = nn.Linear(d, 25)
        nn.init.zeros_(self.output.weight)
        nn.init.constant_(self.output.bias, np.log(1.5))

    def forward(self, x):
        # All tokens are strictly before the target, so bidirectional attention
        # inside this historical context does not expose the next draw.
        hidden = self.input(x-0.6)+self.position
        return self.output(self.encoder(hidden)[:, -1])


def predict_transformer(model, inputs):
    model.eval()
    with torch.no_grad():
        batches = [model(torch.as_tensor(x, dtype=torch.float32)).numpy()
                   for x in np.array_split(inputs, max(1, int(np.ceil(len(inputs)/256))))]
    return np.concatenate(batches)


def fit_transformer(matrix, train_end, config, seed):
    torch.set_num_threads(config['torch_threads'])
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(seed)
    cut = train_end-config['validation_size']
    if cut <= config['context'] or train_end > len(matrix):
        raise ValueError('Insufficient training history')
    train_targets = np.arange(config['context'], cut)
    val_targets = np.arange(cut, train_end)
    x = torch.as_tensor(contexts(matrix, train_targets, config['context']), dtype=torch.float32)
    y = torch.as_tensor(matrix[train_targets], dtype=torch.float32)
    vx = torch.as_tensor(contexts(matrix, val_targets, config['context']), dtype=torch.float32)
    vy = torch.as_tensor(matrix[val_targets], dtype=torch.float32)
    model = TinyTransformer(config)
    optimizer = torch.optim.AdamW(model.parameters(), lr=config['learning_rate'],
                                 weight_decay=config['weight_decay'])
    loss_fn = nn.BCEWithLogitsLoss()
    best, best_epoch, stale = float('inf'), 0, 0
    best_state = copy.deepcopy(model.state_dict())
    losses = []
    for epoch in range(1, config['epochs']+1):
        model.train()
        order = torch.randperm(len(x))
        for batch in order.split(config['batch_size']):
            optimizer.zero_grad()
            loss = loss_fn(model(x[batch]), y[batch])
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.)
            optimizer.step()
        model.eval()
        with torch.no_grad():
            val_loss = loss_fn(model(vx), vy).item()
        losses.append(val_loss)
        if val_loss < best-1e-7:
            best, best_epoch, stale = val_loss, epoch, 0
            best_state = copy.deepcopy(model.state_dict())
        else:
            stale += 1
            if stale >= config['patience']:
                break
    model.load_state_dict(best_state)
    model.eval()
    digest = hashlib.sha256()
    for key, value in model.state_dict().items():
        digest.update(key.encode())
        digest.update(value.detach().numpy().tobytes())
    return model, dict(seed=seed, train_end_exclusive=train_end,
                       max_training_target_index=int(train_targets[-1]),
                       max_validation_target_index=int(val_targets[-1]),
                       best_epoch=best_epoch, epochs_ran=len(losses),
                       validation_losses=losses, best_validation_loss=best,
                       parameters=sum(p.numel() for p in model.parameters()),
                       weights_sha256=digest.hexdigest())


def predict_fold(matrix, train_end, stop, config):
    targets = np.arange(train_end, stop)
    if stop > len(matrix) or train_end >= stop:
        raise ValueError('Invalid test interval')
    result = {'uniform': np.full((len(targets), 25), 0.6)}
    for name, window in [('frequency_long', None), ('frequency_recent', config['recent_window'])]:
        result[name] = project_marginals(frequency_logits(
            matrix, targets, window, config['frequency_prior']))
    features = causal_features(matrix)
    train_targets = np.arange(config['context'], train_end)
    scaler = StandardScaler().fit(features[train_targets])
    tx, testx = scaler.transform(features[train_targets]), scaler.transform(features[targets])
    logits = np.empty((len(targets), 25))
    for number in range(25):
        target = matrix[train_targets, number]
        if len(np.unique(target)) == 1:
            p = (target.sum()+60)/(len(target)+100)
            logits[:, number] = np.log(p/(1-p))
        else:
            classifier = LogisticRegression(C=config['logistic_C'], max_iter=1000,
                                            solver='lbfgs', random_state=0)
            classifier.fit(tx, target)
            logits[:, number] = classifier.decision_function(testx)
    result['logistic'] = project_marginals(logits)
    test_context = contexts(matrix, targets, config['context'])
    shuffled = test_context.copy()
    for i, target in enumerate(targets):
        order = np.random.default_rng(config['shuffle_seed']+int(target)).permutation(config['context'])
        shuffled[i] = shuffled[i, order]
    predictions, placebo_predictions, metadata = [], [], []
    for seed in config['seeds']:
        model, meta = fit_transformer(matrix, train_end, config, seed)
        predictions.append(project_marginals(predict_transformer(model, test_context)))
        placebo_predictions.append(project_marginals(predict_transformer(model, shuffled)))
        metadata.append(meta)
    result['transformer'] = np.mean(predictions, axis=0)
    result['transformer_shuffled_context'] = np.mean(placebo_predictions, axis=0)
    return result, dict(train_end_exclusive=train_end, test_end_exclusive=stop,
                       transformer_fits=metadata)
