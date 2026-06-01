# 📘 Lote C — Loot por Tipo de Inimigo + Status Especiais relevantes

> Documento de estudo/revisão. Branch: `loot-status-LoteC`.
> Foco de POO: **Polimorfismo** (e Herança).

---

## 1. O que mudou e por quê

### 1.1 Loot por tipo de inimigo (polimorfismo)
Antes, todos os inimigos dropavam do mesmo `POOL_LOOT` global. Agora cada tipo
tem um **pool temático**, escolhido por **polimorfismo**: o método `tabela_loot()`
é definido em `Inimigo` (pool padrão) e **sobrescrito** em cada subclasse.

| Tipo | Pool (`tabela_loot()`) |
|---|---|
| comuns / boss (`Inimigo`) | `LOOT_PADRAO` (5 itens — o antigo POOL_LOOT) |
| `GolemDePedra` | `LOOT_GOLEM` — Fragmento de Pedra (+hp), Núcleo de Pedra (+atk) |
| `Nosferatu` | `LOOT_NOSFERATU` — Sangue Vital (+hp), Essência Sombria (+atk) |
| `Banshee` | `LOOT_BANSHEE` — Eco da Banshee (+esq), Grito Cristalizado (+atk) |
| `HordaDeGoblins` | `LOOT_HORDA` — Bolsa de Moedas Goblin (+hp), Adaga Enferrujada (+atk) |

`Masmorra._rolar_loot()` agora faz `random.choice(inimigo.tabela_loot())` — **sem
saber o tipo concreto** do inimigo. É o polimorfismo do slide em ação.

### 1.2 Status especiais agora **relevantes** (decisão por simulação)
O simulador (`sim_status.py`) revelou que as mecânicas especiais (defesa do Golem,
cura do Nosferatu, atordoar da Banshee) **existiam mas eram inofensivas**: os
inimigos apareciam tarde, quando o herói já os matava em 1-2 golpes.

**Dados (HP perdido pelo herói no encontro):**

| Mecânica | Herói forte (andar real) | Herói fraco (aparição cedo) |
|---|---|---|
| Golem absorção 0→2→3 | 7%→7%→9% (irrelevante) | 25%→37%→**47%** |
| Nosferatu cura 0→0.20 | ~0.6% (idêntico) | 25%→28% |
| Banshee atordoar 0→0.30 | 0.5%→0.7% | 17%→**24%** |

**Solução escolhida: antecipar a aparição** (e subir a defesa do Golem):

| Inimigo | Threshold antes | Threshold agora | Outro ajuste |
|---|---|---|---|
| Golem | andar ≥ 8 | **andar ≥ 5** | `absorcao_dano` 2 → **3** |
| Nosferatu | andar ≥ 15 | **andar ≥ 8** | — |
| Banshee | andar ≥ 17 | **andar ≥ 10** | — |

Validação de campanha: vitória ≈ **32.5%** (era 32%) — a curva geral **não** foi
desequilibrada; os especiais continuam raros, mas agora "mordem" quando aparecem.

---

## 2. Pilares de POO (com referência aos slides)

- **Polimorfismo** (slide *"Polimorfismo"*): `tabela_loot()` — mesma chamada,
  comportamento diferente conforme o tipo concreto do inimigo. `_rolar_loot()`
  trata todos uniformemente.
- **Herança** (slide *"Herança"*): as subclasses já herdam de `Inimigo`; agora
  também **sobrescrevem** (override) `tabela_loot()`.
- **Encapsulamento/Abstração**: os pools ficam centralizados em `inimigo.py`; quem
  consome o loot não conhece os detalhes.

> 🛈 **Decisão de arquitetura:** os pools de loot foram definidos em `inimigo.py`
> (a entidade que "dropa" o item). `masmorra.py` **re-exporta** `POOL_LOOT =
> LOOT_PADRAO` por compatibilidade (a API e vários testes importam `POOL_LOOT` de
> `masmorra`). Evita import circular (inimigo não importa masmorra).

---

## 3. Conteúdo além dos slides?

**Não.** Polimorfismo por override, herança e atributos de módulo — tudo nos
slides.

---

## 4. Resultado e arquivos

```
pytest tests/ -q   →  552 passed, 5 skipped  (+9 testes: tabela_loot e thresholds)
sim_balance.py     →  campanha 32.5% (curva preservada)
sim_status.py      →  comprova que as mecânicas agora importam na aparição cedo
```

```
M  randongeon/jogo/entidades/inimigo.py     (pools + tabela_loot + thresholds + golem)
M  randongeon/jogo/sistemas/masmorra.py     (re-export POOL_LOOT + _rolar_loot polimórfico)
M  randongeon/tests/test_inimigo.py         (geração de elite comum no andar 5)
M  randongeon/tests/test_inimigoV3.py       (idem)
M  randongeon/tests/test_novos_inimigos.py  (golem absorção 3, thresholds, TestTabelaLoot)
A  randongeon/sim_status.py                 (simulador de validação dos status)
A  docs/loot-status-LoteC.md                (este documento)
```

> ⚠️ **Importante:** este lote é **backend puro** — a API (`api/main.py`) ainda
> usa o `POOL_LOOT` genérico no seu próprio `_rolar_loot` (duplicado). O loot por
> tipo só chegará ao jogo web quando a API for ressincronizada no **Lote D**.

---
*Lote C — pendente de merge na `main`. Próximo: Lote D (API + inventário).*
