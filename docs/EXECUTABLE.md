# Gerando um executável distribuível para Randongeon

A arquitetura atual do jogo é **híbrida**: frontend React (Vite) + backend
FastAPI (Python) com lógica de jogo em `randongeon/jogo/`. Para distribuir
como um único `.exe` que qualquer usuário Windows possa baixar e abrir, a
estratégia recomendada é **PyWebView + PyInstaller** — empacota o servidor
FastAPI, o build estático do React e uma janela nativa do Windows num único
binário, mantendo toda a lógica Python existente.

> **Status:** ainda não implementado. Este guia documenta os passos para
> quando quisermos produzir o `.exe`.

---

## Estratégia recomendada: PyWebView + PyInstaller

### Por que esta abordagem?

- **Zero refactor de backend** — a lógica em Python (jogador, masmorra,
  gerador, loja, persistência) continua sendo a fonte da verdade.
- **Reaproveita o frontend** — Vite gera um bundle estático que o FastAPI
  serve direto.
- **Tamanho aceitável** — `.exe` final fica entre 60–100 MB com Python +
  Chromium incorporado pelo PyWebView.
- **Cross-platform potencial** — PyInstaller também gera binários para
  macOS e Linux a partir do mesmo `launcher.py`.

### Trade-offs

- Inclui um runtime Python embarcado → binário maior que um app puro.
- Primeira execução pode demorar 1-2s para o uvicorn subir.
- PyWebView usa Edge WebView2 no Windows (já vem em Win10+); macOS usa WKWebView.

---

## Passo a passo (futuro)

### 1. Adicionar dependências

```bash
pip install pywebview pyinstaller
```

### 2. Buildar o frontend para estático

```bash
cd frontend
npm run build
# gera frontend/dist/
```

### 3. Servir o estático pelo FastAPI

Adicionar ao final de `api/main.py`:

```python
from fastapi.staticfiles import StaticFiles
import os

DIST = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.isdir(DIST):
    app.mount("/", StaticFiles(directory=DIST, html=True), name="static")
```

> Em dev (com `npm run dev` rodando), o frontend usa `localhost:5173` e
> bate na API em `localhost:8000`. Só o build estático é servido pelo
> FastAPI — então essa mount não afeta o dev mode.

### 4. Criar `launcher.py` na raiz do projeto

```python
import threading
import uvicorn
import webview
from api.main import app

def run_api():
    uvicorn.run(app, host="127.0.0.1", port=8765, log_level="warning")

if __name__ == "__main__":
    threading.Thread(target=run_api, daemon=True).start()
    webview.create_window(
        "Randongeon",
        "http://127.0.0.1:8765",
        width=1280,
        height=800,
        resizable=True,
    )
    webview.start()
```

### 5. Empacotar com PyInstaller

```bash
pyinstaller --noconsole \
  --name Randongeon \
  --icon assets/icon.ico \
  --add-data "frontend/dist;frontend/dist" \
  --add-data "randongeon;randongeon" \
  launcher.py
```

Saída em `dist/Randongeon/Randongeon.exe` (~60-100 MB com tudo embutido).

### 6. Trocar o backend de save para disco

Hoje o frontend usa `localStorage` via `frontend/src/services/saveService.ts`.
No `.exe`, é melhor gravar em `%APPDATA%/Randongeon/saves/*.json` para o
usuário poder fazer backup, sincronizar com cloud, etc.

Adicionar rotas no FastAPI:

```python
# api/main.py
import os, json
from pathlib import Path

SAVE_DIR = Path(os.getenv("APPDATA", str(Path.home()))) / "Randongeon" / "saves"
SAVE_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/saves/list")
def list_disk_saves():
    return [{"slot": p.stem, "data": json.loads(p.read_text())} for p in SAVE_DIR.glob("*.json")]

@app.post("/saves/{slot}")
def write_disk_save(slot: str, save: SaveStateResponse):
    (SAVE_DIR / f"{slot}.json").write_text(save.model_dump_json(indent=2))
    return {"sucesso": True}
```

E no frontend, alterar o `saveService.ts` para detectar ambiente:

```typescript
const IS_DESKTOP = typeof window !== "undefined" && /pywebview|electron/i.test(navigator.userAgent);
```

Se `IS_DESKTOP`, usa os endpoints `/saves/...`. Senão, usa `localStorage`.

---

## Alternativas (não recomendadas para este projeto)

### Electron

- Empacota o frontend numa janela Chromium própria.
- Backend Python rodaria como **sidecar process** ou seria reescrito em Node.
- **Trade-off:** ~150-200 MB de binário; complexidade de empacotar Python.

### Tauri

- Muito leve (~10 MB) usando o webview do sistema operacional.
- Backend deve ser em Rust ou rodar como sidecar.
- **Trade-off:** exige Rust toolchain; backend Python continua sidecar.

### Reescrever lógica em TypeScript

- Frontend puro estático (zero backend) → deploy estático ou Tauri.
- **Trade-off:** refator profundo da lógica em Python (jogador, masmorra,
  gerador, loja, persistencia). Quebra os 380 testes pytest existentes.

---

## Checklist antes de empacotar

- [ ] `npm run build` no `frontend/` sem erros.
- [ ] `pytest randongeon/tests/ -v` passando 100%.
- [ ] `api/main.py` montando `frontend/dist` como estático.
- [ ] `launcher.py` testado: `python launcher.py` abre janela e o jogo roda.
- [ ] Ícone `.ico` (256x256) preparado em `assets/icon.ico`.
- [ ] Versão registrada no `package.json` e em algum constante Python.
- [ ] Save backend trocado para disco (opcional, mas recomendado).
- [ ] Teste o `.exe` em uma máquina Windows limpa (sem Python instalado).
