# FULL BUILD SHILLONG v3 PRO - AUTOMATIZADO

Write-Host ""
Write-Host "=============================================="
Write-Host "       SHILLONG CONTABILIDAD v3 PRO BUILD     "
Write-Host "=============================================="

# --- CONFIGURACION ---
$root = "D:\ShillongV3"
# Ajusta la ruta de tu Python si es diferente. 
# Si 'python' está en el PATH global, puedes usar simplemente "python"
$python = "python" 
$specFile = "$root\SHILLONG_v3_PRO.spec"
$issFile = "$root\SHILLONG_v3_PRO.iss"

$dist = "$root\dist"
$build = "$root\build"
$output = "$root\Output"

# --- 1. BUSCAR INNO SETUP ---
$innoPaths = @(
  "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
  "C:\Program Files\Inno Setup 6\ISCC.exe"
)
$iscc = $innoPaths | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $iscc) {
  Write-Host "ERROR: No se encontro Inno Setup (ISCC.exe)."
  exit
}
Write-Host "Inno Setup encontrado en: $iscc"

# --- 2. LIMPIEZA ---
Write-Host "Limpiando carpetas dist/ y build/..."
if (Test-Path $dist)  { Remove-Item $dist  -Recurse -Force }
if (Test-Path $build) { Remove-Item $build -Recurse -Force }

# --- 3. COMPILACION PYINSTALLER ---
Write-Host "Compilando con PyInstaller (usando .spec)..."

# Usamos el archivo .spec directamente para no olvidar ninguna configuración
# Quitamos --noconsole porque ya esta en el .spec
& $python -m PyInstaller $specFile --clean --noconfirm

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR CRITICO en PyInstaller. Abortando."
    exit
}

Write-Host "Compilacion completada con exito."

# --- 4. CREAR INSTALADOR ---
Write-Host "Generando instalador con Inno Setup..."
& $iscc $issFile

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR en Inno Setup."
    exit
}

Write-Host "PROCESO TERMINADO! Instalador listo en: $output"
Start-Process $output