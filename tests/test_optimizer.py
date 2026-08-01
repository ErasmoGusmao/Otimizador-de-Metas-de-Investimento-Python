from datetime import datetime

import numpy as np

from duogoal_app import SolverInputs, resolver_duas_metas


def test_resolver_retorna_alocacao_consistente():
    inputs = SolverInputs(
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
        resolucao_aporte_mensal=31,
        resolucao_aporte_extra=31,
        refino_passos=1,
    )

    resultado = resolver_duas_metas(inputs)

    assert np.isfinite(resultado.tempos["t_total"])
    assert resultado.alocacao["a1"] + resultado.alocacao["a2"] == inputs.aporte_mensal_total
    assert round(resultado.alocacao["Ax1"] + resultado.alocacao["Ax2"], 8) == inputs.aporte_extra_total
    assert not resultado.trajetoria.empty
