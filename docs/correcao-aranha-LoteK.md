# Lote K — Correção da "Aranha Gigante"

## Diagnóstico

"Aranha Gigante" aparecia como inimigo comum (dificuldade 1), sorteada junto com
Goblin e Rato Gigante em `NOMES_DIFICULDADE_1`. Não era uma chamada de monstro
"errada" no sentido de crash, mas era um **resquício do Lote F**: quando os
goblins do bando passaram a se chamar "Bando de Goblins", esse nome foi retirado
da lista de comuns e **substituído por "Aranha Gigante"** (ver
`docs/correcoes-LoteF.md`).

O problema real: **não existe sprite de aranha** (`spriteMap.ts` só tem Goblin,
Rato e Nosferatu como comuns). Então uma "Aranha Gigante" era renderizada com o
**sprite do goblin** — nome e imagem em conflito, quebrando a imersão.

## Correção

Remoção de "Aranha Gigante" de `NOMES_DIFICULDADE_1`, que volta a ser
`["Goblin", "Rato Gigante"]` (ambos com sprite próprio). O inimigo de "grupo"
que esse nome tentava representar **já existe** de forma correta como encontro
especial: o **Bando de Goblins** (`HordaDeGoblins` → `BandoDeGoblins`), com sua
própria mecânica de 3 lutas em sequência.

## Arquivos alterados

| Arquivo | Mudança |
|---|---|
| `randongeon/jogo/entidades/inimigo.py` | `NOMES_DIFICULDADE_1` sem "Aranha Gigante" + comentário explicando o histórico. |

## Estado de testes

```
randongeon/tests/ → 572 passed, 5 skipped
```
Os testes que usam `NOMES_DIFICULDADE_1` checam pertencimento
(`Inimigo.gerar(andar=1).nome in NOMES_DIFICULDADE_1`), não a quantidade — então
seguem válidos.
