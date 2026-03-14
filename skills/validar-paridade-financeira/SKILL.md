# Validar Paridade Financeira

Use esta skill quando precisar confirmar que uma nova implementacao preserva o comportamento financeiro do notebook original.

## Objetivo
- comparar resultados de referencia entre implementacoes;
- detectar regressao de formula, distribuicao de aportes ou datas previstas.

## Procedimento
1. Escolha um conjunto fixo de entradas de referencia.
2. Registre os valores esperados do notebook:
   `t1`, `t2`, `t_total`, alocacao mensal, alocacao extra e datas previstas.
3. Execute a nova implementacao com exatamente as mesmas entradas.
4. Compare os resultados numericos com tolerancia explicita para arredondamento.
5. Verifique tambem os rotulos exibidos quando houver nomes personalizados para as metas.
6. Se houver divergencia, localize se ela vem de:
   - conversao de taxa;
   - regra de transferencia de aporte;
   - busca em grade ou refino;
   - exibicao de datas.

## Criterios de saida
- tempos e alocacoes principais batem com a referencia;
- diferencas residuais ficam documentadas;
- a validacao pode ser repetida em testes automatizados.
