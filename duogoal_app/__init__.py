"""DuoGoal Solver application package.

API publica re-exportada aqui: consumidores (app, testes, notebook, scripts)
devem importar de `duogoal_app` diretamente, sem depender de modulos internos.
"""

from duogoal_app.finance import simular_duas_metas, taxa_mensal_equivalente, validar_entradas
from duogoal_app.models import SolverInputs, SolverOutputs, inputs_padrao, inputs_to_dict
from duogoal_app.optimizer import (
    avaliar_tempo_total,
    calcular_fronteira,
    grid_search,
    resolver_duas_metas,
)
from duogoal_app.reporting import montar_resumo

__all__ = [
    "SolverInputs",
    "SolverOutputs",
    "inputs_padrao",
    "inputs_to_dict",
    "taxa_mensal_equivalente",
    "validar_entradas",
    "simular_duas_metas",
    "avaliar_tempo_total",
    "grid_search",
    "calcular_fronteira",
    "resolver_duas_metas",
    "montar_resumo",
]
