# Repository Guidelines

## Estrutura do projeto e organizacao dos modulos
A fonte unica da logica e o pacote `duogoal_app`, dividido por responsabilidade:
- `duogoal_app/models.py`: dataclasses `SolverInputs`/`SolverOutputs` e cenario padrao (`inputs_padrao`).
- `duogoal_app/finance.py`: conversao de taxa, validacao de entradas e simulacao mes a mes com transferencia de aporte.
- `duogoal_app/optimizer.py`: funcao objetivo, grid search, refino local, fronteira e `resolver_duas_metas`.
- `duogoal_app/reporting.py`: tabela-resumo e datas previstas (`montar_resumo`).
- `duogoal_app/charts.py`: graficos Plotly.
- `duogoal_app/__init__.py`: re-exporta a API publica; consumidores importam sempre de `duogoal_app`, nunca de modulos internos.

A direcao das dependencias e sempre num sentido so: `models -> finance -> reporting -> optimizer -> charts -> app`.

Consumidores do pacote:
- `app.py`: interface Streamlit (camada de apresentacao, sem logica financeira).
- `DuoGoal Solver.ipynb`: documentacao executavel do dominio; apenas importa e demonstra o pacote, sem reimplementar logica.
- `tests/test_finance.py` e `tests/test_optimizer.py`: verificacoes automatizadas, um arquivo por modulo.
- skills locais e scripts ad-hoc (via `PYTHONPATH` apontando para o projeto).

## Comandos de build, teste e desenvolvimento
Notebook principal:
- `jupyter lab` ou `jupyter notebook`: abre o notebook localmente para edicao e execucao.
- `@' ... '@ | python -`: valide o notebook com `nbformat` usando um script curto, porque `python -m nbformat --validate` nao funciona neste ambiente.
- `git status`: confirma que apenas as alteracoes esperadas serao versionadas.

Worktree Streamlit:
- `streamlit run app.py`: executa a aplicacao localmente.
- `pytest -q`: executa os testes do solver.
- `pip install -r requirements.txt`: instala as dependencias da app.

Sempre que houver mudanca relevante na estrutura do projeto, no fluxo de desenvolvimento, nas ferramentas principais ou nos comandos oficiais de validacao, atualize este arquivo no mesmo ciclo da mudanca.

## Estilo de codigo e convencoes de nomenclatura
Use indentacao de 4 espacos em Python.
Prefira nomes descritivos em portugues para funcoes e variaveis de dominio, como `simular_duas_metas`, `avaliar_tempo_total` e `resolver_duas_metas`.
Mantenha a logica financeira separada da camada de apresentacao sempre que adicionar codigo fora do notebook.
Evite repetir blocos grandes de calculo: extraia funcoes reutilizaveis antes de duplicar comportamento.

## Diretrizes de teste
Para mudancas no notebook:
- execute as celulas do inicio ao fim;
- confirme que a otimizacao termina sem intervencao manual;
- verifique se tabelas e graficos permanecem coerentes.

Para mudancas na app Streamlit:
- rode `pytest -q`;
- valide o cenario padrao e compare os tempos principais com o notebook;
- verifique se os nomes personalizados das metas aparecem corretamente em metricas, tabelas e graficos.

Quando fizer sentido, adicione asserts pequenos para calculos financeiros centrais em vez de depender so de inspecao visual.

## Diretrizes de commit e pull request
Prefira mensagens curtas, no imperativo, em portugues, com prefixos como `feat:`, `fix:` e `docs:`.
Mantenha cada commit focado em uma unica mudanca.

Pull requests devem incluir:
- resumo objetivo;
- impacto no comportamento financeiro;
- evidencias de validacao;
- capturas de tela quando a saida visual mudar.

## Cuidados com o notebook
O notebook nao contem logica propria: toda celula importa do pacote. Se a tentacao for editar calculo nele, o lugar certo e o modulo correspondente em `duogoal_app/`.
Limpe saidas desnecessarias antes do commit quando elas nao ajudarem na revisao.
Evite renomear `DuoGoal Solver.ipynb` sem necessidade, porque ele continua sendo a porta de entrada didatica do projeto.

## Skills locais
As skills reaproveitaveis descobertas neste projeto ficam em `skills/`.
Hoje o diretorio contem:
- `skills/migrar-notebook-para-streamlit/`: checklist para extrair a logica do notebook para uma app Streamlit.
- `skills/validar-paridade-financeira/`: roteiro para comparar resultados entre notebook e aplicacao.
- `skills/atualizar-agents-md/`: regra operacional para revisar e atualizar o `AGENTS.md` sempre que houver mudanca relevante no projeto.
- `skills/interacao-solver-ia/`: protocolo de perguntas e saida tabelada para simular o DuoGoal conversando com o agente IA, sem rodar a app Streamlit nem o notebook.
