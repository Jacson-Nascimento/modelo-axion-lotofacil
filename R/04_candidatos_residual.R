# ==========================================================
# 6. GERACAO DE CANDIDATOS
# ==========================================================

gerar_candidatos <- function(n, prob) {
  lista <- vector("list", n)
  for (i in seq_len(n)) {
    lista[[i]] <- sort(sample(1:25, size = 15, replace = FALSE, prob = prob))
  }
  mat <- do.call(rbind, lista)
  colnames(mat) <- sprintf("D%02d", 1:15)
  chave <- apply(mat, 1, paste, collapse = "-")
  mat[!duplicated(chave), , drop = FALSE]
}

cat("\nGerando combinacoes candidatas...\n")
mat_candidatos <- gerar_candidatos(config$n_candidatos, prob_amostragem)
cat("Candidatos unicos gerados:", nrow(mat_candidatos), "\n")

# ==========================================================
# 7. METRICAS DAS COMBINACOES CANDIDATAS
# ==========================================================

calcular_metricas_candidatos <- function(mat) {
  mat <- as.matrix(mat)
  n <- nrow(mat)

  pares <- rowSums(mat %% 2 == 0)
  impares <- 15 - pares
  baixas <- rowSums(mat <= 13)
  altas <- 15 - baixas

  primas_set <- c(2, 3, 5, 7, 11, 13, 17, 19, 23)
  borda_set <- c(1, 2, 3, 4, 5, 6, 10, 11, 15, 16, 20, 21, 22, 23, 24, 25)

  primas <- rowSums(matrix(mat %in% primas_set, nrow = n))
  borda <- rowSums(matrix(mat %in% borda_set, nrow = n))
  centro <- 15 - borda
  soma <- rowSums(mat)
  max_consec <- apply(mat, 1, max_run_consecutivo)
  repetidas_ultimo <- rowSums(matrix(mat %in% ultimo_sorteio, nrow = n))

  board <- t(apply(mat, 1, function(x) {
    linhas <- ceiling(x / 5)
    colunas <- ((x - 1) %% 5) + 1
    tab_linhas <- tabulate(linhas, nbins = 5)
    tab_colunas <- tabulate(colunas, nbins = 5)
    c(
      max_linha = max(tab_linhas),
      max_coluna = max(tab_colunas),
      linhas_cheias = sum(tab_linhas == 5),
      colunas_cheias = sum(tab_colunas == 5)
    )
  }))

  entropia <- apply(mat, 1, function(x) {
    p <- prob_hist[x]
    p <- p / sum(p)
    -sum(p * log2(p))
  })

  kl <- apply(mat, 1, function(x) {
    q <- rep(1 / 15, length(x))
    sum(q * log2(q / prob_hist[x]))
  })

  cand_bin <- matriz_binaria(mat)
  max_overlap_hist <- calcular_max_overlap_historico(cand_bin, hist_overlap)

  esperados <- list(
    pares = 15 * 12 / 25,
    altas = 15 * 12 / 25,
    primas = 15 * 9 / 25,
    borda = 15 * 16 / 25
  )

  score_balance <- 1 - (
    abs(pares - esperados$pares) / 7.5 +
      abs(altas - esperados$altas) / 7.5 +
      abs(primas - esperados$primas) / 9 +
      abs(borda - esperados$borda) / 15
  ) / 4
  score_balance <- clip_01(score_balance)

  popularidade_proxy <-
    scale_01(max_consec) * 0.35 +
    scale_01(board[, "max_linha"] + board[, "max_coluna"]) * 0.25 +
    scale_01(board[, "linhas_cheias"] + board[, "colunas_cheias"]) * 0.20 +
    scale_01(abs(soma - mean(somas_hist)) / stats::sd(somas_hist)) * 0.20

  score_antipop <- 1 - clip_01(popularidade_proxy)
  score_div_hist <- 1 - scale_01(max_overlap_hist)
  score_soma <- 1 - scale_01(abs(soma - mean(somas_hist)))

  score_total <-
    config$score$w_entropia * scale_01(entropia) +
    config$score$w_kl_originalidade * scale_01(kl) +
    config$score$w_balanceamento * score_balance +
    config$score$w_antipopularidade * score_antipop +
    config$score$w_diversidade_historica * score_div_hist +
    config$score$w_estabilidade_soma * score_soma

  tibble::tibble(
    id_candidato = seq_len(n),
    soma = soma,
    pares = pares,
    impares = impares,
    altas = altas,
    baixas = baixas,
    primas = primas,
    borda = borda,
    centro = centro,
    max_consecutivas = max_consec,
    repetidas_ultimo = repetidas_ultimo,
    max_linha = board[, "max_linha"],
    max_coluna = board[, "max_coluna"],
    linhas_cheias = board[, "linhas_cheias"],
    colunas_cheias = board[, "colunas_cheias"],
    entropia = entropia,
    kl_divergence = kl,
    max_overlap_historico = max_overlap_hist,
    score_balanceamento = score_balance,
    score_antipopularidade = score_antipop,
    score_diversidade_historica = score_div_hist,
    score_estabilidade_soma = score_soma,
    score_total = score_total
  )
}

