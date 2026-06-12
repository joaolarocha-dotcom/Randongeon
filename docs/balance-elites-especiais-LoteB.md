# Lote B (balance) — Escala dos elites especiais por andar

## Problema

Em teste de jogo, os elites **especiais** (Golem de Pedra, Nosferatu, Banshee)
morriam fácil demais no fim da campanha — um **Goblin comum do andar 16 tankava
mais que o Golem de Pedra**.

**Causa:** os comuns e os elites genéricos (Esqueleto/Orc/Troll) escalam HP/ATK
por andar em `Inimigo.gerar()`, mas os especiais eram instanciados **sem
argumentos** e nasciam com **stats fixas** do próprio construtor — não escalavam.
Por isso, conforme o herói cresce, os especiais viravam alvos triviais.

## Diagnóstico (medido)

`sim_elites_tank.py` (novo) mede o **TTK** — golpes médios do herói para matar
cada tipo, por andar, refletindo `gerar()` + armadura. **Antes:**

| Andar | comum | elite genérico | Golem | Nosferatu | Banshee |
|---|---|---|---|---|---|
| 16 | 2.0 | 3.7 | **1.8** | 1.0 | 1.0 |
| 20 | 2.0 | 3.7 | **1.4** | 1.0 | 1.0 |

→ No A16 o comum (2.0) já tankava mais que o Golem (1.8); Nosferatu/Banshee viram
1-shot a partir do A13. **Depois** (config escolhida):

| Andar | comum | elite | Golem | Nosferatu | Banshee |
|---|---|---|---|---|---|
| 16 | 2.0 | 3.7 | **5.0** | 4.0 | 3.7 |
| 20 | 2.0 | 3.7 | **5.0** | 4.0 | 4.0 |

Hierarquia restaurada: `comum < elite genérico ≤ especiais`, com o Golem como o
tanque do topo.

## Solução

Os construtores dos especiais ganharam **parâmetros opcionais de escala**
(`bonus_hp`, `bonus_atk`; o Golem também `bonus_armadura`), todos com **default
0** — então `GolemDePedra()`/`Nosferatu()`/`Banshee()` sem argumentos mantêm as
stats base, e os testes/uso sem andar não mudam. `Inimigo.gerar()` passa os
bônus escalados ao instanciar um especial.

### Pilar de POO

- **Herança + Polimorfismo:** os especiais continuam sendo `Inimigo`; só
  especializam o construtor (mesma estrutura dos Lotes B/C/2). A geração trata
  todos via o mesmo fluxo.
- **Encapsulamento:** a regra de escala fica nas constantes tunáveis e em
  `gerar()`; o resto do jogo (combate, loot) não muda.

### Constantes (tunáveis, calibradas por Monte Carlo)

| Constante | Valor | Efeito |
|---|---|---|
| `ESPECIAL_HP_MULTIPLICADOR` | `1.6` | bônus de HP dos especiais = `round(bonus_hp_do_andar × 1.6)` (um pouco acima do `1.4` dos elites genéricos) |
| `GOLEM_ARMADURA_PASSO` | `6` | armadura do Golem = `3 + andar // 6` (3 → 5 no A16 → 6 no A20) |

`bonus_atk` reusa a escala de ATK existente (`andar // ESCALA_ATK_DIVISOR`).

## Arquivos alterados

| Arquivo | Mudança |
|---|---|
| `randongeon/jogo/entidades/inimigo.py` | constantes `ESPECIAL_HP_MULTIPLICADOR`/`GOLEM_ARMADURA_PASSO`; params de escala em `GolemDePedra`/`Nosferatu`/`Banshee`; `gerar()` passa os bônus. |
| `randongeon/tests/test_escala_especiais.py` | **novo** — +9 testes (base intacta, params, escala via `gerar`, regressão). |
| `randongeon/sim_elites_tank.py` | **novo** — diagnóstico/medição de TTK por tipo e andar. |

## Estado de testes

```
randongeon/tests/ → 647 passed, 5 skipped   (+9 deste lote)
api/test_api.py   → 30 passed
frontend          → sem mudança (tsc inalterado)
```
