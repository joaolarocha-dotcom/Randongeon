# 🚀 Guia de Deploy — Randongeon (Vercel + PythonAnywhere, 100% grátis)

Este guia coloca o **Randongeon** no ar de graça, com deploy contínuo a cada `git push`.

| Componente | Plataforma | Plano | URL final |
|---|---|---|---|
| Frontend (React + Vite) | **Vercel** | Free (100 GB/mês) | `https://randongeon.vercel.app` |
| API (FastAPI) | **PythonAnywhere** | Free (sempre online) | `https://SEU_USUARIO.pythonanywhere.com` |

---

## ✅ O que já foi preparado neste commit

Todas as mudanças de código necessárias já estão aplicadas:

1. **[`frontend/src/api/client.ts`](frontend/src/api/client.ts)** — URL da API agora vem de `VITE_API_URL`, com fallback `http://localhost:8000` em dev.
2. **[`api/main.py`](api/main.py)** — `sys.path` agora é robusto: aceita env var `RANDONGEON_PATH`, procura a pasta `randongeon/` em vários locais automaticamente.
3. **[`api/session.py`](api/session.py)** — mesma lógica de path do `main.py`.
4. **[`api/main.py`](api/main.py)** — CORS configurável via env var `ALLOWED_ORIGINS` (padrão `*`).
5. **[`frontend/.env.example`](frontend/.env.example)** — template de env var.
6. **[`frontend/vercel.json`](frontend/vercel.json)** — config padrão Vite (SPA rewrites).

---

## Parte 1 — Subir a API no PythonAnywhere (15 min)

