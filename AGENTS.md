# Repository Guidelines

## Estrutura do projeto e organizacao dos modulos
O repositorio agora possui duas frentes principais:
- `DuoGoal Solver.ipynb`: referencia original em notebook para configuracao de entradas, conversao de taxa, simulacao, otimizacao e geracao de graficos.
- aplicacao Streamlit integrada ao `main`, com a seguinte estrutura:
- `app.py`: interface Streamlit
- `duogoal_app/core.py`: logica financeira e otimizacao
- `duogoal_app/charts.py`: graficos Plotly
- `tests/test_core.py`: verificacoes automatizadas do solver

O notebook continua como referencia funcional de dominio, mas a interface Streamlit agora faz parte da estrutura oficial do repositorio.

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
Limpe saidas desnecessarias antes do commit quando elas nao ajudarem na revisao.
Evite renomear `DuoGoal Solver.ipynb` sem necessidade, porque ele continua sendo a referencia central do projeto.

## Skills locais
As skills reaproveitaveis descobertas neste projeto ficam em `skills/`.
Hoje o diretorio contem:
- `skills/migrar-notebook-para-streamlit/`: checklist para extrair a logica do notebook para uma app Streamlit.
- `skills/validar-paridade-financeira/`: roteiro para comparar resultados entre notebook e aplicacao.
- `skills/atualizar-agents-md/`: regra operacional para revisar e atualizar o `AGENTS.md` sempre que houver mudanca relevante no projeto.
