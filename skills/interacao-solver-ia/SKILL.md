# Interacao do Solver via Agente IA

Use esta skill quando o usuario quiser simular o DuoGoal conversando com o agente, sem rodar `streamlit run app.py` nem o notebook.

## Quando aplicar
- pedir "rodar uma simulacao", "simular metas", "qual a melhor distribuicao";
- pedir "interagir com o agente" em vez de executar a app ou o notebook;
- perguntar "quanto tempo para atingir as metas" com base em parametros interativos.

## Fase 1 - Coleta de entradas (uma pergunta por vez)
Ordem obrigatoria, via tool `question`, uma pergunta por vez:
1. Nome da Meta 1
2. Nome da Meta 2
3. Tipo de taxa (anual/mensal) - opcao adicional "pesquisar SELIC atual"
4. Se SELIC: confirmar valor obtido do BC (Fase 1.5)
5. Se nao SELIC: valor da taxa informado pelo usuario
6. Capital inicial Meta 1
7. Capital inicial Meta 2
8. Valor-alvo Meta 1
9. Valor-alvo Meta 2
10. Aporte mensal total
11. Aporte extra total
12. Data base (hoje / 03/02/2026 padrao / inicio do proximo mes)

Parametros do solver (`max_meses`, resolucoes, `refino_passos`, `refino_fator`) NAO sao perguntados: usar defaults de `inputs_padrao()`. Permitir sobrescrever apenas se o usuario pedir explicitamente.

## Fase 1.5 - Pesquisa SELIC (condicional)
Se o usuario pedir a SELIC atual, buscar:
`https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1?formato=json`
Confirmar taxa vigente e data, e apontar a proxima reuniao do Copom. A taxa recebida esta em base anual.

## Fase 2 - Pre-check
Antes de rodar, exibir tabela curta com os inputs coletados para confirmacao visual do usuario.

## Fase 3 - Execucao
Script ad-hoc em `simulacoes/` (subdiretorio do projeto, um arquivo por cenario, ex.: `simulacoes/simular_duogoal.py`), com `PYTHONPATH` apontando para o diretorio do projeto, importando da API publica (`from duogoal_app import SolverInputs, resolver_duas_metas`) e chamando `resolver_duas_metas(SolverInputs(...))`. Nao modificar codigo do projeto. Nunca gravar o script em diretorio temporario fora do projeto: ele fica versionado em `simulacoes/` como registro da simulacao.

## Fase 4 - Saida didatica
Invocar a skill `resumo-visual-em-tabelas` e montar as secoes fixas:
1. Cabecalho de contexto
2. Alocacao otima encontrada
3. Linha do tempo das metas (marcos)
4. Trajetoria dos saldos mes a mes
5. Fronteira de alocacoes equivalentes
6. Armadilhas e observacoes
7. Proximo passo sugerido

## Convencoes visuais
Status: ✅ meta atingida / 🟠 meta em andamento / 🔄 apos pivo de aporte / ✋ inicio / ⚪ sem efeito.
Valores em pt-BR: `R$ 1.234,56`. Datas no formato `dd/mm/aaaa`.

## Criterios de saida
- solver terminou sem `ValueError`;
- todas as secoes da Fase 4 preenchidas;
- proximo passo sugerido ao final da resposta.