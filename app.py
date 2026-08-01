from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st

from duogoal_app import SolverInputs, inputs_padrao, inputs_to_dict, resolver_duas_metas
from duogoal_app.charts import grafico_fronteira, grafico_heatmap, grafico_saldos


st.set_page_config(page_title="DuoGoal Solver", page_icon=":chart_with_upwards_trend:", layout="wide")


def moeda(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def numero(valor: float) -> str:
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


padrao = inputs_padrao()

st.title("DuoGoal Solver")
st.caption("Aplicacao Streamlit para simular e otimizar a distribuicao de aportes entre duas metas.")

with st.sidebar:
    st.header("Entradas")
    with st.form("parametros"):
        nome_meta1 = st.text_input("Nome da Meta 1", value=padrao.nome_meta1)
        nome_meta2 = st.text_input("Nome da Meta 2", value=padrao.nome_meta2)
        taxa_tipo = st.selectbox("Tipo de taxa", options=["anual", "mensal"], index=0)
        taxa_valor = st.number_input("Taxa", min_value=0.0, value=padrao.taxa_valor, step=0.01, format="%.6f")
        capital_meta1 = st.number_input("Capital inicial Meta 1", min_value=0.0, value=padrao.capital_meta1, step=1000.0)
        capital_meta2 = st.number_input("Capital inicial Meta 2", min_value=0.0, value=padrao.capital_meta2, step=1000.0)
        aporte_extra_total = st.number_input(
            "Aporte extra total", min_value=0.0, value=padrao.aporte_extra_total, step=100.0
        )
        aporte_mensal_total = st.number_input(
            "Aporte mensal total", min_value=0.0, value=padrao.aporte_mensal_total, step=100.0
        )
        meta1 = st.number_input("Meta 1", min_value=0.0, value=padrao.meta1, step=1000.0)
        meta2 = st.number_input("Meta 2", min_value=0.0, value=padrao.meta2, step=1000.0)
        data_base = st.date_input("Data base", value=padrao.data_base.date(), format="DD/MM/YYYY")

        st.header("Solver")
        max_meses = st.number_input("Maximo de meses", min_value=1, value=padrao.max_meses, step=12)
        resolucao_aporte_mensal = st.slider("Resolucao do grid para a1", min_value=21, max_value=121, value=61, step=10)
        resolucao_aporte_extra = st.slider("Resolucao do grid para Ax1", min_value=21, max_value=121, value=61, step=10)
        refino_passos = st.slider("Passos de refino", min_value=0, max_value=5, value=padrao.refino_passos)
        refino_fator = st.slider("Fator de refino", min_value=0.05, max_value=1.0, value=padrao.refino_fator)

        st.header("Visualizacao")
        mostrar_heatmap = st.toggle("Mostrar heatmap", value=True)
        mostrar_fronteira = st.toggle("Mostrar fronteira", value=True)

        executar = st.form_submit_button("Calcular melhor distribuicao", use_container_width=True)

if not executar:
    st.info("Ajuste os parametros na barra lateral e clique em calcular para gerar a melhor distribuicao.")
    st.subheader("Cenario base")
    st.json(inputs_to_dict(padrao))
    st.stop()

inputs = SolverInputs(
    taxa_tipo=taxa_tipo,
    taxa_valor=taxa_valor,
    capital_meta1=capital_meta1,
    capital_meta2=capital_meta2,
    aporte_extra_total=aporte_extra_total,
    aporte_mensal_total=aporte_mensal_total,
    meta1=meta1,
    meta2=meta2,
    nome_meta1=nome_meta1 or "Meta 1",
    nome_meta2=nome_meta2 or "Meta 2",
    data_base=datetime.combine(data_base, datetime.min.time()),
    max_meses=int(max_meses),
    resolucao_aporte_mensal=int(resolucao_aporte_mensal),
    resolucao_aporte_extra=int(resolucao_aporte_extra),
    refino_passos=int(refino_passos),
    refino_fator=float(refino_fator),
)

try:
    with st.spinner("Otimizando distribuicao de aportes..."):
        resultados = resolver_duas_metas(inputs)
except ValueError as exc:
    st.error(str(exc))
    st.stop()

col1, col2, col3, col4 = st.columns(4)
col1.metric(f"Tempo {inputs.nome_meta1}", f"{resultados.tempos['t1']:.0f} meses")
col2.metric(f"Tempo {inputs.nome_meta2}", f"{resultados.tempos['t2']:.0f} meses")
col3.metric("Tempo total", f"{resultados.tempos['t_total']:.0f} meses")
col4.metric("Taxa mensal equivalente", f"{resultados.taxa_mensal * 100:.3f}%")

st.subheader("Distribuicao otima")
resumo_col1, resumo_col2, resumo_col3 = st.columns(3)
resumo_col1.metric(f"Aporte mensal em {inputs.nome_meta1}", moeda(resultados.alocacao["a1"]))
resumo_col1.metric(f"Aporte extra em {inputs.nome_meta1}", moeda(resultados.alocacao["Ax1"]))
resumo_col2.metric(f"Aporte mensal em {inputs.nome_meta2}", moeda(resultados.alocacao["a2"]))
resumo_col2.metric(f"Aporte extra em {inputs.nome_meta2}", moeda(resultados.alocacao["Ax2"]))
resumo_col3.metric(f"Data prevista {inputs.nome_meta1}", resultados.datas["meta1"])
resumo_col3.metric(f"Data prevista final", resultados.datas["total"])

st.plotly_chart(grafico_saldos(resultados), width="stretch")

detalhes_tab, traj_tab, grafico_tab = st.tabs(["Resumo", "Trajetoria", "Analises"])

with detalhes_tab:
    resumo_exibicao = resultados.resumo.copy()
    resumo_exibicao["Valor"] = resumo_exibicao["Valor"].apply(
        lambda valor: numero(valor) if isinstance(valor, (int, float)) and pd.notna(valor) else valor
    )
    st.dataframe(resumo_exibicao, use_container_width=True, hide_index=True)

with traj_tab:
    st.dataframe(resultados.trajetoria, use_container_width=True, hide_index=True)

with grafico_tab:
    if mostrar_heatmap:
        st.plotly_chart(grafico_heatmap(resultados), width="stretch")
    if mostrar_fronteira:
        st.plotly_chart(grafico_fronteira(resultados), width="stretch")
    if not mostrar_heatmap and not mostrar_fronteira:
        st.caption("Nenhum grafico opcional habilitado.")