cat("\nCalculando metricas dos candidatos...\n")
metricas <- calcular_metricas_candidatos(mat_candidatos)

# ==========================================================
# 8. FILTROS E ESPACO RESIDUAL
# ==========================================================

filtros_lista <- list(
  "paridade_6_a_9" = metricas$pares >= config$filtros$pares_min & metricas$pares <= config$filtros$pares_max,
  "altas_baixas_6_a_9" = metricas$altas >= config$filtros$altas_min & metricas$altas <= config$filtros$altas_max,
  "soma_faixa_empirica" = metricas$soma >= config$filtros$soma_min & metricas$soma <= config$filtros$soma_max,
  "max_consecutivas" = metricas$max_consecutivas <= config$filtros$max_consecutivas,
  "primas_faixa" = metricas$primas >= config$filtros$primas_min & metricas$primas <= config$filtros$primas_max,
  "borda_faixa" = metricas$borda >= config$filtros$borda_min & metricas$borda <= config$filtros$borda_max,
  "repetidas_ultimo" = metricas$repetidas_ultimo >= config$filtros$repetidas_ultimo_min & metricas$repetidas_ultimo <= config$filtros$repetidas_ultimo_max,
  "similaridade_historica" = metricas$max_overlap_historico <= config$filtros$max_overlap_historico
)

atual <- rep(TRUE, nrow(metricas))
diagnostico_filtros <- purrr::imap_dfr(filtros_lista, function(filtro, nome) {
  antes <- sum(atual)
  atual <<- atual & filtro
  depois <- sum(atual)
  tibble::tibble(
    filtro = nome,
    n_antes = antes,
    n_depois = depois,
    n_eliminados = antes - depois,
    taxa_retencao = ifelse(antes == 0, NA_real_, depois / antes)
  )
})

metricas$filtro_ok <- atual
idx_residual <- which(metricas$filtro_ok)

cat("\nResumo dos filtros:\n")
print(diagnostico_filtros)
cat("\nTamanho do espaco residual:", length(idx_residual), "\n")

readr::write_csv(diagnostico_filtros, file.path(config$pasta_saida, "diagnostico_filtros_v12.csv"))

if (length(idx_residual) == 0) {
  stop(
    "Nenhuma combinacao permaneceu no espaco residual. Revise os filtros no bloco config$filtros.",
    call. = FALSE
  )
}

metricas_residual <- metricas[idx_residual, ] %>%
  dplyr::arrange(dplyr::desc(score_total)) %>%
  dplyr::mutate(rank_residual = dplyr::row_number())

mat_residual <- mat_candidatos[metricas_residual$id_candidato, , drop = FALSE]

# Exporta amostra ranqueada do espaco residual.
n_top <- min(config$n_top_residual_export, nrow(metricas_residual))
top_residual <- dplyr::bind_cols(
  metricas_residual[seq_len(n_top), c("rank_residual", "id_candidato")],
  as_tibble(mat_residual[seq_len(n_top), , drop = FALSE]),
  metricas_residual[seq_len(n_top), setdiff(names(metricas_residual), c("rank_residual", "id_candidato", "filtro_ok"))]
)

readr::write_csv(top_residual, file.path(config$pasta_saida, "top_residual_v12.csv"))
