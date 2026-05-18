@echo off
chcp 65001 >/dev/null 2>&1
title Randongeon - Inicializador

echo ========================================
echo        RANDONGEON - Inicializando
echo ========================================
echo.

:: ── Verificar Python ─────────────────────────────────────────────────────────
where python >/dev/null 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado. Instale Python 3.10+ e tente novamente.
    pause
    exit /b 1
)

:: ── Verificar Node.js ────────────────────────────────────────────────────────
where node >/dev/null 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Node.js nao encontrado. Instale Node.js 18+ e tente novamente.
    pause
    exit /b 1
)

:: ── Criar venv se nao existir ────────────────────────────────────────────────
if not exist ".venv\Scripts\activate.bat" (
    echo [1/4] Criando ambiente virtual...
    python -m venv .venv
) else (
    echo [1/4] Ambiente virtual encontrado.
)

:: ── Instalar dependencias Python ─────────────────────────────────────────────
echo [2/4] Verificando dependencias Python...
.venv\Scripts\pip install -r randongeon\requirements.txt -r api\requirements.txt -q

:: ── Instalar dependencias Frontend ───────────────────────────────────────────
if not exist "frontend\node_modules" (
    echo [3/4] Instalando dependencias do frontend...
    cd frontend
    call npm install
    cd ..
) else (
    echo [3/4] Dependencias do frontend encontradas.
)

:: ── Iniciar servidores ───────────────────────────────────────────────────────
echo [4/4] Iniciando servidores...
echo.

start "Randongeon API" cmd /k "cd /d %~dp0api && %~dp0.venv\Scripts\uvicorn main:app --reload --port 8000"
start "Randongeon Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo ========================================
echo   Servidores iniciados com sucesso!
echo.
echo   API:      http://localhost:8000
echo   Swagger:  http://localhost:8000/docs
echo   Frontend: http://localhost:5173
echo.
echo   Feche as janelas abertas para parar.
echo ========================================
echo.
pause
