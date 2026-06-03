# Correção — Robustez de sessão (campanha "travada" + Desistir)

## Sintomas relatados

1. **Campanha travada:** ao iniciar uma run e clicar em AVANÇAR, o jogador
   ficava preso no andar, "sem avançar nada".
2. **Botão DESISTIR sem efeito**, embora "Menu → Sair sem salvar" funcionasse.

## Causa raiz

As sessões da API vivem **em memória** (`session.py`). Quando o backend
reinicia (ex.: `uvicorn --reload` ao editar/testar durante o desenvolvimento),
as sessões somem, mas o frontend mantém o `sessionId` antigo. As chamadas então
recebem **HTTP 404** ("Sessão não encontrada"), e os `catch` do `gameStore`
apenas guardavam o erro sem reagir:

- `advance()` → caía no `catch`, nada avançava → **"travado no andar"**.
- `quit()` (DESISTIR) → caía no `catch` e **não ia para o game over** → **sem efeito**.
- `exitToMainMenu()` (Menu → Sair sem salvar) já ignorava o erro e resetava de
  qualquer forma → por isso *esse* funcionava.

Isso também explica por que o bug "sumia" ao recarregar a página: o reload cria
uma sessão nova.

> Verificado por teste direto: com sessão válida `/quit` → 200; com sessão
> inexistente `/advance` e `/quit` → **404**.

## Correção (frontend)

- `client.ts`: novo `ApiError` que carrega o `status` HTTP + helper
  `isSessionLost(e)` (true quando 404).
- `gameStore.ts`: todas as ações que dependem da sessão (`advance`, ataques de
  combate, uso de item, baú, loja, `quit`) passam a detectar a perda de sessão e
  **recuperam para o menu principal** com um aviso, em vez de travar.
- `quit()` (DESISTIR) ficou **sempre funcional**: encerra para o game over com
  sessão válida; com sessão perdida volta ao menu com aviso; e em qualquer outra
  falha ainda encerra a run (nunca fica sem efeito).
- `MainMenuScreen.tsx`: passa a exibir o aviso (`error`) — antes só
  Title/LoadGame mostravam.

## Como verificar

1. Inicie uma run (campanha ou infinito).
2. Reinicie o backend (`uvicorn`) — isso descarta a sessão em memória.
3. Clique AVANÇAR (ou DESISTIR): em vez de travar, o jogo volta ao menu
   principal com a mensagem *"Sua sessão expirou…"*.
4. Com o backend estável, AVANÇAR e DESISTIR funcionam normalmente.

## Arquivos alterados

| Arquivo | Mudança |
|---|---|
| `frontend/src/api/client.ts` | `ApiError` (com `status`) + `isSessionLost()`. |
| `frontend/src/store/gameStore.ts` | recuperação de sessão perdida nas ações; `quit()` robusto. |
| `frontend/src/screens/MainMenuScreen.tsx` | exibe o aviso de sessão expirada. |

## Estado de testes

```
frontend → npx tsc --noEmit: 0 erros
```
(Backend inalterado.)
