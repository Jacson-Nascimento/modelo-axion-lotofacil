# AXION-GEO - Protocolo de validação

**Versão:** 0.1.0  
**Data:** 2026-09-10

## 1. Princípio

Visualização é ferramenta de descoberta. Evidência requer comparação formal. O AXION-GEO não promove uma forma, cluster ou score porque ele parece incomum em um gráfico.

## 2. Modelos nulos

### N0, uniforme 15/25

Cada combinação de 15 dezenas entre 25 possui a mesma probabilidade. A Fase 0 utiliza amostragem sem reposição com seed fixa.

Finalidade: testar se a distribuição geométrica observada difere do que a própria combinatória 15/25 produz.

### N1, geometria além das margens, Fase 1

Deverá ser pré-registrado antes de analisar o holdout GEO. Duas implementações candidatas:

1. **margens fixas por edge swaps 2x2**: embaralhar a matriz concurso x dezena preservando 15 seleções por concurso e a frequência histórica total de cada dezena;
2. **permutação de rótulos espaciais**: manter os resultados por dezena, mas permutar a associação entre dezenas e posições 5x5.

O N1 responde a uma pergunta diferente de N0: existe organização espacial adicional depois de controlado o desequilíbrio marginal das dezenas?

A implementação principal recomendada é a de margens fixas, com diagnóstico de mistura da cadeia e replicação por seeds independentes. A permutação de rótulos pode funcionar como teste auxiliar de sensibilidade.

## 3. Gates GEO

`G0 - Integridade`: 25 colunas binárias, 15 seleções por concurso, concursos sem duplicidade.  
`G1 - Reprodutibilidade`: seed, hash da entrada, versão, parâmetros e checksums preservados.  
`G2 - N0`: mesma estatística calculada no real e no nulo uniforme.  
`G3 - Multiplicidade`: FDR por família pré-registrada ou correção mais conservadora quando necessário.  
`G4 - Margens`: candidato precisa sobreviver ao N1 para ser chamado de efeito geométrico.  
`G5 - Estabilidade`: sinal deve persistir em recortes temporais pré-definidos ou validação rolling.  
`G6 - Fora da amostra`: efeito deve sobreviver em concursos não usados para definir a métrica/regra.  
`G7 - Incrementalidade`: informação deve acrescentar algo além de frequências, linhas, colunas e demais métricas já existentes no Axion.  
`G8 - Auditabilidade`: scripts, entradas, saídas e decisões preservados, inclusive resultados negativos.

## 4. Fase 0, teste de triagem

Para cada uma das 47 features:

- calcula-se a média histórica em `N = 3435` concursos;
- gera-se `B = 20.000` combinações N0 independentes;
- calcula-se média e desvio padrão por feature no N0;
- usa-se um z de triagem cuja incerteza inclui a média histórica e a estimação Monte Carlo da média nula;
- calcula-se p bilateral aproximado;
- aplica-se Benjamini-Hochberg aos 47 p-valores.

Essa estatística serve apenas para triagem. Dependência temporal e correlação entre métricas exigem testes mais adequados nas fases seguintes.

## 5. Política contra data snooping

- Não criar motivos como cruz, X, L, moldura ou outros símbolos depois de vê-los repetidos sem antes registrar a definição formal do motivo e sua família de testes.
- Não reduzir a janela temporal até um resultado ficar significativo.
- Não trocar N0, N1, thresholds ou correções após observar o resultado sem registrar a alteração como nova hipótese exploratória.
- Não usar concursos pós-baseline para escolher quais das 47 métricas parecem melhores e depois chamá-los de holdout.
- Resultados negativos permanecem no histórico do projeto.

## 6. Critério para qualquer uso operacional futuro

Uma variável GEO só pode receber peso na geração, exclusão ou ordenação de combinações se ultrapassar, no mínimo, G0 a G7. Antes disso, seu uso é descritivo, de estratificação ou de diversificação experimental, nunca evidência de previsão.
