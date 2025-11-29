# Copia de carpetas para instalador SHILLONG v3 PRO

$root   = "D:\ShillongV3"
$dist   = "D:\ShillongV3\dist\SHILLONG_v3_PRO"

$folders = @("assets", "data", "core", "models", "themes", "ui", "utils")

Write-Host "Preparando estructura para Inno Setup..."

if (!(Test-Path $dist)) {
    Write-Host "ERROR: No existe la carpeta dist\SHILLONG_v3_PRO"
    exit
}

foreach ($f in $folders) {
    $source = "$root\$f"
    $target = "$dist\$f"

    if (Test-Path $target) {
        Remove-Item $target -Force -Recurse
    }

    Copy-Item $source -Destination $target -Recurse -Force
    Write-Host "Copiado: $f"
}

Write-Host "Listo para Inno Setup."
