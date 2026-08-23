# ==========================================================
# Modelo Axion Lotofacil - v1.2
# Autor: Jacson Cruz do Nascimento
# Projeto: Modelo Axion Lotofacil
# Local: Brasilia, DF, Brasil
# Data da versao operacional: 2026-08-19
# ==========================================================

options(stringsAsFactors = FALSE)

config <- list(
  instalar_pacotes = FALSE,
  arquivo_dados = NULL,
  pasta_saida = "saida_axion_lotofacil_v12",
  seed = 20260427,
  n_candidatos = 50000,
  n_jogos_finais = 25,
  n_top_residual_export = 1000,
  historico_overlap_ultimos = 1000,
  pesos_amostragem = list(frequencia = 0.45, atraso = 0.20, uniforme = 0.35),
  filtros = list(
    pares_min = 6, pares_max = 9,
    altas_min = 6, altas_max = 9,
    soma_min = NULL, soma_max = NULL, soma_quantis = c(0.05, 0.95),
    max_consecutivas = 5,
    primas_min = 4, primas_max = 7,
    borda_min = 7, borda_max = 12,
    repetidas_ultimo_min = 6, repetidas_ultimo_max = 12,
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
  selecao = list(max_overlap_entre_jogos = 12),
  simulacao = list(ativar = TRUE, n_sim = 1000)
)

set.seed(config$seed)

carregar_pacote <- function(pkg) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    if (isTRUE(config$instalar_pacotes)) {
      install.packages(pkg, repos = "https://cloud.r-project.org")
    } else {
      stop(paste0("Pacote nao encontrado: ", pkg, ". Instale manualmente ou altere config$instalar_pacotes para TRUE."), call. = FALSE)
    }
  }
  suppressPackageStartupMessages(library(pkg, character.only = TRUE))
}

pacotes <- c("readxl", "dplyr", "tidyr", "purrr", "stringr", "tibble", "readr", "ggplot2")
invisible(lapply(pacotes, carregar_pacote))

normalizar_nome <- function(x) {
  y <- iconv(x, from = "", to = "ASCII//TRANSLIT")
  y <- tolower(y)
  y <- gsub("[^a-z0-9]+", "_", y)
  gsub("^_+|_+$", "", y)
}

scale_01 <- function(x) {
  x <- as.numeric(x)
  if (length(x) == 0) return(x)
  if (all(is.na(x))) return(rep(0.5, length(x)))
  mn <- suppressWarnings(min(x, na.rm = TRUE))
  mx <- suppressWarnings(max(x, na.rm = TRUE))
  if (!is.finite(mn) || !is.finite(mx) || abs(mx - mn) < .Machine$double.eps) return(rep(0.5, length(x)))
  (x - mn) / (mx - mn)
}

clip_01 <- function(x) pmin(pmax(x, 0), 1)

max_run_consecutivo <- function(x) {
  x <- sort(as.integer(x))
  if (length(x) <= 1) return(length(x))
  r <- rle(diff(x) == 1)
  if (!any(r$values)) return(1L)
  as.integer(max(r$lengths[r$values]) + 1L)
}

gerar_pares <- function(dezenas) t(utils::combn(sort(as.integer(dezenas)), 2))
gerar_trios <- function(dezenas) t(utils::combn(sort(as.integer(dezenas)), 3))

matriz_binaria <- function(mat) {
  mat <- as.matrix(mat)
  out <- matrix(0L, nrow = nrow(mat), ncol = 25)
  for (i in seq_len(nrow(mat))) out[i, as.integer(mat[i, ])] <- 1L
  colnames(out) <- sprintf("N%02d", 1:25)
  out
}

calcular_max_overlap_historico <- function(cand_bin, hist_bin, chunk = 2000) {
  n <- nrow(cand_bin)
  out <- integer(n)
  for (ini in seq(1, n, by = chunk)) {
    fim <- min(ini + chunk - 1, n)
    bloco <- cand_bin[ini:fim, , drop = FALSE]
    overlaps <- bloco %*% t(hist_bin)
    out[ini:fim] <- apply(overlaps, 1, max)
  }
  out
}

