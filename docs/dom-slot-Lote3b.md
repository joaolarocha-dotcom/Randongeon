# Lote 3b — Seleção de dom no início da run (frontend)

## Objetivo

Front da escolha de dom (o backend veio no 3a): na tela de criação da run, o
jogador escolhe **um dom** (ou nenhum), que é enviado ao `/game/new`.

## O que mudou

- `frontend/src/data/doms.ts` (novo): lista dos doms (id/nome/descrição),
  espelhando o registro do backend.
- `TitleScreen.tsx`: novo seletor de dom (botões "NENHUM" + 5 doms), com o
  selecionado destacado e a descrição do dom em foco exibida. A escolha é
  passada para `startGame(nome, dom)`.
- `gameStore.startGame(nome, dom?)` e `api.newGame(nome, modo, dom)` passam o
  `dom` (id ou `null`) adiante.

## Fluxo

Título → digita o nome → escolhe um dom (ou NENHUM) → INICIAR → `/game/new`
recebe o `dom` e aplica os modificadores (3a). O dom persiste no save.

## Arquivos alterados

| Arquivo | Mudança |
|---|---|
| `frontend/src/data/doms.ts` | **novo** — lista de doms para a UI. |
| `frontend/src/screens/TitleScreen.tsx` | seletor de dom + descrição. |
| `frontend/src/store/gameStore.ts` | `startGame(nome, dom?)`. |
| `frontend/src/api/client.ts` | `newGame(nome, modo, dom)`. |

## Estado de testes

```
frontend → npx tsc --noEmit: 0 erros
backend  → inalterado (627 passed / 5 skipped, API 30)
```

> O contrato (`/game/new` com `dom`) já é coberto pelos testes do Lote 3a.
