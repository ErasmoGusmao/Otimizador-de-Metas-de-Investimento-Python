from duogoal_app.finance import simular_duas_metas, taxa_mensal_equivalente


def test_taxa_mensal_equivalente_para_taxa_mensal():
    assert taxa_mensal_equivalente("mensal", 0.01) == 0.01


def test_simulacao_conclui_meta_no_tempo_zero():
    t1, t2, trajetoria = simular_duas_metas(
        i=0.01,
        c1=100,
        c2=100,
        ax1=0,
        ax2=0,
        a1=10,
        a2=10,
        m1=90,
        m2=80,
        max_meses=12,
    )
    assert t1 == 0
    assert t2 == 0
    assert len(trajetoria) == 1
