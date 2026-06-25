from pathlib import Path
import shutil

src = Path('ui/Modelo evolutivo presupuestario 26 - blank.xlsx')
dst = Path('backups/Reporte por cuentas -SHILLONG- Modelo seguimiento presupuestario.xlsx')
if not src.exists():
    print('Source blank template not found:', src)
    raise SystemExit(2)

dst.parent.mkdir(parents=True, exist_ok=True)
shutil.copy(src, dst)
print('Copied ->', dst)
