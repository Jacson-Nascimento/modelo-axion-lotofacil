# AXION-GEO - Artefatos da Fase 0

Arquivos compactos preservados no repositório:

- `null_summary_B20000.csv`: comparação das 47 médias históricas com N0;
- `phase0_metadata_B20000.json`: parâmetros, período, hash e política de uso;
- `CHECKSUMS.sha256`: checksums dos artefatos produzidos pela execução completa.

O pipeline também gera `geo_feature_matrix.csv`, com uma linha por concurso. Esse arquivo é derivado e pode ser regenerado a partir da matriz binária de entrada. Por padrão, não é necessário versioná-lo no GitHub.

O checksum registrado para o `geo_feature_matrix.csv` continua no manifesto para permitir auditoria da execução que originou o relatório.