calcular_metricas_conjunto <- function(mat_jogos, prob_hist) {
  mat_jogos <- as.matrix(mat_jogos)
  if (nrow(mat_jogos) == 0) {
    return(tibble::tibble(n_jogos = 0, cobertura_dezenas = NA_real_, cobertura_pares = NA_real_, cobertura_trios = NA_real_, entropia_media = NA_real_, soma_media = NA_real_))
  }
  pares <- unique(as.data.frame(do.call(rbind, lapply(seq_len(nrow(mat_jogos)), function(i) gerar_pares(mat_jogos[i, ])))))
  trios <- unique(as.data.frame(do.call(rbind, lapply(seq_len(nrow(mat_jogos)), function(i) gerar_trios(mat_jogos[i, ])))))
  entropias <- apply(mat_jogos, 1, function(x) { p <- prob_hist[x]; p <- p / sum(p); -sum(p * log2(p)) })
  tibble::tibble(
    n_jogos = nrow(mat_jogos),
    cobertura_dezenas = length(unique(as.vector(mat_jogos))) / 25,
    cobertura_pares = nrow(pares) / choose(25, 2),
    cobertura_trios = nrow(trios) / choose(25, 3),
    entropia_media = mean(entropias),
    soma_media = mean(rowSums(mat_jogos))
  )
}

detectar_arquivo <- function() {
  if (!is.null(config$arquivo_dados) && file.exists(config$arquivo_dados)) return(config$arquivo_dados)
  candidatos <- c(
    "data/raw/lotofacil_historico.xlsx",
    "data/raw/Lotofacil.xlsx",
    "data/raw/Lotofácil.xlsx",
    "Lotofácil(1) - estatistica_descritiva.xlsx",
    "Lotofacil(1) - estatistica_descritiva.xlsx",
    "Lotofácil(1).xlsx",
    "Lotofacil(1).xlsx"
  )
  encontrados <- candidatos[file.exists(candidatos)]
  if (length(encontrados) > 0) return(encontrados[1])
  encontrados_auto <- list.files(pattern = "lotof.*\\.xlsx$", ignore.case = TRUE, full.names = TRUE)
  if (length(encontrados_auto) > 0) return(encontrados_auto[1])
  stop("Arquivo da Lotofacil nao encontrado. Coloque a base em data/raw/ ou informe config$arquivo_dados.", call. = FALSE)
}

arquivo_dados <- detectar_arquivo()
cat("\nArquivo de dados localizado:\n", arquivo_dados, "\n")
dir.create(config$pasta_saida, showWarnings = FALSE, recursive = TRUE)

df_raw <- readxl::read_excel(arquivo_dados)
nomes_originais <- names(df_raw)
nomes_norm <- normalizar_nome(nomes_originais)
col_dezenas <- nomes_originais[grepl("^(bola|dezena)_?[0-9]+$", nomes_norm)]

if (length(col_dezenas) < 15) {
  possiveis <- names(df_raw)[sapply(df_raw, function(z) {
    z_num <- suppressWarnings(as.integer(z))
    mean(!is.na(z_num) & z_num >= 1 & z_num <= 25) > 0.80
  })]
  col_dezenas <- possiveis[seq_len(min(15, length(possiveis)))]
}

if (length(col_dezenas) != 15) stop("Nao foi possivel identificar exatamente 15 colunas de dezenas.", call. = FALSE)

ordem_dezenas <- suppressWarnings(as.integer(stringr::str_extract(normalizar_nome(col_dezenas), "[0-9]+")))
if (all(!is.na(ordem_dezenas))) col_dezenas <- col_dezenas[order(ordem_dezenas)]

