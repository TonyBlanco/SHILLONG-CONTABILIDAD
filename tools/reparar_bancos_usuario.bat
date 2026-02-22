@echo off
setlocal EnableExtensions EnableDelayedExpansion

title Reparar bancos - SHILLONG

set "SIMULAR=0"
set "SILENCIOSO=0"
set "APP_DIR="
set "DATA_DIR="
set "BACKUP_DIR="
set "USER_PATH="

for %%A in (%*) do (
  if /I "%%~A"=="--simular" (
    set "SIMULAR=1"
  ) else (
    set "USER_PATH=%%~fA"
    set "SILENCIOSO=1"
  )
)

if not "%USER_PATH%"=="" (
  set "APP_DIR=%USER_PATH%"
  goto :after_detect
)

rem 1) Ruta por defecto del instalador
set "APP_DIR=%LOCALAPPDATA%\SHILLONG CONTABILIDAD v3 PRO"
call :set_paths
if exist "%BACKUP_DIR%" goto :after_detect

rem 2) Carpeta donde está este BAT (por si lo copian junto al EXE)
for %%I in ("%~dp0") do set "APP_DIR=%%~fI"
call :set_paths
if exist "%BACKUP_DIR%" goto :after_detect

rem 3) Carpeta padre del BAT (por si está dentro de tools\)
for %%I in ("%~dp0..") do set "APP_DIR=%%~fI"
call :set_paths
if exist "%BACKUP_DIR%" goto :after_detect

rem 4) Buscar instalación bajo %LOCALAPPDATA%\SHILLONG*
for /d %%D in ("%LOCALAPPDATA%\SHILLONG*") do (
  if exist "%%~fD\backups" (
    set "APP_DIR=%%~fD"
    goto :after_detect
  )
)

echo.
echo No se detecto automaticamente la carpeta de instalacion.
set /p APP_DIR=Escribe la carpeta de instalacion de SHILLONG (ej. C:\Apps\Shillong): 
if "%APP_DIR%"=="" (
  echo ERROR: No se proporciono ninguna ruta.
  echo.
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
