# Auditoria de Aderência aos Slides de POO — Randongeon (PROVA)

> Documento consolidado do **Lote 7**. Compara o conteúdo dos slides do professor
> (Fernando Henrique Vieira Trindade) com **todo o código Python** do projeto
> (`randongeon/jogo/`, `randongeon/sistemas/` e `api/`), mapeando cada tópico ao
> trecho onde é usado, destacando as técnicas mais avançadas e por quê, e
> registrando com honestidade o que **não** foi usado.

## 1. O que o professor cobrou (fonte)

Três PDFs: `POO Slide.pdf` e `POO aula.pdf` (idênticos — os 4 pilares) e
`POO_Python_Código.pdf` (22 págs, o vocabulário detalhado em Python). Tópicos:

- **Fundamentos:** paradigma OO (dados+comportamento juntos), classe vs objeto,
  construtor `__init__`/`self`, **atributos de instância vs de classe**.
- **Encapsulamento:** 3 níveis de visibilidade (`público` / `_protegido` /
  `__privado` com name mangling) e **`@property`** (getter/setter com validação).
- **Herança:** `Filha(Pai)`, `super()`, sobrescrita.
- **Polimorfismo:** mesmo método, comportamento por tipo (override); overloading.
- **Abstração:** **ABC** + `@abstractmethod` (contrato); interfaces e **duck typing**.
- **Avançados:** herança múltipla e **MRO**; **`@staticmethod`/`@classmethod`**.
- **Dunder methods:** `__init__`, `__str__`, `__repr__`, `__eq__`, `__lt__`,
  `__len__`, `__add__`, `__contains__`, `__iter__`, `__getitem__`.
- **Composição vs Herança:** "é um" (herda) vs "tem um" (compõe).

## 2. Mapa conteúdo → código (resumo)

| Tópico do professor | Status | Onde (arquivo · símbolo) |
|---|---|---|
| Classe/Objeto, `__init__`, `self` | ✅ | todas as entidades (`jogador.py`, `inimigo.py`, `item.py`, `efeitos.py`, `dom.py`, `loja.py`, `gerador.py`, `masmorra.py`) |
| Atributos de **instância vs classe** | ✅ | `Jogador` — constantes de classe `ATK_POR_NIVEL`, `HP_POR_NIVEL`, `XP_BASE_NIVEL`, `CURA_NIVEL_FRACAO`… vs `self.hp/atk/xp`; `BandoDeGoblins.TAMANHO` |
| Encapsulamento — público | ✅ | `self.nome`, `self.hp`, `self.atk` (Entidade/Jogador/Inimigo) |
| Encapsulamento — `_protegido` | ✅ | `Jogador._atualizar_nivel()`, `GeradorSala._chance_item`, `Masmorra._rolar_loot()`, `CoracaoDaMasmorra._ja_renasceu` |
| Encapsulamento — `__privado` (name mangling) | ❌ | não usado (ver §5) |
| **`@property`** (getter) | ✅ (getter) | `Jogador.pontuacao`, `Jogador.veneno_turnos`, `Jogador.envenenado`, `CoracaoDaMasmorra.ja_renasceu` |
| `@property.setter` (com validação) | ❌ | não usado — validação fica no `__init__`/métodos (ver §5) |
| **Herança** + `super()` + sobrescrita | ✅ | `Jogador(Entidade)`, `Inimigo(Entidade)`, 8 subclasses de `Inimigo`, 3 de `EfeitoStatus`; `super().__init__` em todas |
| **Polimorfismo** (override sem `if tipo`) | ✅ | `receber_dano()`, `tabela_loot()`, `tentar_renascer()`, hooks de `EfeitoStatus` |
| **ABC** + `@abstractmethod` | ✅ | `Entidade(ABC)` com `receber_dano` abstrato; `EfeitoStatus(ABC)` |
| **Duck typing** | ✅ | `getattr(alvo,"evasao_passiva",0.0)` em `Inimigo.atacar`; `getattr(jogador,"curar_veneno",None)` em `Item.usar`; vários no `masmorra.py` |
| **`@staticmethod`** (fábrica) | ✅ | `Inimigo.gerar(andar)` |
| `@classmethod` | ❌ | não usado (a fábrica é `@staticmethod`) — ver §5 |
| Herança múltipla / MRO | ❌ | não usado (hierarquia é de herança simples) — ver §5 |
| **Dunder** `__init__` / `__repr__` | ✅ | `__init__` em tudo; `__repr__` em `Jogador`, `Inimigo`, `Item` |
| Dunder ricos (`__eq__`,`__lt__`,`__len__`,`__iter__`,`__getitem__`,`__contains__`,`__add__`,`__str__`) | ❌ | não usados (ver §5) |
| **Composição vs Herança** | ✅ | `BandoDeGoblins` **TEM** Goblins (composição) vs `Goblin(Inimigo)` (herança); `Masmorra` TEM `Jogador`+`GeradorSala` |

