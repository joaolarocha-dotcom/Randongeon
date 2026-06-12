# Recalibração geral — curva de boss (config C)

## Diagnóstico (Monte Carlo da campanha inteira)

`sim_recalibracao.py` (novo) roda campanhas story completas (andares 1..20) com as
**entidades reais** e a ordem de turno da API (crítico, esquiva do inimigo,
lifesteal, veneno/fraqueza/esquiva-debuff, bando sequencial, escala de elites do
Lote B, boss de 2 fases do Lote 4, cura ao subir de nível). Mede a taxa de
vitória e **onde as runs morrem**.

**Antes da recalibração (n=5000):**

| Métrica | Valor |
|---|---|
| Vitória de campanha | **11,6%** |
| Mortes contra bosses | **87%** do total |
| Mortes no boss do **andar 5** | **61,2%** de TODAS as runs |
| Win-rate do boss A5 | **38,8%** |
| Chega ao A20 | 28% |

→ O gargalo **não** era o pré-boss (os comuns/elites quase não matavam — a escala
do Lote B está saudável). Era o **primeiro boss (A5)**, desproporcional: o herói
chega no andar 5 fraco e o **ATK 8** do boss o derruba na corrida.

## Decisão (config "C" — só ATK)

Entre as opções simuladas, foi escolhida a mais **cirúrgica**: mexer só no **ATK**
dos bosses, mantendo **todo o HP** (sensação de tanque) e o **ATK do boss final
intacto**.

- Curva de boss agora vem de constantes **tunáveis** em `masmorra.py`:
  `hp = BOSS_HP_BASE + fator*BOSS_HP_STEP` · `atk = round(BOSS_ATK_BASE + fator*BOSS_ATK_STEP)`.
- Config C: `BOSS_ATK_BASE=2`, `BOSS_ATK_STEP=3.75` (HP base/step inalterados).

| Andar | HP (igual) | ATK antes | **ATK depois** |
|---|---|---|---|
| 5 | 40 | 8 | **6** |
| 10 | 60 | 11 | **10** |
| 15 | 80 | 14 | **13** |
| 20 | 100 | 17 | **17** (intocado) |

## Resultado (n=5000)

| Métrica | Antes | Depois |
|---|---|---|
| **Vitória de campanha** | 11,6% | **21,6%** |
| Win-rate boss A5 | 38,8% | **69,9%** |
| Mortes no A5 | 61,2% | **30,1%** |
| Chega ao A20 | 28,1% | **53,6%** |
| Win-rate boss A20 | 40,7% | **40,2%** (preservado) |

Funil saudável: bosses intermediários ~70-92%, e o **boss final (2 fases) é o
decisor** (~40%) — o spike inicial sumiu sem aliviar o clímax.

## Pilar de POO

Os números de balance ficam em **constantes tunáveis** (atributos de
módulo/classe), separados da lógica de geração — mesma decisão de design dos
outros lotes de balance. A regra (`gerar_boss`) não muda; só a parametrização.

## Arquivos alterados

| Arquivo | Mudança |
|---|---|
| `randongeon/jogo/sistemas/masmorra.py` | constantes `BOSS_HP_*`/`BOSS_ATK_*`; `gerar_boss()` usa a curva tunável (config C). |
| `randongeon/sim_recalibracao.py` | **novo** — Monte Carlo da campanha inteira (diagnóstico). |
| `randongeon/tests/test_masmorra.py` | ATK dos bosses A5/A10/A15 atualizado (8→6, 11→10, 14→13). |
| `randongeon/tests/test_balance.py` | fórmula de boss + dano sofrido no A5 atualizados. |
| `api/test_api.py` | teste do boss A20 tornado determinístico (patch do `random`, era flaky). |

## Estado de testes

```
randongeon/tests/ → 656 passed, 5 skipped
api/test_api.py   → 35 passed
frontend          → sem mudança
```
