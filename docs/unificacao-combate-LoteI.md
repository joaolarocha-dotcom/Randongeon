# Lote I — Unificação do turno de combate (`Inimigo.atacar`)

## Objetivo

Eliminar a **lógica de combate duplicada** que existia em três lugares e mover o
comportamento de ataque do inimigo para dentro da própria classe `Inimigo`.

Antes deste lote, a sequência de regras do turno do inimigo (escalada de ATK,
erro/`chance_miss`, roubo de vida/`cura_percentual`, atordoamento/`chance_atordoar`)
estava **copiada e colada** em três laços de combate diferentes:

1. `Masmorra.resolver_combate()` — combate automático (usado por testes e simuladores);
2. `Masmorra._combate_interativo()` — combate da versão CLI/terminal;
3. `api/main.py::_processar_ataque_inimigo()` — combate turno-a-turno da API REST.

Cada cópia acessava os atributos com `getattr(inimigo, 'cura_percentual', 0)`
defensivo — justamente porque a lógica vivia **fora** do objeto que era dono dos dados.

## O que mudou

### Novo método: `Inimigo.atacar(alvo) -> dict`
`randongeon/jogo/entidades/inimigo.py`

O inimigo agora executa o próprio turno e **reporta** o que aconteceu, sem mexer
em estado externo (atordoamento do jogador, logs de tela):

```python
relatorio = inimigo.atacar(jogador)
# {
#   "dano":      int,   # dano efetivo causado (0 se errou)
#   "errou":     bool,  # errou o ataque (chance_miss)
#   "curou":     int,   # HP recuperado por roubo de vida (Nosferatu)
#   "atordoou":  bool,  # atordoou o alvo neste turno (Banshee)
#   "subiu_atk": int,   # quanto o ATK escalou neste turno
# }
```

Os três laços de combate passaram a **chamar `inimigo.atacar(alvo)`** e apenas
reagir ao relatório (montar mensagem na tela / atualizar estado da sessão).
A regra de negócio existe **uma vez só**.

## Pilares de POO aplicados (base: slides da disciplina)

| Pilar | Como aparece |
|---|---|
| **Encapsulamento** | O inimigo é o DONO das suas mecânicas de turno. Os `getattr(...)` defensivos sumiram dos chamadores: a lógica e os dados ficam juntos, dentro de `Inimigo`. |
| **Abstração** | Quem combate (CLI, API, automático) chama `inimigo.atacar(alvo)` sem conhecer as regras internas de cada tipo de inimigo. A interface esconde a implementação. |
| **Polimorfismo** | A mesma chamada `atacar()` serve para qualquer subclasse — `Nosferatu` rouba vida, `Banshee` atordoa, comum só bate — guiada pelos atributos da instância, **sem `if` por tipo concreto**. |
| **Herança** | `atacar()` é definido na base `Inimigo` e herdado por `Nosferatu`, `GolemDePedra`, `Banshee`, `HordaDeGoblins`, `Goblin` sem reescrita. |

> Observação de projeto: o método **não decide** sobre estado externo
> (atordoamento do jogador, mensagens). Ele só aplica o efeito e devolve um
> relatório — separação de responsabilidades (lógica ≠ apresentação), o mesmo
> princípio já usado em `GeradorSala` e `Loja.comprar()`.

## Arquivos alterados

| Arquivo | Mudança |
|---|---|
| `randongeon/jogo/entidades/inimigo.py` | **+** método `Inimigo.atacar(alvo)`. |
| `randongeon/jogo/sistemas/masmorra.py` | `resolver_combate()` e `_combate_interativo()` passam a delegar o turno do inimigo a `atacar()`. Mensagens da CLI preservadas. |
| `api/main.py` | `_processar_ataque_inimigo()` delega a `atacar()`. **Assinatura e mensagens preservadas** (inclui o `"drenou"`). |
| `randongeon/tests/test_novos_inimigos.py` | **+** `TestAtacar` (6 testes: alvo None, acerto, erro, lifesteal, atordoamento, escala de ATK). |

## Compatibilidade

- Comportamento idêntico ao anterior — a ordem das regras e as probabilidades
  foram preservadas. A assinatura pública `_processar_ataque_inimigo(state,
  inimigo, mensagem) -> (dano, errou, msg)` continua igual (há teste que a importa
  diretamente).

## Estado de testes

```
randongeon/tests/  → 572 passed, 5 skipped   (era 566 + 6 novos de TestAtacar)
api/test_api.py    → 24 passed
```
