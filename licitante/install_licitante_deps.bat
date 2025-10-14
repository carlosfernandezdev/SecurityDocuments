@echo off
setlocal ENABLEDELAYEDEXPANSION
title Licitante - INSTALAR DEPENDENCIAS (sin venv)

:: Rutas
set "ROOT=%~dp0"
set "BACKEND=%ROOT%backend"
set "FRONTEND=%ROOT%frontend"

:: Detectar Python
set "PY_CMD="
where py >nul 2>nul && set "PY_CMD=py"
if not defined PY_CMD (
  where python >nul 2>nul && set "PY_CMD=python"
)
if not defined PY_CMD (
  echo [ERROR] Python no encontrado. Agrega python al PATH o instala desde python.org
  pause & goto :EOF
)

:: Actualizar pip
%PY_CMD% -m pip install --upgrade pip

:: Instalar paquetes mínimos para el backend (solo si faltan)
for %%P in (fastapi uvicorn python-multipart pydantic httpx) do (
  %PY_CMD% -m pip show %%P >nul 2>nul || (
    echo [INFO] Instalando %%P ...
    %PY_CMD% -m pip install %%P
  )
)

:: Frontend: npm install si hace falta
where node >nul 2>nul || (echo [ERROR] Node.js no encontrado. Instala Node 18+. & pause & goto :EOF)
where npm  >nul 2>nul || (echo [ERROR] npm no encontrado. & pause & goto :EOF)

if not exist "%FRONTEND%\package.json" (
  echo [ERROR] No existe %FRONTEND%\package.json
  pause & goto :EOF
)

if not exist "%FRONTEND%\node_modules" (
  echo [INFO] Instalando dependencias del frontend...
  pushd "%FRONTEND%"
  npm install
  popd
) else (
  echo [INFO] node_modules ya existe. Saltando npm install.
)

echo.
echo [OK] Dependencias listas.
pause
endlocal
