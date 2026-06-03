# Lote — Save/Carregar run em arquivo .txt

## Objetivo

Permitir **exportar a run atual para um arquivo `.txt`** (campanha ou infinito) e
**importá-lo depois** para retomar exatamente de onde parou — mesmo após fechar o
jogo. Salva vida, andar, status, moedas, XP, nível, inventário **e o veneno**.

## O que já existia x o que mudou

O projeto já tinha exportação/importação (`saveService.ts` + `LoadGameScreen`),
mas: exportava como **`.json`**, **não incluía o veneno**, e só dava para
exportar **a partir de um slot salvo** (não a run ao vivo). Ajustes:

### Backend (`api/main.py`)
- `/game/{id}/save` passou a incluir **`veneno_turnos`** no estado serializado.
- `/game/load` **restaura `veneno_turnos`** no jogador (limitado ao teto
  `Jogador.VENENO_DURACAO`).

### Frontend
- `saveService.ts`: `exportSaveToFile` agora gera um **`.txt`** (conteúdo JSON,
  `text/plain`). O `importSaveFromFile` lê pelo conteúdo, então aceita `.txt`
  (e ainda `.json` antigo).
- `LoadGameScreen.tsx`: rótulo e `accept` do import atualizados para `.txt`.
- `MenuScreen.tsx`: novo botão **"⬇ .TXT"** (no painel SALVAR) que **exporta a
  run atual direto para arquivo**, sem precisar salvar num slot antes.

## Fluxo de uso

1. Numa run → **SALVAR** → **⬇ .TXT** → baixa `randongeon_<nome>_andar<N>.txt`.
2. Mais tarde → menu principal → **CARREGAR JOGO** → **IMPORTAR ARQUIVO .txt** →
   escolhe o arquivo → a run é restaurada (vai para um slot livre) → **CARREGAR**.

## Arquivos alterados

| Arquivo | Mudança |
|---|---|
| `api/main.py` | `veneno_turnos` no save e no load. |
| `frontend/src/services/saveService.ts` | export em `.txt`. |
| `frontend/src/screens/LoadGameScreen.tsx` | import aceita `.txt`. |
| `frontend/src/screens/MenuScreen.tsx` | botão "⬇ .TXT" exporta a run atual. |
| `api/test_api.py` | **+1** teste (round-trip do veneno no save/load). |

## Estado de testes

```
api/test_api.py → 26 passed   (25 + 1)
frontend        → npx tsc --noEmit: 0 erros
randongeon/tests → inalterado (588 passed, 5 skipped)
```
