from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class SolverInputs:
    taxa_tipo: str
    taxa_valor: float
    capital_meta1: float
    capital_meta2: float
    aporte_extra_total: float
    aporte_mensal_total: float
    meta1: float
    meta2: float
    nome_meta1: str
    nome_meta2: str
    data_base: datetime
    max_meses: int = 6000
    resolucao_aporte_mensal: int = 61
    resolucao_aporte_extra: int = 61
    refino_passos: int = 3
    refino_fator: float = 0.25


@dataclass(frozen=True)
class SolverOutputs:
    taxa_mensal: float
    melhor: dict
    trajetoria: pd.DataFrame
    resumo: pd.DataFrame
    tempos: dict
    alocacao: dict
    datas: dict
    grid: dict
    fronteira: pd.DataFrame
    inputs: SolverInputs


def taxa_mensal_equivalente(taxa_tipo: str, taxa_valor: float) -> float:
    if taxa_tipo.lower() == "anual":
        return (1.0 + float(taxa_valor)) ** (1.0 / 12.0) - 1.0
    return float(taxa_valor)


def validar_entradas(inputs: SolverInputs) -> float:
    taxa_mensal = taxa_mensal_equivalente(inputs.taxa_tipo, inputs.taxa_valor)

    if taxa_mensal < 0.0:
        raise ValueError("A taxa mensal equivalente deve ser maior ou igual a zero.")
    if inputs.aporte_mensal_total < 0.0:
        raise ValueError("O aporte mensal total deve ser maior ou igual a zero.")
    if inputs.aporte_extra_total < 0.0:
        raise ValueError("O aporte extra total deve ser maior ou igual a zero.")
    if inputs.capital_meta1 < 0.0 or inputs.capital_meta2 < 0.0:
        raise ValueError("Os capitais iniciais devem ser maiores ou iguais a zero.")
    if inputs.meta1 < 0.0 or inputs.meta2 < 0.0:
        raise ValueError("As metas devem ser maiores ou iguais a zero.")
    if inputs.max_meses <= 0:
        raise ValueError("max_meses deve ser positivo.")
    if inputs.resolucao_aporte_mensal < 2 or inputs.resolucao_aporte_extra < 2:
        raise ValueError("As resolucoes do grid devem ser maiores ou iguais a 2.")
    if inputs.refino_passos < 0:
        raise ValueError("refino_passos nao pode ser negativo.")
    if not (0 < inputs.refino_fator <= 1):
        raise ValueError("refino_fator deve estar no intervalo (0, 1].")

    return taxa_mensal


def simular_duas_metas(
    i: float,
    c1: float,
    c2: float,
    ax1: float,
    ax2: float,
    a1: float,
    a2: float,
    m1: float,
    m2: float,
    max_meses: int = 6000,
) -> tuple[float, float, pd.DataFrame]:
    b1 = float(c1 + ax1)
    b2 = float(c2 + ax2)

    a1_cur = float(a1)
    a2_cur = float(a2)

    done1 = b1 >= m1
    done2 = b2 >= m2
    t1 = 0 if done1 else np.inf
    t2 = 0 if done2 else np.inf

    if done1 and a1_cur > 0.0:
        a2_cur += a1_cur
        a1_cur = 0.0
    if done2 and a2_cur > 0.0:
        a1_cur += a2_cur
        a2_cur = 0.0

    meses = [0]
    saldo1 = [b1]
    saldo2 = [b2]
    aporte1 = [a1_cur]
    aporte2 = [a2_cur]
    done1_list = [done1]
    done2_list = [done2]

    if done1 and done2:
        return t1, t2, pd.DataFrame(
            {
                "mes": meses,
                "saldo1": saldo1,
                "saldo2": saldo2,
                "aporte1": aporte1,
                "aporte2": aporte2,
                "done1": done1_list,
                "done2": done2_list,
            }
        )

    for mes in range(1, max_meses + 1):
        b1 = b1 * (1.0 + i) + a1_cur
        b2 = b2 * (1.0 + i) + a2_cur

        if (not done1) and (b1 >= m1):
            done1 = True
            t1 = mes
            if a1_cur > 0.0:
                a2_cur += a1_cur
                a1_cur = 0.0

        if (not done2) and (b2 >= m2):
            done2 = True
            t2 = mes
            if a2_cur > 0.0:
                a1_cur += a2_cur
                a2_cur = 0.0

        meses.append(mes)
        saldo1.append(b1)
        saldo2.append(b2)
        aporte1.append(a1_cur)
        aporte2.append(a2_cur)
        done1_list.append(done1)
        done2_list.append(done2)

        if done1 and done2:
            break

    traj = pd.DataFrame(
        {
            "mes": meses,
            "saldo1": saldo1,
            "saldo2": saldo2,
            "aporte1": aporte1,
            "aporte2": aporte2,
            "done1": done1_list,
            "done2": done2_list,
        }
    )

    if not done1:
        t1 = np.inf
    if not done2:
        t2 = np.inf

    return t1, t2, traj


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


