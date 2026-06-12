# 📘 Lote G — VictoryScreen + Vitória de Campanha

> Documento de estudo/revisão. Branch: `victoryscreen-LoteG`.
> Natureza: frontend (tela nova + roteamento) + pequeno adianto de backend.

---

## 1. O problema (a "tela preta")

O backend já retornava `resultado="vitoria_campanha"` ao derrotar o boss do
andar 20, mas o **frontend não tratava esse resultado** e **não existia uma tela
de vitória**:
- O `Screen` type ia só até `"game_over"`.
- O `handleCombatResult` tratava `vitoria`/`derrota`/`fuga` e jogava todo o resto
  no `else` (continua) → `vitoria_campanha` caía aí → estado quebrado = **tela preta**.

## 2. A solução

| Camada | Mudança |
|---|---|
| `api/schemas.py` | `JogadorStatus` ganha `pontuacao` (prévia do Lote H) |
| `api/main.py` | `_jogador_status` envia `jogador.pontuacao` |
| `client.ts` | `JogadorStatus` ganha `pontuacao: number` |
| `gameStore.ts` | `+ "victory"` no `Screen`; campo `victoryMsg`; ramo `vitoria_campanha` no `handleCombatResult` → `screen: "victory"`; `reset()` limpa `victoryMsg` |
| `App.tsx` | `import` + rota `{screen === "victory" && <VictoryScreen />}` |
| `screens/VictoryScreen.tsx` | **nova tela**: 🏆 VITÓRIA!, herói, "Andar 20 conquistado", nível, XP, moedas, **pontuação**, botão → `reset()` (menu principal) |

## 3. Fluxo

```
... andar 20 → boss "Coração da Masmorra"
  → ataca/esquiva → derrota o boss
  → API: resultado="vitoria_campanha" (+ jogador completo) e encerra a sessão
  → gameStore: ramo vitoria_campanha → após ~4s → screen "victory"
  → VictoryScreen mostra status finais + pontuação
  → [MENU PRINCIPAL] → reset() → main_menu
```

> No andar 20 **não dá pra fugir** do boss (Lote F): é vencer ou morrer. Então o
> jogador sempre chega a uma tela definida (vitória ou game over) — sem mais tela preta.

## 4. Validação

- **API (automatizado):** `test_derrotar_boss_andar_20_retorna_vitoria_campanha`
  (chega ao andar 20, derrota o boss → `vitoria_campanha`) e
  `test_status_inclui_pontuacao`.
- **Frontend:** `npx tsc --noEmit` → 0 erros.
- **Manual (ponta-a-ponta):** modo story, avançar até o andar 20, derrotar o
  boss → deve aparecer a VictoryScreen.

```
game logic:  pytest tests/ -q       → 561 passed, 5 skipped
API:         pytest api/test_api.py  → 23 passed   (+2 do Lote G)
frontend:    npx tsc --noEmit        → 0 erros
```

## 5. POO / notas

- Lote de **integração/frontend** — sem pilar novo. O backend só **expôs** a
  `@property pontuacao` (encapsulamento já existente do Lote A).
- **Score completo** (exibição no modo infinito, leaderboard) continua sendo o
  **Lote H** — aqui só adiantamos a exibição da pontuação na vitória.
- **Áudio:** a tela toca `bgm_victory` (se o arquivo existir; senão é silencioso,
  não quebra).

---
*Lote G — pendente de merge na `main`. Próximo: Lote H (score no modo infinito).*
