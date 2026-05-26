# 🗡️ Randongeon

> **RPG de Texto com Geração Procedural e Testes Unitários em Python**

Universidade Tiradentes — UNIT | Curso de Ciência da Computação
Disciplina: Laboratório de Programação | Aracaju-SE, 2026

---

## 👥 Integrantes do Grupo

| Nome |
- Gabriel Henrique Costa Novaes
- João pedro Neiva de Souza
- Moisés Menezes dos Santos
- ⁠Raphael Paiva Almeida de Andrade Gomes
- ⁠Letícia Freire Fonseca
- João Luís Aragão Rocha
- ⁠Eduarda Santana Santos

---

## 📋 Sumário

1. [Descrição do Projeto](#1-descrição-do-projeto)
2. [Requisitos e Instalação](#2-requisitos-e-instalação)
3. [Como Executar](#3-como-executar)
4. [Estrutura do Projeto](#4-estrutura-do-projeto)
5. [Funcionalidades](#5-funcionalidades)
6. [Arquitetura e Decisões Técnicas](#6-arquitetura-e-decisões-técnicas)
7. [Testes Unitários](#7-testes-unitários)
8. [Conceitos Aplicados da Disciplina](#8-conceitos-aplicados-da-disciplina)
9. [Exemplos de Execução](#9-exemplos-de-execução)
10. [Manual de Inicialização do Projeto](#10-manual-de-inicialização-do-projeto)

---

## 1. Descrição do Projeto

O **Randongeon** é um RPG de texto desenvolvido em Python no contexto da disciplina de Laboratório de Programação. O jogador controla um aventureiro que desce progressivamente pelos andares de uma masmorra proceduralmente gerada, enfrentando inimigos, coletando itens, comprando na loja do mercador e enfrentando chefões a cada quinto andar.

O projeto foi concebido com **duplo propósito**: entregar um sistema de jogo funcional e interativo, e servir como plataforma de aprendizado e demonstração de boas práticas de engenharia de software — em especial a construção de uma suíte completa de testes unitários automatizados com `pytest`.

O projeto suporta um modo de geração de conteúdo:
- **GeradorSimples** — geração aleatória local, sem dependências externas.

### 1.1 Motivação

A escolha do tema RPG de texto foi motivada pela adequação natural do gênero à prática de testes unitários: sistemas de RPG possuem regras claras, entidades bem definidas e comportamentos verificáveis — o que torna cada classe um candidato ideal para cobertura de testes. Além disso, o gênero permite explorar conceitos como **aleatoriedade controlada**, **separação de camadas** (lógica versus apresentação) e **injeção de dependência**.

### 1.2 Escopo Geral

- Sistema de combate por turnos com ataque, esquiva e fuga
- Geração procedural de salas com três tipos de evento: inimigo, item e loja
- Sistema de progressão: XP, moedas, atributos escaláveis
- Cinco classes de entidades: `Jogador`, `Inimigo`, `Item`, `Loja`, `GeradorSala`
- Dois sistemas de orquestração: `Masmorra` e `GeradorSala`
- Backends de geração: `GeradorSimples` (local)
- Suíte de **352+ testes unitários automatizados** com `pytest`
- Cobertura de código de aproximadamente **95%** da lógica de negócio

---

## 2. Requisitos e Instalação

### 2.1 Pré-requisitos

| Requisito | Versão |
|-----------|--------|
| **Python** | 3.10 ou superior |
| **Sistema Operacional** | Windows 10+, Linux ou macOS |
| **Dependências** | `pytest >= 7.4.0`, `pytest-cov >= 4.1.0`

### 2.2 Instalação Passo a Passo

**Passo 1 — Obter o código**

Clone o repositório ou extraia o arquivo compactado:

```bash
git clone https://github.com/<usuario>/randongeon.git
cd randongeon
```

**Passo 2 — Criar e ativar o ambiente virtual**

O ambiente virtual isola as dependências do projeto. Este passo é recomendado, mas não obrigatório.

```bash
# Criar o ambiente virtual
python -m venv .venv

# Ativar — Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Ativar — Linux / macOS
source .venv/bin/activate
```

O terminal exibirá `(.venv)` no início da linha quando o ambiente estiver ativo.

**Passo 3 — Instalar as dependências**

```bash
pip install -r requirements.txt
```

O arquivo `requirements.txt` contém:

```
pytest>=7.4.0       # framework de testes unitários
pytest-cov>=4.1.0   # relatório de cobertura de código
openai              # necessário apenas para o GeradorIA
```

---

## 3. Como Executar

### 3.1 Executar o Jogo

Com o terminal aberto na raiz do projeto e o ambiente virtual ativo:

```bash
python src/main.py
```

O jogo exibirá a lore introdutória, solicitará o nome do aventureiro e iniciará o loop principal. Os controles são realizados por entrada numérica no terminal:

| Contexto | Controles |
|----------|-----------|
| **Menu principal** | `1` = Avançar · `2` = Ver Status · `3` = Desistir |
| **Em combate** | `1` = Atacar · `2` = Esquivar e Atacar · `3` = Fugir |
| **Na loja** | `1` ou `2` = Comprar item · `0` = Sair da loja |


### 3.2 Executar os Testes Unitários

**Rodar a suíte completa:**

```bash
pytest tests/ -v
```

**Rodar com relatório de cobertura no terminal:**

```bash
pytest tests/ -v --cov=src --cov-report=term-missing
```

**Rodar com relatório HTML (visualização no navegador):**

```bash
pytest tests/ -v --cov=src --cov-report=html
# Abra o arquivo htmlcov/index.html no navegador
```

**Rodar um arquivo de testes específico:**

```bash
pytest tests/test_inimigo.py -v
pytest tests/test_jogador.py -v
pytest tests/test_jogo.py -v
```

---

## 4. Estrutura do Projeto

O projeto adota a separação clássica de responsabilidades: **entidades** (dados e comportamentos individuais), **geradores** (estratégias de criação de conteúdo) e **testes** (verificação automatizada de cada camada).

```
randongeon/
├── src/
│   ├── main.py                        # Ponto de entrada do jogo
│   ├── geradores/
│   │   ├── __init__.py
│   │   ├── gerador_base.py            # Interface/contrato base (GeradorBase)
│   │   ├── gerador_simples.py         # Geração aleatória local
│   │   └── gerador_ia.py              # Geração via OpenAI
│   └── jogo/
│       ├── __init__.py
│       ├── inimigo.py                 # Entidade Inimigo
│       ├── jogador.py                 # Entidade Jogador
│       └── jogo.py                    # Orquestrador principal (loop de turnos)
├── tests/
│   ├── __init__.py
│   ├── test_inimigo.py
│   ├── test_jogador.py
│   └── test_jogo.py
├── requirements.txt
└── README.md
```

| Arquivo / Pasta | Responsabilidade |
|-----------------|-----------------|
| `src/main.py` | Ponto de entrada. Inicializa o gerador, cria o `Jogo` e mantém o loop principal. |
| `src/geradores/gerador_base.py` | Classe abstrata `GeradorBase` com interface `gerar_sala()` e `gerar_inimigo()`. |
| `src/geradores/gerador_simples.py` | Implementação local com listas fixas e `random`. Sem dependências externas. |
| `src/geradores/gerador_ia.py` | Implementação via OpenAI. Gera sala e inimigo com linguagem natural. |
| `src/jogo/inimigo.py` | Classe `Inimigo` com atributos `nome`, `vida`, `ataque` e método `atacar()`. |
| `src/jogo/jogador.py` | Classe `Jogador` com atributos `vida`, `ataque` e método `atacar()`. |
| `src/jogo/jogo.py` | Classe `Jogo` — orquestrador. Gerencia turnos, combate e condição de vitória/derrota. |
| `tests/` | Arquivos de teste cobrindo as entidades e o fluxo de jogo. |

---

## 5. Funcionalidades

### 5.1 Sistema de Combate

O combate é executado em turnos. O jogador sempre age primeiro. O inimigo contra-ataca apenas se ainda estiver vivo após o ataque do jogador.

- **Atacar:** o jogador inflige dano aleatório no HP do inimigo baseado em seu atributo de ataque.
- **Esquivar e Atacar:** o jogador tenta esquivar antes de contra-atacar. Sucesso evita o dano; falha recebe dano dobrado.
- **Fugir:** tentativa com 50% de chance de sucesso. Em falha, o jogador ainda recebe dano do inimigo.
- **Vitória:** derrota o inimigo e avança para a próxima sala.

### 5.2 Geração Procedural de Salas

A cada turno, uma sala é gerada pelo gerador configurado. O `GeradorSimples` sorteia entre descrições pré-definidas e pools de inimigos por dificuldade:

| Tipo de sala | Descrição |
|--------------|-----------|
| **Inimigo (80%)** | Um inimigo aleatório aparece para o combate. |
| **Item (10%)** | Um baú com item aparece; o jogador pode abrir ou ignorar. |
| **Loja (10%)** | A loja do mercador com até 2 itens disponíveis para compra. |

### 5.3 Inimigos e Dificuldade

- **Comum (Dificuldade 1):** HP 3–8, ATK 1–3. Ex: Goblin, Rato Gigante, Nosferatu.
- **Elite (Dificuldade 2):** HP 8–15, ATK 3–5. Aparece a partir do andar 3 com 30% de chance.
- **Boss (Dificuldade 3):** Aparece a cada múltiplo de 5 andares, com atributos escalados.
- **Mímico:** Inimigo especial que se disfarça de baú; aparece com 1/20 de chance em salas de inimigo.

### 5.4 Backends de Geração

| Gerador | Como funciona |
|---------|---------------|
| `GeradorSimples` | Utiliza `random.choice()` em listas de descrições e nomes pré-definidos. Sem dependências externas. |

---

## 6. Arquitetura e Decisões Técnicas

### 6.1 Padrão Strategy no Gerador

A arquitetura central do projeto usa o **padrão Strategy**: a classe `GeradorBase` define a interface (`gerar_sala`, `gerar_inimigo`), e `GeradorSimples` são implementações intercambiáveis. A classe `Jogo` depende apenas da abstração, não da implementação concreta — permitindo trocar o backend sem modificar a lógica de jogo.

```python
# main.py — trocar o gerador é tudo que muda
jogo = Jogo(GeradorSimples())   # local
```

### 6.2 Separação entre Lógica e Apresentação

Todo método com lógica verificável (combate, progressão, geração) não realiza `print()`, `input()` ou `time.sleep()`. Esses elementos ficam exclusivamente nos métodos de apresentação. Esta separação é a condição necessária para que os testes unitários possam exercitar a lógica sem efeitos colaterais de terminal — aplicação direta do **Single Responsibility Principle (SRP)**.

### 6.3 Injeção de Dependência no Jogo

A classe `Jogo` recebe o gerador como parâmetro no construtor. Nos testes, isso permite substituir o gerador por um `FakeGerador` controlado que retorna conteúdo fixo, eliminando aleatoriedade e garantindo testes determinísticos.

```python
class FakeGerador:
    def gerar_sala(self):
        return "Sala fake"
    def gerar_inimigo(self):
        return Inimigo("Fake", 5, 1)

jogo = Jogo(FakeGerador())  # totalmente controlado nos testes
```

### 6.4 Separação de Imports por Contexto

O projeto usa dois esquemas de import dependendo do contexto de execução:

- **Execução direta** (`python src/main.py`): imports relativos sem prefixo de pacote.
- **Execução via pytest** (`pytest tests/`): imports com prefixo `src.` para resolução correta do pacote.

---

## 7. Testes Unitários

### 7.1 Visão Geral da Suíte

| Arquivo de Teste | Testes | Destaques |
|-----------------|--------|-----------|
| `test_jogador.py` | ~55 | Atributos iniciais, métodos de progressão, parametrize em dano |
| `test_inimigo.py` | ~45 | Criação, ataque, mocks com `side_effect` |
| `test_jogo.py` | ~107 | Injeção de `FakeGerador`, inicialização, fluxo de turno |

**Total: 352+ testes | Cobertura: ~95%**

### 7.2 Padrão AAA (Arrange-Act-Assert)

Todos os testes seguem o padrão AAA:

```python
def test_jogador_vida_inicial():
    # Arrange
    j = Jogador()
    # Act / Assert
    assert j.vida == 20
```

### 7.3 Cobertura de Código

A cobertura medida pelo `pytest-cov` fica em torno de **95%** para o pacote `src/`. Os 5% restantes correspondem aos métodos de apresentação que dependem de `input()` e não são alvo de testes unitários.

```
Name                                Stmts   Miss  Cover
-------------------------------------------------------
src/jogo/inimigo.py                    12      0   100%
src/jogo/jogador.py                    10      0   100%
src/jogo/jogo.py                       28      3    89%
src/geradores/gerador_base.py           4      0   100%
src/geradores/gerador_simples.py       14      0   100%
-------------------------------------------------------
TOTAL                                  68      3    96%
```

### 7.4 Técnicas de Isolamento Utilizadas

- **`@pytest.fixture`** — objetos pré-configurados reutilizáveis em múltiplos testes.
- **`@patch` (unittest.mock)** — substituição de `random.random`, `random.randint` e `random.choice` por stubs com valores fixos, tornando os testes determinísticos.
- **`MagicMock`** — dublê genérico para verificar que métodos foram chamados com os argumentos corretos (`assert_called_once_with`).
- **`FakeGerador`** — classe stub inline que retorna sempre o mesmo conteúdo de sala, isolando a lógica do `Jogo` da aleatoriedade do gerador.

---

## 8. Conceitos Aplicados da Disciplina

### 8.1 Programação Orientada a Objetos

- **Classes e instâncias:** `Jogador`, `Inimigo`, `GeradorBase`, `GeradorSimples`, `GeradorIA`, `Jogo`.
- **Herança:** `GeradorSimples` herda de `GeradorBase`.
- **Encapsulamento:** atributos validados no `__init__` com `ValueError` para entradas inválidas.
- **Polimorfismo:** `Jogo` chama `gerador.gerar_sala()` sem saber qual implementação está sendo usada.
- **Composição:** `Jogo` contém um `Jogador` e um `GeradorBase`.

### 8.2 Estruturas de Dados

- **Listas:** pools de nomes de inimigos, descrições de salas, catálogos de itens.
- **Dicionários:** estrutura de retorno dos métodos de combate e compra (`{sucesso, mensagem, dano}`).
- **Tuplas:** retornos múltiplos de `gerar_sala()` (tipo, conteúdo, descrição).

### 8.3 Controle de Fluxo e Funções

- **Expressões booleanas compostas:** `andar >= 3 and random.random() < 0.3`.
- **Operador módulo:** `self.sala_atual % BOSS_A_CADA_ANDARES == 0` para detectar andares de boss.
- **`min()` / `max()`:** para limitar dano e cura dentro de faixas válidas.
- **F-strings:** utilizadas em toda a camada de apresentação.

### 8.4 Testes Unitários com pytest

- Fixtures globais (`conftest.py`) e locais por arquivo.
- `pytest.raises` para verificar exceções esperadas.
- `@pytest.mark.parametrize` para executar o mesmo teste com múltiplos conjuntos de dados.
- Mocks com `@patch` e `MagicMock` para controlar dependências externas.
- Cobertura de código com `pytest-cov` e relatório `term-missing`.

---

## 9. Exemplos de Execução

### 9.1 Saída Esperada do Jogo

```
Qual o seu nome, aventureiro?
> Neiva

--- O QUE DESEJA FAZER? ---
1 - Avançar
2 - Ver status
3 - Desistir
> 1

--- Sala 1 ---
Uma sala escura com cheiro de mofo.
Um Goblin apareceu! (Vida: 7)

[A]tacar ou [F]ugir: a
Você causou 4 de dano.
O Goblin causou 2 de dano.

[A]tacar ou [F]ugir: a
Você causou 5 de dano.
Você derrotou o Goblin!
```

### 9.2 Saída Esperada dos Testes

```
$ pytest tests/ -v

tests/test_jogador.py::test_jogador_vida_inicial PASSED
tests/test_inimigo.py::test_inimigo_criacao PASSED
tests/test_jogo.py::test_jogo_inicializacao PASSED

352 passed in 2.84s
```

### 9.3 Saída Esperada da Cobertura

```
$ pytest tests/ --cov=src --cov-report=term-missing

Name                                Stmts   Miss  Cover   Missing
-----------------------------------------------------------------
src/jogo/inimigo.py                    12      0   100%
src/jogo/jogador.py                    10      0   100%
src/jogo/jogo.py                       28      3    89%   (métodos interativos)
src/geradores/gerador_simples.py       14      0   100%
-----------------------------------------------------------------
TOTAL                                  68      3    96%
```

---

## 10. Manual de Inicialização do Projeto

O Randongeon é composto por três módulos que trabalham juntos: o **backend de lógica** (Python puro), a **API REST** (FastAPI) e o **frontend web** (React + Vite). Abaixo está o passo a passo para colocar tudo rodando do zero.

### 10.1 Pré-requisitos Gerais

| Ferramenta | Versão mínima | Para quê |
|------------|---------------|----------|
| **Python** | 3.10+ | Backend e API |
| **Node.js** | 18+ | Frontend |
| **npm** | 9+ | Gerenciador de pacotes do frontend |
| **Git** | 2.30+ | Clonar o repositório |

### 10.2 Clonar o Repositório

```bash
git clone https://github.com/GabrielCNovaesDev/Randongeon.git
cd Randongeon
```

### 10.3 Configurar o Backend (randongeon/)

O módulo `randongeon/` contém toda a lógica do jogo e os testes unitários.

```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar — Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Ativar — Windows (CMD)
.venv\Scripts\activate.bat

# Ativar — Linux / macOS
source .venv/bin/activate

# Instalar dependências de teste
pip install -r randongeon/requirements.txt
```

**Verificar se está tudo certo:**

```bash
# Rodar os testes unitários
pytest randongeon/tests/ -v

# Rodar o jogo no terminal (modo texto)
python randongeon/main.py
```

### 10.4 Configurar a API (api/)

A API expõe a lógica do jogo via endpoints REST para o frontend consumir.

```bash
# Com o ambiente virtual ativo, instalar dependências da API
pip install -r api/requirements.txt
```

**Iniciar o servidor:**

```bash
# A partir da raiz do projeto
uvicorn api.main:app --reload --port 8000
```

O servidor estará disponível em `http://localhost:8000`. A documentação interativa (Swagger) fica em `http://localhost:8000/docs`.

**Endpoints principais:**

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/game/new` | Criar nova partida |
| GET | `/game/{id}/status` | Status do jogador |
| GET | `/game/{id}/lore` | Texto de lore introdutória |
| POST | `/game/{id}/advance` | Avançar para próxima sala |
| POST | `/game/{id}/combat/attack` | Atacar inimigo |
| POST | `/game/{id}/combat/dodge` | Esquivar e atacar |
| POST | `/game/{id}/combat/flee` | Fugir do combate |
| POST | `/game/{id}/chest/open` | Abrir baú |
| POST | `/game/{id}/chest/ignore` | Ignorar baú |
| POST | `/game/{id}/shop/buy` | Comprar item na loja |
| POST | `/game/{id}/shop/leave` | Sair da loja |
| POST | `/game/{id}/quit` | Desistir da partida |

### 10.5 Configurar o Frontend (frontend/)

O frontend é uma aplicação React com TypeScript e Vite.

```bash
# Entrar na pasta do frontend
cd frontend

# Instalar dependências
npm install

# Iniciar o servidor de desenvolvimento
npm run dev
```

O frontend estará disponível em `http://localhost:5173` (porta padrão do Vite).

**Outros comandos úteis:**

```bash
# Build de produção
npm run build

# Verificar lint
npm run lint

# Preview do build de produção
npm run preview
```

### 10.6 Executar Tudo Junto (Resumo Rápido)

**Forma mais fácil — um único comando:**

```bash
start.bat
```

O script `start.bat` na raiz do projeto faz tudo automaticamente:
- Verifica se Python e Node.js estão instalados
- Cria o ambiente virtual se necessário
- Instala todas as dependências
- Abre a API e o frontend em janelas separadas

**Forma manual — três terminais:**

**Terminal 1 — API:**
```bash
cd api
..\.venv\Scripts\uvicorn main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 3 — (Opcional) Testes:**
```bash
.venv\Scripts\activate.bat
pytest randongeon/tests/ -v
```

### 10.7 Estrutura Atualizada do Projeto

```
Randongeon/
├── api/                          # API REST (FastAPI)
│   ├── main.py                   # Endpoints e lógica de roteamento
│   ├── schemas.py                # Modelos Pydantic de request/response
│   ├── session.py                # Gerenciamento de sessões em memória
│   └── requirements.txt          # fastapi, uvicorn
├── frontend/                     # Interface web (React + Vite)
│   ├── src/
│   │   ├── api/client.ts         # Cliente HTTP para a API
│   │   ├── components/           # Componentes reutilizáveis (HPBar, DialogBox, etc.)
│   │   ├── screens/              # Telas do jogo (Combat, Shop, Chest, etc.)
│   │   ├── store/gameStore.ts    # Estado global (Zustand)
│   │   ├── App.tsx               # Componente raiz
│   │   └── main.tsx              # Ponto de entrada
│   ├── package.json
│   └── vite.config.ts
├── randongeon/                   # Lógica do jogo (Python puro)
│   ├── jogo/
│   │   ├── entidades/            # Jogador, Inimigo, Item, Loja
│   │   └── sistemas/             # Gerador de salas, Masmorra
│   ├── tests/                    # Testes unitários (pytest)
│   ├── main.py                   # Jogo no terminal (modo texto)
│   ├── conftest.py               # Fixtures globais do pytest
│   └── requirements.txt          # pytest, pytest-cov
└── README.md
```

### 10.8 Solução de Problemas Comuns

| Problema | Solução |
|----------|---------|
| `ModuleNotFoundError` ao rodar a API | Certifique-se de estar na raiz do projeto ao executar `uvicorn api.main:app` |
| Frontend não conecta na API | Verifique se a API está rodando na porta 8000 |
| Testes falham com import error | Ative o ambiente virtual e rode `pytest` a partir da raiz do projeto |
| `npm install` falha | Verifique se Node.js 18+ está instalado (`node --version`) |
| Porta 8000 já em uso | Use `uvicorn api.main:app --reload --port 8001` e ajuste o frontend |

---

*Randongeon — Laboratório de Programação — UNIT 2026*