def montar_resumo(
    inputs: SolverInputs,
    taxa_mensal: float,
    a1_opt: float,
    ax1_opt: float,
    t1: float,
    t2: float,
    t_total: float,
    trajetoria: pd.DataFrame,
) -> tuple[pd.DataFrame, dict, dict, dict]:
    a2_opt = inputs.aporte_mensal_total - a1_opt
    ax2_opt = inputs.aporte_extra_total - ax1_opt
    anos_total = t_total / 12.0 if np.isfinite(t_total) else np.inf
    saldo_final_1 = float(trajetoria["saldo1"].iloc[-1])
    saldo_final_2 = float(trajetoria["saldo2"].iloc[-1])
    saldo_final_total = saldo_final_1 + saldo_final_2

    data_t1 = inputs.data_base + timedelta(days=float(t1) * 30) if np.isfinite(t1) else None
    data_t2 = inputs.data_base + timedelta(days=float(t2) * 30) if np.isfinite(t2) else None
    data_total = inputs.data_base + timedelta(days=float(t_total) * 30) if np.isfinite(t_total) else None

    resumo = pd.DataFrame(
        {
            "Item": [
                "Taxa mensal equivalente",
                f"Capital inicial {inputs.nome_meta1}",
                f"Capital inicial {inputs.nome_meta2}",
                "Aporte extra total",
                "Aporte mensal total",
                f"Meta {inputs.nome_meta1}",
                f"Meta {inputs.nome_meta2}",
                f"Aporte mensal otimo - {inputs.nome_meta1}",
                f"Aporte mensal otimo - {inputs.nome_meta2}",
                f"Aporte extra otimo - {inputs.nome_meta1}",
                f"Aporte extra otimo - {inputs.nome_meta2}",
                f"Tempo para {inputs.nome_meta1}",
                f"Tempo para {inputs.nome_meta2}",
                "Tempo total",
                "Tempo total em anos",
                f"Saldo final {inputs.nome_meta1}",
                f"Saldo final {inputs.nome_meta2}",
                "Saldo final total",
            ],
            "Valor": [
                taxa_mensal,
                inputs.capital_meta1,
                inputs.capital_meta2,
                inputs.aporte_extra_total,
                inputs.aporte_mensal_total,
                inputs.meta1,
                inputs.meta2,
                a1_opt,
                a2_opt,
                ax1_opt,
                ax2_opt,
                t1,
                t2,
                t_total,
                anos_total,
                saldo_final_1,
                saldo_final_2,
                saldo_final_total,
            ],
        }
    )

    tempos = {"t1": t1, "t2": t2, "t_total": t_total, "anos_total": anos_total}
    alocacao = {"a1": a1_opt, "a2": a2_opt, "Ax1": ax1_opt, "Ax2": ax2_opt}
    datas = {
        "meta1": data_t1.strftime("%Y-%m-%d") if data_t1 else "Nao atinge",
        "meta2": data_t2.strftime("%Y-%m-%d") if data_t2 else "Nao atinge",
        "total": data_total.strftime("%Y-%m-%d") if data_total else "Nao atinge",
    }
    return resumo, tempos, alocacao, datas


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


def inputs_padrao() -> SolverInputs:
    return SolverInputs(
        taxa_tipo="anual",
        taxa_valor=0.14,
        capital_meta1=176_547.74,
        capital_meta2=19_367.89,
        aporte_extra_total=1_165.24,
        aporte_mensal_total=8_000.00,
        meta1=450_000.0,
        meta2=45_000.0,
        nome_meta1="Apartamento",
        nome_meta2="Reserva",
        data_base=datetime.strptime("2026-02-03", "%Y-%m-%d"),
    )


def inputs_to_dict(inputs: SolverInputs) -> dict:
    data = asdict(inputs)
    data["data_base"] = inputs.data_base.strftime("%Y-%m-%d")
    return data