col_concurso <- nomes_originais[which(nomes_norm %in% c("concurso", "numero_concurso", "n_concurso"))[1]]
col_data <- nomes_originais[which(nomes_norm %in% c("data", "data_sorteio", "dt_sorteio"))[1]]

matriz_hist <- df_raw %>%
  dplyr::select(dplyr::all_of(col_dezenas)) %>%
  dplyr::mutate(dplyr::across(dplyr::everything(), ~ suppressWarnings(as.integer(.x)))) %>%
  as.matrix()

linhas_invalidas <- which(apply(matriz_hist, 1, function(x) any(is.na(x)) || any(x < 1 | x > 25) || length(unique(x)) != 15))
if (length(linhas_invalidas) > 0) stop(paste0("Base contem linhas invalidas nas dezenas. Exemplos: ", paste(head(linhas_invalidas, 10), collapse = ", ")), call. = FALSE)

matriz_hist <- t(apply(matriz_hist, 1, sort))
colnames(matriz_hist) <- sprintf("Bola%02d", 1:15)
concurso <- if (!is.na(col_concurso)) df_raw[[col_concurso]] else seq_len(nrow(df_raw))

cat("\nConcursos importados:", nrow(matriz_hist), "\n")
cat("Colunas de dezenas:", paste(col_dezenas, collapse = ", "), "\n")

hist_bin_completo <- matriz_binaria(matriz_hist)
freq_abs <- tabulate(as.vector(matriz_hist), nbins = 25)
freq_rel <- freq_abs / sum(freq_abs)

ultimo_indice_dezena <- sapply(1:25, function(d) { pos <- which(hist_bin_completo[, d] == 1); if (length(pos) == 0) NA_integer_ else max(pos) })
atraso_atual <- nrow(matriz_hist) - ultimo_indice_dezena
atraso_atual[is.na(atraso_atual)] <- nrow(matriz_hist)
atraso_maximo <- sapply(1:25, function(d) { pos <- which(hist_bin_completo[, d] == 1); max(diff(c(0, pos, nrow(matriz_hist) + 1)) - 1) })

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
pesos_raw <- config$pesos_amostragem$frequencia * stats_dezenas$peso_freq_norm + config$pesos_amostragem$atraso * stats_dezenas$peso_atraso_norm + config$pesos_amostragem$uniforme
prob_amostragem <- pesos_raw / sum(pesos_raw)
stats_dezenas$prob_amostragem <- prob_amostragem
readr::write_csv(stats_dezenas, file.path(config$pasta_saida, "estatisticas_dezenas_v12.csv"))

somas_hist <- rowSums(matriz_hist)
if (is.null(config$filtros$soma_min) || is.null(config$filtros$soma_max)) {
  q_soma <- as.numeric(stats::quantile(somas_hist, probs = config$filtros$soma_quantis, na.rm = TRUE))
  config$filtros$soma_min <- floor(q_soma[1])
  config$filtros$soma_max <- ceiling(q_soma[2])
}

ultimo_sorteio <- matriz_hist[nrow(matriz_hist), ]
hist_overlap <- hist_bin_completo
if (!is.null(config$historico_overlap_ultimos) && nrow(hist_bin_completo) > config$historico_overlap_ultimos) {
  idx_ini <- nrow(hist_bin_completo) - config$historico_overlap_ultimos + 1
  hist_overlap <- hist_bin_completo[idx_ini:nrow(hist_bin_completo), , drop = FALSE]
}

gerar_candidatos <- function(n, prob) {
  lista <- vector("list", n)
  for (i in seq_len(n)) lista[[i]] <- sort(sample(1:25, size = 15, replace = FALSE, prob = prob))
  mat <- do.call(rbind, lista)
  colnames(mat) <- sprintf("D%02d", 1:15)
  chave <- apply(mat, 1, paste, collapse = "-")
  mat[!duplicated(chave), , drop = FALSE]
}

