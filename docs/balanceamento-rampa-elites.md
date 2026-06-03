# Balanceamento — Rampa de presença de elites/especiais

## Objetivo

Os inimigos elite (dif 2) e especiais (Golem/Nosferatu/Banshee) apareciam pouco e
com taxa **fixa**. Pedido: deixá-los **mais presentes a partir do andar 6**, nos
dois modos.

## O que mudou

`Inimigo.gerar()` usava chances constantes (entrar no ramo elite/especial = 25%;
dentro dele, virar especial = 40%). Agora ambas **escalam com o andar** a partir
do 6 (`inimigo.py`):

```
chance_elite(andar)   = 0.25 no A5; A6+ → min(0.60, 0.25 + (andar-5)*0.04)
ratio_especial(andar) = min(0.60, 0.40 + (andar-5)*0.02)
```

Vale para campanha **e** infinito (a geração é por andar). Até o A5 nada muda.

## Calibração (Monte Carlo — config "MODERADA")

3000 runs de campanha (combate automático, pessimista) + 20k encontros/andar com
a `gerar()` real:

| Andar | Comum | Elite | Especial | Horda |
|---|---|---|---|---|
| A5  | 67% | 14% | 9%  | 10% |
| A6  | 64% | 15% | 11% | 10% |
| A10 | 50% | 20% | 20% | 10% |
| A15 | 36% | 21% | 32% | 10% |
| A20 | 37% | 21% | 32% | 10% |

**Win-rate da campanha ~estável** (≈19–20%): mais elites/especiais dão mais XP, o
herói sobe de nível mais rápido e compensa. Ou seja, a **presença** sobe sem
quebrar a dificuldade — a dificuldade extra virá das **novas habilidades** dos
inimigos (lote seguinte: Troll tira esquiva, Orc enfraquece etc.).

> Comparado a alternativas: a "AGRESSIVA" levava especiais a ~46% no fim (comuns
> quase sumiam); ficou descartada a favor da MODERADA.

## Arquivos alterados

| Arquivo | Mudança |
|---|---|
| `randongeon/jogo/entidades/inimigo.py` | constantes da rampa + `chance_elite()`/`ratio_especial()`; `gerar()` usa as funções. |
| `randongeon/tests/test_novos_inimigos.py` | **+5** testes (`TestRampaElites`). |

## Estado de testes

```
randongeon/tests/ → 593 passed, 5 skipped   (588 + 5; testes de threshold antigos seguem válidos)
api/test_api.py   → 26 passed
```
