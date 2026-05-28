# Randongeon — Roadmap de Funcionalidades

> Documento de planejamento vivo. Cada seção descreve o escopo,
> impacto em arquivos e decisões de design pendentes.

---

## Status atual (v3.1)

| Feature | Estado |
|---|---|
| 5 inimigos especiais com mecânicas únicas | ✅ |
| Fuga variável por tipo | ✅ |
| Mecânica de miss (jogador e inimigo) | ✅ |
| Sistema de loot (drop de itens por inimigos) | ✅ |
| Balance patch de bosses | ✅ |
| Frontend: badges de tipo especial + atordoamento | ✅ |
| Frontend: miss e loot no log de combate | 🔲 |
| Save system | 🔲 |
| Menu com modos de jogo | 🔲 |
| Tutorial | 🔲 |

---

## 1. Frontend: Miss e Loot no Log de Combate

**Prioridade: alta — os campos já chegam pela API**

`CombatActionResponse` já carrega `miss_jogador`, `miss_inimigo` e `loot`.
O frontend só precisa consumi-los.

**Mudanças necessárias:**

`gameStore.ts`
- Ao receber `res.loot !== null`, adicionar entrada no log com tipo `"loot"`.
- `miss_jogador` e `miss_inimigo` já estão no response — adicionar tipo `"miss"` ao log.

`CombatScreen.tsx`
- Cor diferente para entradas de miss (cinza/amarelo fraco).
- Entrada de loot com destaque dourado e emoji de item: `✨ Item encontrado: Poção Menor de Cura!`
- O badge de loot pode aparecer brevemente no centro da tela antes de entrar no log.

---

## 2. Sistema de Save

**Prioridade: média**

### Regra de negócio definida
- Salvar preserva: `hp`, `hp_max`, `atk`, `esq`, `xp`, `moedas` (estado atual, não inicial).
- Ao **reiniciar** uma run com personagem salvo: moedas são zeradas, todos os outros atributos são mantidos.
- Ao **continuar** (carregar partida em andamento): tudo é mantido, incluindo moedas e andar atual.

### Opções de persistência (decisão pendente)
| Opção | Prós | Contras |
|---|---|---|
| JSON em disco (servidor) | simples, sem dependência | perde dados se o servidor reinicia |
| SQLite + SQLAlchemy | robusto, sem servidor externo | adiciona dependência |
| PostgreSQL (já existe no SEED) | produção-ready | overhead para MVP |

**Recomendação**: começar com SQLite para MVP. Migrar para PostgreSQL quando o projeto escalar.

### Arquivos impactados
```
api/
├── database.py     (novo) — engine SQLAlchemy + models
├── models.py       (novo) — SavedPlayer, SavedRun
├── session.py      — GameState ganha save_id opcional
└── main.py         — novos endpoints /save e /load

frontend/src/
├── api/client.ts   — saveGame(), loadGame()
├── screens/LoadScreen.tsx  (novo)
└── store/gameStore.ts — loadSave(), saveGame()
```

### Endpoints novos
```
POST /game/{id}/save         → salva estado atual da run
GET  /saves                  → lista saves disponíveis
POST /game/load/{save_id}    → carrega run em andamento
POST /game/new-from-save/{save_id}  → nova run com personagem salvo (moedas=0)
DELETE /saves/{save_id}      → apaga save
```

---

## 3. Menu com Modos de Jogo

**Prioridade: média — requer save system primeiro**

### Modos definidos

#### 3.1 Nova Campanha
- Modo balanceado com **andar 20 como andar final**.
- Boss final no andar 20: "Coração da Masmorra" (já nomeado no `gerar_boss()`).
- Ao chegar no andar 21 após vencer o boss final: tela de vitória com créditos.
- Salva a run automaticamente ao avançar de andar (checkpoint).
- **Novos inimigos só aparecem gradualmente** (threshold por andar já implementado).
- Xp e moedas ganhos persistem para o modo "Nova Run com Personagem Salvo".

#### 3.2 Carregar Partida
- Lista as runs salvas do jogador com: nome, andar atual, XP, data.
- Permite continuar de onde parou, incluindo moedas.

#### 3.3 Dungeon Infinita
- Modo atual de funcionamento do jogo.
- Sem andar final — inimigos e bosses escalam indefinidamente.
- Sistema de pontuação: `score = andares × (xp ÷ turnos_totais)`.
- Leaderboard local (top 10 runs desta sessão).
- **Não salva** — é um modo arcade.

