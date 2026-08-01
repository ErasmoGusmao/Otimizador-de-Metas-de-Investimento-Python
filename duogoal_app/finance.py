from __future__ import annotations

import numpy as np
import pandas as pd

from duogoal_app.models import SolverInputs


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
