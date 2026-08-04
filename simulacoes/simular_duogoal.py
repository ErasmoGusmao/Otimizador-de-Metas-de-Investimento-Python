"""Simulacao ad-hoc do DuoGoal executada pelo agente IA.

Cenario: Apartamento (R$ 450 mil) + Reserva de emergencia (R$ 45 mil),
SELIC 14,25% a.a., aporte mensal R$ 7.000, sem aporte extra, base 02/08/2026.

Uso: $env:PYTHONPATH = "<raiz do projeto>"; python simulacoes/simular_duogoal.py
Convencao: um arquivo por cenario neste diretorio; nao modificar codigo do pacote.
"""

from datetime import datetime, timedelta

import numpy as np

from duogoal_app import SolverInputs, resolver_duas_metas

inputs = SolverInputs(
    taxa_tipo="anual",
    taxa_valor=0.1425,
    capital_meta1=200_000.0,
    capital_meta2=19_367.89,
    aporte_extra_total=0.0,
    aporte_mensal_total=7_000.0,
    meta1=450_000.0,
    meta2=45_000.0,
    nome_meta1="Apartamento",
    nome_meta2="Reserva de emergencia",
    data_base=datetime(2026, 8, 2),
)

out = resolver_duas_metas(inputs)

print("TAXA_MENSAL", f"{out.taxa_mensal:.8f}")
print("ALOCACAO", out.alocacao)
print("TEMPOS", out.tempos)
print("DATAS", out.datas)
print()
print("=== RESUMO ===")
print(out.resumo.to_string(index=False))
print()

traj = out.trajetoria.copy()
t_total = int(round(out.tempos["t_total"]))
marcos = set(range(0, t_total + 1, 12))
marcos.add(t_total)
idx_pivo = traj.index[traj["done2"]].tolist()
if idx_pivo:
    marcos.add(int(traj.loc[idx_pivo[0], "mes"]))
sel = traj[traj["mes"].isin(sorted(marcos))].copy()
sel["data"] = [
    (inputs.data_base + timedelta(days=int(m) * 30)).strftime("%m/%Y")
    for m in sel["mes"]
]
print("=== MARCOS ===")
print(
    sel[["mes", "data", "saldo1", "saldo2", "aporte1", "aporte2", "done1", "done2"]].to_string(
        index=False
    )
)
print()

f = out.fronteira
melhor_t = out.tempos["t_total"]
prox = f[np.isfinite(f["t_total"])].copy()
prox = prox[(prox["t_total"] - melhor_t).abs() <= 1.0].sort_values("a1")
passo = max(1, len(prox) // 10)
amostra = prox.iloc[::passo]
print("=== FRONTEIRA (t_total dentro de 1 mes do otimo) ===")
print(amostra.to_string(index=False))
print(f"fronteira rows: {len(f)}, dentro da tolerancia: {len(prox)}")
