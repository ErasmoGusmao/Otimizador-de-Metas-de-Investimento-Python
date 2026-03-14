# Atualizar AGENTS.md

Use esta skill sempre que houver uma mudanca relevante no projeto.

## Quando aplicar
- mudanca de estrutura de diretorios ou arquivos principais;
- inclusao ou remocao de comandos oficiais de desenvolvimento, teste ou execucao;
- entrada de uma nova interface, modulo, pacote ou fluxo operacional;
- alteracao no processo de validacao, entrega ou manutencao;
- integracao de uma branch experimental que mude o estado oficial do repositorio.

## Procedimento
1. Releia o `AGENTS.md` atual.
2. Compare o estado documentado com o estado real do repositorio.
3. Atualize secoes impactadas:
   - estrutura do projeto;
   - comandos de build, teste e desenvolvimento;
   - diretrizes de teste;
   - observacoes operacionais e skills locais.
4. Evite deixar no arquivo instrucoes de estados temporarios ja superados.
5. Se a mudanca for relevante, versionar a atualizacao do `AGENTS.md` junto com a propria mudanca do projeto.

## Criterio de conclusao
- o `AGENTS.md` descreve corretamente o estado atual do repositorio;
- nao existem instrucoes obsoletas sobre arquitetura, worktrees, comandos ou fluxo;
- a nova mudanca relevante ficou refletida na documentacao operacional.
