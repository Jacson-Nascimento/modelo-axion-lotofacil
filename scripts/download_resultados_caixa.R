# ==========================================================
# Download da base historica oficial da Lotofacil - CAIXA
# Autor: Jacson Cruz do Nascimento
# Projeto: Modelo Axion Lotofacil
# ==========================================================

url_caixa <- "https://servicebus2.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Lotof%C3%A1cil"
destino <- file.path("data", "raw", "lotofacil_historico.xlsx")
proveniencia <- file.path("data", "raw", "SOURCE_CAIXA.md")

dir.create(dirname(destino), recursive = TRUE, showWarnings = FALSE)

cat("Baixando base historica oficial da Lotofacil - CAIXA...\n")
cat("URL:", url_caixa, "\n")

utils::download.file(url_caixa, destino, mode = "wb", quiet = FALSE)

if (!file.exists(destino) || file.info(destino)$size <= 0) {
  stop("Falha no download da base historica da Lotofacil.", call. = FALSE)
}

texto_proveniencia <- c(
  "# Fonte dos dados - Lotofacil",
  "",
  "**Projeto:** Modelo Axion Lotofacil",
  "**Autor:** Jacson Cruz do Nascimento",
  "**Fonte:** Portal Loterias CAIXA",
  "**Endpoint de download:** https://servicebus2.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Lotof%C3%A1cil",
  "**Pagina institucional:** https://loterias.caixa.gov.br/Paginas/Lotofacil.aspx",
  "",
  paste0("**Arquivo gerado:** `", destino, "`"),
  paste0("**Data/hora local da execucao:** ", format(Sys.time(), "%Y-%m-%d %H:%M:%S %Z")),
  "",
  "O arquivo deve ser tratado como insumo externo. A reproducao dos resultados depende da versao efetivamente baixada e dos hashes gerados apos a execucao."
)

writeLines(texto_proveniencia, proveniencia, useBytes = TRUE)

cat("Download concluido. Arquivo salvo em:", destino, "\n")
cat("Tamanho do arquivo:", file.info(destino)$size, "bytes\n")
