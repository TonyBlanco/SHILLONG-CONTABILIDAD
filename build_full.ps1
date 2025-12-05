# FULL BUILD SHILLONG v3 PRO - AUTOMATIZADO (hardening)

param(
    [switch]$NoClean,
    [switch]$NoOpen
)

Write-Host ""
Write-Host "=============================================="
Write-Host "       SHILLONG CONTABILIDAD v3 PRO BUILD     "
Write-Host "=============================================="

# --- CONFIGURACION ---
$root = Split-Path -Parent $PSCommandPath
Set-Location $root

$python = "python"
$specFile = Join-Path $root "SHILLONG_v3_PRO.spec"
$issFile  = Join-Path $root "SHILLONG_v3_PRO.iss"

$dist   = Join-Path $root "dist"
$build  = Join-Path $root "build"
$output = Join-Path $root "Output"

# --- VALIDAR PYTHON / PYINSTALLER ---
try {
    $pyver = & $python -V 2>&1
    Write-Host "Python detectado: $pyver"
} catch {
    Write-Host "ERROR: No se encontró Python en PATH."; exit 1
}

try {
    $piver = & $python -m PyInstaller --version 2>&1
    Write-Host "PyInstaller detectado: $piver"
} catch {
    Write-Host "ERROR: PyInstaller no está disponible. Instala con 'pip install pyinstaller'."; exit 1
}

# --- BUSCAR INNO SETUP ---
$innoPaths = @(
  "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
  "C:\Program Files\Inno Setup 6\ISCC.exe"
)
$iscc = $innoPaths | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $iscc) {
  Write-Host "ERROR: No se encontró Inno Setup (ISCC.exe)."; exit 1
}
Write-Host "Inno Setup: $iscc"

# --- LIMPIEZA ---
if (-not $NoClean) {
    Write-Host "Limpiando carpetas dist/ y build/..."
    if (Test-Path $dist)  { Remove-Item $dist  -Recurse -Force }
    if (Test-Path $build) { Remove-Item $build -Recurse -Force }
} else {
    Write-Host "Saltando limpieza (-NoClean)"
}

# --- COMPILACION PYINSTALLER ---
Write-Host "Compilando con PyInstaller (spec)..."
& $python -m PyInstaller $specFile --clean --noconfirm
if ($LASTEXITCODE -ne 0) { Write-Host "ERROR CRITICO en PyInstaller."; exit 1 }
Write-Host "Compilacion completada."

# --- CREAR INSTALADOR ---
Write-Host "Generando instalador con Inno Setup..."
& $iscc $issFile
if ($LASTEXITCODE -ne 0) { Write-Host "ERROR en Inno Setup."; exit 1 }

# --- VALIDAR INSTALADOR ---
$installer = Get-ChildItem -Path $output -Filter "*.exe" -File | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $installer) {
    Write-Host "ADVERTENCIA: No se encontró instalador en $output."; exit 1
}
Write-Host "Instalador listo: $($installer.FullName)"

if (-not $NoOpen) {
    Start-Process $output
}
