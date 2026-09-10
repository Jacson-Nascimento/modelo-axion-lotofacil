# AXION-GEO - Log de decisões

## 2026-09-10 - D001 - Criar AXION-GEO como braço separado

**Decisão:** aprofundar a geometria do volante 5x5 sem alterar o núcleo preditivo do Axion.  
**Motivo:** preservar rastreabilidade e evitar confundir análise espacial exploratória com regras já validadas ou rejeitadas em outros módulos.

## 2026-09-10 - D002 - Congelar primeiro métricas, depois visualizar

**Decisão:** a primeira entrega é representação, features, testes e nulo.  
**Motivo:** reduzir risco de definir métricas depois de reconhecer padrões visualmente atraentes.

## 2026-09-10 - D003 - Catálogo Fase 0 com 47 métricas

**Decisão:** usar oito famílias, ocupação, adjacência, conectividade, momentos, forma, anéis, corridas e simetrias.  
**Observação:** existem redundâncias determinísticas, mantidas para interpretação. A inferência futura deverá usar famílias não redundantes pré-registradas.

## 2026-09-10 - D004 - N0 uniforme 15/25

**Decisão:** Fase 0 com `B=20.000`, seed `20260910`.  
**Motivo:** formar referência combinatória explícita e reproduzível.

## 2026-09-10 - D005 - Resultado da Fase 0 não promove feature

**Decisão:** nenhuma variável é integrada ao Axion principal.  
**Evidência:** nenhum dos 47 testes de média alcançou `q_BH < 0,05`. Menor `q` aproximadamente 0,0601.

## 2026-09-10 - D006 - Tratar centroid_x e col_5 como uma hipótese correlata

**Decisão:** não contar os dois menores q-valores como sinais independentes.  
**Motivo:** ambos refletem deslocamento horizontal/marginal e podem ser consequência das frequências das dezenas posicionadas no lado direito do volante.

## 2026-09-10 - D007 - Criar N1 na Fase 1

**Decisão:** antes de interpretar desvio como morfologia, testar um nulo que preserve margens por dezena.  
**Implementação preferida:** randomização com margens fixas por edge swaps 2x2, com diagnóstico de mistura.  
**Teste auxiliar:** permutação da associação entre dezenas e posições 5x5.

## 2026-09-10 - D008 - Concursos posteriores ao 3435

**Decisão:** não usar concursos posteriores ao baseline para ajustar o catálogo GEO.  
**Ressalva:** outros braços do Axion já realizaram análises espaciais e prospectivas em períodos posteriores. Portanto, esses concursos não serão descritos como globalmente virgens. A alegação será restrita: não foram usados para ajustar o novo catálogo GEO da Fase 0.
