# Lote 4b — Coração da Masmorra: 2ª fase (frontend)

## Objetivo

Fechar o ciclo da 2ª fase do boss final no **frontend**. O backend (Lote 4a) já
faz o Coração renascer 1× e devolve `resultado="renasceu"` na resposta de
combate. Aqui a tela de combate passa a **tratar esse resultado**: não abrir a
tela de Vitória, mostrar o boss **voltando a ~50%** do HP e sinalizar a **fúria**
(2ª fase) com um aviso visual.

Frontend puro — **nenhuma mudança de backend/schema** neste lote.

## O que mudou

- **`store/gameStore.ts`**
  - Novo estado `bossEnraged: boolean` (default `false`).
  - `handleCombatResult` ganhou um ramo dedicado para `resultado === "renasceu"`:
    - **não** dispara a Victory (continua sendo um ramo separado de
      `vitoria`/`vitoria_campanha`);
    - liga `bossEnraged = true` e enfileira o texto sombrio de renascimento;
    - SFX dramático: `sfx_enemy_defeat` (o golpe derruba o boss) seguido de
      `sfx_level_up` ~450 ms depois (o boss ressurge em fúria);
    - volta ao `idle` quando o diálogo esvazia (mesmo fallback do `continua`),
      então a luta prossegue normalmente na 2ª fase.
  - A barra de HP do inimigo **sobe** rumo a `inimigo.hp` (50%) — lê-se como o
    boss "ressurgindo a meia-vida".
  - `bossEnraged` é **resetado** ao iniciar qualquer combate novo (`advance`) e no
    `reset()` da run.
- **`components/battle/EnemyStatusBox.tsx`** — prop opcional `enraged`; quando
  ligada, mostra um badge **🔥 FÚRIA** ao lado do nome do boss.
- **`screens/CombatScreen.tsx`** — lê `bossEnraged` do store e repassa para o
  `EnemyStatusBox`.

## Fluxo (campanha, andar 20)

1. Jogador zera o HP do Coração → API responde `resultado="renasceu"` com o boss
   já a 50% e em fúria (ATK ×1.25).
2. Frontend mostra o texto de renascimento + SFX, a barra sobe a 50%, surge o
   badge **🔥 FÚRIA**, e o menu de ações volta — a luta continua.
3. Jogador zera o HP de novo → API responde `resultado="vitoria_campanha"` →
   tela de Vitória (fluxo já existente, Lote G).

## Pilar de POO (frontend)

O frontend só **consome** o contrato do backend: reage ao novo valor de
`resultado` sem saber nada sobre `CoracaoDaMasmorra` nem sobre a regra de
renascimento (que vive encapsulada no modelo). Mesma separação de camadas dos
outros lotes — a UI é apresentação, a regra é do domínio.

## Verificação

- `npx tsc --noEmit` → **0 erros**.
- Suítes de backend (base da branch, inalteradas): `randongeon/tests/` 638
  passed, `api/test_api.py` 30 passed.
- O caminho visual completo (renascer no andar 20) exige uma run inteira contra a
  API real; foi validado por tipos + revisão. O `resultado="renasceu"` em si já é
  coberto por teste no backend (Lote 4a).

## Arquivos alterados

| Arquivo | Mudança |
|---|---|
| `frontend/src/store/gameStore.ts` | estado `bossEnraged`; ramo `renasceu` em `handleCombatResult`; resets. |
| `frontend/src/components/battle/EnemyStatusBox.tsx` | prop `enraged` + badge 🔥 FÚRIA. |
| `frontend/src/screens/CombatScreen.tsx` | repassa `bossEnraged` ao status do inimigo. |

## Estado do roadmap

Lote 4 (2ª fase do Coração) **concluído** — 4a (backend) + 4b (frontend).
Próximos: ★ Recalibração, Lote 5 (badge de efeitos na UI), Lote 6 (tutorial),
Lote 7 (auditoria de POO).
