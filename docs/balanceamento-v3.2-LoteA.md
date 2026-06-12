# 📘 Lote A — Sistema de Nível, Pontuação e Boss Progressivo (v3.2)

> Documento de estudo/revisão. Descreve **o que mudou**, **por que**, **quais pilares
> de POO** foram usados (com referência aos slides da disciplina) e **quais arquivos**
> foram tocados. Branch: `balanceamento-xp-nivel`.

---

## 1. Motivação (decidida por simulação, não por palpite)

Um simulador Monte Carlo (`randongeon/sim_balance.py`, 4.000 runs) mostrou que:

- **Antes:** o boss do andar 5 tinha **0% de vitória** — invencível. O XP só acumulava
  um número e **não virava poder** (não havia sistema de nível).
- **Depois (config I):** A5 ≈ **34%**, e após passá-lo o jogador "bola-de-neve"
  (97%+ nos bosses seguintes). Vitória de campanha ≈ **32%**.

| Boss | win@boss (antes) | win@boss (depois) |
|---|---|---|
| A5  | 0%  | 34% |
| A10 | —   | 97% |
| A15 | —   | 98% |
| A20 | —   | 98% |

---

## 2. Mudanças por arquivo

### 2.1 `randongeon/jogo/entidades/jogador.py` — Nível + Pontuação

**O que mudou**
- Novo atributo de instância `nivel` (começa em 1).
- Novas **constantes de classe**: `ATK_POR_NIVEL=2`, `HP_POR_NIVEL=12`,
  `XP_BASE_NIVEL=10`, `ESQ_POR_NIVEL=0.005`, `ESQ_MAXIMA=0.6`.
- `ganhar_xp()` agora chama `_atualizar_nivel()` ao final.
- Novo método `xp_para_proximo_nivel()` — custo triangular `base * nivel * (nivel+1)`.
- Novo método protegido `_atualizar_nivel()` — sobe de nível em laço enquanto houver
  XP; a cada nível: `+ATK`, `+HP_max`, `+ESQ` (com teto) e **cura total**.
- Nova `@property pontuacao` — `xp + (nivel-1)*50 + moedas` (só leitura).
- `__repr__` agora inclui o nível.

**Pilares de POO usados** (todos cobertos pelos slides)
- **Encapsulamento** (slide *"Encapsulamento — 3 níveis de visibilidade"* e
  *"@property — Getter e Setter"*):
  - `_atualizar_nivel()` é **_protegido** (prefixo `_`): detalhe interno, não faz
    parte da interface usada por telas/API.
  - `pontuacao` é exposta via **`@property`** (getter calculado, **sem setter** →
    tentativa de escrita levanta `AttributeError`). Protege a integridade do valor.
- **Atributos de Classe vs Instância** (slide *"Atributos de Instância e de Classe"*):
  as constantes de balanceamento são **atributos de classe** (valem para todos os
  heróis); `nivel`, `hp`, `atk` são **de instância** (variam por objeto).
- **Abstração** (slide *"Os 4 Pilares: Abstração"*): quem chama `ganhar_xp()` não
  precisa saber que existe um cálculo de nível por trás — o "como" fica escondido.
- **Dunder methods** (slide *"Dunder Methods"*): atualização do `__repr__`.

> ⚠️ **Nota de design (esquiva com dois tetos):** o ganho de esquiva por **nível**
> é limitado a `ESQ_MAXIMA = 0.6`, enquanto a esquiva por **itens** (`aumenta_esq`)
> continua usando `esq_max = 1.0`. São limites propositalmente diferentes: a
> progressão natural não passa de 60%, mas itens raros ainda podem empurrar além.

### 2.2 `randongeon/jogo/sistemas/masmorra.py` — Boss progressivo

**O que mudou** — em `gerar_boss()`, a fórmula de HP/ATK:

| | Antes (v3.1) | Depois (v3.2 / config I) |
|---|---|---|
| HP  | `40 + fator*18` | `20 + fator*20` |
| ATK | `8 + fator*3`   | `5 + fator*3`   |
| XP / moedas | `80+f*40` / `25+f*8` | **inalterados** |

Efeito: **suaviza o primeiro boss** (A5: 58→40 HP) e **mantém os tardios fortes**
(A20: 100 HP, próximo dos 112 antigos). Base baixa + passo alto = curva progressiva.

**Pilar de POO usado**
- **Abstração**: `gerar_boss()` continua expondo "gera um Inimigo de boss para este
  andar" e esconde a fórmula interna — quem chama não muda.

### 2.3 Testes atualizados/adicionados
- `tests/test_balance.py` — `TestEscalonamentoBoss`: novos valores de HP/ATK
  (40/60/80/100 e 8/11/14/17) e recálculo de `test_boss_andar_5_n_mata_em_um_golpe`.
- `tests/test_masmorra.py` — `TestGerarBoss`: novos asserts de HP/ATK (XP/moedas
  permaneceram, pois a fórmula não mudou).
- `tests/test_jogador.py` — **novas** classes `TestNivel` (10 testes) e
  `TestPontuacao` (4 testes).

---

## 3. Conteúdo além dos slides?

**Não.** Todo o Lote A usa apenas conceitos presentes nos slides (atributos de
classe, `@property`, método `_protegido`, `__repr__`, validações). Não foi
necessário ABC, herança múltipla, duck typing nem outros tópicos avançados.
*(Quando algum lote exigir isso, será marcado no código com
`# [POO AVANÇADO — fora dos slides]`.)*

---

## 4. Resultado

```
pytest tests/ -q  →  557 passed, 6 skipped
sim_balance.py    →  campanha 32%, A5 34%, A10-A20 ~97%
```

## 5. Arquivos modificados/criados

```
M  randongeon/jogo/entidades/jogador.py       (nível + pontuação)
M  randongeon/jogo/sistemas/masmorra.py       (boss progressivo)
M  randongeon/tests/test_balance.py           (valores de boss)
M  randongeon/tests/test_masmorra.py          (valores de boss)
M  randongeon/tests/test_jogador.py           (testes de nível e pontuação)
A  randongeon/sim_balance.py                  (simulador de validação — análise)
A  docs/balanceamento-v3.2-LoteA.md           (este documento)
```

---
*Lote A — v3.2 — pendente de merge na `main`. Lote B (refatoração de inimigos:
remover Caçador, Vampiro→Nosferatu) virá em branch separada após o merge.*
