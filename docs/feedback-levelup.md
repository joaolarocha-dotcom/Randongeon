# Lote (feedback) — Anúncio de level-up + barra de XP correta

## Problema

Ao acumular XP e subir de nível, o jogador é **curado** (60% do HP máx) e ganha
ATK/HP/esquiva — mas **nada no jogo dizia isso**. A vida "voltava do nada" e o
jogador não entendia o que aconteceu. Pior: a tela de combate mostrava o nível
estimado por `xp/50`, que **diverge** da curva real de progressão (triangular,
`10·N·(N+1)`) — então o "L" exibido e a barra de XP ficavam errados.

## Solução

### Backend

- **`jogador.py`**
  - `ganhar_xp()` agora **retorna quantos níveis** o herói subiu (0 se nenhum) —
    antes descartava o resultado de `_atualizar_nivel()`.
  - `mensagem_level_up(nome, novo_nivel, niveis)` — função de módulo (mesmo padrão
    de `mensagem_veneno`) com o texto comemorativo, reusada por API e CLI.
  - `progresso_nivel()` → `(xp_no_nivel, xp_total_do_nivel)` usando a **curva
    real**, para a barra de XP da UI.
- **`api/main.py`** — `_resolver_derrota_inimigo()` captura os níveis ganhos no
  `ganhar_xp()` e **anexa a mensagem** comemorativa (vale para vitória, vitória de
  campanha e cada goblin do bando). `_jogador_status()` expõe
  `xp_nivel_atual`/`xp_nivel_total`.
- **`api/schemas.py`** — `JogadorStatus` ganhou `xp_nivel_atual`/`xp_nivel_total`.
- **`masmorra.py` (CLI)** — `resolver_combate()` imprime a mesma mensagem ao subir.

### Frontend

- **`PlayerStatusBox.tsx`** — passa a usar o **nível real** (`jogador.nivel`) e a
  barra de XP com `xp_nivel_atual/total` (a estimativa `xp/50` foi removida).
- **`gameStore.ts`** — detecta o level-up comparando o `nivel` antes/depois do
  combate e toca o jingle `sfx_level_up`. A mensagem já chega em `res.mensagem`.
- **`client.ts`** — `JogadorStatus` ganhou os campos `xp_nivel_atual/total`.

A mensagem ("⭐ PARABÉNS! … subiu para o nível N! Vida recuperada e ATK, HP máximo
e esquiva aumentados!") aparece no diálogo de combate junto do XP ganho.

## Pilar de POO

- **Encapsulamento:** a regra de quanto falta para o próximo nível vive em
  `progresso_nivel()` (curva única), não mais duplicada/estimada na UI.
- **Reuso (função de módulo):** `mensagem_level_up()` é a fonte única do texto
  para API e CLI — mesma decisão dos textos de veneno/fraqueza.

## Verificação

- `npx tsc --noEmit` → **0 erros**.
- `randongeon/tests/` → **656 passed** (+9: retorno de `ganhar_xp`,
  `progresso_nivel`, `mensagem_level_up`).
- `api/test_api.py` → **35 passed** (+2: barra de XP no status; combate que sobe
  de nível anuncia "PARABÉNS").

## Arquivos alterados

| Arquivo | Mudança |
|---|---|
| `randongeon/jogo/entidades/jogador.py` | `ganhar_xp` retorna níveis; `progresso_nivel()`; `mensagem_level_up()`. |
| `randongeon/jogo/sistemas/masmorra.py` | CLI imprime o level-up. |
| `api/main.py` | anuncia level-up no fluxo de morte; expõe progresso de XP. |
| `api/schemas.py` | `xp_nivel_atual`/`xp_nivel_total` no `JogadorStatus`. |
| `frontend/src/components/battle/PlayerStatusBox.tsx` | nível real + barra de XP correta. |
| `frontend/src/store/gameStore.ts` | SFX de level-up ao subir. |
| `frontend/src/api/client.ts` | campos de progresso de XP. |
| `randongeon/tests/test_levelup_feedback.py` (novo), `api/test_api.py` | +11 testes. |

## Estado de testes

```
randongeon/tests/ → 656 passed, 5 skipped
api/test_api.py   → 35 passed
frontend          → tsc --noEmit: 0 erros
```