cat("\nGerando combinacoes candidatas...\n")
mat_candidatos <- gerar_candidatos(config$n_candidatos, prob_amostragem)
cat("Candidatos unicos gerados:", nrow(mat_candidatos), "\n")

calcular_metricas_candidatos <- function(mat) {
  mat <- as.matrix(mat)
  n <- nrow(mat)
  pares <- rowSums(mat %% 2 == 0)
  baixas <- rowSums(mat <= 13)
  altas <- 15 - baixas
  primas_set <- c(2, 3, 5, 7, 11, 13, 17, 19, 23)
  borda_set <- c(1, 2, 3, 4, 5, 6, 10, 11, 15, 16, 20, 21, 22, 23, 24, 25)
  primas <- rowSums(matrix(mat %in% primas_set, nrow = n))
  borda <- rowSums(matrix(mat %in% borda_set, nrow = n))
  soma <- rowSums(mat)
  max_consec <- apply(mat, 1, max_run_consecutivo)
  repetidas_ultimo <- rowSums(matrix(mat %in% ultimo_sorteio, nrow = n))
  board <- t(apply(mat, 1, function(x) {
    linhas <- ceiling(x / 5); colunas <- ((x - 1) %% 5) + 1
    tab_linhas <- tabulate(linhas, nbins = 5); tab_colunas <- tabulate(colunas, nbins = 5)
    c(max_linha = max(tab_linhas), max_coluna = max(tab_colunas), linhas_cheias = sum(tab_linhas == 5), colunas_cheias = sum(tab_colunas == 5))
  }))
  entropia <- apply(mat, 1, function(x) { p <- prob_hist[x]; p <- p / sum(p); -sum(p * log2(p)) })
  kl <- apply(mat, 1, function(x) { q <- rep(1 / 15, length(x)); sum(q * log2(q / prob_hist[x])) })
  cand_bin <- matriz_binaria(mat)
  max_overlap_hist <- calcular_max_overlap_historico(cand_bin, hist_overlap)
  score_balance <- 1 - (abs(pares - 15 * 12 / 25) / 7.5 + abs(altas - 15 * 12 / 25) / 7.5 + abs(primas - 15 * 9 / 25) / 9 + abs(borda - 15 * 16 / 25) / 15) / 4
  score_balance <- clip_01(score_balance)
  popularidade_proxy <- scale_01(max_consec) * 0.35 + scale_01(board[, "max_linha"] + board[, "max_coluna"]) * 0.25 + scale_01(board[, "linhas_cheias"] + board[, "colunas_cheias"]) * 0.20 + scale_01(abs(soma - mean(somas_hist)) / stats::sd(somas_hist)) * 0.20
  score_antipop <- 1 - clip_01(popularidade_proxy)
  score_div_hist <- 1 - scale_01(max_overlap_hist)
  score_soma <- 1 - scale_01(abs(soma - mean(somas_hist)))
  score_total <- config$score$w_entropia * scale_01(entropia) + config$score$w_kl_originalidade * scale_01(kl) + config$score$w_balanceamento * score_balance + config$score$w_antipopularidade * score_antipop + config$score$w_diversidade_historica * score_div_hist + config$score$w_estabilidade_soma * score_soma
  tibble::tibble(id_candidato = seq_len(n), soma = soma, pares = pares, impares = 15 - pares, altas = altas, baixas = baixas, primas = primas, borda = borda, centro = 15 - borda, max_consecutivas = max_consec, repetidas_ultimo = repetidas_ultimo, max_linha = board[, "max_linha"], max_coluna = board[, "max_coluna"], linhas_cheias = board[, "linhas_cheias"], colunas_cheias = board[, "colunas_cheias"], entropia = entropia, kl_divergence = kl, max_overlap_historico = max_overlap_hist, score_balanceamento = score_balance, score_antipopularidade = score_antipop, score_diversidade_historica = score_div_hist, score_estabilidade_soma = score_soma, score_total = score_total)
}

