# Checksums

Esta pasta registra os hashes SHA-256 dos arquivos relevantes da execucao.

Arquivo recomendado:

```text
CHECKSUMS.sha256
```

Exemplo em Linux ou macOS:

```bash
sha256sum data/raw/* outputs/* figures/* > checksums/CHECKSUMS.sha256
```

Exemplo em PowerShell:

```powershell
Get-ChildItem .\data\raw\*, .\outputs\*, .\figures\* -File | Get-FileHash -Algorithm SHA256 | Format-Table Hash, Path
```

Apos a execucao validada, salve a saida no arquivo `checksums/CHECKSUMS.sha256`.
