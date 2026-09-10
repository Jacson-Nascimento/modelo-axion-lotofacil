# AXION-GEO - Nota de reconstrução da matriz congelada

Data: 2026-09-10  
Autor: Jacson Cruz do Nascimento

Durante a primeira execução da Fase 1 no GitHub Actions foi identificado um problema técnico nos shards comprimidos usados para transportar a matriz binária congelada da Fase 0.

A reconstrução bruta apresentou 3436 linhas, com duplicidade dos concursos 1030 e 1031 e ausência do concurso 687. As duas ocorrências duplicadas de cada concurso foram verificadas como idênticas. O concurso 687 foi restaurado a partir da matriz canônica congelada e preservado explicitamente em `geo/data/repair/contest_0687.csv`.

O workflow passou a realizar uma reconstrução canônica controlada: valida o padrão conhecido de duplicidades e ausência, elimina apenas duplicidades idênticas, acrescenta a linha 687, ordena os concursos de 1 a 3435 e regrava o CSV com terminador CRLF.

A reconstrução final contém 3435 concursos, 25 colunas binárias, exatamente 15 células selecionadas por concurso e SHA-256:

`1b914b6ce9c566c12352d92ba739177ab741a587eaf1be4f64e5de1597768166`

Esse hash é idêntico ao da matriz canônica congelada utilizada na Fase 0. Portanto, a correção afeta apenas o mecanismo de transporte/reconstrução no repositório, não altera os dados analíticos nem os resultados da Fase 0.
