# Lote M — Veneno (dano por turno / DoT)

## Objetivo

Adicionar um efeito de **veneno** ao jogo, na mesma linha das mecânicas de tipo
(lifesteal do Nosferatu, armadura do Golem): **apenas Goblin e Rato Gigante**
têm uma chance pequena de envenenar o jogador ao acertar um golpe.

Regras:
- Veneno causa **1 de dano por turno**, por no **máximo 3 turnos**
  (`Jogador.VENENO_DURACAO`).
- O estado vive **no jogador**, então **persiste entre andares** — sai de uma
  luta envenenado e continua corroendo na próxima.
- Cura: **usar uma poção de cura** (qualquer item com `bonus_hp > 0`) **ou subir
  de nível** remove o veneno.
- Não acumula: uma nova picada apenas **renova** a duração para o teto.

## Calibração (simulação Monte Carlo)

20 000 encontros comuns por configuração (`sim` inline sobre as classes do jogo):

| Chance | Dano médio de veneno / encontro | % de encontros que envenenam ≥1x |
|---|---|---|
| 5%  | 0,10 HP | 3,3% |
| **8% (escolhido)** | **0,16 HP** | **5,4%** |
| 12% | 0,26 HP | 8,5% |

Escolhido **`CHANCE_VENENO = 0.08`**: raro mas perceptível, sem distorcer o
balanceamento (impacto < 0,2 HP por encontro em média). Trocar é uma linha em
`inimigo.py`.

## Design / Pilares de POO

| Pilar | Como aparece |
|---|---|
| **Encapsulamento** | O estado e as regras do veneno ficam no `Jogador` (`envenenar`, `curar_veneno`, `tick_veneno`, `@property envenenado`). Os laços de combate só chamam esses métodos. |
| **Polimorfismo / reuso** | O envenenamento entra no `Inimigo.atacar()` (Lote I) como mais um campo do relatório (`envenenou`), igual a `curou`/`atordoou`. Os 3 laços de combate (automático, CLI, API) reagem ao relatório sem `if` por tipo. |
| **Abstração** | `atacar()` só **reporta** que envenenou; quem cuida do combate aplica `jogador.envenenar()`. O inimigo não conhece o estado interno do jogador. |

### Quando o veneno "tica"
O veneno de turnos **anteriores** age no início da troca de golpes (quando o
inimigo tem seu turno). A picada nova de uma rodada só começa a corroer no
**turno seguinte** — evita dano dobrado no mesmo turno em que é aplicado. A morte
por veneno é tratada pelas checagens de `hp <= 0` que já existiam após o turno
do inimigo.

## Arquivos alterados

| Arquivo | Mudança |
|---|---|
| `randongeon/jogo/entidades/jogador.py` | `veneno_turnos`, `VENENO_DURACAO`, `envenenar()`, `curar_veneno()`, `tick_veneno()`, `@property envenenado`; cura ao subir de nível. |
| `randongeon/jogo/entidades/item.py` | poção de cura (`bonus_hp > 0`) purga o veneno. |
| `randongeon/jogo/entidades/inimigo.py` | `chance_veneno` + `CHANCE_VENENO`/`NOMES_PODEM_ENVENENAR`; `atacar()` reporta `envenenou`; `gerar()` atribui aos comuns Goblin/Rato. |
| `randongeon/jogo/sistemas/masmorra.py` | tick + aplicação no combate automático e na CLI. |
| `api/main.py` | tick + aplicação em `_processar_ataque_inimigo`; `veneno_turnos` em `_jogador_status`. |
| `api/schemas.py` | `JogadorStatus.veneno_turnos`. |
| `frontend/src/api/client.ts` | `JogadorStatus.veneno_turnos?`. |
| `conftest.py`, `tests/test_masmorra.py`, `tests/test_novos_inimigos.py` | dummies via `__new__` recebem `chance_veneno = 0.0`. |
| `tests/test_jogador.py`, `tests/test_novos_inimigos.py` | **+13 testes** (estado de veneno + envenenamento no `atacar`). |

## Estado de testes

```
randongeon/tests/ → 585 passed, 5 skipped   (572 + 13 novos)
api/test_api.py   → 24 passed
frontend          → npx tsc --noEmit: 0 erros
```

> O estado `veneno_turnos` já é exposto no `JogadorStatus`. O **Lote N (save em
> arquivo)** vai incluí-lo no `.txt` para que o veneno sobreviva ao fechar/abrir
> o jogo, como combinado.
