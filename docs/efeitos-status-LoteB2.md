# Lote B2 — Sistema de `EfeitoStatus` + debuffs de Troll e Orc

## Objetivo

Sobre a base `Entidade(ABC)` (B1), criar um **sistema de efeitos de status**
(classe base + subclasses, Polimorfismo), migrar o **veneno** para ele e usá-lo
para dois debuffs novos de elite:
- **Orc** → **Fraqueza** (reduz o ATK do jogador por alguns turnos).
- **Troll das Cavernas** → reduz a **esquiva** do jogador (golpe de maça, 1 turno).

## Arquitetura

`jogo/entidades/efeitos.py` (novo):

```python
class EfeitoStatus(ABC):          # base com hooks neutros (Polimorfismo)
    tipo; remove_ao_curar; turnos
    ao_iniciar_turno(portador) -> int   # DoT
    modifica_atk(atk) -> int
    modifica_esquiva(esq) -> float

class Veneno(EfeitoStatus):           # DoT 1/turno, sai ao curar/subir nível
class Fraqueza(EfeitoStatus):         # modifica_atk: −reducao (mínimo 1)
class EsquivaReduzida(EfeitoStatus):  # modifica_esquiva: −reducao (mínimo 0)
```

`Entidade` ganhou a lista `efeitos` e os métodos `aplicar_efeito` (renova, não
empilha), `buscar_efeito`, `remover_efeitos`, `processar_efeitos_turno`.

`Jogador` ganhou `atk_efetivo()` e `esquiva_efetiva()` (aplicam os hooks dos
efeitos sobre o ATK/esquiva base). O combate (API + CLI + automático) passou a
usar esses valores efetivos e a aplicar os debuffs reportados pelo `atacar()`.

### Veneno migrado
`veneno_turnos` virou uma `@property` derivada do efeito `Veneno`; `envenenar`,
`curar_veneno`, `envenenado` e `tick_veneno` agora delegam ao sistema de efeitos.
A API de fora ficou **idêntica** — save/load e todos os testes seguem válidos
(o `load` passou a usar `envenenar(n)` no lugar de atribuir o atributo).

## Como os debuffs entram no combate

Igual ao veneno: o `Inimigo.atacar()` **reporta** (`fraqueza`,
`esquiva_reduzida`) e o laço de combate aplica `jogador.aplicar_efeito(...)`.
- `Inimigo` ganhou `chance_fraqueza` e `chance_esquiva_debuff`.
- `Inimigo.gerar()` os atribui por nome: **Orc** → `CHANCE_FRAQUEZA` (0.30);
  **Troll das Cavernas** → `CHANCE_ESQUIVA_DEBUFF` (0.35).
- Textos próprios (`mensagem_fraqueza`, `mensagem_esquiva_reduzida`).

> ⚠️ As **chances e magnitudes** (0.30/0.35, −2 ATK por 2 turnos, −0.20 esquiva
> por 1 turno) são iniciais — vamos **calibrar na próxima rodada de
> balanceamento**, como combinado.

## Pilares de POO

| Pilar | Onde |
|---|---|
| **Abstração** | `EfeitoStatus` define a interface de um efeito; o combate não conhece o tipo concreto. |
| **Polimorfismo** | `Veneno`/`Fraqueza`/`EsquivaReduzida` sobrescrevem só o hook que importa; `processar_efeitos_turno`/`atk_efetivo`/`esquiva_efetiva` tratam todos igual. |
| **Herança** | efeitos herdam de `EfeitoStatus`; entidades herdam a lista de efeitos de `Entidade`. |
| **Encapsulamento** | estado e regras de cada efeito ficam na sua classe; a Entidade só orquestra. |

## Arquivos alterados

| Arquivo | Mudança |
|---|---|
| `jogo/entidades/efeitos.py` | **novo** — `EfeitoStatus` + Veneno/Fraqueza/EsquivaReduzida. |
| `jogo/entidades/entidade.py` | lista de efeitos + `aplicar/buscar/remover/processar`. |
| `jogo/entidades/jogador.py` | veneno migrado; `atk_efetivo`/`esquiva_efetiva`; level-up purga efeitos `remove_ao_curar`. |
| `jogo/entidades/inimigo.py` | `chance_fraqueza`/`chance_esquiva_debuff`; `atacar` reporta; `gerar` atribui a Orc/Troll; textos. |
| `jogo/sistemas/masmorra.py` | combate usa stats efetivos e aplica os debuffs. |
| `api/main.py` | idem na API; `load` restaura veneno via `envenenar()`. |
| `conftest.py` + 3 testes | dummies recebem os novos atributos; **+7** testes (`TestEfeitosDebuff`). |
| `api/test_api.py` | teste do texto do bando reescrito (robusto a misses). |

## Estado de testes

```
randongeon/tests/ → 604 passed, 5 skipped   (597 + 7)
api/test_api.py   → 26 passed
```