cat("\nCalculando metricas dos candidatos...\n")
metricas <- calcular_metricas_candidatos(mat_candidatos)

filtros_lista <- list(
  paridade_6_a_9 = metricas$pares >= config$filtros$pares_min & metricas$pares <= config$filtros$pares_max,
  altas_baixas_6_a_9 = metricas$altas >= config$filtros$altas_min & metricas$altas <= config$filtros$altas_max,
  soma_faixa_empirica = metricas$soma >= config$filtros$soma_min & metricas$soma <= config$filtros$soma_max,
  max_consecutivas = metricas$max_consecutivas <= config$filtros$max_consecutivas,
  primas_faixa = metricas$primas >= config$filtros$primas_min & metricas$primas <= config$filtros$primas_max,
  borda_faixa = metricas$borda >= config$filtros$borda_min & metricas$borda <= config$filtros$borda_max,
  repetidas_ultimo = metricas$repetidas_ultimo >= config$filtros$repetidas_ultimo_min & metricas$repetidas_ultimo <= config$filtros$repetidas_ultimo_max,
  similaridade_historica = metricas$max_overlap_historico <= config$filtros$max_overlap_historico
)

atual <- rep(TRUE, nrow(metricas))
diagnostico_filtros <- purrr::imap_dfr(filtros_lista, function(filtro, nome) {
  antes <- sum(atual); atual <<- atual & filtro; depois <- sum(atual)
  tibble::tibble(filtro = nome, n_antes = antes, n_depois = depois, n_eliminados = antes - depois, taxa_retencao = ifelse(antes == 0, NA_real_, depois / antes))
})

metricas$filtro_ok <- atual
idx_residual <- which(metricas$filtro_ok)
readr::write_csv(diagnostico_filtros, file.path(config$pasta_saida, "diagnostico_filtros_v12.csv"))
if (length(idx_residual) == 0) stop("Nenhuma combinacao permaneceu no espaco residual. Revise os filtros.", call. = FALSE)

metricas_residual <- metricas[idx_residual, ] %>% dplyr::arrange(dplyr::desc(score_total)) %>% dplyr::mutate(rank_residual = dplyr::row_number())
mat_residual <- mat_candidatos[metricas_residual$id_candidato, , drop = FALSE]
n_top <- min(config$n_top_residual_export, nrow(metricas_residual))
top_residual <- dplyr::bind_cols(metricas_residual[seq_len(n_top), c("rank_residual", "id_candidato")], as_tibble(mat_residual[seq_len(n_top), , drop = FALSE]), metricas_residual[seq_len(n_top), setdiff(names(metricas_residual), c("rank_residual", "id_candidato", "filtro_ok"))])
readr::write_csv(top_residual, file.path(config$pasta_saida, "top_residual_v12.csv"))

selecionar_jogos_diversos <- function(mat, n_jogos, max_overlap) {
  bin <- matriz_binaria(mat); selecionados <- integer(0)
  for (i in seq_len(nrow(mat))) {
    if (length(selecionados) == 0) selecionados <- c(selecionados, i) else {
      overlaps <- bin[i, , drop = FALSE] %*% t(bin[selecionados, , drop = FALSE])
      if (max(overlaps) <= max_overlap) selecionados <- c(selecionados, i)
    }
    if (length(selecionados) >= n_jogos) break
  }
  selecionados
}

max_overlap_sel <- config$selecao$max_overlap_entre_jogos
idx_sel_local <- selecionar_jogos_diversos(mat_residual, config$n_jogos_finais, max_overlap_sel)
while (length(idx_sel_local) < config$n_jogos_finais && max_overlap_sel < 15) {
  max_overlap_sel <- max_overlap_sel + 1
  idx_sel_local <- selecionar_jogos_diversos(mat_residual, config$n_jogos_finais, max_overlap_sel)
}

