# `simulacoes/` — Ferramentas de calibração (Monte Carlo)

> **O que NÃO é:** estes arquivos **não são testes** (não rodam no `pytest`) e
> **não fazem parte do jogo**. Nenhum código do jogo, da API ou dos testes importa
> daqui.

## O que são

Scripts de **análise estatística** que rodei **manualmente** para tomar decisões
de **balanceamento com dados** (e não no chute). Cada um importa as classes reais
do jogo (`jogo/...`), simula **milhares de partidas** (método de Monte Carlo) e
imprime estatísticas — por exemplo: "com este ATK de boss, qual a taxa de vitória
da campanha?". As decisões que eles embasaram estão documentadas em `../../docs/`.

Eles **não modificam** nenhum arquivo do jogo — só leem e simulam.

## Os scripts

| Script | Para que serve |
|---|---|
| `sim_balance.py` | Valida a taxa de vitória da campanha sobre o código real (config aprovada). |
| `sim_balance_v4.py` | Calibra a escala de inimigos comuns/elite por andar (+ economia de moedas). |
| `sim_status.py` | Mede o quão ameaçador cada inimigo especial é no andar em que aparece. |
| `sim_boss_fase2.py` | Calibra a **fúria** do Coração da Masmorra na 2ª fase (Lote 4). |
| `sim_elites_tank.py` | Mede o TTK (golpes para matar) por tipo de inimigo e andar (Lote B). |
| `sim_recalibracao.py` | Diagnóstico da campanha **inteira**: onde as runs morrem (★ recalibração). |

## Como rodar

A partir da pasta `randongeon/` (com o venv ativo):

```powershell
cd randongeon
./.venv/Scripts/Activate.ps1
python simulacoes/sim_recalibracao.py
```

Cada script tem um bootstrap de `sys.path` no topo, então também funciona rodando
de dentro de `simulacoes/`. A saída é texto no terminal (tabelas de win-rate, TTK
etc.) — nada é gravado em disco.

## Relação com os testes

- **Testes de verdade** (validam o código, rodam no `pytest`): `randongeon/tests/`
  e `api/test_api.py`.
- **Estas simulações**: ferramentas de decisão de balanceamento, executadas à mão.
