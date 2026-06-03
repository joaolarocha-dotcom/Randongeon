# Lote 4a — Coração da Masmorra: 2ª fase (backend)

## Objetivo

Dar um clímax à campanha: o boss final (andar 20, **Coração da Masmorra**) deixa
de morrer no primeiro abate. Ao zerar o HP pela 1ª vez ele **renasce uma única
vez**, volta com **50% do HP máximo** e entra em **fúria** (ATK maior). Só a
**2ª morte** vence a campanha (`vitoria_campanha`).

Este lote é o **backend** (modelo + API + CLI). O toque de **frontend** (não
disparar a tela de vitória no renascimento; mostrar o boss voltando a 50%) é o
**Lote 4b**.

## Pilares de POO usados

- **Herança:** `CoracaoDaMasmorra(Inimigo)` — É UM Inimigo. Herda todo o combate
  (`atacar`/`receber_dano`/`tabela_loot`) e recebe as stats já escaladas via
  `gerar_boss()`, então os testes que travam HP/ATK/XP/moedas/nome do boss do
  andar 20 continuam valendo sem alteração.
- **Polimorfismo + Template Method:** a base `Inimigo` ganhou o hook
  `tentar_renascer()` que devolve **False** (inimigos comuns/bosses normais
  morrem de vez). `CoracaoDaMasmorra` **sobrescreve** o hook para ressuscitar 1×.
  O fluxo de morte chama `inimigo.tentar_renascer()` **sem `if tipo`** — quem
  decide é o objeto.
- **Encapsulamento:** o boss é dono do seu próprio estado de fase (`_ja_renasceu`,
  exposto só-leitura via `@property ja_renasceu`); reaproveita `curar()` da base
  `Entidade` para a cura de renascimento. Números em **constantes tunáveis**.

## Mecânica (constantes tunáveis em `inimigo.py`)

| Constante | Valor | Significado |
|---|---|---|
| `CORACAO_CURA_RENASCIMENTO` | `0.50` | ao renascer, volta com 50% do HP máx (travado no roadmap) |
| `CORACAO_FURIA_ATK_MULT` | `1.25` | fúria: `ATK = max(atk+1, round(atk×1.25))` → 17 vira **21** |

`tentar_renascer()` é idempotente: devolve `True` só na 1ª morte e `False` na 2ª
(e enquanto o boss estiver vivo). Renascer aplica cura + fúria de uma vez.

## Fluxo de morte

- **API** (`api/main.py`): `_resolver_derrota_inimigo()` chama
  `inimigo.tentar_renascer()` **antes** de conceder XP/loot. Se renasceu, retorna
  `CombatActionResponse(resultado="renasceu", ...)` com o boss já a 50% do HP e em
  fúria — a luta continua. Só a 2ª morte segue para `vitoria`/`vitoria_campanha`.
  Novo valor de `resultado`: **`"renasceu"`** (documentado em `schemas.py`).
- **CLI** (`masmorra.resolver_combate`): a luta foi envolvida num laço externo
  que **recomeça** quando `tentar_renascer()` devolve `True` (imprime o texto
  sombrio de renascimento). Para inimigos comuns o hook é `False` e roda uma vez.

## Calibração por simulação (Monte Carlo)

`sim_boss_fase2.py` (novo) roda campanhas story completas com a escala real
(config "F") e troca o boss final por uma luta de 2 fases parametrizada pela
fúria. **n=6000, seed fixa.** Win-rate medido **só do boss** (condicional a
chegar no andar 20 — a taxa de chegada ~18% é o balance pré-boss, do item
★ Recalibração, não deste lote):

| Config | ATK 2ª fase | Win-rate só do boss |
|---|---|---|
| Baseline (1 fase, antigo) | 17 | 85,2% |
| 2 fases · fúria ×1.00 | 18 | 43,3% |
| **2 fases · fúria ×1.25 (escolhido)** | **21** | **36,4%** |
| 2 fases · fúria ×1.50 | 26 | 26,4% |
| 2 fases · fúria ×2.00 | 34 | 20,0% |

A própria 2ª fase (cura de 50% + 1 ressurreição) já derruba o win-rate de 85%
para ~43%; a fúria ×1.25 ajusta para ~36% mantendo o boss vencível por quem
chega bem equipado.

## Arquivos alterados

| Arquivo | Mudança |
|---|---|
| `randongeon/jogo/entidades/inimigo.py` | hook base `tentar_renascer()`; classe `CoracaoDaMasmorra` + constantes + `MENSAGEM_RENASCIMENTO`. |
| `randongeon/jogo/sistemas/masmorra.py` | `gerar_boss()` instancia o Coração no andar 20; `resolver_combate` honra o renascimento (CLI). |
| `api/main.py` | `_resolver_derrota_inimigo()` chama o hook → `resultado="renasceu"`. |
| `api/schemas.py` | comentário de `resultado` inclui `"renasceu"` (e `"proximo"`). |
| `api/test_api.py` | teste do boss 20 atualizado para a 2ª fase (renasce → 2ª morte vence). |
| `randongeon/tests/test_coracao_fase2.py` | **novo** — +9 testes (hook base, geração, renascimento, CLI). |
| `randongeon/sim_boss_fase2.py` | **novo** — Monte Carlo de calibração da fúria. |

## Próximo (4b — frontend)

Tela de combate: tratar `resultado="renasceu"` (não abrir Victory; mostrar o boss
voltando a ~50% com aviso de "fúria"/2ª fase), e — se quisermos — expor a fase no
`InimigoInfo` para um indicador visual.

## Estado de testes

```
randongeon/tests/ → 638 passed, 5 skipped   (+9 do Lote 4a)
api/test_api.py   → 30 passed
frontend          → tsc --noEmit: 0 erros (sem mudança de frontend neste lote)
```
