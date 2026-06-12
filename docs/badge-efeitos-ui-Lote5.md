# Lote 5 — Badge de efeitos de status na UI

## Objetivo

Dar **feedback visual** dos status ativos do jogador na tela de combate. Antes, o
jogador sofria veneno/fraqueza/esquiva-reduzida (Lotes M/B2) e carregava o dom
(Lote 3) sem nenhum indicador — só o texto do diálogo avisava, e só no turno em
que o efeito era aplicado. Agora há **badges** persistentes mostrando o que está
ativo e por quantos turnos.

## O que mudou

### Backend (expor os efeitos no contrato)

- **`api/schemas.py`** — novo modelo `EfeitoAtivo {tipo, turnos}` e quatro campos
  em `JogadorStatus`:
  - `efeitos: List[EfeitoAtivo]` — efeitos temporários ativos (veneno/fraqueza/
    esquiva-reduzida) com turnos restantes;
  - `lifesteal`, `dom`, `evasao_passiva` — passivos (Lote 3) para a UI.
- **`api/main.py`** — `_jogador_status()` monta `efeitos` a partir de
  `jogador.efeitos` (só os `ativo()`), e repassa os passivos. `veneno_turnos`
  (Lote M) foi mantido por compatibilidade.

O modelo de domínio **não mudou** — apenas passou a ser exposto. Os efeitos já
viviam como `EfeitoStatus` na lista `jogador.efeitos` (Lote B2); o `tipo`/`turnos`
de cada um alimenta o badge.

### Frontend (renderizar os badges)

- **`components/battle/StatusBadges.tsx`** (novo) — recebe o `JogadorStatus` e
  renderiza pílulas: ☠️ VENENO (Nx), 💪 FRACO (Nx), 💫 ZONZO (Nx), e ⭐ + nome do
  dom (cobre lifesteal/Ágil etc.). Não renderiza nada se não houver efeitos nem
  dom.
- **`components/battle/PlayerStatusBox.tsx`** — passa a renderizar
  `<StatusBadges>` abaixo da barra de EXP.
- **`api/client.ts`** — interface `EfeitoAtivo` + campos novos em `JogadorStatus`
  (opcionais, para tolerar respostas antigas).

## Pilar de POO

Reaproveita o **polimorfismo** do sistema de `EfeitoStatus`: a API serializa
qualquer efeito da lista lendo só `tipo`/`turnos` da base, sem saber o efeito
concreto. O frontend só **consome** o contrato (separação de camadas).

## Verificação

- `npx tsc --noEmit` → **0 erros**.
- `api/test_api.py` → **33 passed** (+3: lista vazia sem efeitos; veneno+fraqueza
  aparecem com turnos; dom/lifesteal expostos).
- `randongeon/tests/` → 647 passed (modelo de domínio inalterado).
- O badge em si é presentacional e type-safe; o render ao vivo depende de subir
  frontend + API (o preview local tem o atrito conhecido do caminho do `npm` com
  espaços). Contrato coberto por testes de API.

## Arquivos alterados

| Arquivo | Mudança |
|---|---|
| `api/schemas.py` | `EfeitoAtivo` + campos `efeitos`/`lifesteal`/`dom`/`evasao_passiva` no `JogadorStatus`. |
| `api/main.py` | `_jogador_status()` monta `efeitos` + passivos. |
| `api/test_api.py` | +3 testes (classe `TestEfeitosNoStatus`). |
| `frontend/src/components/battle/StatusBadges.tsx` | **novo** — pílulas de status. |
| `frontend/src/components/battle/PlayerStatusBox.tsx` | renderiza `StatusBadges`. |
| `frontend/src/api/client.ts` | `EfeitoAtivo` + campos novos no `JogadorStatus`. |

## Estado de testes

```
randongeon/tests/ → 647 passed, 5 skipped
api/test_api.py   → 33 passed   (+3 do Lote 5)
frontend          → tsc --noEmit: 0 erros
```
