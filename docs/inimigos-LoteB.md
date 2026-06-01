# 📘 Lote B — Refatoração de Inimigos (Nosferatu / remoção do Caçador)

> Documento de estudo/revisão. Branch: `inimigos-nosferatu` (a partir da `main` com
> o Lote A já mergeado). Foco de POO: **Herança** e **Polimorfismo**.

---

## 1. O que mudou (decisões do usuário)

1. **Removido** o inimigo especial `CacadorSombrio` (classe + aparições em `gerar()`).
2. **Renomeado** `VampiroDasSombras → Nosferatu` (nome de exibição e `tipo_especial`).
3. Na lista de nomes de inimigos comuns, `"Nosferatu"` (que era um comum genérico)
   foi trocado por **`"Bando de Goblins"`** — evita colidir com a classe especial
   `HordaDeGoblins` (que tem `nome = "Horda de Goblins"`).

---

## 2. Mudanças por arquivo

### 2.1 `randongeon/jogo/entidades/inimigo.py`
- `NOMES_DIFICULDADE_1`: `"Nosferatu"` → `"Bando de Goblins"`.
- Classe `VampiroDasSombras` renomeada para **`Nosferatu`**; `nome="Nosferatu"`,
  `tipo_especial="nosferatu"` (a mecânica de regeneração 20% foi mantida).
- Classe `CacadorSombrio` **removida**.
- `gerar()`: removida a entrada do Caçador (`andar >= 10`); a do vampiro virou
  `Nosferatu` (`andar >= 15`). Pool de especiais agora: Golem (8), Nosferatu (15),
  Banshee (17) — além da Horda (qualquer andar).

### 2.2 `randongeon/jogo/sistemas/masmorra.py`
- `_indicador_especial`: chave `"vampiro"` → `"nosferatu"`; entrada `"cacador"` removida.
- Textos fixos "O Vampiro das Sombras absorveu..." passaram a usar `inimigo.nome`
  (dinâmico) — funciona para o Nosferatu e qualquer futuro inimigo com cura.

### 2.3 `randongeon/tests/test_novos_inimigos.py`
- Import e referências de `VampiroDasSombras` → `Nosferatu`; asserts de nome/tipo.
- Classe `TestCacadorSombrio` removida; testes de threshold/fuga/dispatcher do
  Caçador removidos; `Nosferatu` mantido em todos os testes equivalentes.

---

## 3. Pilares de POO em destaque (com referência aos slides)

### Herança — slide *"Herança"* e *"Composição vs Herança"*
`Nosferatu`, `GolemDePedra`, `HordaDeGoblins` e `Banshee` **são um** `Inimigo`
(relação "é um" → herança). Cada subclasse:
```python
class Nosferatu(Inimigo):
    def __init__(self) -> None:
        super().__init__(nome="Nosferatu", hp=..., tipo_especial="nosferatu", ...)
```
- Usa **`super().__init__(...)`** para reaproveitar a construção/validações da
  superclasse `Inimigo` (evita repetição de código — exatamente o propósito de
  herança citado no slide).
- Herda métodos como `receber_dano()`, `curar()`, `esta_vivo()` sem reescrevê-los.

### Polimorfismo — slide *"Polimorfismo"*
O código que consome inimigos trata todos pela **mesma interface**, e cada tipo
responde à sua maneira:
- `Inimigo.gerar(andar)` devolve `Inimigo` OU qualquer subclasse; quem chama não
  precisa saber qual é.
- `_indicador_especial(inimigo)` e o laço de combate usam `inimigo.tipo_especial`,
  `inimigo.cura_percentual` etc. de forma uniforme — o mesmo trecho lida com
  Golem, Nosferatu, Banshee e comuns.

### Abstração / Encapsulamento (apoio)
- O `tipo_especial` é a "etiqueta" que abstrai a mecânica para a camada de
  apresentação (badges) sem ela conhecer a classe concreta.

---

## 4. Conteúdo além dos slides?

**Não.** O Lote B usa apenas Herança (`super()`), Polimorfismo (mesma interface,
tipos diferentes) e construtores — tudo presente nos slides. *(A convenção
`# [POO AVANÇADO — fora dos slides]` segue reservada para quando for necessário.)*

> 🛈 **Nota técnica:** o atributo `bonus_atk_por_turno` (antes usado só pelo Caçador)
> ficou **dormente** — nenhum inimigo o usa agora, mas a infraestrutura genérica
> (`Inimigo.__init__` + tratamento em `masmorra`/API) foi **mantida** de propósito,
> para um futuro inimigo poder reutilizá-la sem reescrever nada.

---

## 5. Resultado e arquivos

```
pytest tests/ -q  →  543 passed, 5 skipped
(queda vs. 557 do Lote A = remoção dos ~14 testes do Caçador)
```

```
M  randongeon/jogo/entidades/inimigo.py
M  randongeon/jogo/sistemas/masmorra.py
M  randongeon/tests/test_novos_inimigos.py
A  docs/inimigos-LoteB.md
```

> Frontend: sem quebra. `nome="Nosferatu"` passa a usar o sprite `nosferatu.png`
> já existente (`spriteMap.ts`); a API envia `tipo_especial` dinamicamente.

---
*Lote B — pendente de merge na `main`.*