mat_final <- mat_residual[idx_sel_local, , drop = FALSE]
metricas_final <- metricas_residual[idx_sel_local, , drop = FALSE]
jogos_final <- dplyr::bind_cols(tibble::tibble(jogo = seq_len(nrow(mat_final))), as_tibble(mat_final), metricas_final %>% dplyr::select(rank_residual, id_candidato, score_total, entropia, kl_divergence, soma, pares, impares, altas, baixas, primas, borda, centro, max_consecutivas, repetidas_ultimo, max_overlap_historico, score_balanceamento, score_antipopularidade, score_diversidade_historica, score_estabilidade_soma))
readr::write_csv(jogos_final, file.path(config$pasta_saida, "jogos_final_v12.csv"))

metricas_final_conjunto <- calcular_metricas_conjunto(mat_final, prob_hist) %>% dplyr::mutate(tipo = "modelo_v12")
readr::write_csv(metricas_final_conjunto, file.path(config$pasta_saida, "metricas_conjunto_final_v12.csv"))

if (isTRUE(config$simulacao$ativar)) {
  sim_lista <- vector("list", config$simulacao$n_sim)
  for (s in seq_len(config$simulacao$n_sim)) {
    mat_sim <- do.call(rbind, replicate(config$n_jogos_finais, sort(sample(1:25, 15, replace = FALSE)), simplify = FALSE))
    sim_lista[[s]] <- calcular_metricas_conjunto(mat_sim, prob_hist) %>% dplyr::mutate(simulacao = s, tipo = "aleatorio_uniforme")
  }
  simulacoes <- dplyr::bind_rows(sim_lista)
  readr::write_csv(simulacoes, file.path(config$pasta_saida, "simulacao_monte_carlo_v12.csv"))
  resumo_simulacao <- simulacoes %>% dplyr::summarise(dplyr::across(c(cobertura_dezenas, cobertura_pares, cobertura_trios, entropia_media, soma_media), list(media = mean, p05 = ~ stats::quantile(.x, 0.05), p50 = ~ stats::quantile(.x, 0.50), p95 = ~ stats::quantile(.x, 0.95)), .names = "{.col}_{.fn}"))
  readr::write_csv(resumo_simulacao, file.path(config$pasta_saida, "resumo_simulacao_v12.csv"))
}

p_freq <- ggplot2::ggplot(stats_dezenas, ggplot2::aes(x = dezena, y = frequencia_abs)) + ggplot2::geom_col() + ggplot2::scale_x_continuous(breaks = 1:25) + ggplot2::labs(title = "Frequencia historica das dezenas - Lotofacil", x = "Dezena", y = "Frequencia absoluta") + ggplot2::theme_minimal()
ggplot2::ggsave(file.path(config$pasta_saida, "grafico_frequencia_dezenas_v12.png"), plot = p_freq, width = 10, height = 6, dpi = 150)

p_score <- ggplot2::ggplot(metricas_residual, ggplot2::aes(x = score_total)) + ggplot2::geom_histogram(bins = 40) + ggplot2::labs(title = "Distribuicao do score total no espaco residual", x = "Score total", y = "Quantidade de combinacoes") + ggplot2::theme_minimal()
ggplot2::ggsave(file.path(config$pasta_saida, "grafico_score_residual_v12.png"), plot = p_score, width = 10, height = 6, dpi = 150)

relatorio_txt <- c(
  "Modelo Axion Lotofacil - v1.2",
  "================================",
  "Autor: Jacson Cruz do Nascimento",
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
  "Nota metodologica:",
  "Este modelo nao aumenta a probabilidade matematica de acerto de uma combinacao especifica.",
  "O objetivo e auditar, eliminar padroes, reduzir redundancia e selecionar combinacoes com criterios rastreaveis."
)
writeLines(relatorio_txt, file.path(config$pasta_saida, "relatorio_execucao_v12.txt"))
cat("\nExecucao concluida. Verifique a pasta:\n", normalizePath(config$pasta_saida), "\n")
