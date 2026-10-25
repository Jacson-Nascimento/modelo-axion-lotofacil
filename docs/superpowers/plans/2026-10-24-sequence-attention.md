# AXION Sequence Attention Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** comparar atenção temporal e referências simples sem vazamento de resultados futuros.

**Architecture:** pipeline Python independente com matriz binária, atributos causais, avaliação por blocos temporais e probabilidades de soma 15. Relatório exploratório acompanha os dados por concurso e não promove automaticamente um modelo.

**Tech Stack:** Python 3.12, unittest, NumPy, SciPy, pandas, scikit-learn, PyTorch CPU, matplotlib.

**Spec:** docs/superpowers/specs/2026-10-24-sequence-attention.md

## Global Constraints

- Preservar arquivos anteriores; escrever somente na branch experimental.
- Snapshot fixado em db2d1d49855b31748c9fd3012f9775bb349cc586.
- Desfecho primário Brier; arquitetura, seeds, janelas e inferência definidos na especificação.
- Não usar resultados futuros, não chamar retrospectiva de prospectiva, não promover apostas.

## Review Focus

- Resultado alvo ou futuro não pode entrar nos atributos nem no ajuste.
- Concursos ausentes, dezenas duplicadas e datas inválidas devem interromper a ingestão.
- Probabilidades devem somar 15 sem NaN, inclusive com logits extremos.
- Contexto embaralhado não pode alterar rótulos ou misturar concursos futuros.
- Escrita de resultados deve recusar sobrescrita de uma rodada já existente.

### Task 1: dados e fundamentos

Files: experiments/sequence_attention/core.py, tests/test_core.py, data/SOURCE.json.

Interfaces: load_history(path)->(frame,matrix); causal_features(matrix)->array; project_marginals(logits)->array; temporal_folds(n,start=2000,block=300)->list.

- [x] Escrever e observar testes falharem para integridade, causalidade, projeção e separação temporal.
- [x] Implementar funções e executar python -m unittest discover -s tests -v. Expected: todos os testes deste componente passam.

### Task 2: modelos e avaliação

Files: experiments/sequence_attention/models.py, run.py, tests/test_models.py, tests/test_evaluation.py.

Interfaces: fit_transformer(matrix,train_end,config,seed)->(model,metadata); predict_transformer(model,contexts)->logits; bootstrap_summary(deltas)->dict; run(config)->resultados.

- [x] Escrever testes que falhem para treino reprodutível em dados pequenos, efeito de aprendizagem, imutabilidade do futuro e geração de saídas.
- [x] Implementar modelos fixos e pipeline, com teste integral pequeno. Expected: suíte completa verde.

### Task 3: execução e revisão

Files: config.json, results/run_2026-10-24/*, README.md, requirements.txt.

- [x] Congelar config/proveniência e rodar experimento completo, sem mudar modelos pelos resultados.
- [x] Conferir contagens, métricas e hashes; documentar limitações e auditoria prospectiva.
- [x] Revisão independente do código e método; corrigir falhas materiais com teste de regressão.
- [x] Executar suíte completa, publicar commit aditivo e PR em rascunho; verificar leitura do GitHub.
