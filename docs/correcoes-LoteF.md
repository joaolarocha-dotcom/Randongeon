# 📘 Lote F — Correções e Ajustes (pós-teste)

> Documento de estudo/revisão. Branch: `correcoes-LoteF`.
> Natureza: correção de bugs encontrados no teste manual + 2 sugestões.

---

## 1. Bugs corrigidos

| # | Bug relatado | Causa-raiz | Correção |
|---|---|---|---|
| 1 | "Goblin" e "bando goblin" iguais | Os goblins do bando se chamavam `"Goblin"` e `"Bando de Goblins"` estava na lista de **comuns** | Goblins do bando agora se chamam **"Bando de Goblins"**; tirei esse nome dos comuns (virou "Aranha Gigante") |
| 2 | Ninguém dropa item | O loot era **auto-aplicado** (`item.usar()`) e sumia, nunca ia ao inventário | Loot agora vai pro **inventário** (`jogador.adicionar_item`) + mensagem `✨ X caiu no chão!` |
| 3 | Nosferatu não cura | A cura era **silenciosa** e havia um heal **errado** (curava quando o player batia nele) | Mantido só o lifesteal correto (cura ao **atacar**) + mensagem `drenou X de vida!`; removido o heal errado |

## 2. Sugestões implementadas

- **Itens iniciais:** toda run (qualquer modo) começa com **2 itens básicos**
  (Poção de Cura Pequena `+4 hp`, Punhal Gasto `+1 atk`) — em `create_session`.
- **Fuga do boss na campanha:** a cada boss a fuga fica mais difícil
  (`modificador_fuga = -0.15 * (andar // 5)`); no **andar 20 a fuga é
  impossível** — vencer ou morrer. Isso também evita o cenário da tela preta
  ao fugir do boss final.

## 3. Arquivos

```
M  randongeon/jogo/entidades/inimigo.py     (NOMES_DIFICULDADE_1; nome do bando)
M  api/session.py                           (itens iniciais em create_session)
M  api/main.py                              (loot->inventário; lifesteal Nosferatu; fuga do boss)
M  randongeon/tests/test_novos_inimigos.py  (nome do bando + comum distinto)
M  api/test_api.py                          (itens iniciais; +TestCorrecoesLoteF)
A  docs/correcoes-LoteF.md
```

## 4. Verificação

```
game logic:  pytest tests/ -q       → 561 passed, 5 skipped
API:         pytest api/test_api.py  → 21 passed   (+5 do Lote F)
```

## 5. Observações importantes (fora do escopo deste lote)

- **Score:** ainda **não implementado** — é o próximo **Lote H** (a `@property
  pontuacao` existe mas não é exposta/exibida).
- **VictoryScreen / `vitoria_campanha`:** o frontend ainda não tem a tela de
  vitória nem trata esse resultado → é o **Lote G** (vencer o boss final ainda
  cairia em tela preta; este lote só impediu a *fuga* do boss final).
- **Balanceamento profundo** (inimigos subirem de nível por andar, rever HP por
  level, economia de loot/moedas): **lote futuro**, como combinado.
- **Sprite do bando:** os goblins usam o sprite `"Goblin"` (fallback `goblin.png`).
  Para um sprite próprio, adicione `"Bando de Goblins": s("arquivo.png", w, h)`
  em `frontend/src/assets/spriteMap.ts`.

---
*Lote F — pendente de merge na `main`. Próximo: Lote G (VictoryScreen + campanha).*
