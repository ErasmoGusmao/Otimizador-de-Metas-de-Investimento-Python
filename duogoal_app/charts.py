from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

from duogoal_app.models import SolverOutputs


def grafico_saldos(resultados: SolverOutputs) -> go.Figure:
    df = resultados.trajetoria
    inputs = resultados.inputs

    x = df["mes"].values
    y1 = df["saldo1"].values
    y2 = df["saldo2"].values
    ap1 = df["aporte1"].values
    ap2 = df["aporte2"].values
    total = y1 + y2

    custom1 = np.stack([ap1, y1, y2, total], axis=1)
    custom2 = np.stack([ap2, y1, y2, total], axis=1)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y1,
            mode="lines",
            name=f"{inputs.nome_meta1} (saldo)",
            customdata=custom1,
            hovertemplate=(
                "Mes: %{x}<br>"
                "Saldo Meta 1: %{y:,.2f}<br>"
                "Aporte prox. mes: %{customdata[0]:,.2f}<br>"
                "Saldo Meta 2: %{customdata[2]:,.2f}<br>"
                "Total: %{customdata[3]:,.2f}<extra></extra>"
            ),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y2,
            mode="lines",
            name=f"{inputs.nome_meta2} (saldo)",
            customdata=custom2,
            hovertemplate=(
                "Mes: %{x}<br>"
                "Saldo Meta 2: %{y:,.2f}<br>"
                "Aporte prox. mes: %{customdata[0]:,.2f}<br>"
                "Saldo Meta 1: %{customdata[1]:,.2f}<br>"
                "Total: %{customdata[3]:,.2f}<extra></extra>"
            ),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x,
            y=total,
            mode="lines",
            name="Saldo total",
            hovertemplate="Mes: %{x}<br>Total: %{y:,.2f}<extra></extra>",
        )
    )

    fig.add_hline(y=inputs.meta1, line_dash="dash", annotation_text=f"Meta {inputs.nome_meta1}")
    fig.add_hline(y=inputs.meta2, line_dash="dash", annotation_text=f"Meta {inputs.nome_meta2}")

    if np.isfinite(resultados.tempos["t1"]):
        fig.add_vline(x=int(resultados.tempos["t1"]), line_dash="dot", annotation_text=inputs.nome_meta1)
    if np.isfinite(resultados.tempos["t2"]):
        fig.add_vline(x=int(resultados.tempos["t2"]), line_dash="dot", annotation_text=inputs.nome_meta2)

    fig.update_layout(
        title="Evolucao dos saldos com transferencia de aporte",
        xaxis_title="Tempo (meses)",
        yaxis_title="Saldo",
        hovermode="x unified",
    )
    return fig


def grafico_heatmap(resultados: SolverOutputs) -> go.Figure:
    inputs = resultados.inputs
    a1_grid = resultados.grid["a1_grid"]
    ax1_grid = resultados.grid["ax1_grid"]
    tempos = resultados.grid["t_total"]
    a1_opt = resultados.alocacao["a1"]
    a2_opt = resultados.alocacao["a2"]
    ax1_opt = resultados.alocacao["Ax1"]
    ax2_opt = resultados.alocacao["Ax2"]

    ax1_mesh, a1_mesh = np.meshgrid(ax1_grid, a1_grid)
    a2_mat = inputs.aporte_mensal_total - a1_mesh
    ax2_mat = inputs.aporte_extra_total - ax1_mesh
    custom = np.stack([a1_mesh, a2_mat, ax1_mesh, ax2_mat], axis=2)

    fig = go.Figure(
        data=go.Heatmap(
            z=tempos,
            x=ax1_grid,
            y=a1_grid,
            customdata=custom,
            hovertemplate=(
                "a1: %{customdata[0]:,.2f}<br>"
                "a2: %{customdata[1]:,.2f}<br>"
                "Ax1: %{customdata[2]:,.2f}<br>"
                "Ax2: %{customdata[3]:,.2f}<br>"
                "Tempo total: %{z:.0f} meses<extra></extra>"
            ),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[ax1_opt],
            y=[a1_opt],
            mode="markers",
            name="Otimo",
            marker={"size": 10, "symbol": "x"},
            hovertemplate=(
                "OTIMO<br>"
                f"a1={a1_opt:,.2f}<br>a2={a2_opt:,.2f}<br>"
                f"Ax1={ax1_opt:,.2f}<br>Ax2={ax2_opt:,.2f}<br>"
                f"t_total={resultados.tempos['t_total']:.0f} meses<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        title="Mapa do tempo total por distribuicao de aportes",
        xaxis_title=f"Ax1 (aporte extra em {inputs.nome_meta1})",
        yaxis_title=f"a1 (aporte mensal em {inputs.nome_meta1})",
    )
    return fig


def grafico_fronteira(resultados: SolverOutputs) -> go.Figure:
    fronteira = resultados.fronteira

    custom = np.stack(
        [
            fronteira["a2"].values,
            fronteira["Ax1"].values,
            fronteira["Ax2"].values,
            fronteira["t1"].values,
            fronteira["t2"].values,
        ],
        axis=1,
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=fronteira["a1"],
            y=fronteira["t_total"],
            mode="lines+markers",
            name="Melhor tempo total dado a1",
            customdata=custom,
            hovertemplate=(
                "a1: %{x:,.2f}<br>"
                "Tempo total: %{y:.0f} meses<br>"
                "a2: %{customdata[0]:,.2f}<br>"
                "Ax1*: %{customdata[1]:,.2f}<br>"
                "Ax2*: %{customdata[2]:,.2f}<br>"
                "t1*: %{customdata[3]:.0f} meses<br>"
                "t2*: %{customdata[4]:.0f} meses<extra></extra>"
            ),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[resultados.alocacao["a1"]],
            y=[resultados.tempos["t_total"]],
            mode="markers",
            name="Otimo global",
            marker={"size": 12, "symbol": "star"},
        )
    )
    fig.update_layout(
        title="Fronteira de melhor tempo por aporte mensal na Meta 1",
        xaxis_title="a1",
        yaxis_title="Tempo total (meses)",
    )
    return fig
