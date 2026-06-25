import openpyxl
wb=openpyxl.load_workbook('dist/SHILLONG_v3_PRO/_internal/ui/Modelo evolutivo presupuestario 26.xlsx', data_only=True)
ws=wb.active
found=False
for r in range(8,101):
    vals=[ws.cell(r,c).value for c in range(3,10)]
    if any(v not in (None,0,'',0.0) for v in vals):
        print(r, vals)
        found=True
if not found:
    print('No visible data found in rows 8-100 (columns 3-9)')
