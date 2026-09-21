@echo off
setlocal
cd /d "%~dp0"
title 3SeaTech DataAI Server
echo ============================================
echo       3.SEATECH DATAAI - API LOCAL
echo ============================================
where py >nul 2>&1 || (echo Python no encontrado.& pause & exit /b 1)
if not exist ".venv\Scripts\python.exe" (
  echo [1/4] Creando entorno virtual...
  py -3 -m venv .venv || goto :error
)
echo [2/4] Instalando/verificando dependencias...
".venv\Scripts\python.exe" -m pip install -q -r requirements.txt || goto :error
if "%DATAAI_ADMIN_USER%"=="" (
  echo.
  echo ERROR: DATAAI_ADMIN_USER no esta configurado.
  echo Ejemplo: setx DATAAI_ADMIN_USER "admin"
  echo Genere el hash con: .venv\Scripts\python crear_password.py
  pause & exit /b 1
)
if "%DATAAI_ADMIN_PASSWORD_HASH%"=="" (
  echo ERROR: DATAAI_ADMIN_PASSWORD_HASH no esta configurado.
  echo Genere el hash con: .venv\Scripts\python crear_password.py
  pause & exit /b 1
)
echo [3/4] Verificando servicio cloudflared...
sc query cloudflared | find /I "RUNNING" >nul
if errorlevel 1 (
  echo Iniciando servicio cloudflared...
  net start cloudflared >nul 2>&1
)
echo [4/4] Iniciando FastAPI en http://127.0.0.1:8000
echo API publica esperada: https://api-data.3seatech.com
".venv\Scripts\python.exe" -m uvicorn main:app --host 127.0.0.1 --port 8000
exit /b
:error
echo ERROR iniciando DataAI.
pause
