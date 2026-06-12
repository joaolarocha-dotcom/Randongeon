# Lote J — Botão "Ver Placar" no menu principal

## Objetivo

Expor o **placar de melhores pontuações** (top-5, criado no Lote H) a partir do
menu principal. Antes, o placar só aparecia no fim da run (GameOver/Victory);
agora o jogador pode consultá-lo a qualquer momento.

## O que mudou

- Nova tela **`LeaderboardScreen`** — somente leitura: lê as pontuações via
  `getScores()` e renderiza a lista (com modo, andar, data e score), além de um
  estado vazio quando ainda não há runs registradas.
- Novo botão **"VER PLACAR"** no `MainMenuScreen`.
- Nova ação de navegação **`goToLeaderboard`** e nova tela `"leaderboard"` no
  roteamento do `gameStore`/`App`.

> O **registro** de pontuação continua exclusivamente no fim da run
> (`recordScore` em GameOver/Victory). Esta tela apenas **consome** o serviço —
> mantém a responsabilidade de escrita num único lugar.

## Pilares de POO / design aplicados

| Conceito | Como aparece |
|---|---|
| **Encapsulamento / separação de responsabilidades** | A persistência do placar fica isolada no serviço `leaderboard.ts`. A nova tela só usa a interface pública `getScores()` — não conhece a chave do localStorage nem o formato de armazenamento. Escrita (`recordScore`) e leitura (`getScores`) seguem separadas. |
| **Reuso** | O layout da lista reaproveita o padrão visual já usado no `GameOverScreen`, e o cabeçalho com "VOLTAR" segue o mesmo padrão do `SettingsScreen`. |

> Lote majoritariamente de **frontend/produto** (como o Lote G). O ganho de POO
> está em consumir o serviço encapsulado sem duplicar a lógica de armazenamento.

## Arquivos alterados

| Arquivo | Mudança |
|---|---|
| `frontend/src/screens/LeaderboardScreen.tsx` | **novo** — tela do placar (somente leitura). |
| `frontend/src/screens/MainMenuScreen.tsx` | **+** botão "VER PLACAR". |
| `frontend/src/store/gameStore.ts` | **+** tela `"leaderboard"` e ação `goToLeaderboard`. |
| `frontend/src/App.tsx` | **+** rota da tela `leaderboard`. |

## Estado de testes

```
frontend → npx tsc --noEmit: 0 erros
```
(Backend inalterado: randongeon 572 passed / 5 skipped · api 24 passed.)
