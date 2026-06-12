# Lote 2 — Identidade & evasão de inimigos

## Objetivo

Deixar o jogo mais longo e menos monótono: acabar com o "fico forte e mato tudo
num golpe". Para isso, uma mecânica nova (**evasão do inimigo**) e identidade
própria para os elites.

## Mecânica nova: evasão (`Inimigo.esquiva`)

Chance de o inimigo **desviar do golpe do jogador** (≠ `chance_miss`, que é o
inimigo errar o *próprio* ataque). Encapsulada em `Inimigo.tentar_esquivar()`
(curto-circuito: `esquiva==0` não consome a sorte). Aplicada **antes** do
`rolar_dano()` em todo o combate (API, CLI e automático); se desvia, dano 0 +
mensagem *"X desviou do seu golpe!"*.

## Identidade dos elites (agora subclasses)

`Orc` e `TrollDasCavernas` foram **promovidos a subclasses** (como
Nosferatu/Golem/Banshee); `Esqueleto Guerreiro` segue genérico. O `gerar()`
despacha por nome, mantendo a escala por andar.

| Inimigo | Identidade | Números (verificados por simulação) |
|---|---|---|
| **Troll das Cavernas** | tanque de **HP**, **sem armadura** | ~60% mais HP que um elite (A10: ~58 vs ~36); mantém o debuff de esquiva (maça, B2) |
| **Orc** | "inteligente" | **15%** de evasão + Fraqueza (B2) |
| **Banshee** | fantasma etéreo | **30%** de evasão (+ atordoamento) |
| Golem | tanque por **armadura** | inalterado (mitiga por absorção, não esquiva) |

## Pilares de POO

- **Herança/Polimorfismo:** Orc e Troll viram subclasses de `Inimigo` com
  identidade própria; o combate trata todos via `tentar_esquivar()`/`atacar()`.
- **Encapsulamento:** a regra de evasão vive em `Inimigo.tentar_esquivar()`.

## Balanceamento

Crítico (Lote 1) encurta lutas; evasão (este lote) alonga. Os números
(15%/30%/×1.6 HP) são iniciais — a **recalibração por simulação** (próximo passo
★ do roteiro) vai medir a win-rate por boss e ajustar crit + evasão + debuffs
juntos.

## Arquivos alterados

| Arquivo | Mudança |
|---|---|
| `randongeon/jogo/entidades/inimigo.py` | `esquiva` + `tentar_esquivar()`; subclasses `Orc`/`TrollDasCavernas`; Banshee com evasão; `gerar()` despacha por nome. |
| `randongeon/jogo/sistemas/masmorra.py` | evasão no combate automático e na CLI. |
| `api/main.py` | evasão no ataque e no contra-ataque. |
| `conftest.py` + 3 testes | dummies recebem `esquiva`; **+7** testes (`TestIdentidadeEvasao`). |

## Estado de testes

```
randongeon/tests/ → 615 passed, 5 skipped   (608 + 7)
api/test_api.py   → 27 passed
```
