# 📘 Balanceamento v4 — Inimigos escalam por andar + economia

> Documento de estudo/revisão. Branch: `balanceamento-v4`.
> Natureza: balanceamento (regra de jogo), calibrado por simulação.

---

## 1. O problema (medido)

O jogo virava um "passeio" depois do andar 5:
- **Comuns triviais:** one-shot em 1 turno, jogador perdia **0.2% do HP** no andar 5+
  (HP fixo 3-8 pra sempre, enquanto o ATK do herói ia a 22).
- **Bosses tardios triviais:** A10-A20 com **97-98%** de vitória.
- Só o boss A5 era desafio (e mal posicionado, logo no início).

## 2. A decisão (alavancas + alvo)

Direção escolhida: **inimigos comuns/elite escalam por andar** + **economia de moedas**,
mirando **"desafio consistente"** (campanha ~25-35%, comuns mordendo ~5-12% no fim).
*Não* mexemos em HP/nível nem na curva de boss.

## 3. Calibração (simulação Monte Carlo)

`sim_balance_v4.py` varreu várias escalas. Aprendizados:
- **Moedas não mudam a dificuldade** (o jogador não é limitado por moedas) → o ajuste
  de moedas é recompensa/feel, não dificuldade.
- A ameaça vem do **HP/ATK por andar** (o ATK controla o HP perdido por luta).

**Config escolhida (F):**

| Parâmetro | Valor |
|---|---|
| Bônus de HP (comum) | `round(andar × 1.8)` |
| Bônus de ATK | `andar // 5` (+1 a cada 5 andares) |
| Bônus de moedas | `andar // 2` |
| Elite | HP escala ×1.4, ATK +1 extra |

Constantes em `inimigo.py`: `ESCALA_HP_POR_ANDAR`, `ESCALA_ATK_DIVISOR`,
`ESCALA_MOEDAS_DIVISOR`, `ELITE_HP_MULTIPLICADOR` (fáceis de re-tunar).

## 4. Resultado (no jogo real)

| Métrica | Antes | Depois |
|---|---|---|
| Vitória de campanha | 32.5% | **25.4%** (no alvo) |
| Boss A10-A20 (win) | 97-98% | **~90-92%** |
| HP perdido vs comum (A5/A20) | ~1% / 0.2% | **~10% / ~5-8%** |

Cada andar passou a exigir atenção, sem virar punitivo. Comuns no fim mordem
~5-10% do HP (antes: nada).

## 5. POO / notas

- A escala fica em `Inimigo.gerar()` (fábrica `@staticmethod`), com constantes de
  módulo — sem mudar a interface. Especiais (Golem/Nosferatu/Banshee/Horda) e
  bosses **não** mudaram.
- **Economia:** moedas escalam por andar (recompensa cresce com a dificuldade). As
  taxas de **drop de loot ficaram estáveis** — a calibração mostrou que não afetam
  a dificuldade, e o loot já vai pro inventário (Lote F); mexer nelas agora só
  arriscaria desestabilizar. Fica como ajuste futuro se desejado.

## 6. Verificação

```
game logic:  pytest tests/ -q       → 566 passed, 5 skipped  (+2 testes de escala)
API:         pytest api/test_api.py  → 24 passed
sim_balance: campanha 25.4% (alvo 25-35%)
```

Testes atualizados (assumiam stats fixas): `test_inimigo.py` e `test_inimigoV3.py`
(valores de elite/comum no andar 5 agora incluem o bônus de escala).

---
*Balanceamento v4 — pendente de merge na `main`.*
