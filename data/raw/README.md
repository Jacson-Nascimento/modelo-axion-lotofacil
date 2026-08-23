# Dados brutos

**Autor:** Jacson Cruz do Nascimento

Armazene aqui a base historica original usada na execucao do Modelo Axion Lotofacil v1.2.

## Fonte recomendada

- Pagina institucional: https://loterias.caixa.gov.br/Paginas/Lotofacil.aspx
- Endpoint de download de resultados: https://servicebus2.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Lotof%C3%A1cil

Nome recomendado para a base baixada:

```text
lotofacil_historico.xlsx
```

A rotina Python `python/run_all.py` baixa automaticamente o arquivo acima quando nenhuma base compativel estiver presente nesta pasta. O workflow `lotofacil-v12-reproducibility.yml` usa essa rotina.

## Regra de preservacao

O arquivo bruto deve ser preservado sem edicoes manuais. Quando houver nova atualizacao da base, registre a data de obtencao, mantenha o arquivo de proveniencia `SOURCE_CAIXA.md` e gere novo hash SHA-256.
