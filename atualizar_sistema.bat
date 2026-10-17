@echo off
cd /d "%~dp0"
set LOG=atualizar_log.txt
echo ==== Atualizacao Sistema GVI %date% %time% ==== > %LOG%

set PY=
rem 1) lancador py do Windows
py -3 --version >nul 2>&1 && set PY=py -3
rem 2) Python instalado pelo site python.org
if not defined PY for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do if exist "%%D\python.exe" set PY="%%D\python.exe"
if not defined PY for /d %%D in ("C:\Program Files\Python3*") do if exist "%%D\python.exe" set PY="%%D\python.exe"
rem 3) ambiente virtual de projetos do PyCharm
if not defined PY for /d %%D in ("%USERPROFILE%\PycharmProjects\*") do if exist "%%D\.venv\Scripts\python.exe" set PY="%%D\.venv\Scripts\python.exe"
if not defined PY for /d %%D in ("%USERPROFILE%\PycharmProjects\*") do if exist "%%D\venv\Scripts\python.exe" set PY="%%D\venv\Scripts\python.exe"

if not defined PY (
    echo RESULTADO: FALHOU - Python nao encontrado >> %LOG%
    echo FIM >> %LOG%
    exit /b 1
)

echo Python: %PY% >> %LOG%
%PY% --version >> %LOG% 2>&1

echo --- Instalando dependencias --- >> %LOG%
%PY% -m pip install --upgrade pypdf flask pyinstaller >> %LOG% 2>&1

echo --- Limpando --- >> %LOG%
if exist main.spec del /q main.spec
if exist build rmdir /s /q build
if exist __pycache__ rmdir /s /q __pycache__
if exist dist\Sistema_GVI.exe del /q dist\Sistema_GVI.exe

echo --- Gerando executavel --- >> %LOG%
%PY% -m PyInstaller --noconfirm Sistema_GVI.spec >> %LOG% 2>&1

if exist dist\Sistema_GVI.exe (
    copy /y *.pdf dist\ >nul
    echo RESULTADO: OK - dist\Sistema_GVI.exe gerado >> %LOG%
) else (
    echo RESULTADO: FALHOU - veja as mensagens acima >> %LOG%
)
echo FIM >> %LOG%
