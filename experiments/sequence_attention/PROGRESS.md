# Execution ledger: docs/superpowers/plans/2026-10-24-sequence-attention.md

Execução autorizada diretamente pelo usuário, sem nova rodada de aprovação. Implementação local em branch isolada; publicação apenas aditiva e PR em rascunho.

Pre-flight: Task 1 fornece matriz e projeção consumidas pela Task 2; Task 2 produz previsões por concurso consumidas pela Task 3. Interfaces compatíveis.

Baseline: repositório dedicado sem suíte de testes na branch main. Ambiente inicialmente sem PyTorch; instalado PyTorch CPU do índice oficial.

Task 1: complete. Seis testes falharam antes da implementação e passaram depois. Snapshot materializado a partir do commit fixado. Projeção e atributos causais testados.

Task 2: complete. Seis novos testes falharam antes da implementação e passaram depois. Suíte completa: 12/12 em 3,88 s. Testes cobrem treino com sinal conhecido, reprodutibilidade, ausência de vazamento, controle de multiplicidade e preservação de saídas existentes.

Final review: revisão independente do commit edd22ed, sem falhas materiais no código/método. A execução completa encontrou problema de data na ingestão, antes de criar resultados. Revisão identificou o mesmo bloqueio.

Final: Ruling: datas iguais entre concursos são permitidas quando a própria CAIXA as registra, porque a ordem causal é o identificador do concurso; datas retrocedentes continuam proibidas. A API oficial confirma 3715 e 3716 em 20/06/2026. Custo se a fonte estiver errada: rótulo de data incorreto, sem mudança na ordem usada pelo modelo.

Final: fixed data ingestion: consulta oficial confirma 3490 em 18/09/2025, não 18/08/2025. Criado derivado com uma única correção de data, números e original preservados. Dois testes adicionais RED antes da correção; revalidação completa a seguir.

Final: Ruling: revisão não cobriu concordância integral do histórico com CAIXA nem desempenho ainda pendente. Serão declarados sete spot checks, não validação integral. Nenhuma promoção operacional depende dessas checagens parciais.

Task 3: execução completa concluída: sete blocos, 1.812 alvos, 10.872 linhas de previsão, 21 ajustes de Transformer. Nenhum dos quatro modelos passou em Holm. Transformer p Holm=0,3104; ordem temporal não acrescentou ganho demonstrado.

Verificação final: 14/14 testes passaram em3,016s; Brier recalculado independentemente; hashes conferidos; uma correção de data, nenhuma alteração de dezenas; figura inspecionada. Publicação somente aditiva em branch e PR rascunho, sem merge.

Publicação: o Git local não dispõe de autenticação de escrita. Usado o conector GitHub para criar os objetos e atualizar somente a nova branch. O bundle verificado preserva o commit exato de execução e seus ancestrais locais; não depende de credenciais no shell.
