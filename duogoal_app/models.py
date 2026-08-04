from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime

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


def inputs_padrao() -> SolverInputs:
    return SolverInputs(
        taxa_tipo="anual",
        taxa_valor=0.1425,
        capital_meta1=231_807.40,
        capital_meta2=40_772.54,
        aporte_extra_total=0.0,
        aporte_mensal_total=8_000.0,
        meta1=450_000.0,
        meta2=45_000.0,
        nome_meta1="Apartamento",
        nome_meta2="Reserva de emergencia",
        data_base=datetime.strptime("2026-09-04", "%Y-%m-%d"),
    )


def inputs_to_dict(inputs: SolverInputs) -> dict:
    data = asdict(inputs)
    data["data_base"] = inputs.data_base.strftime("%Y-%m-%d")
    return data
