# ==========================================================
# 9. SELECAO FINAL COM CONTROLE DE REDUNDANCIA
# ==========================================================

selecionar_jogos_diversos <- function(mat, metricas_rank, n_jogos, max_overlap) {
  bin <- matriz_binaria(mat)
  selecionados <- integer(0)

  for (i in seq_len(nrow(mat))) {
    if (length(selecionados) == 0) {
      selecionados <- c(selecionados, i)
    } else {
      overlaps <- bin[i, , drop = FALSE] %*% t(bin[selecionados, , drop = FALSE])
      if (max(overlaps) <= max_overlap) {
        selecionados <- c(selecionados, i)
      }
    }
    if (length(selecionados) >= n_jogos) break
  }

  selecionados
}

max_overlap_sel <- config$selecao$max_overlap_entre_jogos
idx_sel_local <- selecionar_jogos_diversos(
  mat = mat_residual,
  metricas_rank = metricas_residual,
  n_jogos = config$n_jogos_finais,
  max_overlap = max_overlap_sel
)

# Relaxamento controlado caso o criterio de diversidade seja restritivo demais.
while (length(idx_sel_local) < config$n_jogos_finais && max_overlap_sel < 15) {
  max_overlap_sel <- max_overlap_sel + 1
  idx_sel_local <- selecionar_jogos_diversos(
    mat = mat_residual,
    metricas_rank = metricas_residual,
    n_jogos = config$n_jogos_finais,
    max_overlap = max_overlap_sel
  )
}

mat_final <- mat_residual[idx_sel_local, , drop = FALSE]
metricas_final <- metricas_residual[idx_sel_local, , drop = FALSE]

jogos_final <- dplyr::bind_cols(
  tibble::tibble(jogo = seq_len(nrow(mat_final))),
  as_tibble(mat_final),
  metricas_final %>%
    dplyr::select(
      rank_residual, id_candidato, score_total, entropia, kl_divergence,
      soma, pares, impares, altas, baixas, primas, borda, centro,
      max_consecutivas, repetidas_ultimo, max_overlap_historico,
      score_balanceamento, score_antipopularidade,
      score_diversidade_historica, score_estabilidade_soma
    )
)

readr::write_csv(jogos_final, file.path(config$pasta_saida, "jogos_final_v12.csv"))

cat("\nJogos finais selecionados:", nrow(jogos_final), "\n")
cat("Max overlap entre jogos finais usado:", max_overlap_sel, "\n")
print(jogos_final %>% dplyr::select(jogo, D01:D15, score_total))

# ==========================================================
# 10. VALIDACAO POR SIMULACAO
# ==========================================================

metricas_final_conjunto <- calcular_metricas_conjunto(mat_final, prob_hist) %>%
  dplyr::mutate(tipo = "modelo_v12")

if (isTRUE(config$simulacao$ativar)) {
  cat("\nExecutando simulacao Monte Carlo de referencia...\n")

  sim_lista <- vector("list", config$simulacao$n_sim)
  for (s in seq_len(config$simulacao$n_sim)) {
    mat_sim <- do.call(
      rbind,
      replicate(
        config$n_jogos_finais,
        sort(sample(1:25, 15, replace = FALSE)),
        simplify = FALSE
      )
    )
    sim_lista[[s]] <- calcular_metricas_conjunto(mat_sim, prob_hist) %>%
      dplyr::mutate(simulacao = s, tipo = "aleatorio_uniforme")
  }

  simulacoes <- dplyr::bind_rows(sim_lista)
  readr::write_csv(simulacoes, file.path(config$pasta_saida, "simulacao_monte_carlo_v12.csv"))

  resumo_simulacao <- simulacoes %>%
    dplyr::summarise(
      dplyr::across(
        c(cobertura_dezenas, cobertura_pares, cobertura_trios, entropia_media, soma_media),
        list(
          media = mean,
          p05 = ~ stats::quantile(.x, 0.05),
          p50 = ~ stats::quantile(.x, 0.50),
          p95 = ~ stats::quantile(.x, 0.95)
        ),
        .names = "{.col}_{.fn}"
      )
    )

  readr::write_csv(resumo_simulacao, file.path(config$pasta_saida, "resumo_simulacao_v12.csv"))
} else {
  simulacoes <- NULL
  resumo_simulacao <- NULL
}

