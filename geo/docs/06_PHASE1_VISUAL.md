# AXION-GEO - Fase 1 Visual

**Versão:** 0.2.0  
**Autor:** Jacson Cruz do Nascimento  
**Status:** exploratório, sem uso preditivo

## 1. Objetivo

A Fase 1 transforma a matriz binária congelada do AXION-GEO em um conjunto de visualizações comparáveis ao modelo nulo N0. A finalidade é localizar estruturas espaciais aparentes, verificar sua estabilidade em diferentes janelas temporais e separar concentração marginal de hipóteses morfológicas que mereçam teste posterior.

## 2. Base

A execução utiliza `geo/data/binary_matrix.csv.gz`, equivalente à matriz binária da Fase 0, com concursos 1 a 3435. Cada concurso contém 25 indicadores `d01` a `d25`, organizados no volante 5x5 em ordem row-major, com exatamente 15 células ocupadas.

## 3. Referência nula

Para cada célula do volante, sob seleção uniforme de 15 entre 25, a probabilidade marginal é 0,60. Para uma janela com `n` concursos:

- frequência esperada: `n x 0,60`;
- desvio padrão: `sqrt(n x 0,60 x 0,40)`;
- resíduo padronizado: `(observado - esperado) / desvio padrão`.

Esse z por célula é diagnóstico. A Fase 1 não executa correção de 25 testes para promover células individualmente, porque a camada é visual e exploratória. Qualquer hipótese derivada daqui deverá ser pré-registrada e testada em etapa própria.

## 4. Janelas

São apresentadas quatro visões:

1. histórico total;
2. últimos 1000 concursos;
3. últimos 500 concursos;
4. últimos 250 concursos.

A comparação serve para distinguir efeitos persistentes de concentrações restritas a períodos específicos.

## 5. Produtos

A execução automatizada gera:

- heatmap observado total;
- heatmap esperado sob N0;
- heatmap de resíduos padronizados;
- small multiples das frequências relativas por janela;
- small multiples dos resíduos por janela;
- painel de macrogeometria baseado nos z-scores já calculados na Fase 0;
- dashboard consolidado;
- tabela de resumo por célula;
- metadados, manifesto e checksums;
- README com os resultados incorporados em Markdown.

## 6. Governança

O workflow `.github/workflows/axion-geo-visual.yml` executa testes unitários antes da geração visual, usa a base congelada, produz os artefatos, apresenta síntese no GitHub Actions Job Summary e grava os arquivos em `geo/outputs/visuals/`.

A geração automática não altera filtros, pesos ou estratégias de seleção do Axion. O compromisso metodológico permanece o mesmo: padrão visual não é evidência preditiva.

## 7. Gate seguinte

A próxima etapa inferencial é o N1, com preservação das frequências marginais históricas por dezena. O objetivo será perguntar se a estrutura visual permanece depois de controlar a heterogeneidade marginal que já apareceu em análises anteriores do Axion.

Somente efeitos que permaneçam relevantes após N1, estabilidade temporal, controle de multiplicidade e validação fora da amostra poderão ser candidatos a investigação operacional.
