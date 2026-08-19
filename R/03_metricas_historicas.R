# ==========================================================
# 4. METRICAS HISTORICAS DAS DEZENAS
# ==========================================================

hist_bin_completo <- matriz_binaria(matriz_hist)

freq_abs <- tabulate(as.vector(matriz_hist), nbins = 25)
freq_rel <- freq_abs / sum(freq_abs)

ultimo_indice_dezena <- sapply(1:25, function(d) {
  pos <- which(hist_bin_completo[, d] == 1)
  if (length(pos) == 0) return(NA_integer_)
  max(pos)
})

atraso_atual <- nrow(matriz_hist) - ultimo_indice_dezena
atraso_atual[is.na(atraso_atual)] <- nrow(matriz_hist)

atraso_maximo <- sapply(1:25, function(d) {
  pos <- which(hist_bin_completo[, d] == 1)
  gaps <- diff(c(0, pos, nrow(matriz_hist) + 1)) - 1
  max(gaps)
})

stats_dezenas <- tibble::tibble(
  dezena = 1:25,
  frequencia_abs = freq_abs,
  frequencia_rel = freq_rel,
  atraso_atual = atraso_atual,
  atraso_maximo = atraso_maximo,
  peso_freq_norm = scale_01(freq_abs),
  peso_atraso_norm = scale_01(atraso_atual)
)

prob_hist <- stats_dezenas$frequencia_rel + 1e-12
prob_hist <- prob_hist / sum(prob_hist)

pesos_raw <-
  config$pesos_amostragem$frequencia * stats_dezenas$peso_freq_norm +
  config$pesos_amostragem$atraso * stats_dezenas$peso_atraso_norm +
  config$pesos_amostragem$uniforme * rep(1, 25)

prob_amostragem <- pesos_raw / sum(pesos_raw)
stats_dezenas$prob_amostragem <- prob_amostragem

readr::write_csv(stats_dezenas, file.path(config$pasta_saida, "estatisticas_dezenas_v12.csv"))

# ==========================================================
# 5. PARAMETROS EMPIRICOS DOS FILTROS
# ==========================================================

somas_hist <- rowSums(matriz_hist)
if (is.null(config$filtros$soma_min) || is.null(config$filtros$soma_max)) {
  q_soma <- as.numeric(stats::quantile(somas_hist, probs = config$filtros$soma_quantis, na.rm = TRUE))
  config$filtros$soma_min <- floor(q_soma[1])
  config$filtros$soma_max <- ceiling(q_soma[2])
}

ultimo_sorteio <- matriz_hist[nrow(matriz_hist), ]

# Se configurado, reduz historico usado no overlap para as ultimas N linhas.
hist_overlap <- hist_bin_completo
if (!is.null(config$historico_overlap_ultimos) && nrow(hist_bin_completo) > config$historico_overlap_ultimos) {
  idx_ini <- nrow(hist_bin_completo) - config$historico_overlap_ultimos + 1
  hist_overlap <- hist_bin_completo[idx_ini:nrow(hist_bin_completo), , drop = FALSE]
}
