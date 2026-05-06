# -*- coding: utf-8 -*-
"""
models/ExportadorModeloEvolutivo.py
Programmatically generates the "Modelo evolutivo presupuestario" report
in the same logical layout used by the UI/template.

Public API:
- exportar_modelo_evolutivo(ruta, totales_exactos, cuentas_by_section, anio, periodo_str)

This module intentionally keeps the exporter pure (no dependency on UI widgets).
It expects `totales_exactos` to be a dict mapping account -> {cur_banco, cur_caja, prev_total}.
`cuentas_by_section` is a dict with keys '6','7','2' mapping to ordered lists of account codes.
"""

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from pathlib import Path
from collections import defaultdict


def _headers_for_section(seccion, anio):
    if seccion == "6":
        return [
            "CUENTA",
            "NOMBRE",
            "GASTOS",
            "BANCO",
            "CAJA",
            "GASTO MESES ANTERIORES",
            "SUMA DE GASTO ACUMULADO",
            f"PRESUPUESTO {anio}",
            "DIFERENCIA",
        ]
    if seccion == "7":
        return [
            "CUENTA",
            "NOMBRE",
            "INGRESOS",
            "BANCO",
            "CAJA",
            "INGRESOS MESES ANTERIORES",
            "SUMA DE INGRESO ACUMULADO",
            f"PRESUPUESTO {anio}",
            "DIFERENCIA",
        ]
    return [
        "CUENTA",
        "NOMBRE",
        "INVERSIONES",
        "BANCO",
        "CAJA",
        "INVERSIONES MESES ANTER.",
        "SUMA DE GASTO ACUMULADO",
        f"PRESUPUESTO {anio}",
        "DIFERENCIA",
    ]


def _rollup_for(codigo, totales_exactos):
    """Roll up helper similar to UI behaviour: sum subaccounts with same prefix and same length."""
    codigo = str(codigo).strip()
    if not codigo:
        return {"cur_banco": 0.0, "cur_caja": 0.0, "prev_total": 0.0}

    if codigo.endswith("000") and len(codigo) > 3:
        pref = codigo[:-3]
    elif codigo.endswith("00") and len(codigo) > 2:
        pref = codigo[:-2]
    else:
        pref = codigo

    cur_banco = 0.0
    cur_caja = 0.0
    prev_total = 0.0
    for cta, vals in totales_exactos.items():
        cta_s = str(cta)
        if len(cta_s) != len(codigo):
            continue
        if not cta_s.startswith(pref):
            continue
        cur_banco += float(vals.get("cur_banco", 0) or 0)
        cur_caja += float(vals.get("cur_caja", 0) or 0)
        prev_total += float(vals.get("prev_total", 0) or 0)

    return {"cur_banco": cur_banco, "cur_caja": cur_caja, "prev_total": prev_total}


