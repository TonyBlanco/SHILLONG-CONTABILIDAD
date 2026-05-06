#!/usr/bin/env python3
import sys
import json
from pathlib import Path
# Ensure repo root is on sys.path so imports like `models.*` work
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))
from models.ExportadorModeloEvolutivo import exportar_modelo_evolutivo

# Load JSON data
json_path = Path('data/shillong_2026.json')
if not json_path.exists():
    print('JSON not found:', json_path); sys.exit(2)
with open(json_path, 'r', encoding='utf-8') as f:
    d = json.load(f)
movs = d.get('movimientos', [])
cuentas = d.get('cuentas', {})

# compute totals per cuenta (same logic as InformesView._totales_sisters_por_cuenta)
import datetime, re
ini = datetime.date(2025, 11, 1)
fin = datetime.date(2026, 1, 31)

tot = {}
for m in movs:
    cuenta = str(m.get('cuenta', '')).strip()
    if not cuenta or not cuenta[0].isdigit():
        continue
    if cuenta[0] not in ('6','7','2'):
        continue
    fecha_str = m.get('fecha','')
    try:
        dpart = [int(x) for x in fecha_str.split('/')]
        fecha = datetime.date(dpart[2], dpart[1], dpart[0])
    except Exception:
        continue
    debe = float(m.get('debe',0) or 0)
    haber = float(m.get('haber',0) or 0)
    if cuenta[0] == '7':
        importe = haber
    else:
        importe = debe
    if ini <= fecha <= fin:
        if cuenta not in tot:
            tot[cuenta] = {'cur_banco':0.0, 'cur_caja':0.0, 'prev_total':0.0}
        # Simple: put all into cur_banco (we don't have banco indicator here)
        tot[cuenta]['cur_banco'] += float(importe)

# Build cuentas_by_section naive from cuentas keys
cuentas_by_section = {
    '6': sorted([c for c in cuentas.keys() if str(c).startswith('6')]),
    '7': sorted([c for c in cuentas.keys() if str(c).startswith('7')]),
    '2': sorted([c for c in cuentas.keys() if str(c).startswith('2')]),
}

# call exporter
exportar_modelo_evolutivo('test_out.xlsx', tot, cuentas_by_section, 2026, '01/11/2025 - 31/01/2026', nombre_por_cuenta=None)
print('Generated test_out.xlsx')