readr::write_csv(metricas_final_conjunto, file.path(config$pasta_saida, "metricas_conjunto_final_v12.csv"))

# ==========================================================
# 11. GRAFICOS
# ==========================================================

p_freq <- ggplot2::ggplot(stats_dezenas, ggplot2::aes(x = dezena, y = frequencia_abs)) +
  ggplot2::geom_col() +
  ggplot2::scale_x_continuous(breaks = 1:25) +
  ggplot2::labs(
    title = "Frequencia historica das dezenas - Lotofacil",
    x = "Dezena",
    y = "Frequencia absoluta"
  ) +
  ggplot2::theme_minimal()

ggplot2::ggsave(
  filename = file.path(config$pasta_saida, "grafico_frequencia_dezenas_v12.png"),
  plot = p_freq,
  width = 10,
  height = 6,
  dpi = 150
)

p_score <- ggplot2::ggplot(metricas_residual, ggplot2::aes(x = score_total)) +
  ggplot2::geom_histogram(bins = 40) +
  ggplot2::labs(
    title = "Distribuicao do score total no espaco residual",
    x = "Score total",
    y = "Quantidade de combinacoes"
  ) +
  ggplot2::theme_minimal()

ggplot2::ggsave(
  filename = file.path(config$pasta_saida, "grafico_score_residual_v12.png"),
  plot = p_score,
  width = 10,
  height = 6,
  dpi = 150
)

# ==========================================================
# 12. RELATORIO DE EXECUCAO
# ==========================================================

relatorio_txt <- c(
  "Framework Axion Lotofacil - v1.2",
  "=================================",
  paste("Data/hora da execucao:", format(Sys.time(), "%Y-%m-%d %H:%M:%S")),
  paste("Arquivo de dados:", arquivo_dados),
  paste("Concursos importados:", nrow(matriz_hist)),
  paste("Ultimo concurso considerado:", tail(concurso, 1)),
  paste("Candidatos unicos gerados:", nrow(mat_candidatos)),
  paste("Espaco residual:", length(idx_residual)),
  paste("Jogos finais selecionados:", nrow(jogos_final)),
  paste("Max overlap entre jogos finais:", max_overlap_sel),
  "",
  "Filtros aplicados:",
  paste(capture.output(print(diagnostico_filtros)), collapse = "\n"),
  "",
  "Metricas do conjunto final:",
  paste(capture.output(print(metricas_final_conjunto)), collapse = "\n"),
  "",
  "Arquivos gerados:",
  "- estatisticas_dezenas_v12.csv",
  "- diagnostico_filtros_v12.csv",
  "- top_residual_v12.csv",
  "- jogos_final_v12.csv",
  "- metricas_conjunto_final_v12.csv",
  "- simulacao_monte_carlo_v12.csv, se simulacao ativada",
  "- resumo_simulacao_v12.csv, se simulacao ativada",
  "- grafico_frequencia_dezenas_v12.png",
  "- grafico_score_residual_v12.png",
  "",
  "Nota metodologica:",
  "Este modelo nao aumenta a probabilidade matematica de acerto de uma combinacao especifica.",
  "O objetivo e auditar, eliminar padroes, reduzir redundancia e selecionar combinacoes com criterios rastreaveis."
)

writeLines(relatorio_txt, file.path(config$pasta_saida, "relatorio_execucao_v12.txt"))

cat("\nExecucao concluida. Verifique a pasta:\n", normalizePath(config$pasta_saida), "\n")

# ==========================================================
# FIM
# ==========================================================
