@echo off
title SHILLONG v3 PRO - Compilador Automático
color 0A

echo ===============================================
echo   SHILLONG CONTABILIDAD v3 PRO - COMPILADOR
echo   TonyBlanco © 2025
echo ===============================================
echo.

REM ---- Ir al directorio del proyecto ----
cd /d "%~dp0"

echo Limpiando carpetas previas de compilacion...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo OK.
echo.

REM ---- Verificar que Python 3.12 está instalado ----
if not exist "C:\Python312\python.exe" (
    echo ERROR: No se encontró Python 3.12 en C:\Python312\
    echo Instala Python correctamente o corrige esta ruta.
    pause
    exit /b
)

REM ---- Instalar dependencias si faltan ----
echo Verificando dependencias...
C:\Python312\python.exe -m pip install --upgrade pip >nul
C:\Python312\python.exe -m pip install pyinstaller pyside6 pandas openpyxl >nul
echo Dependencias OK.
echo.

REM ---- Verificar que las carpetas necesarias existen ----
for %%F in (data ui models templates reports) do (
    if not exist "%%F" (
        echo Creando carpeta faltante: %%F
        mkdir "%%F"
    )
)

if not exist "ui\Dialogs" (
    echo Creando carpeta faltante: ui\Dialogs
    mkdir "ui\Dialogs"
)

echo Carpetas verificadas OK.
echo.

REM ---- Verificar icono ----
if not exist "shillong_logo.ico" (
    echo ERROR: No se encontró el icono shillong_logo.ico
    echo Coloca el icono junto a este archivo .bat
    pause
    exit /b
)

REM ---- COMPILACIÓN ----
echo Compilando SHILLONG v3 PRO...
echo Esto puede tardar unos segundos...
echo.

C:\Python312\python.exe -m PyInstaller ^
--noconsole ^
--name SHILLONG ^
--icon=shillong_logo.ico ^
--add-data "data;data" ^
--add-data "ui;ui" ^
--add-data "ui/Dialogs;ui/Dialogs" ^
--add-data "models;models" ^
--add-data "reports;reports" ^
--add-data "templates;templates" ^
main.py

echo.
echo ===============================================
echo       COMPILACION FINALIZADA
echo ===============================================
echo.

REM ---- Confirmar que el EXE existe ----
if exist "dist\SHILLONG\SHILLONG.exe" (
    echo EXITO: El ejecutable se encuentra en:
    echo   dist\SHILLONG\SHILLONG.exe
) else (
    echo ERROR: La compilacion no genero el ejecutable.
)

echo.
pause
