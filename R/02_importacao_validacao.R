# ==========================================================
# 3. LOCALIZACAO E IMPORTACAO DOS DADOS
# ==========================================================

detectar_arquivo <- function() {
  if (!is.null(config$arquivo_dados) && file.exists(config$arquivo_dados)) {
    return(config$arquivo_dados)
  }

  candidatos <- c(
    "Lotofácil(1) - estatistica_descritiva.xlsx",
    "Lotofacil(1) - estatistica_descritiva.xlsx",
    "Lotofácil(1).xlsx",
    "Lotofacil(1).xlsx",
    "data/raw/lotofacil_historico.xlsx"
  )

  encontrados <- candidatos[file.exists(candidatos)]
  if (length(encontrados) > 0) return(encontrados[1])

  encontrados_auto <- list.files(pattern = "lotof.*\\.xlsx$", ignore.case = TRUE, full.names = TRUE)
  if (length(encontrados_auto) > 0) return(encontrados_auto[1])

  encontrados_data <- list.files("data/raw", pattern = "lotof.*\\.xlsx$", ignore.case = TRUE, full.names = TRUE)
  if (length(encontrados_data) > 0) return(encontrados_data[1])

  stop(
    "Arquivo da Lotofacil nao encontrado. Coloque o Excel no diretorio de trabalho ou informe config$arquivo_dados.",
    call. = FALSE
  )
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

if (length(col_dezenas) != 15) {
  stop(
    paste0(
      "Nao foi possivel identificar exatamente 15 colunas de dezenas. Colunas candidatas: ",
      paste(col_dezenas, collapse = ", ")
    ),
    call. = FALSE
  )
}

ordem_dezenas <- suppressWarnings(as.integer(stringr::str_extract(normalizar_nome(col_dezenas), "[0-9]+")))
if (all(!is.na(ordem_dezenas))) {
  col_dezenas <- col_dezenas[order(ordem_dezenas)]
}

col_concurso <- nomes_originais[which(nomes_norm %in% c("concurso", "numero_concurso", "n_concurso"))[1]]
col_data <- nomes_originais[which(nomes_norm %in% c("data", "data_sorteio", "dt_sorteio"))[1]]

matriz_hist <- df_raw %>%
  dplyr::select(dplyr::all_of(col_dezenas)) %>%
  dplyr::mutate(dplyr::across(dplyr::everything(), ~ suppressWarnings(as.integer(.x)))) %>%
  as.matrix()

linhas_invalidas <- which(
  apply(matriz_hist, 1, function(x) any(is.na(x)) || any(x < 1 | x > 25) || length(unique(x)) != 15)
)

if (length(linhas_invalidas) > 0) {
  stop(
    paste0(
      "Base contem linhas invalidas nas dezenas. Exemplos de linhas: ",
      paste(head(linhas_invalidas, 10), collapse = ", ")
    ),
    call. = FALSE
  )
}

matriz_hist <- t(apply(matriz_hist, 1, sort))
colnames(matriz_hist) <- sprintf("Bola%02d", 1:15)

concurso <- if (!is.na(col_concurso)) df_raw[[col_concurso]] else seq_len(nrow(df_raw))
data_sorteio <- if (!is.na(col_data)) df_raw[[col_data]] else rep(NA, nrow(df_raw))

cat("\nConcursos importados:", nrow(matriz_hist), "\n")
cat("Colunas de dezenas:", paste(col_dezenas, collapse = ", "), "\n")
