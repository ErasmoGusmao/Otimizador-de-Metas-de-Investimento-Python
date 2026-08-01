from __future__ import annotations

from datetime import timedelta

import numpy as np
import pandas as pd

from duogoal_app.models import SolverInputs


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
