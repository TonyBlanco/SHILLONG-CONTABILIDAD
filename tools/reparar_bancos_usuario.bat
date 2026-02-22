@echo off
setlocal EnableExtensions EnableDelayedExpansion

title Reparar bancos - SHILLONG

set "SIMULAR=0"
set "SILENCIOSO=0"
set "APP_DIR="

rem ── ARGUMENTO PASADO (desde Inno Setup o manual con ruta) ─────────────────
for %%A in (%*) do (
  if /I "%%~A"=="--simular" (
    set "SIMULAR=1"
  ) else if not "%%~fA"=="" (
    set "APP_DIR=%%~fA"
    set "SILENCIOSO=1"
  )
)
if defined APP_DIR goto :after_detect

rem ── METODO 1: Registro de Windows (Inno guarda la ruta aqui siempre) ──────
set "REG_KEY=HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\{B3F1A19F-2235-44C1-8C3B-AEE0F98EF003}_is1"
for /f "tokens=2*" %%A in ('reg query "%REG_KEY%" /v "InstallLocation" 2^>nul') do set "APP_DIR=%%~B"
if defined APP_DIR (
  rem Quitar barra final si la tiene
  if "!APP_DIR:~-1!"=="\" set "APP_DIR=!APP_DIR:~0,-1!"
  goto :after_detect
)

rem ── METODO 2: Mismo registro en HKLM (instalacion para todos los usuarios) ─
set "REG_KEY=HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\{B3F1A19F-2235-44C1-8C3B-AEE0F98EF003}_is1"
for /f "tokens=2*" %%A in ('reg query "%REG_KEY%" /v "InstallLocation" 2^>nul') do set "APP_DIR=%%~B"
if defined APP_DIR (
  if "!APP_DIR:~-1!"=="\" set "APP_DIR=!APP_DIR:~0,-1!"
  goto :after_detect
)

rem ── METODO 3: Carpeta donde esta este BAT (cuando esta junto al .exe) ──────
set "APP_DIR=%~dp0"
if "!APP_DIR:~-1!"=="\" set "APP_DIR=!APP_DIR:~0,-1!"
if exist "!APP_DIR!\backups" goto :after_detect

rem ── METODO 4: Carpeta padre del BAT (cuando esta en tools\) ─────────────────
for %%I in ("%~dp0..") do set "APP_DIR=%%~fI"
if exist "!APP_DIR!\backups" goto :after_detect

rem ── METODO 5: Buscar en TODOS los discos disponibles ────────────────────────
for %%D in (C D E F G H Q R S T U V W X Y Z) do (
  for /d %%P in ("%%D:\*SHILLONG*") do (
    if exist "%%~fP\backups" (
      set "APP_DIR=%%~fP"
      goto :after_detect
    )
  )
)

rem ── METODO 6: Preguntar al usuario ──────────────────────────────────────────
echo.
echo No se encontro la instalacion automaticamente.
echo.
set /p APP_DIR=Escribe la carpeta donde instalaste SHILLONG (ej. D:\MisApps\Shillong): 
if not defined APP_DIR (
  echo ERROR: No se proporciono ninguna ruta.
  pause
  exit /b 1
)

:after_detect
call :set_paths

echo.
echo ==============================================
echo      REPARAR BANCOS - SHILLONG CONTABILIDAD
echo ==============================================
echo.
echo Carpeta de aplicacion: %APP_DIR%
echo Carpeta de datos:      %DATA_DIR%
echo Carpeta de backups:    %BACKUP_DIR%
echo.

if not exist "%BACKUP_DIR%" (
  if "%SILENCIOSO%"=="0" (
    echo ERROR: No existe carpeta de backups en:
    echo   %BACKUP_DIR%
    echo.
    echo Consejo: ejecuta este BAT pasando la ruta de instalacion:
    echo   reparar_bancos_usuario.bat "C:\RUTA\DE\INSTALACION"
    echo.
    pause
  )
  exit /b 0
)

set "LATEST="
for /f "delims=" %%F in ('dir /b /a-d /o-d "%BACKUP_DIR%\bancos*.bak" 2^>nul') do (
  set "LATEST=%%F"
  goto :found_backup
)

:found_backup
if "%LATEST%"=="" (
  if "%SILENCIOSO%"=="0" (
    echo ERROR: No se encontro ningun backup de bancos (bancos*.bak).
    echo.
    pause
  )
  exit /b 0
)

echo Backup detectado: %LATEST%
echo.

if "%SIMULAR%"=="1" (
  echo MODO SIMULACION: no se realizara ningun cambio.
  echo Se copiaria:
  echo   "%BACKUP_DIR%\%LATEST%"
  echo a
  echo   "%DATA_DIR%\bancos.json"
  echo.
  pause
  exit /b 0
)

if not exist "%DATA_DIR%" mkdir "%DATA_DIR%"

if exist "%DATA_DIR%\bancos.json" (
  copy /y "%DATA_DIR%\bancos.json" "%DATA_DIR%\bancos.pre_reparacion.bak" >nul
)

copy /y "%BACKUP_DIR%\%LATEST%" "%DATA_DIR%\bancos.json" >nul
if errorlevel 1 (
  if "%SILENCIOSO%"=="0" (
    echo ERROR: No se pudo restaurar bancos.json
    echo.
    pause
  )
  exit /b 1
)

if "%SILENCIOSO%"=="0" (
  echo OK: bancos restaurados correctamente.
  echo.
  echo Recomendacion: abre SHILLONG y pulsa "Actualizar lista" en la pantalla de registro.
  echo.
  pause
)
exit /b 0

:set_paths
set "DATA_DIR=%APP_DIR%\data"
set "BACKUP_DIR=%APP_DIR%\backups"
exit /b 0
