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
Get-FileHash .\data\raw\* -Algorithm SHA256
Get-FileHash .\outputs\* -Algorithm SHA256
Get-FileHash .\figures\* -Algorithm SHA256
```
