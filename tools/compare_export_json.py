#!/usr/bin/env python3
import json, openpyxl, datetime, re, sys
from pathlib import Path

excel_path = Path('test_out.xlsx')
json_path = Path('data/shillong_2026.json')

if not excel_path.exists():
    print('Excel not found:', excel_path); sys.exit(2)
if not json_path.exists():
    print('JSON not found:', json_path); sys.exit(2)

with open(json_path, 'r', encoding='utf-8') as f:
    d = json.load(f)
movs = d.get('movimientos', [])

# period used in test_informes.py
ini = datetime.date(2025, 11, 1)
fin = datetime.date(2026, 1, 31)

# compute totals per cuenta (same logic as _totales_sisters_por_cuenta, invertido=False)
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
        tot[cuenta] = tot.get(cuenta, 0.0) + float(importe)

# load excel
wb = openpyxl.load_workbook(excel_path, data_only=True)
ws = wb.active

mismatches = []
seen_codes = set()
for r in range(1, ws.max_row+1):
    code_raw = ws.cell(r, 3).value
    val = ws.cell(r, 5).value
    if code_raw is None:
        continue
    s = str(code_raw).strip()
    code = re.sub(r'[^0-9]', '', s)
    if not code or not code[0].isdigit():
        continue
    seen_codes.add(code)
    excel_val = val or 0.0
    if isinstance(excel_val, str):
        try:
            excel_val = float(excel_val.replace(',','').replace(' ','') )
        except Exception:
            excel_val = 0.0
    try:
        excel_val = float(excel_val)
    except Exception:
        excel_val = 0.0
    json_val = float(tot.get(code, 0.0))
    diff = json_val - excel_val
    if abs(diff) > 0.01:
        mismatches.append((r, code, excel_val, json_val, diff))

if mismatches:
    print('Mismatches found:')
    for r, code, excel_val, json_val, diff in mismatches:
        print(f'Row {r}: code={code}, excel={excel_val}, json={json_val}, diff={diff}')
else:
    print('No mismatches found for rows scanned.')

missing_in_excel = [(c,v) for c,v in tot.items() if c not in seen_codes and abs(v) > 0.0001]
if missing_in_excel:
    print('\nCodes present in JSON (non-zero) but not in Excel:')
    for c,v in missing_in_excel:
        print(f'{c} -> {v}')

print('\nDone')
