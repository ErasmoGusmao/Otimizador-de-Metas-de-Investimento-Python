from __future__ import annotations

import numpy as np
import pandas as pd

from duogoal_app.finance import simular_duas_metas, validar_entradas
from duogoal_app.models import SolverInputs, SolverOutputs
from duogoal_app.reporting import montar_resumo


def avaliar_tempo_total(
    i: float,
    c1: float,
    c2: float,
    ax_total: float,
    a_total: float,
    m1: float,
    m2: float,
    a1: float,
    ax1: float,
    max_meses: int,
) -> tuple[float, float, float]:
    a2 = a_total - a1
    ax2 = ax_total - ax1

    if a1 < 0.0 or a2 < 0.0:
        return np.inf, np.inf, np.inf
    if ax1 < 0.0 or ax2 < 0.0:
        return np.inf, np.inf, np.inf

    t1, t2, _ = simular_duas_metas(
        i=i,
        c1=c1,
        c2=c2,
        ax1=ax1,
        ax2=ax2,
        a1=a1,
        a2=a2,
        m1=m1,
        m2=m2,
        max_meses=max_meses,
    )
    return max(t1, t2), t1, t2


def grid_search(
    i: float,
    c1: float,
    c2: float,
    ax_total: float,
    a_total: float,
    m1: float,
    m2: float,
    max_meses: int,
    na: int = 61,
    nx: int = 61,
    a1_bounds: tuple[float, float] | None = None,
    ax1_bounds: tuple[float, float] | None = None,
) -> tuple[dict, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    a1_min, a1_max = (0.0, a_total) if a1_bounds is None else a1_bounds
    ax1_min, ax1_max = (0.0, ax_total) if ax1_bounds is None else ax1_bounds

    a1_grid = np.linspace(a1_min, a1_max, na)
    ax1_grid = np.linspace(ax1_min, ax1_max, nx)

    t_total_grid = np.full((na, nx), np.inf, dtype=float)
    t1_grid = np.full((na, nx), np.inf, dtype=float)
    t2_grid = np.full((na, nx), np.inf, dtype=float)

    melhor = {"t_total": np.inf, "a1": None, "Ax1": None, "t1": None, "t2": None}

    for ia, a1 in enumerate(a1_grid):
        for ix, ax1 in enumerate(ax1_grid):
            t_total, t1, t2 = avaliar_tempo_total(
                i=i,
                c1=c1,
                c2=c2,
                ax_total=ax_total,
                a_total=a_total,
                m1=m1,
                m2=m2,
                a1=float(a1),
                ax1=float(ax1),
                max_meses=max_meses,
            )
            t_total_grid[ia, ix] = t_total
            t1_grid[ia, ix] = t1
            t2_grid[ia, ix] = t2

            if t_total < melhor["t_total"]:
                melhor = {
                    "t_total": t_total,
                    "a1": float(a1),
                    "Ax1": float(ax1),
                    "t1": t1,
                    "t2": t2,
                }

    return melhor, a1_grid, ax1_grid, t_total_grid, t1_grid, t2_grid


def calcular_fronteira(
    i: float,
    c1: float,
    c2: float,
    ax_total: float,
    a_total: float,
    m1: float,
    m2: float,
    max_meses: int,
    pontos_a1: int = 101,
    pontos_ax1: int = 121,
) -> pd.DataFrame:
    a1_line = np.linspace(0.0, a_total, pontos_a1)
    ax1_line_grid = np.linspace(0.0, ax_total, pontos_ax1)

    registros: list[dict] = []
    for a1_val in a1_line:
        melhor_t = np.inf
        melhor_ax1 = 0.0
        melhor_t1 = np.inf
        melhor_t2 = np.inf

        for ax1_val in ax1_line_grid:
            t_total, t1, t2 = avaliar_tempo_total(
                i=i,
                c1=c1,
                c2=c2,
                ax_total=ax_total,
                a_total=a_total,
                m1=m1,
                m2=m2,
                a1=float(a1_val),
                ax1=float(ax1_val),
                max_meses=max_meses,
            )
            if t_total < melhor_t:
                melhor_t = t_total
                melhor_ax1 = float(ax1_val)
                melhor_t1 = t1
                melhor_t2 = t2

        registros.append(
            {
                "a1": float(a1_val),
                "a2": float(a_total - a1_val),
                "Ax1": melhor_ax1,
                "Ax2": float(ax_total - melhor_ax1),
                "t_total": melhor_t,
                "t1": melhor_t1,
                "t2": melhor_t2,
            }
        )

    return pd.DataFrame(registros)


def resolver_duas_metas(inputs: SolverInputs) -> SolverOutputs:
    taxa_mensal = validar_entradas(inputs)

    melhor, a1_grid, ax1_grid, t_grid, t1_grid, t2_grid = grid_search(
        i=taxa_mensal,
        c1=inputs.capital_meta1,
        c2=inputs.capital_meta2,
        ax_total=inputs.aporte_extra_total,
        a_total=inputs.aporte_mensal_total,
        m1=inputs.meta1,
        m2=inputs.meta2,
        max_meses=inputs.max_meses,
        na=inputs.resolucao_aporte_mensal,
        nx=inputs.resolucao_aporte_extra,
    )

    for k in range(inputs.refino_passos):
        janela_a = inputs.aporte_mensal_total * (inputs.refino_fator ** (k + 1))
        janela_ax = inputs.aporte_extra_total * (inputs.refino_fator ** (k + 1))

        a1_min = max(0.0, melhor["a1"] - janela_a)
        a1_max = min(inputs.aporte_mensal_total, melhor["a1"] + janela_a)
        ax1_min = max(0.0, melhor["Ax1"] - janela_ax)
        ax1_max = min(inputs.aporte_extra_total, melhor["Ax1"] + janela_ax)

        melhor_local, _, _, _, _, _ = grid_search(
            i=taxa_mensal,
            c1=inputs.capital_meta1,
            c2=inputs.capital_meta2,
            ax_total=inputs.aporte_extra_total,
            a_total=inputs.aporte_mensal_total,
            m1=inputs.meta1,
            m2=inputs.meta2,
            max_meses=inputs.max_meses,
            na=max(41, inputs.resolucao_aporte_mensal // 2),
            nx=max(41, inputs.resolucao_aporte_extra // 2),
            a1_bounds=(a1_min, a1_max),
            ax1_bounds=(ax1_min, ax1_max),
        )
        if melhor_local["t_total"] < melhor["t_total"]:
            melhor = melhor_local

    a1_opt = melhor["a1"]
    ax1_opt = melhor["Ax1"]
    a2_opt = inputs.aporte_mensal_total - a1_opt
    ax2_opt = inputs.aporte_extra_total - ax1_opt

    t1, t2, trajetoria = simular_duas_metas(
        i=taxa_mensal,
        c1=inputs.capital_meta1,
        c2=inputs.capital_meta2,
        ax1=ax1_opt,
        ax2=ax2_opt,
        a1=a1_opt,
        a2=a2_opt,
        m1=inputs.meta1,
        m2=inputs.meta2,
        max_meses=inputs.max_meses,
    )
    t_total = max(t1, t2)

    resumo, tempos, alocacao, datas = montar_resumo(
        inputs=inputs,
        taxa_mensal=taxa_mensal,
        a1_opt=a1_opt,
        ax1_opt=ax1_opt,
        t1=t1,
        t2=t2,
        t_total=t_total,
        trajetoria=trajetoria,
    )

    fronteira = calcular_fronteira(
        i=taxa_mensal,
        c1=inputs.capital_meta1,
        c2=inputs.capital_meta2,
        ax_total=inputs.aporte_extra_total,
        a_total=inputs.aporte_mensal_total,
        m1=inputs.meta1,
        m2=inputs.meta2,
        max_meses=inputs.max_meses,
    )

    return SolverOutputs(
        taxa_mensal=taxa_mensal,
        melhor=melhor,
        trajetoria=trajetoria,
        resumo=resumo,
        tempos=tempos,
        alocacao=alocacao,
        datas=datas,
        grid={
            "a1_grid": a1_grid,
            "ax1_grid": ax1_grid,
            "t_total": t_grid,
            "t1": t1_grid,
            "t2": t2_grid,
        },
        fronteira=fronteira,
        inputs=inputs,
    )
