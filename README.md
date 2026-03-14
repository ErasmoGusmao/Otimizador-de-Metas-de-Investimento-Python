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
- `duogoal_app/core.py`: logica financeira e otimizacao
- `duogoal_app/charts.py`: graficos Plotly
- `tests/test_core.py`: verificacoes basicas de consistencia

## Validacao

```powershell
pytest
```
