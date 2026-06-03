# Lote 2 (textos) — Bando sequencial + flavor de veneno

Dois ajustes de texto pedidos após teste manual.

## 1. Texto do Bando de Goblins (combate sequencial)

**Antes:** ao derrotar cada goblin do bando, o log dizia
*"Bando de Goblins foi derrotado! Bando de Goblins avança!"* — estranho, porque
o bando inteiro parecia morrer e ressuscitar a cada goblin.

**Agora** (`api/main.py`, `_resolver_derrota_inimigo`):
- Enquanto houver goblins na fila (intermediários):
  *"O goblin foi derrotado! Outro goblin avança rangendo os dentes!"*
- Só quando o **último** goblin tomba:
  *"O último goblin tombou — o Bando de Goblins foi derrotado!"*

O bando continua se chamando "Bando de Goblins" (sprite/identidade preservados);
mudou apenas o texto de derrota/avanço.

## 2. Flavor de veneno por inimigo

**Antes:** mensagem genérica *"{nome} foi envenenado!"*.

**Agora**, cada envenenador tem sua descrição (`inimigo.mensagem_veneno`):
- **Rato Gigante:** *"O Rato Gigante crava seus dentes imundos em você; a saliva
  contaminada arde na ferida. Você foi ENVENENADO!"*
- **Goblin:** *"A faca enferrujada e suja do Goblin te acerta de raspão e um
  mal-estar sobe pelo corpo. Você foi ENVENENADO!"*
- Fallback genérico para qualquer outro caso.

As mensagens ficam em `inimigo.py` (junto da definição dos inimigos) e são
usadas tanto pela **API** (`_processar_ataque_inimigo`) quanto pela **CLI**
(`_combate_interativo`) — fonte única, sem duplicação.

## Arquivos alterados

| Arquivo | Mudança |
|---|---|
| `api/main.py` | texto do bando sequencial; usa `mensagem_veneno()`. |
| `randongeon/jogo/entidades/inimigo.py` | `MENSAGENS_VENENO` + `mensagem_veneno()`. |
| `randongeon/jogo/sistemas/masmorra.py` | CLI usa `mensagem_veneno()`. |
| `api/test_api.py` | **+1** teste (diferenciação do texto do bando). |
| `randongeon/tests/test_novos_inimigos.py` | **+3** testes (flavor de veneno). |

## Estado de testes

```
randongeon/tests/ → 588 passed, 5 skipped   (585 + 3)
api/test_api.py   → 25 passed                (24 + 1)
```
