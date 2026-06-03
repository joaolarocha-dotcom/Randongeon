# Lote B1 — Base abstrata `Entidade(ABC)`

## Objetivo

Fundação do sistema de status (Lote B). Extrair a vida compartilhada por
`Jogador` e `Inimigo` para uma **classe base abstrata** `Entidade(ABC)`,
removendo duplicação e introduzindo o pilar de POO que ainda faltava no código:
**classes abstratas (`ABC` / `@abstractmethod`)**.

## O que mudou

Novo `jogo/entidades/entidade.py`:

```python
class Entidade(ABC):
    def __init__(self, nome, hp): ...   # valida nome/hp; define nome/hp_max/hp
    def esta_vivo(self) -> bool: ...    # compartilhado
    def curar(self, q) -> int: ...      # compartilhado
    @abstractmethod
    def receber_dano(self, dano) -> int: ...   # cada subclasse define
```

- `Jogador(Entidade)` e `Inimigo(Entidade)` agora **herdam** `esta_vivo()` e
  `curar()` (antes eram idênticos e duplicados nas duas classes).
- `receber_dano()` é **abstrato** e cada um implementa o seu (Polimorfismo):
  - **Inimigo**: desconta `absorcao_dano` (armadura) antes de aplicar.
  - **Jogador**: sofre o dano direto.
- A validação de `nome`/`hp` foi centralizada na base.

`BandoDeGoblins` continua **fora** da hierarquia (é composição, não é uma
`Entidade`).

## Pilares de POO

| Pilar | Como aparece |
|---|---|
| **Abstração + ABC** | `Entidade` define a interface comum e não pode ser instanciada (`receber_dano` abstrato). |
| **Herança** | `Jogador`/`Inimigo` reaproveitam vida/cura da base; sumiu a duplicação. |
| **Polimorfismo** | `receber_dano()` se comporta diferente por subclasse (armadura vs direto). |

## Escopo (e o que vem a seguir)

Este lote entrega **só a fundação `Entidade(ABC)`**, sem mudar comportamento — é
uma refatoração validada pelos ~597 testes existentes. O **sistema de
`EfeitoStatus`** (com a migração do veneno) e os **efeitos novos** (Troll →
−esquiva, Orc → fraqueza) vêm no **Lote B2**, onde múltiplos efeitos justificam o
framework.

## Correção de brinde

`test_jogador` tinha um dummy inline (criado via `__new__`) sem `chance_veneno`,
o que tornava `test_vitoria_de_combate_concede_moedas` **flaky** (quebrava só
quando o jogador errava o 1º golpe e o inimigo chegava a atacar). Atributo
adicionado ao dummy.

## Arquivos alterados

| Arquivo | Mudança |
|---|---|
| `randongeon/jogo/entidades/entidade.py` | **novo** — `Entidade(ABC)`. |
| `randongeon/jogo/entidades/jogador.py` | `Jogador(Entidade)`; remove vida duplicada; mantém `receber_dano`. |
| `randongeon/jogo/entidades/inimigo.py` | `Inimigo(Entidade)`; remove vida duplicada; `receber_dano` com armadura. |
| `randongeon/tests/test_novos_inimigos.py` | **+4** testes (`TestEntidadeBase`). |
| `randongeon/tests/test_jogador.py` | corrige dummy flaky (`chance_veneno`). |

## Estado de testes

```
randongeon/tests/ → 597 passed, 5 skipped   (593 + 4)
api/test_api.py   → 26 passed
```
