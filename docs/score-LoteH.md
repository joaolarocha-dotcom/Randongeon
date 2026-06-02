# 📘 Lote H — Sistema de Score + Placar Local

> Documento de estudo/revisão. Branch: `score-LoteH`.
> Natureza: regra de jogo (score) + frontend (placar local).

---

## 1. O que mudou

O modo infinito (e a campanha) agora têm um **score de run** e um **placar local**
(top-5) — o "comparativo de competição" pedido.

- **Fórmula:** `score = jogador.pontuacao + andar × 100`
  (onde `pontuacao = xp + (nível-1)·50 + moedas`). O peso do **andar** faz ir mais
  fundo no infinito valer muito mais — um bom critério competitivo.
- O score aparece no **game over** (fim de run do infinito) e na **VictoryScreen**.
- As melhores runs ficam num **placar local** (`localStorage`), com destaque de
  **🏆 NOVO RECORDE!**.

## 2. Onde cada parte vive

| Camada | Mudança |
|---|---|
| `masmorra.py` | **`calcular_score()`** — `jogador.pontuacao + andar*100` (regra de jogo testável) |
| `api/schemas.py` | `JogadorStatus` ganha `score` |
| `api/main.py` | `_jogador_status` envia `state.masmorra.calcular_score()` |
| `client.ts` | `JogadorStatus` ganha `score: number` |
| `services/leaderboard.ts` | **novo** — `recordScore()` / `getScores()` (top-5 no localStorage) |
| `GameOverScreen.tsx` | mostra o score, registra a run, exibe o placar + "novo recorde" |
| `VictoryScreen.tsx` | mostra o score e registra a run vitoriosa |

## 3. POO / decisões

- A **fórmula do score é regra de jogo** → ficou num método de `Masmorra`
  (`calcular_score`), que tem acesso ao `jogador` (pontuação) **e** ao `andar`.
  Fonte única, testável no game logic. A API só **expõe** o valor.
- **Encapsulamento:** a API e o frontend consomem o score pela interface
  (`calcular_score()` / campo `score`), sem reimplementar a fórmula.
- O placar é **frontend puro** (`localStorage`), seguindo o padrão do `saveService`.
- Nenhum conteúdo fora dos slides.

## 4. Verificação

```
game logic:  pytest tests/ -q       → 564 passed, 5 skipped  (+3 TestCalcularScore)
API:         pytest api/test_api.py  → 24 passed              (+1 score no status)
frontend:    npx tsc --noEmit        → 0 erros
```

**Manual:** jogue o modo infinito até morrer → o game over mostra a **pontuação**
e o **placar**; repita para ver o ranking e o "novo recorde".

## 5. Possíveis evoluções (futuro)

- Botão "Ver placar" no menu principal (hoje o placar só aparece no fim da run).
- Fórmula com turnos (`andares × xp/turnos`, como no Roadmap) — exigiria contar
  turnos, que hoje não são rastreados.

---
*Lote H — pendente de merge na `main`. Restam: higiene (.gitignore) e o
balanceamento profundo (inimigos por andar, HP/level, economia de loot).*
