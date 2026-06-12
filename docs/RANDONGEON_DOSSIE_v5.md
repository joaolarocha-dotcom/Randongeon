# 📜 RANDONGEON — DOSSIÊ DE MEMÓRIA v5
**Gerado durante o ciclo de "balanceamento, status e builds" (sobre o v4).**
**Repositório:** `https://github.com/joaolarocha-dotcom/Randongeon`
**Branch base:** `main` (atual no PR #29 — Lote 3b). `balance-loot-cura-v2` pronta para merge.
**Estado:** ✅ jogável de ponta a ponta, testado e documentado lote a lote.

---

## ⚙️ PROMPT INTERNO — LEIA PRIMEIRO AO RETOMAR

```
Você é o secretário técnico e segundo cérebro de Neivinha no projeto Randongeon.
Ao retomar:

1. Leia TODO este dossiê antes de agir.
2. Sincronize a main e rode as duas suítes:
     cd randongeon ; .\.venv\Scripts\Activate.ps1 ; pytest tests/ -q   → ~627 passed, 5 skipped
     cd api        ; pytest test_api.py -q                            → ~30 passed
     cd frontend   ; npx tsc --noEmit                                 → 0 erros
   (Com a balance-loot-cura-v2 mergeada: ~629 passed.)
3. Compare o estado documentado aqui com os arquivos reais antes de agir.

FLUXO DE TRABALHO ACORDADO (sempre):
  - NUNCA trabalhe na main. Cada lote vai numa BRANCH própria.
  - Após entregar a branch, AGUARDE o usuário fazer o merge antes de prosseguir.
  - Entregas cirúrgicas: edições pontuais; nada de reescrever arquivos inteiros.
  - DOCUMENTAÇÃO obrigatória por lote em docs/ (é conteúdo de PROVA): o que mudou,
    quais PILARES de POO foram usados, e quais arquivos.
  - Decisões de BALANCEAMENTO são calibradas por SIMULAÇÃO Monte Carlo ANTES de
    fixar números. Apresentar dados, deixar o usuário decidir. Números ficam em
    CONSTANTES tunáveis.
  - Lotes grandes podem ser FATIADOS (ex.: backend depois frontend).

Contexto: Neivinha (João/Rafael) — desenvolvedor(a), UNIT Aracaju. Disciplina:
Laboratório de Programação. Estilo: direto, construtivo.
Pilares de POO da disciplina: Abstração, Encapsulamento, Herança, Polimorfismo
(+ @property, ABC, @staticmethod/@classmethod, dunder, composição).
```

---

## 🏗️ STACK E ARQUITETURA

```
Randongeon/
├── api/                          ← FastAPI (REST). RODA DE DENTRO DE api/
│   ├── main.py · schemas.py · session.py · test_api.py · requirements.txt
├── randongeon/                   ← lógica do jogo (Python puro) + testes
│   ├── jogo/
│   │   ├── entidades/  entidade.py(ABC) · jogador.py · inimigo.py · item.py
│   │   │                · loja.py · efeitos.py · dom.py
│   │   └── sistemas/   masmorra.py · gerador.py · persistencia.py
│   ├── tests/                    ← testes pytest (validam o código)
│   ├── conftest.py
│   ├── simulacoes/               ← ferramentas Monte Carlo (NÃO são testes nem jogo)
│   │                               sim_balance · sim_status · sim_balance_v4
│   │                               sim_boss_fase2 · sim_elites_tank · sim_recalibracao · README.md
├── frontend/                     ← React + TS + Vite + Zustand
│   └── src/
│       ├── api/client.ts · store/gameStore.ts
│       ├── data/  tutorials.ts · doms.ts
│       ├── screens/  Title · MainMenu · Menu · Combat · Shop · Chest · Lore
│       │              · LoadGame · Settings · Leaderboard · GameOver · Victory · Tutorials
│       └── services/  saveService.ts · leaderboard.ts
└── docs/                         ← documentação de POO por lote (prova)
```

**Como rodar** (⚠️ a API sobe de DENTRO de `api/`):
```powershell
# API   (uvicorn pode faltar no .venv — instale com: pip install uvicorn)
cd randongeon ; .\.venv\Scripts\Activate.ps1 ; cd ..\api
uvicorn main:app --reload --port 8000
# Frontend
cd frontend ; npm install ; npm run dev          # http://localhost:5173
```

---

## 📦 LOTES DESTA SESSÃO (v4 → v5) — todos mergeados salvo indicado

| Lote / PR | Conteúdo | Pilares de POO | Doc |
|---|---|---|---|
| **I** (#15) | Unificação do turno de combate em `Inimigo.atacar()` | Encapsulamento, Abstração, Polimorfismo | `docs/unificacao-combate-LoteI.md` |
| **J** (#16) | Botão "Ver Placar" no menu | Encapsulamento (consome serviço) | `docs/placar-no-menu-LoteJ.md` |
| **K** (#17) | Remoção da "Aranha Gigante" (resíduo sem sprite) | — | `docs/correcao-aranha-LoteK.md` |
| **L** (#18) | Reescrita de textos & flavor (sombrio c/ humor) | Frontend + dados | `docs/reescrita-textos-LoteL.md` |
| **M** (#19) | Veneno / DoT (Goblin, Rato Gigante) | Encapsulamento, Polimorfismo | `docs/veneno-LoteM.md` |
| **Robustez** (#20) | Recuperação de sessão perdida (404) + DESISTIR robusto | — (frontend) | `docs/correcao-robustez-sessao.md` |
| **Textos** (#21) | Bando sequencial ("um goblin de cada vez") + flavor de veneno por inimigo | — | `docs/textos-bando-veneno.md` |
| **Save .txt** (#22) | Exportar/importar run em `.txt` (com veneno) | Encapsulamento | `docs/save-arquivo-txt.md` |
| **Rampa** (#23) | Elites/especiais escalam por andar a partir do A6 | — (balance) | `docs/balanceamento-rampa-elites.md` |
| **B1** (#24) | Base abstrata `Entidade(ABC)` (Jogador+Inimigo) | **ABC**, Herança, Polimorfismo | `docs/entidade-abc-LoteB1.md` |
| **B2** (#25) | Sistema `EfeitoStatus` + debuffs Orc (fraqueza) / Troll (esquiva-debuff) | ABC, Polimorfismo, Herança | `docs/efeitos-status-LoteB2.md` |
| **1 — Crítico** (#26) | Dano crítico do jogador (`rolar_dano`) | Encapsulamento | `docs/dano-critico-Lote1.md` |
| **2 — Evasão** (#27) | Orc/Troll subclasses; evasão de inimigo; Troll HP-tanque; Banshee evasão | Herança, Polimorfismo | `docs/identidade-evasao-Lote2.md` |
| **3a — Dom backend** (#28) | Doms de slot único (passivo permanente) + save | Encapsulamento (value object) | `docs/dom-slot-Lote3a.md` |
| **3b — Dom tela** (#29) | Seleção de dom na criação da run | Frontend | `docs/dom-slot-Lote3b.md` |
| **★ Balance** (`balance-loot-cura-v2`, PENDENTE) | Cura parcial no level-up (60%) + mais loot | — (balance) | `docs/balanceamento-loot-cura.md` |

---

## 🔧 REFERÊNCIA TÉCNICA (números atuais — TODOS tunáveis por constante)

### Jogador (`jogador.py`)
- Início: `hp=20, atk=5, esq=0.3, nivel=1`, 2 itens iniciais.
- **Nível:** custo `10·N·(N+1)`; por nível `+2 ATK`, `+12 HP_max`, `+0.005 esq` (teto `ESQ_MAXIMA=0.6`).
  - **Cura ao subir:** `CURA_NIVEL_FRACAO=0.60` → 60% do HP máx (não mais total). *(no balance-loot-cura-v2)*
- **Crítico:** `CHANCE_CRITICO_BASE=0.10`, `MULTIPLICADOR_CRITICO=1.5`. Método `rolar_dano() → (dano, foi_critico)`.
- **Pontuação** (`@property`): `xp + (nivel-1)·50 + moedas`.
- **Status/passivos:** `veneno_turnos` (@property via efeitos), `lifesteal`, `evasao_passiva`, `dom`.
- **Efeitos:** `aplicar_efeito`, `processar_efeitos_turno`, `atk_efetivo()`, `esquiva_efetiva()`, `aplicar_lifesteal()`.

### Entidade base (`entidade.py`, ABC) — Lote B1
- `Jogador` e `Inimigo` herdam `hp/hp_max/esta_vivo/curar` + lista `efeitos` + `processar_efeitos_turno`.
- `receber_dano()` é **abstrato** (Inimigo desconta armadura; Jogador sofre direto).

### Efeitos de status (`efeitos.py`, ABC) — Lote B2
- `EfeitoStatus` (hooks `ao_iniciar_turno`, `modifica_atk`, `modifica_esquiva`).
- Subclasses: `Veneno` (1/turno, `remove_ao_curar`), `Fraqueza` (−ATK), `EsquivaReduzida` (−esquiva).

### Doms (`dom.py`) — Lote 3 (escolhidos no início; passivo permanente; entram no save)
| Dom | Efeito | Trade-off |
|---|---|---|
| Bruto | +3 ATK | −0.10 esquiva, −0.05 crítico |
| Resistente | +10 HP máx | −0.05 esquiva |
| Ágil | +0.10 esquiva, inimigos erram +10% (`evasao_passiva`) | −5 HP máx |
| Sortudo | +0.15 crítico | −1 ATK |
| Sanguessuga | lifesteal 10% | — |

### Inimigos (`inimigo.py`)
- Constantes: escala por andar (`ESCALA_*`), `chance_elite(andar)`/`ratio_especial(andar)` (rampa A6+),
  `CHANCE_VENENO=0.08`, `CHANCE_FRAQUEZA=0.30`, `CHANCE_ESQUIVA_DEBUFF=0.35`,
  `ESQUIVA_ORC=0.15`, `ESQUIVA_BANSHEE=0.30`, `TROLL_HP_MULTIPLICADOR=1.6`,
  `CHANCE_DROP_PADRAO=0.15` *(balance-loot-cura-v2)*.
- `Inimigo.atacar(alvo) → dict` (errou/dano/curou/atordoou/envenenou/fraqueza/esquiva_reduzida/subiu_atk);
  o erro considera `alvo.evasao_passiva`.
- `Inimigo.tentar_esquivar()` — inimigo desvia do golpe do jogador (≠ chance_miss).
- Subclasses: `Nosferatu`, `GolemDePedra` (armadura 3), `Banshee` (atordoa+evasão),
  `Orc` (fraqueza+evasão), `TrollDasCavernas` (HP-tanque sem armadura), `Goblin`/`BandoDeGoblins` (composição).
- Geração de elite: `gerar()` despacha por nome → `Orc(...)`, `TrollDasCavernas(...)`, ou Esqueleto genérico.

### Combate / Loot
- Miss do jogador 10%; cada laço usa `rolar_dano()` (crítico) e checa `inimigo.tentar_esquivar()` antes do dano; lifesteal após.
- Sala (`gerador.py`): `SORTE_MAX_LOJA=3` (15%), `SORTE_MAX_ITEM=6` (15% item) *(balance-loot-cura-v2)*, resto inimigo.

### Modos / Boss
- `story` boss a cada 5 (andar máx 20, fuga impossível no 20) · `infinite` boss a cada 3, ∞.
- Bosses: `gerar_boss` (HP `20+f·20`, ATK `5+f·3`). Nomes A5/10/15/20 fixos (travados por teste).

---

## 📡 API — pontos relevantes (`main.py`)
- `POST /game/new` aceita `{nome, modo, dom}` → `create_session(nome, modo, dom)`.
- Combate (`/combat/attack|dodge|flee`) usa `rolar_dano`, evasão do inimigo, lifesteal, e aplica debuffs do `atacar()`.
- Save (`GET /game/{id}/save`) inclui: `veneno_turnos, chance_critico, dom, lifesteal, evasao_passiva` (+ stats).
  `POST /game/load` restaura tudo (stats já vêm baked; passivos/dom restaurados).
- **Robustez:** `ApiError` com `status`; o frontend detecta 404 (sessão perdida) e volta ao menu sem travar; DESISTIR sempre funciona.

---

## 🧪 ESTADO DE TESTES
```
randongeon/tests/  → 627 passed, 5 skipped   (629 com balance-loot-cura-v2)
api/test_api.py    → 30 passed
frontend           → tsc --noEmit: 0 erros
```
> ⚠️ Dummies de inimigo criados via `Inimigo.__new__` (em `conftest.py`,
> `test_masmorra.py`, `test_novos_inimigos.py`, `test_jogador.py`) precisam ganhar
> CADA novo atributo de combate (chance_*, esquiva, etc.) senão `atacar()` quebra.

---

## 🗺️ ROADMAP DE CONTINUIDADE (decisões já travadas)

| # | Lote | Decisões travadas |
|---|---|---|
| ★ | **Balance (loot+cura)** | Pronto em `balance-loot-cura-v2` — **fazer o merge** e **apagar a `balance-loot-cura` antiga** (conflito). |
| **4a** ✅ MERGEADO | **Boss: 2ª fase do Coração (backend)** | **Mergeado** (PR #31). Subclasse `CoracaoDaMasmorra(Inimigo)` com hook `tentar_renascer()` (Template Method/Polimorfismo): renasce 1×, cura **50%**, fúria **ATK ×1.25** (calibrada por `sim_boss_fase2.py` → win-rate boss ~36%). Fluxo de morte da API → `resultado="renasceu"`; CLI honra renascimento. +9 testes. Doc: `docs/boss-coracao-fase2-Lote4a.md`. |
| **4b** ✅ MERGEADO | **Boss: 2ª fase do Coração (frontend)** | **Mergeado** (PR #32). `handleCombatResult` trata `resultado="renasceu"`: **não** abre Victory; boss volta a ~50% (barra sobe) + badge **🔥 FÚRIA** (estado `bossEnraged`) + SFX de abate/fúria; luta continua até a 2ª morte. Frontend puro. Doc: `docs/boss-coracao-fase2-Lote4b.md`. **Lote 4 concluído (4a+4b).** |
| **B** ✅ ENTREGUE | **Recalibração: tankiness de elites especiais** | **ENTREGUE** na branch `balance-elites-especiais` (commit `11b97df`, aguardando PR/merge). Bug: Golem/Nosferatu/Banshee tinham stats fixas e não escalavam (Golem do A16 com TTK 1.8 < comum 2.0). Fix: params opcionais de escala (HP `×1.6`, ATK por andar, armadura do Golem `3 + andar//6`) com default 0 → base intacta. Calibrado por `sim_elites_tank.py`. Pós-fix A16: Golem 5.0 / Nosferatu 4.0 / Banshee 3.7. +9 testes. Doc: `docs/balance-elites-especiais-LoteB.md`. |
| ★ ✅ ENTREGUE | **Recalibração geral** | **ENTREGUE** na branch `recalibracao-geral` (aguardando PR/merge). Diagnóstico Monte Carlo da campanha inteira (`sim_recalibracao.py`): o gargalo era o **1º boss (A5)** — 61% das mortes, win ~38%; causa = **ATK 8** (não o pré-boss). Config "C" (curva de boss tunável, só ATK: `round(2+fator*3.75)` → 6/10/13/17, HP e A20 intactos). Vitória de campanha **11,6% → 21,6%**; A5 win 38%→70%; clímax A20 preservado (~40%). Docs: `docs/recalibracao-geral.md`. |
| **5** ✅ MERGEADO | **Badge de efeitos na UI** | **Mergeado** (PR #34). `JogadorStatus` expõe `efeitos[]` (tipo+turnos) + passivos (`lifesteal`/`dom`/`evasao_passiva`); `StatusBadges.tsx` mostra pílulas ☠️ VENENO/💪 FRACO/💫 ZONZO + ⭐ dom no `PlayerStatusBox`. +3 testes de API. Doc: `docs/badge-efeitos-ui-Lote5.md`. |
| **C** ✅ ENTREGUE | **Feedback de level-up + barra de XP correta** | **ENTREGUE** na branch `feedback-levelup` (commit aguardando PR/merge). A cura ao subir de nível era silenciosa e o nível exibido usava `xp/50` (divergia da curva real). Agora: `ganhar_xp()` retorna níveis; `mensagem_level_up()` (API+CLI) anuncia "⭐ PARABÉNS! nível N! vida recuperada…"; `progresso_nivel()` + `xp_nivel_atual/total` no status dão a barra de XP correta; `PlayerStatusBox` usa o nível real; jingle `sfx_level_up`. +11 testes. Doc: `docs/feedback-levelup.md`. |
| **6** ✅ ENTREGUE | **Tutorial atualizado** | **ENTREGUE** na branch `tutorial-atualizado` (commit `6aa25c8`, aguardando PR/merge). `data/tutorials.ts` reescrito (4→9 páginas) cobrindo crítico, doms, badges de status, elites/especiais, boss 2 fases, level-up (cura 60%), save .txt, placar. Corrige infos erradas (esquivar não é dano dobrado; cura é no level-up; itens iniciais reais). Só conteúdo. Doc: `docs/tutorial-atualizado-Lote6.md`. |
| **7** (final) ✅ ENTREGUE | **Auditoria de aderência aos slides de POO (PROVA)** | **ENTREGUE** na branch `auditoria-poo` (commit `8842a56`, aguardando PR/merge). Slides analisados (4 pilares + PDF de código de 22 págs); comparados com todo o Python do projeto. Doc `docs/auditoria-poo-prova.md`: mapa conteúdo→arquivo→trecho, técnicas avançadas (ABC, Template Method `tentar_renascer`, polimorfismo sem `if tipo`, composição vs herança, duck typing, `@property`, `@staticmethod`) com o porquê, e lista honesta dos 5 tópicos não usados (`__privado`, setter, `@classmethod`, herança múltipla/MRO, dunders ricos) com encaixe sugerido. **Decisão: Lote 7b (preencher os gaps) DISPENSADO** — fica só a auditoria. |

**Ideias adiadas (não no roteiro):** descrição/flavor de itens (precisa campo `descricao` + UI); dom "Imune" (resistência a veneno) ficou de fora do roster.

---

## ⚠️ PONTOS DE ATENÇÃO / ARMADILHAS CONHECIDAS
- **Ordem dos `random` em `atacar()`:** novos rolls só rolam quando a chance > 0 (curto-circuito) — preserva sequências de testes seeded. Mantenha esse padrão.
- **Dummies via `__new__`:** ver aviso na seção de testes.
- **git/OneDrive:** o repo está dentro do OneDrive; já houve `unable to write new index file`/`checkout aborting`. Se a `main` divergir, a fonte da verdade é `origin/main` (`git fetch` + `git reset --hard origin/main` numa branch de trabalho).
- **Branches de terceiros:** existem `origin/NovosEnemys_Status_Bestiario` e `origin/easy-mode` (de outro colaborador, GabrielCNovaesDev) — não mexer.
- **uvicorn:** pode faltar no `.venv` apesar de estar no `requirements.txt` (`pip install uvicorn`).
- **Browser headless local:** o Vite às vezes sobe só em IPv6 `localhost`; para automação use `--host 0.0.0.0` e a porta certa.

---

*Dossiê v5 — Randongeon. Sobre o v4: combate unificado, placar no menu, textos
imersivos, veneno, robustez de sessão, save em .txt, rampa de elites, base
`Entidade(ABC)`, sistema de `EfeitoStatus`, crítico, evasão/identidade de
inimigos, doms de slot único e balanceamento de loot/cura — tudo calibrado por
simulação e documentado lote a lote. Próximo grande passo: a 2ª fase do Coração
da Masmorra.*