### 1.1 Criar conta
- Acesse [pythonanywhere.com](https://www.pythonanywhere.com) e crie uma conta gratuita (`*Beginner*`).
- O nome de usuário vira o subdomínio da sua API: `https://SEU_USUARIO.pythonanywhere.com`.

### 1.2 Subir o código
**Opção A — via Git (recomendado, facilita updates):**
- Abra um **Bash console** no PythonAnywhere (menu *Consoles*).
- Clone o repositório:
  ```bash
  cd ~
  git clone https://github.com/GabrielCNovaesDev/Randongeon.git
  ```
  Se o repo for privado, faça upload do ZIP pelo painel *Files* (veja opção B).

**Opção B — upload manual:**
- *Files* → upload do ZIP do projeto → descompacte em `/home/SEU_USUARIO/Randongeon`.

### 1.3 Verificar dependências (todas já vêm no plano Free)
O PythonAnywhere *Beginner* tem estas libs pré-instaladas — nada de `pip install`:
- `fastapi` ✅
- `uvicorn` ✅
- `pydantic` ✅
- `httpx` ✅ (pra testes, não precisa em runtime)

Se faltar alguma, abra um console e rode:
```bash
pip install --user fastapi uvicorn[standard]
```

### 1.4 Criar a Web App
1. Menu **Web** → **Add a new web app** → *Next* → **Manual configuration** → **Python 3.10** (ou 3.11).
2. Na tela de configuração, em **Code**:
   - **Source code**: `/home/SEU_USUARIO/Randongeon`
   - **Working directory**: `/home/SEU_USUARIO/Randongeon`
3. Em **WSGI configuration file**, edite o arquivo (clique no link) e substitua o conteúdo por:

```python
import sys
import os

# Caminho absoluto da raiz do projeto no PythonAnywhere
project_home = '/home/SEU_USUARIO/Randongeon'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Aponta a API pra encontrar o pacote randongeon/
os.environ['RANDONGEON_PATH'] = os.path.join(project_home, 'randongeon')

# Importa o app FastAPI
from api.main import app
```

> ⚠️ Substitua `SEU_USUARIO` pelo seu username do PythonAnywhere em **todos** os lugares.

4. Clique em **Reload** (botão verde no topo da página *Web*).

### 1.5 Testar
Abra no navegador: `https://SEU_USUARIO.pythonanywhere.com/docs`
- Deve aparecer a documentação interativa do FastAPI (Swagger).
- Se aparecer erro 500, vá em *Web* → *Log files* → *Error log* pra ver o que deu errado.

Teste rápido de saúde (deve retornar 404 "Sessão não encontrada", o que **prova que a API tá rodando**):
```
https://SEU_USUARIO.pythonanywhere.com/game/teste/status
```

### 1.6 Configurar CORS (opcional, mas recomendado)
No PythonAnywhere, em **Web** → **Environment variables**, adicione:
```
ALLOWED_ORIGINS = https://randongeon.vercel.app,http://localhost:5173
```
Clique em **Reload** de novo.

---

## Parte 2 — Subir o Frontend no Vercel (5 min)

### 2.1 Criar conta
- Acesse [vercel.com](https://vercel.com) e logue com sua conta GitHub.

### 2.2 Importar o projeto
1. **Add New → Project** → selecione o repo `Randongeon` (autorize o acesso se necessário).
2. Na tela de configuração:
   - **Framework Preset**: Vite (detectado automaticamente)
   - **Root Directory**: clique em *Edit* e selecione `frontend`
   - **Build Command**: `npm run build` (padrão, não mexa)
   - **Output Directory**: `dist` (padrão, não mexa)

### 2.3 Configurar a env var
Antes de clicar em **Deploy**, expanda **Environment Variables** e adicione:

| Name | Value |
|---|---|
| `VITE_API_URL` | `https://SEU_USUARIO.pythonanywhere.com` |

> ⚠️ **Sem barra no final** da URL! E use `https://`.

Clique em **Deploy** e espere ~1 minuto.

### 2.4 Testar
A Vercel vai te dar uma URL tipo `https://randongeon.vercel.app`. Abra no navegador, crie uma partida, avance uma sala — se tudo carregar, **tá no ar** 🎉.

---

## Parte 3 — Updates futuros (fluxo de trabalho)

Depois do setup inicial, o ciclo é simples:

```bash
# faça mudanças no código
git add .
git commit -m "feat: nova feature"
git push origin main
```

- **Vercel** detecta o push e faz redeploy automático em ~30s.
- **PythonAnywhere**: abra o Bash console, rode `git pull` e clique em *Reload* no painel *Web*:
  ```bash
  cd ~/Randongeon && git pull
  ```

---

## 🛠️ Solução de problemas

| Sintoma | Causa provável | Solução |
|---|---|---|
| `ModuleNotFoundError: No module named 'jogo'` | `RANDONGEON_PATH` errado | Confira o caminho em *Environment variables* e o `sys.path` no WSGI |
| `DisallowedHost` / CORS error no console do browser | Origem não liberada | Adicione a URL do Vercel em `ALLOWED_ORIGINS` |
| Frontend carrega mas `localhost:8000` nas Network | `VITE_API_URL` não configurada no build | Adicione a env var na Vercel e faça redeploy |
| API retorna 404 em tudo | Sessão em memória reiniciou | Normal — sessões somem a cada reload. Crie um novo jogo |
| `ImportError: cannot import name 'X' from 'jogo'` | Código local desatualizado | Rode `git pull` no PythonAnywhere e dê *Reload* |

---

## 📋 Checklist final

- [ ] Conta no PythonAnywhere criada
- [ ] Código no PythonAnywhere (Git ou upload)
- [ ] Web app criada com WSGI apontando pra `api.main:app`
- [ ] `https://SEU_USUARIO.pythonanywhere.com/docs` abre o Swagger
- [ ] (Opcional) `ALLOWED_ORIGINS` configurado
- [ ] Conta na Vercel logada com GitHub
- [ ] Projeto importado com Root Directory = `frontend`
- [ ] Env var `VITE_API_URL` = URL do PythonAnywhere
- [ ] Deploy feito e jogo rodando em `https://randongeon.vercel.app`