## 3. Os 4 pilares no Randongeon (com trechos)

### Abstração — `Entidade(ABC)` (`jogo/entidades/entidade.py`)
```python
class Entidade(ABC):                 # não instanciável (abstração + ABC)
    def esta_vivo(self) -> bool: ...
    def curar(self, quantidade): ...
    @abstractmethod
    def receber_dano(self, dano: int) -> int:   # contrato: cada filho implementa
        raise NotImplementedError
```
Define a **interface comum** (o "O QUÊ": tem vida, cura, sofre dano) e esconde o
"COMO". `Jogador` e `Inimigo` são tratados uniformemente "como Entidades".

### Encapsulamento — visibilidade + `@property` (`jogo/entidades/jogador.py`)
```python
class Jogador(Entidade):
    ATK_POR_NIVEL = 2      # atributo de CLASSE (constante compartilhada)
    CURA_NIVEL_FRACAO = 0.60
    def _atualizar_nivel(self):    # _protegido: detalhe interno (não é API pública)
        ...
    @property
    def pontuacao(self) -> int:    # getter calculado, sem expor o cálculo
        return self.xp + (self.nivel - 1) * 50 + self.moedas
```
Usa **público** (`self.hp`), **`_protegido`** (`_atualizar_nivel`) e **`@property`**
(leitura derivada). Constantes de balanceamento ficam em **atributos de classe**.

### Herança — `super()` e sobrescrita (`jogo/entidades/inimigo.py`)
```python
class Nosferatu(Inimigo):          # "é um" Inimigo
    def __init__(self, bonus_hp=0, bonus_atk=0):
        super().__init__(nome="Nosferatu", hp=..., cura_percentual=0.20, ...)
    def tabela_loot(self):         # sobrescreve o pool de loot
        return LOOT_NOSFERATU
```
8 subclasses de `Inimigo` (Nosferatu, GolemDePedra, Banshee, Orc, TrollDasCavernas,
HordaDeGoblins, Goblin, CoracaoDaMasmorra) reaproveitam o construtor via `super()`.

### Polimorfismo — mesmo método, sem `if tipo` (`jogo/entidades/inimigo.py`)
```python
# Quem rola o loot NÃO sabe o tipo concreto:
return random.choice(inimigo.tabela_loot())   # cada classe devolve o seu pool

# receber_dano é polimórfico: Inimigo desconta armadura, Jogador sofre direto.
# atacar() é guiado pelos ATRIBUTOS da instância (cura_percentual, chance_atordoar…),
# então Nosferatu rouba vida e Banshee atordoa SEM um if por tipo.
```

## 4. Técnicas mais avançadas/complexas — e **por quê**

1. **ABC + método abstrato** (`Entidade`, `EfeitoStatus`). *Por quê:* garantir um
   **contrato** — toda Entidade obriga `receber_dano`; todo efeito expõe os hooks.
   Elimina o código de vida/cura duplicado que existia em Jogador e Inimigo.

2. **Template Method** (`Inimigo.tentar_renascer`). *Por quê:* o fluxo de morte do
   combate chama `inimigo.tentar_renascer()` sem saber o tipo; a base devolve
   `False` e só `CoracaoDaMasmorra` sobrescreve para ressuscitar 1×. Adiciona a
   "2ª fase" do boss **sem um `if`** no laço de combate.

3. **Polimorfismo guiado por dados** (`Inimigo.atacar`, `tabela_loot`,
   `receber_dano`). *Por quê:* um único laço de combate serve a todos os inimigos;
   comportamentos especiais (lifesteal, atordoar, veneno, armadura) vêm dos
   atributos/override, não de `if`s por tipo — mais extensível e testável.

