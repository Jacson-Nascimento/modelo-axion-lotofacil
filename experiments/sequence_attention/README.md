# AXION: atenção temporal para o próximo concurso

Autor do projeto: Jacson Cruz do Nascimento.

Experimento independente que compara um Transformer pequeno com uniforme, frequências e regressão logística. A rodada de 24/10/2026 usa 3.812 concursos, com 1.812 alvos de avaliação histórica. Não encontrou vantagem suficiente na métrica primária para promover um modelo a apostas.

- [Relatório completo e figura](results/run_2026-10-24/REPORT.md)
- [Resumo numérico](results/run_2026-10-24/summary.json)
- [Resultados por bloco](results/run_2026-10-24/fold_scores.csv)
- [Todas as previsões e probabilidades](results/run_2026-10-24/predictions.csv.gz)
- [Configuração e proveniência da execução](results/run_2026-10-24/manifest.json)
- [Proveniência dos dados e correção de data](data/SOURCE.json)
- [Checagens oficiais pontuais](data/official_spot_checks.json)
- [Auditoria dos registros prospectivos antigos](data/prospective_audit.json)

## Reproduzir

Na raiz do repositório, usando Python 3.12 e CPU:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r experiments/sequence_attention/requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu
python -m unittest discover -s tests -v
python -m experiments.sequence_attention.run --output experiments/sequence_attention/results/reproducao_local
python -m experiments.sequence_attention.report experiments/sequence_attention/results/reproducao_local
```

O diretório de saída deve ser novo. A execução recusa sobrescrever rodadas existentes. Os arquivos brutos e o derivado conferido já acompanham o repositório. Para reconstruir o derivado, mantenha o existente e execute `derive_checked_history` com outro caminho de saída; `prepare_data.py` também recusa substituir o arquivo presente.

## Limites de interpretação

O histórico já havia sido explorado pelo projeto. A separação temporal evita vazamento operacional no experimento, mas não transforma esses dados em validação prospectiva inédita. As probabilidades são marginais com soma 15; não se deve multiplicá-las para obter a chance de uma combinação. O controle com contextos embaralhados é secundário e não integra os quatro testes primários corrigidos por Holm.

O resultado negativo também faz parte do projeto. Código anterior, manifests antigos e resultados legados foram preservados. A implementação está isolada em uma branch experimental, sem alteração dos pipelines operacionais existentes.

## Commit exato da execução

O conector publica uma nova fotografia dos arquivos. Para preservar os hashes locais usados no manifesto, `execution_source.bundle` acompanha o experimento. O bundle contém o commit de execução `13657aacd7ac96530d8bc0e6abe0c87428a0259f` e depende do commit-base público `0af651dd3b9d6fa171cc53c411f6c0105faf2e32`. Após clonar este repositório, ele pode ser importado sem alterar a branch corrente:

```bash
git fetch experiments/sequence_attention/execution_source.bundle refs/tags/execution-source-2026-10-24:refs/tags/execution-source-2026-10-24
git show execution-source-2026-10-24:experiments/sequence_attention/config.json
```
