# Dados - Modelo Axion Lotofacil v1.2

**Autor:** Jacson Cruz do Nascimento

A pasta `data/` organiza os insumos do Modelo Axion Lotofacil.

## Estrutura

```text
data/
├── raw/
│   └── README.md
└── processed/
    └── README.md
```

## Requisitos da base historica

A base deve conter:

- uma linha por concurso;
- identificador do concurso, quando disponivel;
- data do sorteio, quando disponivel;
- quinze colunas com dezenas sorteadas;
- dezenas entre 1 e 25;
- quinze dezenas distintas por linha.

O script tenta identificar automaticamente colunas com padrao `Bola1` a `Bola15` ou nomes equivalentes.