4. **Sistema de `EfeitoStatus` (hooks polimórficos)** (`jogo/entidades/efeitos.py`).
   *Por quê:* em vez de flags soltas (`veneno_turnos`, `fraqueza_turnos`…), cada
   efeito é uma classe com `ao_iniciar_turno`/`modifica_atk`/`modifica_esquiva`; a
   Entidade processa todos uniformemente. Estende-se criando uma subclasse.

5. **Composição vs Herança** (`BandoDeGoblins` × `Goblin`). *Por quê:* um Goblin
   **é um** Inimigo (herda combate); um Bando **tem** Goblins (relação "tem um") —
   não é um Inimigo, é um agrupador. Decisão explícita do slide.

6. **Duck typing defensivo** (`getattr(alvo,"evasao_passiva",0.0)`). *Por quê:* o
   combate funciona com qualquer "coisa atacável" que exponha os atributos certos,
   sem exigir herança — tolera dummies de teste e evita acoplamento.

7. **`@property` calculada** (`pontuacao`, `veneno_turnos`). *Por quê:* expor um
   valor **derivado** com sintaxe de atributo, sem deixar o estado ser escrito de
   fora — encapsulamento sem getters verbosos.

8. **Fábrica `@staticmethod`** (`Inimigo.gerar`). *Por quê:* centraliza a geração
   procedural (sorteio de comum/elite/especial + escala por andar) numa função
   ligada à classe que não depende de instância.

9. **Atributos de classe como constantes de balanceamento** (`Jogador.*`,
   `BandoDeGoblins.TAMANHO`, constantes de módulo em `inimigo.py`/`masmorra.py`).
   *Por quê:* números tunáveis compartilhados por todas as instâncias, separados
   da lógica — calibrados por simulação Monte Carlo.

## 5. Tópicos do professor **não** usados (honestidade) + onde caberiam

| Tópico | Por que não foi necessário | Onde caberia (se quiser demonstrar) |
|---|---|---|
| `__privado` (name mangling) | O projeto usa `_protegido` (convenção) + validação no `__init__`; nada exigia bloqueio forte de acesso. | `Jogador.__xp` com `@property` de leitura. |
| `@property.setter` com validação | As `@property` do projeto são **calculadas/somente-leitura**; a validação mora no `__init__`/métodos. | setter de `esq` validando `0..esq_max`. |
| `@classmethod` | A fábrica `Inimigo.gerar` é `@staticmethod` (não usa `cls`). | `CoracaoDaMasmorra.from_andar(cls, andar)`. |
| Herança múltipla / MRO | A hierarquia é de **herança simples** (mais clara); o domínio não pediu mistura de duas bases. | um mixin `Venenoso`/`Atordoante`. |
| Dunder ricos (`__eq__`, `__lt__`, `__len__`, `__iter__`, `__getitem__`, `__contains__`, `__add__`, `__str__`) | Só `__init__`/`__repr__` foram necessários até aqui. | `BandoDeGoblins.__len__/__iter__/__getitem__` (já é coleção!); `Item.__eq__/__lt__` (ordenar por bônus). |

> Esses **não são erros** — são tópicos do material que o domínio não exigiu. Estão
> listados para transparência da prova; vários têm um encaixe natural se o professor
> quiser vê-los demonstrados (ver Lote 7b, opcional).

## 6. Cobertura

- **4 pilares:** ✅ todos com trecho real (Abstração/ABC, Encapsulamento/@property,
  Herança/super, Polimorfismo/override).
- **Vocabulário do PDF de código:** ~12 de ~17 itens usados de forma concreta;
  os 5 ausentes estão documentados em §5 com encaixe sugerido.
- **Extras do professor** ("Python adiciona"): `@property` ✅, duck typing ✅,
  dunder (parcial: `__init__`/`__repr__`) ⚠️, herança múltipla ❌.

O código **já cita os slides** nos comentários (ex.: "slide 'Classes Abstratas'",
"slide 'Composição vs Herança'", "slide 'Atributos de Instância e de Classe'"),
o que evidencia que foi escrito com o material em mãos.
