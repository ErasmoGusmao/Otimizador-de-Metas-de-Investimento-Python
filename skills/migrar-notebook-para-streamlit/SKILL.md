# Migrar Notebook para Streamlit

Use esta skill quando o objetivo for transformar um notebook financeiro em uma aplicacao Streamlit sem perder a logica existente.

## Objetivo
- extrair a logica financeira para modulos Python reutilizaveis;
- manter a paridade com os resultados do notebook;
- isolar interface, graficos e testes.

## Checklist
1. Identifique no notebook quais celulas sao entradas, quais sao funcoes e quais sao visualizacoes.
2. Mova as funcoes puras para um modulo como `duogoal_app/core.py`.
3. Coloque a geracao de graficos em um modulo separado, como `duogoal_app/charts.py`.
4. Crie um `dataclass` para centralizar as entradas do solver.
5. Defina valores padrao iguais aos usados no notebook de referencia.
6. Monte a interface Streamlit em `app.py` usando formulario lateral e metricas resumidas.
7. Garanta que a aplicacao mostre tempos, alocacoes e datas previstas.
8. Adicione testes minimos para taxa, simulacao e consistencia das alocacoes.

## Criterios de saida
- o solver roda sem depender do notebook;
- os valores padrao produzem o mesmo resultado principal do notebook;
- a app abre com `streamlit run app.py`;
- `pytest` passa.