#### 3.4 Tutorial
- Duração máxima: 5 andares.
- Andares fixos (não aleatórios): inimigo fraco → baú com item → loja → inimigo médio → mini-boss.
- Pop-ups contextuais a cada evento:
  - Andar 1 (inimigo): explica Atacar, Esquivar, Fugir e as chances base.
  - Andar 2 (baú): explica sistema de itens e como Mímico funciona.
  - Andar 3 (loja): explica moedas e como a loja funciona.
  - Andar 4 (inimigo médio): explica dificuldades e inimigos especiais com badges.
  - Andar 5 (mini-boss): explica mecânica de boss e escalamento.
- Sem penalidade por morte — retorna ao menu com mensagem encorajadora.

### Mudanças necessárias

`frontend/src/`
```
screens/
├── MainMenuScreen.tsx   (novo)   — 4 botões principais
├── LoadScreen.tsx       (novo)   — lista de saves
└── TutorialScreen.tsx   (novo)   — wrapper com pop-ups contextuais

store/gameStore.ts       — adicionar gameMode: "campaign" | "infinite" | "tutorial"
App.tsx                  — adicionar rota "main_menu" antes de "title"
```

`randongeon/jogo/sistemas/`
```
tutorial.py   (novo) — GeradorTutorial implementando a interface do GeradorSala
                        com salas fixas e eventos garantidos
```

`api/main.py`
```
/game/new aceita parâmetro mode: "campaign" | "infinite" | "tutorial"
/game/{id}/advance verifica andar_max se mode == "campaign"
```

---

## 4. Sistema de Loot por Inimigo (expansão futura)

**v3.1 implementou o drop básico. Esta seção descreve a expansão.**

### Estado atual (v3.1)
- Todos os inimigos compartilham o mesmo `POOL_LOOT` global.
- Chance determinada por `inimigo.chance_drop` (8-50%).
- Item é aleatório dentro do pool.

### Expansão planejada

**Pool por tipo de inimigo:**
```python
LOOT_POOLS = {
    "vampiro":  [Item("Sangue Vital", bonus_hp=6), Item("Essência Sombria", bonus_atk=2)],
    "golem":    [Item("Fragmento de Pedra", bonus_hp=4), Item("Núcleo de Pedra", bonus_atk=2)],
    "cacador":  [Item("Trofeu do Caçador", bonus_atk=2), Item("Pele do Caçador", bonus_esq=0.05)],
    "banshee":  [Item("Eco da Banshee", bonus_esq=0.08), Item("Grito Cristalizado", bonus_atk=1)],
    "horda":    [Item("Moeda Goblin Extra", bonus_hp=2)],
    None:       POOL_LOOT,   # inimigos comuns usam pool geral
}
```

**Raridade:** cada item no pool terá um peso de probabilidade.
Itens raros (bonus alto) com peso menor.

**Arquivos impactados:**
- `masmorra.py`: `_rolar_loot()` consulta pool do tipo específico.
- `inimigo.py`: pools definidos externamente ou como atributo de classe.

---

## 5. Mecânica de Miss (expansão futura)

**v3.1 implementou miss simples. Esta seção descreve a expansão.**

### Estado atual (v3.1)
- `CHANCE_MISS_JOGADOR = 0.10` — constante global.
- `inimigo.chance_miss` — definido por tipo (5-20%).

### Expansão planejada

**Miss do jogador influenciado por itens:**
- Novo atributo do Jogador: `precisao: float = 0.90` (base: 10% de miss).
- Items podem aumentar `precisao` (ex: "Talismã do Mestre": +0.05 precisao).
- A chance de miss passa a ser `1 - jogador.precisao`.

**Miss do inimigo influenciado por esquiva:**
- O atributo `esq` do jogador já serve para o dodge ativo.
- Para o miss passivo, a esquiva pode adicionar 50% do seu valor à chance de miss do inimigo.
- Fórmula: `chance_miss_efetiva = inimigo.chance_miss + (jogador.esq * 0.5)`
- Teto: 50% (inimigo não pode errar mais da metade dos ataques por esquiva).

**Arquivos impactados:**
- `jogador.py`: novo atributo `precisao`, validação e método `aumentar_precisao()`.
- `masmorra.py`: atualizar fórmula de miss em `resolver_combate()`.
- `api/main.py`: atualizar em `_turno_combate()`.

---

## Ordem de implementação sugerida

```
Agora:
  [1] Frontend: miss e loot no log  ← sem dependências, campos já na API

Próximo ciclo:
  [2] SQLite save system             ← independente do resto
  [3] Modo Campanha (andar max=20)   ← requer save
  [4] Menu principal + LoadScreen    ← requer save + campanha

Ciclo seguinte:
  [5] Tutorial                       ← GeradorTutorial + pop-ups
  [6] Loot por tipo de inimigo       ← expansão do sistema atual
  [7] Miss com precisao do jogador   ← expansão do sistema atual
  [8] Dungeon Infinita com score     ← polimento final do modo atual
```