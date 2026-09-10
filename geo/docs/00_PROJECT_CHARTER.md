# AXION-GEO - Termo de abertura

**Versão:** 0.1.0  
**Data:** 2026-09-10  
**Autor:** Jacson Cruz do Nascimento

## 1. Problema de pesquisa

Os módulos anteriores do Axion concentram-se em estatísticas combinatórias, frequências, séries temporais e resumos espaciais. A representação do volante da Lotofácil, entretanto, possui uma geometria fixa 5x5. É possível que propriedades da forma ocupada pelas 15 dezenas sejam descritivamente diferentes do que se observa em combinações uniformemente aleatórias.

A pergunta da nova frente é:

> As configurações geométricas observadas no histórico real são distinguíveis das configurações produzidas por um mecanismo Lotofácil uniforme 15/25 e, caso alguma diferença apareça, ela representa morfologia espacial além de simples desequilíbrios marginais de frequência?

## 2. Objetivo

Construir uma camada auditável de representação, mensuração, visualização e teste de geometria espacial para os concursos da Lotofácil.

A Fase 0 não tenta prever dezenas. Ela constrói a infraestrutura, congela as métricas e executa uma triagem inicial contra o modelo nulo uniforme.

## 3. Escopo da Fase 0

Incluído:

- matriz 5x5 binária por concurso;
- 47 atributos espaciais definidos antes da inspeção dos resultados GEO;
- testes unitários de propriedades estruturais;
- modelo nulo N0 uniforme 15/25;
- comparação descritiva das médias observadas e nulas;
- correção Benjamini-Hochberg;
- metadados, seed, hash e checksums dos artefatos.

Fora do escopo:

- escolha de jogos;
- pesos ou filtros no Axion principal;
- mineração manual de símbolos ou desenhos;
- ajuste de motivos depois de observar os resultados;
- alegação de capacidade preditiva.

## 4. Distinção em relação ao estudo de quadrantes

O estudo de quadrantes reduz cada concurso a coordenadas agregadas e classifica regiões do espaço. O AXION-GEO trabalha no nível da ocupação das 25 posições, preservando relações locais e globais de forma. Assim, componentes conectados, perímetro, anisotropia, corridas e simetria não são equivalentes ao quadrante de um concurso.

## 5. Hipótese prioritária

A hipótese prioritária é que os concursos reais são compatíveis com um mecanismo uniforme de seleção de 15 dezenas entre 25. Qualquer aparente regularidade geométrica deve demonstrar o contrário com evidência suficiente.

## 6. Critério de fechamento da Fase 0

A Fase 0 é considerada concluída quando:

1. o mapeamento 5x5 estiver fixado;
2. o catálogo de métricas estiver documentado;
3. os testes unitários passarem;
4. a base for validada;
5. o N0 for executado com seed e quantidade de simulações registradas;
6. os resultados forem preservados sem alteração retrospectiva das métricas;
7. nenhuma regra preditiva for criada a partir da triagem.

Todos os sete itens foram atendidos na execução de 2026-09-10.

## 7. Próxima hipótese a ser pré-registrada

A Fase 1 deverá introduzir um segundo modelo nulo, N1, capaz de preservar as margens históricas por dezena ou, alternativamente, testar permutações da associação entre dezenas e posições do volante. Isso é necessário para separar um verdadeiro efeito de morfologia de um simples excesso ou déficit de determinadas dezenas em posições específicas.
