# -*- coding: utf-8 -*-
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

class ExportadorExcelMensual:
    @staticmethod
    def exportar(ruta: str, movimientos: list):
        wb = Workbook()
        ws = wb.active
        ws.title = "Libro Mensual"

        medium = Side(border_style="medium")
        border = Border(left=medium, right=medium, top=medium, bottom=medium)
        header_fill = PatternFill(start_color="e5e7eb", fill_type="solid")
        total_fill = PatternFill(start_color="FFF2CC", fill_type="solid")
        bold = Font(bold=True)
        right = Alignment(horizontal="right")
        center = Alignment(horizontal="center")

        headers = ["Cuenta", "Nombre Cuenta", "Fecha", "Concepto", "Debe", "Haber", "Saldo", "Banco", "Estado", "Documento"]
        ws.append(headers)
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = bold
            cell.alignment = center
            cell.border = border

        saldo_acum = total_debe = total_haber = 0
        for m in movimientos:
            debe = m["debe"]
            haber = m["haber"]
            saldo_acum += haber - debe
            total_debe += debe
            total_haber += haber
            row = [m["cuenta"], m["nombre_cuenta"], m["fecha"], m["concepto"], debe, haber, saldo_acum, m["banco"], m["estado"], m["documento"]]
            ws.append(row)

        ws.append([])
        ws.append(["", "", "", "", "", "TOTAL GASTO:", total_debe, "", "", ""])
        ws.append(["", "", "", "", "", "TOTAL INGRESO:", total_haber, "", "", ""])
        ws.append(["", "", "", "", "", "SALDO FINAL:", saldo_acum, "", "", ""])

        for r in range(ws.max_row - 2, ws.max_row + 1):
            ws.row_dimensions[r].height = 20

            ws.cell(r, 6).fill = total_fill
            ws.cell(r, 6).font = bold
            ws.cell(r, 6).border = border
            ws.cell(r, 6).alignment = Alignment(horizontal="left")

            ws.cell(r, 7).fill = total_fill
            ws.cell(r, 7).font = bold
            ws.cell(r, 7).border = border
            ws.cell(r, 7).alignment = right
            ws.cell(r, 7).number_format = '#,##0.00'

        for row in ws.iter_rows(min_row=2, max_row=ws.max_row-4):
            for cell in row:
                cell.border = border
                if isinstance(cell.value, (int, float)):
                    cell.number_format = '#,##0.00'
                    cell.alignment = right

        anchos = [12, 22, 14, 26, 12, 12, 14, 16, 12, 14]
        for i, w in enumerate(anchos, 1):
            ws.column_dimensions[get_column_letter(i)].width = w

        wb.save(ruta)