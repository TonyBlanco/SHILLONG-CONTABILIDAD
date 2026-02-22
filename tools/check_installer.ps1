$p = Join-Path $env:LOCALAPPDATA 'SHILLONG CONTABILIDAD v3 PRO'
if (Test-Path $p) {
    Get-ChildItem -Path $p -Force | Select-Object Name,Length | Format-Table -AutoSize
    Write-Host '---CONFIG JSON---'
    $cfg = Join-Path $p 'config.json'
    if (Test-Path $cfg) { Get-Content -Path $cfg } else { Write-Host 'CONFIG_MISSING' }
} else {
    Write-Host 'MISSING_DIR'
}