def exportar_modelo_evolutivo(ruta_archivo, totales_exactos, cuentas_by_section, anio, periodo_str="", nombre_por_cuenta=None):
    """Generate an XLSX file with the model layout programmatically.

    - `totales_exactos`: dict account-> {cur_banco, cur_caja, prev_total}
    - `cuentas_by_section`: {'6': [...], '7': [...], '2': [...]} ordered lists of account codes
    - `nombre_por_cuenta`: optional callable or dict to resolve account name: nombre_por_cuenta(cta) or nombre_por_cuenta[cta]
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Modelo Evolutivo"

    # Style constants (keep consistent with ExportadorExcelMensual)
    morado = PatternFill(start_color="7030A0", end_color="7030A0", fill_type="solid")
    verde = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
    blanco = Font(color="FFFFFF", bold=True)
    centro = Alignment(horizontal="center", vertical="center")
    borde_fino = Side(style="thin", color="000000")
    border = Border(left=borde_fino, right=borde_fino, top=borde_fino, bottom=borde_fino)

    row = 1

    # Report title
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=9)
    cell = ws.cell(row=row, column=1, value="MODELO EVOLUTIVO PRESUPUESTARIO")
    cell.font = Font(bold=True, size=14, color="FFFFFF")
    cell.fill = morado
    cell.alignment = centro
    row += 2

    # Periodo info
    if periodo_str:
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=9)
        ws.cell(row=row, column=1, value=f"Periodo: {periodo_str}")
        row += 2

    # Iterate sections 6(Gastos),7(Ingresos),2(Inversiones)
    grand_totals = {"cur": 0.0, "banco": 0.0, "caja": 0.0, "prev": 0.0}

    for seccion, titulo in [("6", "SUMA TOTAL GASTOS"), ("7", "SUMA TOTAL INGRESOS"), ("2", "INVERSIONES")]:
        headers = _headers_for_section(seccion, anio)

        # Section title
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=len(headers))
        cell = ws.cell(row=row, column=1, value=titulo)
        cell.fill = morado
        cell.font = Font(bold=True, color="FFFFFF")
        cell.alignment = centro
        row += 1

        # Header row
        for c, h in enumerate(headers, start=1):
            cell = ws.cell(row=row, column=c, value=h)
            cell.fill = morado
            cell.font = Font(bold=True, color="FFFFFF")
            cell.border = border
            cell.alignment = Alignment(horizontal="center")
            # set column width modestly
            letra = get_column_letter(c)
            ws.column_dimensions[letra].width = 18
        row += 1

        total_cur = 0.0
        total_banco = 0.0
        total_caja = 0.0
        total_prev = 0.0

        cuentas = cuentas_by_section.get(seccion, [])
        for cta in cuentas:
            nombre = ""
            if callable(nombre_por_cuenta):
                try:
                    nombre = nombre_por_cuenta(cta)
                except Exception:
                    nombre = ""
            elif isinstance(nombre_por_cuenta, dict):
                nombre = nombre_por_cuenta.get(cta, "")

            vals = _rollup_for(cta, totales_exactos)
            cur_banco = float(vals.get("cur_banco", 0) or 0)
            cur_caja = float(vals.get("cur_caja", 0) or 0)
            cur_total = cur_banco + cur_caja
            prev_total = float(vals.get("prev_total", 0) or 0)
            acum = cur_total + prev_total
            presupuesto_num = 0.0
            diferencia_num = round(presupuesto_num - acum, 2)

            fila = [cta, nombre, cur_total, cur_banco, cur_caja, prev_total, acum, presupuesto_num, diferencia_num]

            for c, val in enumerate(fila, start=1):
                cell = ws.cell(row=row, column=c, value=val)
                cell.border = border
                if c >= 3:
                    cell.number_format = "#,##0.00"
                    cell.alignment = Alignment(horizontal="right")
            row += 1

            total_cur += cur_total
            total_banco += cur_banco
            total_caja += cur_caja
            total_prev += prev_total

        # Totals row
        cell = ws.cell(row=row, column=2, value=f"{titulo}")
        cell.font = Font(bold=True)
        cell.fill = verde
        for c in range(3, 7):
            cell = ws.cell(row=row, column=c)
            cell.fill = verde
            if c == 3:
                ws.cell(row=row, column=3, value=round(total_cur, 2)).number_format = "#,##0.00"
            if c == 4:
                ws.cell(row=row, column=4, value=round(total_banco, 2)).number_format = "#,##0.00"
            if c == 5:
                ws.cell(row=row, column=5, value=round(total_caja, 2)).number_format = "#,##0.00"
            if c == 6:
                ws.cell(row=row, column=6, value=round(total_prev, 2)).number_format = "#,##0.00"
        # total acum
        ws.cell(row=row, column=7, value=round(total_cur + total_prev, 2)).number_format = "#,##0.00"
        row += 2

        grand_totals["cur"] += total_cur
        grand_totals["banco"] += total_banco
        grand_totals["caja"] += total_caja
        grand_totals["prev"] += total_prev

    # Footer summary
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=9)
    footer = ws.cell(row=row, column=1, value="REPORTE GENERADO")
    footer.alignment = Alignment(horizontal="center")
    row += 1

    # Save
    p = Path(ruta_archivo)
    p.parent.mkdir(parents=True, exist_ok=True)
    wb.save(p)
    return True
