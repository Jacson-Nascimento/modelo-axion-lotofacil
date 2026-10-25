# AXION: previsão temporal com atenção

Autorização: em 24/10/2026 o autor autorizou a execução e a escolha técnica. A implementação ocorre em branch experimental, preservando arquivos anteriores.

## Objetivo e arquitetura

Testar se um Transformer pequeno melhora probabilidades marginais para o próximo conjunto de 15 dezenas, comparado com uniforme, frequência longa, frequência recente e regressão logística regularizada. Não assumir que existe sinal. Usar Python, NumPy, SciPy, scikit-learn e PyTorch CPU, com código legível e testes unittest.

## Protocolo fixado antes da execução desta rodada

- Snapshot: histórico do repositório original, commit db2d1d49855b31748c9fd3012f9775bb349cc586, concursos 1 a 3812. Trata-se de fonte secundária do projeto, sem nova reconciliação integral com a CAIXA.
- Todo o histórico é exploratório e já esteve disponível ao projeto. Nenhum trecho é denominado teste prospectivo inédito.
- Avaliação expanding-window dos alvos 2001 a 3812, blocos de até 300 concursos. O treino de cada bloco termina antes do primeiro alvo. Dentro de cada bloco, atributos podem usar resultados anteriores já observados, nunca o alvo ou resultados futuros.
- Modelos fixos: uniforme 0,6; frequência longa com prior 100; frequência dos últimos 250 concursos com prior 100; regressão logística C=0,01 com atributos causais de frequência em 5/25/100/500 concursos e resultado anterior; Transformer com contexto 32, dimensão 16, duas cabeças, uma camada, feedforward 32 e dropout 0,1, média de três seeds 17/43/97.
- Transformer: AdamW lr=0,001, weight_decay=0,01; até 30 épocas, paciência 5, lote 128. As últimas 256 observações do treino servem apenas à parada antecipada. Não procurar arquitetura alternativa após ver os resultados externos.
- Todas as probabilidades são estritamente interiores e ajustadas por intercepto logístico para somar 15. Não se afirma que as margens especificam uma distribuição conjunta.
- Desfecho primário: Brier marginal médio por concurso, comparado com uniforme. Log-loss marginal e acertos do top-15 são secundários. Empates no top-15 usam ranking pseudoaleatório determinístico por concurso, idêntico para todos os modelos.
- Inferência exploratória: diferenças pareadas por concurso, bootstrap circular em blocos de 25, 9999 réplicas, seed 20261024; p unilateral centrado e Holm nos quatro concorrentes. Não interpretar p como validação confirmatória depois das explorações históricas. Reportar dependência da hipótese de estabilidade temporal do bootstrap.
- Preservar previsões de todos os modelos, métricas por bloco, seeds, épocas, hashes dos dados/código, versões de bibliotecas e configuração completa. Não gerar apostas como se houvesse vantagem comprovada.
- Acrescentar verificação de sensibilidade com contextos embaralhados no Transformer, sem ajuste de parâmetros, explicitamente secundária.
- Registro prospectivo antigo: documentar o resumo com zero concursos avaliados e os commits de manifests 3780 e 3813. Timestamp de commit não comprova, sozinho, hora de publicação nem antecedência ao sorteio.
- Decisão operacional desta rodada: nenhum modelo promovido a regra de apostas; resultado histórico serve para decidir pesquisa posterior.

## Alternativas e decisão

Usar uma LLM pronta não oferece controle de contaminação e desperdiça a representação numérica. Aumentar o modelo eleva sobreajuste num histórico pequeno. Escolha técnica do implementador: comparar um Transformer pequeno com baselines fortes, dentro do motor AXION-P já previsto no Documento Mestre 2.0.

## Entregáveis

Código independente em experiments/sequence_attention, snapshot e proveniência, testes de integridade/causalidade/reprodutibilidade, resultados completos, relatório em português e figura. Publicar a proposta numa branch e abrir PR em rascunho, sem merge.
