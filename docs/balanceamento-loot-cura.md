# Balanceamento — Mais loot + cura parcial no level-up

> Recriado limpo sobre a `main` atual (a branch antiga `balance-loot-cura` ficou
> com conflitos depois que Lote 2 / crítico / evasão / dom entraram). Mesmas
> mudanças, sem conflito.

## Objetivo

Tirar o "peso zero" do pós-boss: o herói não é totalmente restaurado de graça ao
subir de nível; precisa **gerenciar recursos** (poções/loot). Compensa com **mais
loot**.

## Achado que guiou

Não existe "regeneração ao derrotar boss" separada — a única cura por progresso é
a **cura total ao subir de nível**. Como o boss dá muito XP → sobe de nível →
curava 100%. Logo, o ajuste é na cura de level-up.

## Mudanças (constantes tunáveis)

| Constante | Antes | Agora | Onde |
|---|---|---|---|
| Cura ao subir de nível | 100% do HP máx | **60%** (`Jogador.CURA_NIVEL_FRACAO`) | `jogador.py` |
| Drop de comuns/elites | 0.10 | **0.15** (`CHANCE_DROP_PADRAO`) | `inimigo.py` |
| Sala com item | 10% (sorte 4-5) | **15%** (sorte 4-6, `SORTE_MAX_ITEM`) | `gerador.py` |

Comuns/elites (inclusive Orc/Troll/Esqueleto) dropam mais; especiais e boss
mantêm suas taxas próprias.

## Calibração (Monte Carlo — 4000 campanhas, combate automático pessimista)

| Config | Vitória campanha | Mortes por boss (A5·A10·A15·A20) |
|---|---|---|
| ATUAL (pré-balance) | 22,9% | 71% · 2% · 2% · 1% |
| **PROPOSTO** | 20,2% | 73% · 3% · 1% · 2% |

Ajuste sutil (~−2,7pp): a cura parcial endurece, o loot extra compensa. No jogo
real (Esquivar + uso estratégico de poções) o loot vale ainda mais e a cura
parcial cria a tensão de recursos desejada — sem quebrar a vitória.

## Arquivos alterados

| Arquivo | Mudança |
|---|---|
| `randongeon/jogo/entidades/jogador.py` | `CURA_NIVEL_FRACAO`; cura parcial no level-up. |
| `randongeon/jogo/entidades/inimigo.py` | `CHANCE_DROP_PADRAO`; comuns/elites/Orc/Troll usam-no. |
| `randongeon/jogo/sistemas/gerador.py` | `SORTE_MAX_LOJA`/`SORTE_MAX_ITEM`; item 10%→15%. |
| `randongeon/tests/*` | cura parcial; sala-item ampliada; drop de comum; ajuste do teste de inimigo (randint 6→7). |

## Estado de testes

```
randongeon/tests/ → 629 passed, 5 skipped
api/test_api.py   → 30 passed
```
