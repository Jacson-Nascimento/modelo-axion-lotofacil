# ==========================================================
# 1. PACOTES
# ==========================================================

carregar_pacote <- function(pkg) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    if (isTRUE(config$instalar_pacotes)) {
      install.packages(pkg, repos = "https://cloud.r-project.org")
    } else {
      stop(
        paste0(
          "Pacote nao encontrado: ", pkg,
          ". Instale manualmente com install.packages('", pkg, "') ",
          "ou altere config$instalar_pacotes para TRUE."
        ),
        call. = FALSE
      )
    }
  }
  suppressPackageStartupMessages(library(pkg, character.only = TRUE))
}

pacotes <- c("readxl", "dplyr", "tidyr", "purrr", "stringr", "tibble", "readr", "ggplot2")
invisible(lapply(pacotes, carregar_pacote))

# ==========================================================
# 2. FUNCOES UTILITARIAS
# ==========================================================

normalizar_nome <- function(x) {
  y <- iconv(x, from = "", to = "ASCII//TRANSLIT")
  y <- tolower(y)
  y <- gsub("[^a-z0-9]+", "_", y)
  y <- gsub("^_+|_+$", "", y)
  y
}

scale_01 <- function(x) {
  x <- as.numeric(x)
  if (length(x) == 0) return(x)
  if (all(is.na(x))) return(rep(0.5, length(x)))
  mn <- suppressWarnings(min(x, na.rm = TRUE))
  mx <- suppressWarnings(max(x, na.rm = TRUE))
  if (!is.finite(mn) || !is.finite(mx) || abs(mx - mn) < .Machine$double.eps) {
    return(rep(0.5, length(x)))
  }
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

gerar_pares <- function(dezenas) {
  dezenas <- sort(as.integer(dezenas))
  t(utils::combn(dezenas, 2))
}

gerar_trios <- function(dezenas) {
  dezenas <- sort(as.integer(dezenas))
  t(utils::combn(dezenas, 3))
}

matriz_binaria <- function(mat) {
  mat <- as.matrix(mat)
  out <- matrix(0L, nrow = nrow(mat), ncol = 25)
  for (i in seq_len(nrow(mat))) {
    out[i, as.integer(mat[i, ])] <- 1L
  }
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
    return(tibble::tibble(
      n_jogos = 0,
      cobertura_dezenas = NA_real_,
      cobertura_pares = NA_real_,
      cobertura_trios = NA_real_,
      entropia_media = NA_real_,
      soma_media = NA_real_
    ))
  }

  dezenas_unicas <- unique(as.vector(mat_jogos))

  pares <- do.call(rbind, lapply(seq_len(nrow(mat_jogos)), function(i) gerar_pares(mat_jogos[i, ])))
  pares <- unique(as.data.frame(pares))

  trios <- do.call(rbind, lapply(seq_len(nrow(mat_jogos)), function(i) gerar_trios(mat_jogos[i, ])))
  trios <- unique(as.data.frame(trios))

  entropias <- apply(mat_jogos, 1, function(x) {
    p <- prob_hist[x]
    p <- p / sum(p)
    -sum(p * log2(p))
  })

  tibble::tibble(
    n_jogos = nrow(mat_jogos),
    cobertura_dezenas = length(dezenas_unicas) / 25,
    cobertura_pares = nrow(pares) / choose(25, 2),
    cobertura_trios = nrow(trios) / choose(25, 3),
    entropia_media = mean(entropias),
    soma_media = mean(rowSums(mat_jogos))
  )
}
