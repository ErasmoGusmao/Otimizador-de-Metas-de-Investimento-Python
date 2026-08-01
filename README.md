# DuoGoal Solver Streamlit

Aplicacao em Streamlit para transformar o notebook em uma calculadora guiada de duas metas.

## Ambiente

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Execucao

```powershell
streamlit run app.py
```

## Estrutura

- `app.py`: interface Streamlit
- `duogoal_app/models.py`: dataclasses e cenario padrao
- `duogoal_app/finance.py`: taxa, validacao e simulacao
- `duogoal_app/optimizer.py`: grid search, refino, fronteira e `resolver_duas_metas`
- `duogoal_app/reporting.py`: resumo e datas previstas
- `duogoal_app/charts.py`: graficos Plotly
- `DuoGoal Solver.ipynb`: documentacao executavel que importa o pacote
- `tests/test_finance.py`, `tests/test_optimizer.py`: verificacoes basicas de consistencia

## Validacao

```powershell
pytest
```
