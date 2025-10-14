@echo off
setlocal
title Licitante - RUN (sin venv)

:: Rutas
set "ROOT=%~dp0"
set "BACKEND=%ROOT%backend"
set "FRONTEND=%ROOT%frontend"

:: Detectar Python
set "PY_CMD="
where py >nul 2>nul && set "PY_CMD=py"
if not defined PY_CMD ( where python >nul 2>nul && set "PY_CMD=python" )
if not defined PY_CMD (
  echo [ERROR] Python no encontrado. Ejecuta primero install_licitante_deps.bat
  pause & goto :EOF
)

:: Verificar uvicorn (si no, pedir instalar)
%PY_CMD% -m pip show uvicorn >nul 2>nul || (
  echo [ERROR] Faltan dependencias del backend. Ejecuta install_licitante_deps.bat
  pause & goto :EOF
)

:: Backend y Frontend
set "BACKEND_HOST=127.0.0.1"
set "BACKEND_PORT=8000"

echo ================================================
echo  Backend:  http://%BACKEND_HOST%:%BACKEND_PORT%   (Swagger: /docs)
echo  Frontend: http://localhost:5173
echo  WS:       ws://%BACKEND_HOST%:%BACKEND_PORT%/licitante/ws?user=TU_USUARIO
echo ================================================
echo.

:: Abrir backend (deja la ventana abierta con logs)
start "Licitante Backend" cmd /k ^
  "cd /d \"%BACKEND%\" && %PY_CMD% -m uvicorn app:app --reload --host %BACKEND_HOST% --port %BACKEND_PORT%"

:: Abrir frontend
start "Licitante Frontend" cmd /k ^
  "cd /d \"%FRONTEND%\" && npm run dev"

echo [OK] Lanzado. Esta ventana se puede cerrar.
endlocal
