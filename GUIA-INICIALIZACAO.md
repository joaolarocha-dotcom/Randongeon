# 🎮 Guia de Inicialização — Randongeon (Pokémon-style)

Este guia leva você do zero ao jogo rodando no navegador, em estilo batalha Pokémon Gen 1.

> **Resumo:** abra dois terminais — um para a API Python (porta 8000) e outro para o frontend React (porta 5173). Depois acesse `http://localhost:5173` no navegador.

---

## 📋 Pré-requisitos

Verifique que você tem instalado:

| Ferramenta | Versão mínima | Comando para checar |
|------------|---------------|---------------------|
| **Python**  | 3.10+ | `python --version` |
| **Node.js** | 18+ | `node --version` |
| **npm**     | 9+ | `npm --version` |

Se algum estiver faltando:
- Python: https://www.python.org/downloads/
- Node.js (já vem com npm): https://nodejs.org/

---

## 🚀 Opção 1: Inicialização rápida (Windows)

Na raiz do projeto, há um script `start.bat` que faz tudo automaticamente:

```powershell
start.bat
```

Esse script:
- Cria o ambiente virtual Python se necessário
- Instala dependências da API e do frontend
- Abre a API e o frontend em janelas separadas

Aguarde até as duas janelas aparecerem e depois abra **http://localhost:5173** no navegador.

---

## 🛠️ Opção 2: Passo a passo manual

Use esta opção se for sua primeira vez ou se algo der errado.

### 2.1 Abra um terminal na raiz do projeto

```powershell
cd "C:\Users\Gabriel\Desktop\PROJETOS\PROJETOS - PESSOAIS\Randongeon\Randongeon"
```

### 2.2 Criar e ativar o ambiente virtual Python

```powershell
# Cria o venv (só uma vez)
python -m venv .venv

# Ativa no PowerShell
.\.venv\Scripts\Activate.ps1
```

> Se o PowerShell bloquear o script de ativação, rode antes:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

No CMD use `.\.venv\Scripts\activate.bat`.

### 2.3 Instalar dependências Python

```powershell
pip install -r api\requirements.txt
pip install -r randongeon\requirements.txt
```

### 2.4 (Opcional) Rodar os testes do backend

```powershell
pytest randongeon\tests\ -v
```

Devem passar 352+ testes.

### 2.5 Iniciar a API (terminal 1)

Com o venv ativo, **na raiz do projeto**:

```powershell
uvicorn api.main:app --reload --port 8000
```

Aguarde a mensagem `Uvicorn running on http://127.0.0.1:8000`. Você pode testar abrindo:
- **API:** http://localhost:8000
- **Docs interativas:** http://localhost:8000/docs

Deixe esse terminal aberto.

### 2.6 Instalar dependências do frontend (1ª vez)

Abra um **segundo terminal** na raiz do projeto:

```powershell
cd frontend
npm install
```

### 2.7 Iniciar o frontend (terminal 2)

```powershell
npm run dev
```

Aguarde a mensagem `Local: http://localhost:5173/`.

### 2.8 Abrir o jogo no navegador

Acesse: **http://localhost:5173**

---

## 🎮 Controles do jogo

### Tela de título
- Digite seu nome e clique **INICIAR**.

### Tela de masmorra (overworld)
- **AVANÇAR** → entra na próxima sala (combate, baú ou loja).
- **DESISTIR** → encerra a partida.

### Batalha (estilo Pokémon)
- Após o diálogo de introdução, o menu 2x2 aparece:
  - **LUTAR** → ataque normal.
  - **ITEM** → (em breve) usar item do inventário.
  - **ESQUIVAR** → tenta esquivar e contra-atacar.
  - **FUGIR** → 50% de chance de fugir.
- **Teclas do menu de batalha:** setas (↑↓←→) para navegar, **Enter** ou **Espaço** para confirmar.
- **Clique** na caixa de diálogo branca para pular a digitação ou avançar para o próximo texto.

### Baú
- **ABRIR** → ganha o item ou revela um Mímico (combate forçado).
- **IGNORAR** → segue em frente sem riscos.

### Loja
- Clique no preço de uma oferta para comprar (precisa de moedas suficientes).
- **SAIR DA LOJA** → volta ao overworld.

### Tela final
- **JOGAR NOVAMENTE** → reinicia a sessão.

---

## 🔊 Áudio

O jogo toca BGM e SFX automaticamente. Por restrições do navegador, a música só inicia **depois do primeiro clique** (no botão INICIAR da tela de título). Se ouvir só silêncio, certifique-se de:
1. O volume do sistema não está mutado.
2. Você clicou pelo menos uma vez na página.
3. Os arquivos de áudio existem em `frontend/public/assets/sounds/` (faltas são silenciosas, não quebram o jogo).

---

## 🩹 Solução de problemas

| Sintoma | Causa provável | Solução |
|---------|----------------|---------|
| `ModuleNotFoundError: No module named 'api'` | Rodou uvicorn de outra pasta | Volte para a raiz e rode `uvicorn api.main:app --reload --port 8000` |
| Frontend mostra "Erro: Failed to fetch" | API não está rodando | Confirme o terminal 1 com `uvicorn` ativo na porta 8000 |
| `npm install` falha | Node.js antigo | Atualize para Node 18+ (`node --version`) |
| Porta 8000 ocupada | Outro processo | Use `--port 8001` no uvicorn e edite `frontend/src/api/client.ts` linha 1 (`API_BASE`) |
| Porta 5173 ocupada | Outro Vite rodando | Encerre o outro ou rode `npm run dev -- --port 5174` |
| Sprites quebrados (X vermelho) | Arquivo faltando | O jogo cai automaticamente para `goblin.png` via `onError`. Cheque o nome em `public/assets/sprites/` |
| Sem música | Browser bloqueou autoplay | Clique em qualquer lugar do jogo — após a primeira interação a música começa |
| Tela toda branca | Erro JS | Abra o DevTools (F12) → aba **Console** e veja a mensagem de erro |
| `Press Start 2P` não carrega | Sem internet | A fonte vem do Google Fonts CDN; sem net o fallback é monospace genérico |

---

## 🛑 Como parar tudo

- **Terminal 1 (API):** `Ctrl + C`
- **Terminal 2 (frontend):** `Ctrl + C`
- Se algum ficou preso: `Get-Process node, python | Stop-Process` no PowerShell.

---

## 📂 Comandos úteis (referência rápida)

```powershell
# Backend
.\.venv\Scripts\Activate.ps1              # ativa venv
uvicorn api.main:app --reload --port 8000 # roda API
pytest randongeon\tests\ -v               # roda testes

# Frontend
cd frontend
npm install                                # 1ª vez
npm run dev                                # dev server (porta 5173)
npm run build                              # build de produção
npm run preview                            # preview do build
npm run lint                               # checa lint
```

---

*Boa caçada na masmorra, herói.* ⚔️
