# 📘 Lote E — Bando de Goblins (combate sequencial)

> Documento de estudo/revisão. Branch: `bando-goblins-LoteE`.
> Foco de POO: **Herança + Polimorfismo + Composição** (os três num só lote).

---

## 1. O que mudou

Uma **horda** (o inimigo especial que aparece 10% em qualquer andar) deixou de
ser um único inimigo e passou a ser um **Bando de Goblins**: **3 goblins
IDÊNTICOS enfrentados em sequência** (derrota um → o próximo avança). Cada goblin
dá sua própria recompensa (XP/moedas/loot). Fugir escapa do bando inteiro.

Os 3 goblins são iguais entre si (mesmo nome "Goblin", mesmas stats) e usam um
**único sprite** — o `"Goblin"` (`goblin.png`) já mapeado em `spriteMap.ts`. Sem
necessidade de sprites distintos por goblin; basta customizar o asset se quiser.

## 2. POO — os 3 pilares juntos

```python
class Goblin(Inimigo):                 # HERANÇA: "é um" Inimigo
    def __init__(self, nome, hp, atk, xp, moedas):
        super().__init__(..., tipo_especial="horda")   # reaproveita a base
    def tabela_loot(self):             # POLIMORFISMO: override do pool de loot
        return LOOT_HORDA

class BandoDeGoblins:                   # COMPOSIÇÃO: "tem" 3 Goblins idênticos
    def __init__(self):
        hp, atk, xp, moedas = ...        # rola UMA vez
        self.goblins = [Goblin("Goblin", hp, atk, xp, moedas) for _ in range(3)]
    def fila(self):
        return list(self.goblins)       # cópia defensiva
```

- **Herança** (slide *"Herança"*): `Goblin` É UM `Inimigo` — herda `receber_dano`,
  `curar`, `esta_vivo`… e usa `super().__init__`.
- **Polimorfismo** (slide *"Polimorfismo"*): `Goblin.tabela_loot()` sobrescreve o
  pool (loot da horda).
- **Composição** (slide *"Composição vs Herança"*): `BandoDeGoblins` **TEM** 3
  `Goblin` (não herda de Inimigo — é um agrupador). O combate continua consumindo
  **um** `Inimigo` por vez.

## 3. Fluxo do combate sequencial (API)

| Camada | Mudança |
|---|---|
| `session.py` | `GameState.fila_inimigos: list` — goblins restantes do bando |
| `main.py` `advance` | se a sala gera tipo `"horda"`, monta `BandoDeGoblins().fila()`: `inimigo_ativo = fila[0]`, `fila_inimigos = fila[1:]` |
| `main.py` helper | `_resolver_derrota_inimigo()` — centraliza o "inimigo morreu" (antes duplicado em attack/dodge): dá recompensa e, **se houver fila**, retorna `resultado="proximo"` com o próximo goblin; senão `"vitoria"` |
| `main.py` `flee` | fuga bem-sucedida limpa `fila_inimigos` (escapa do bando) |
| `gameStore.ts` | ramo para `"proximo"`: reseta a barra de HP exibida para o HP cheio do novo goblin e toca o SFX de derrota |

**Contrato:** nenhum schema mudou — `resultado` já é string livre. O novo valor
`"proximo"` cai no ramo "continua" do frontend (segue em combate), com o ajuste
da barra de HP.

## 4. Conteúdo além dos slides?

**Não.** Herança, Polimorfismo e Composição são todos dos slides. O `dataclass`
`field(default_factory=list)` já era usado no `GameState`.

## 5. Resultado e arquivos

```
game logic:  pytest tests/ -q       → 560 passed, 5 skipped  (+8 testes do Bando)
API:         pytest api/test_api.py  → 16 passed              (+3 testes sequenciais)
frontend:    npx tsc --noEmit        → 0 erros
```

```
M  randongeon/jogo/entidades/inimigo.py     (Goblin + BandoDeGoblins)
M  randongeon/tests/test_novos_inimigos.py  (TestBandoDeGoblins)
M  api/session.py                           (GameState.fila_inimigos)
M  api/main.py                              (advance + helper + flee)
M  api/test_api.py                          (TestBandoSequencial)
M  frontend/src/store/gameStore.ts          (ramo 'proximo')
A  docs/bando-goblins-LoteE.md
```

> Observação: o combate sequencial é da camada web (a fila é estado da sessão da
> API). No jogo de terminal (`masmorra.avancar`) a horda continua sendo um único
> inimigo — o foco do projeto é o jogo web.

---
*Lote E — pendente de merge na `main`. Próximo: Lote F (score infinito).*
