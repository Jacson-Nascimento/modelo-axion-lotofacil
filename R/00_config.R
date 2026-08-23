# ==========================================================
# Framework Axion Lotofacil - v1.2
# Autor: Jacson Cruz do Nascimento
# Data-base da versao: 27/04/2026
# Objetivo:
#   Transformar a analise exploratoria da Lotofacil em um motor operacional
#   de eliminacao, espaco residual, score multicriterio, selecao diversificada
#   de jogos e validacao por simulacao.
#
# Observacao metodologica:
#   Este script nao promete previsao de sorteios. Sorteios regulares sao
#   eventos aleatorios. O objetivo e selecionar combinacoes com criterios
#   auditaveis de diversidade, aderencia estatistica e baixa obviedade.
# ==========================================================

options(stringsAsFactors = FALSE)

# ==========================================================
# 0. PARAMETROS GERAIS
# ==========================================================

config <- list(
  instalar_pacotes = FALSE,

  # Se NULL, o script tentara localizar automaticamente a base no diretorio atual.
  # Exemplo Windows:
  # arquivo_dados = "C:/Users/Nascimento/Desktop/Projeto_Loterias_2025/Lotofacil(1).xlsx"
  arquivo_dados = NULL,

  pasta_saida = "saida_axion_lotofacil_v12",
  seed = 20260427,

  # Quantidade de combinacoes candidatas aleatorias ou ponderadas a serem geradas.
  # A Lotofacil possui choose(25, 15) = 3.268.760 combinacoes possiveis.
  # Gerar todo o espaco e possivel, mas pode ser mais lento. O padrao abaixo e operacional.
  n_candidatos = 50000,

  # Quantidade final de jogos selecionados.
  n_jogos_finais = 25,

  # Quantidade de combinacoes residuais mais bem ranqueadas a exportar.
  n_top_residual_export = 1000,

  # Quantidade de concursos historicos usados para medir similaridade.
  # NULL usa todo o historico. Para bases grandes, 1000 costuma ser suficiente.
  historico_overlap_ultimos = 1000,

  # Pesos de amostragem das dezenas na geracao dos candidatos.
  # A soma nao precisa dar 1, pois sera normalizada internamente.
  pesos_amostragem = list(
    frequencia = 0.45,
    atraso = 0.20,
    uniforme = 0.35
  ),

  filtros = list(
    pares_min = 6,
    pares_max = 9,
    altas_min = 6,
    altas_max = 9,

    # Se soma_min e soma_max forem NULL, o script usa os quantis historicos abaixo.
    soma_min = NULL,
    soma_max = NULL,
    soma_quantis = c(0.05, 0.95),

    max_consecutivas = 5,
    primas_min = 4,
    primas_max = 7,
    borda_min = 7,
    borda_max = 12,

    # Repeticoes em relacao ao ultimo sorteio historico.
    repetidas_ultimo_min = 6,
    repetidas_ultimo_max = 12,

    # Evita jogo identico ou quase identico ao historico.
    max_overlap_historico = 14
  ),

  score = list(
    w_entropia = 0.20,
    w_kl_originalidade = 0.12,
    w_balanceamento = 0.20,
    w_antipopularidade = 0.15,
    w_diversidade_historica = 0.18,
    w_estabilidade_soma = 0.15
  ),

  selecao = list(
    # Controle de redundancia entre jogos finais.
    # Quanto menor, mais diverso. Se ficar restritivo demais, o script relaxa automaticamente.
    max_overlap_entre_jogos = 12
  ),

  simulacao = list(
    ativar = TRUE,
    n_sim = 1000
  )
)

set.seed(config$seed)
