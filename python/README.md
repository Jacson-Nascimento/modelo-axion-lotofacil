# Execucao Python - Modelo Axion Lotofacil v1.2

**Autor:** Jacson Cruz do Nascimento

Esta pasta contem a versao operacional em Python do Modelo Axion Lotofacil v1.2.

## Papel da versao Python

A versao Python e a rotina principal para execucao no GitHub Actions. Ela executa o ciclo completo:

1. baixar a base historica oficial da Lotofacil, quando ausente;
2. validar a estrutura dos dados;
3. calcular metricas historicas das dezenas;
4. gerar combinacoes candidatas;
5. aplicar filtros combinatorios;
6. formar e ranquear o espaco residual;
7. selecionar a carteira final;
8. gerar simulacao Monte Carlo de referencia;
9. exportar CSVs, graficos, relatorio e checksums.

## Comando

A partir do diretorio `lotofacil_axion`:

```bash
python python/run_all.py
```

## Observacao sobre a versao R

Os scripts R permanecem preservados no repositorio como referencia metodologica e historica. A execucao automatizada do GitHub Actions passa a usar Python como rotina principal.
