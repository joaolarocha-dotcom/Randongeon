# Lote 3a — Dom de slot único (backend)

## Objetivo

Dar identidade/variabilidade a cada run: o jogador escolhe **um dom** (passivo
permanente) na criação. Sem acúmulo e sem depender de sorte/itens — cada dom tem
um **trade-off** (lado fraco) para manter o equilíbrio.

Este lote é o **backend** (sistema + save). A **tela de seleção** vem no 3b.

## Doms (números tunáveis — base atk5/hp20/esq0.30/crít0.10)

| Dom | Efeito | Trade-off |
|---|---|---|
| **Bruto** | +3 ATK | −0.10 esquiva, −0.05 crítico |
| **Resistente** | +10 HP máx | −0.05 esquiva |
| **Ágil** | +0.10 esquiva e inimigos erram +10% (evasão passiva) | −5 HP máx |
| **Sortudo** | +0.15 crítico | −1 ATK |
| **Sanguessuga** | cura 10% do dano causado | — |

## Arquitetura

`jogo/entidades/dom.py` (novo): classe `Dom` (value object) que sabe se
**aplicar** a um Jogador, + registro `DONS` e `aplicar_dom(jogador, id)`. Quem
cria a run só chama `aplicar_dom` — POO/encapsulamento.

- `Jogador` ganhou `dom`, `lifesteal`, `evasao_passiva` (defaults neutros) e
  `aplicar_lifesteal(dano)`.
- **Lifesteal (Sanguessuga):** após o dano do jogador, cura `lifesteal × dano`
  (API/CLI/auto).
- **Evasão passiva (Ágil):** `Inimigo.atacar()` soma `alvo.evasao_passiva` à sua
  chance de errar → inimigos erram mais contra o Ágil.
- Os doms de stat (Bruto/Resistente/Sortudo) ajustam os atributos na criação.

## API & persistência

- `POST /game/new` aceita `dom` (id) → `create_session(nome, modo, dom)`.
- O save guarda `dom`, `lifesteal` e `evasao_passiva`; o load os restaura (os
  stats já vêm "baked" nos campos salvos, então não se re-aplica o dom).

## Arquivos alterados

| Arquivo | Mudança |
|---|---|
| `randongeon/jogo/entidades/dom.py` | **novo** — `Dom` + `DONS` + `aplicar_dom`. |
| `randongeon/jogo/entidades/jogador.py` | `dom`/`lifesteal`/`evasao_passiva` + `aplicar_lifesteal()`. |
| `randongeon/jogo/entidades/inimigo.py` | `atacar()` soma a evasão passiva do alvo. |
| `randongeon/jogo/sistemas/masmorra.py` | lifesteal no combate (auto + CLI). |
| `api/session.py`, `api/main.py`, `api/schemas.py` | `dom` em new game; save/load dos passivos. |
| `randongeon/tests/test_dom.py` (novo), `api/test_api.py` | **+15** testes. |

## Próximo (3b)

Tela de seleção do dom no início da run (frontend: `TitleScreen` + `client.ts`),
e expor o dom no `JogadorStatus`/UI se quisermos mostrá-lo.

## Estado de testes

```
randongeon/tests/ → 627 passed, 5 skipped
api/test_api.py   → 30 passed
```
