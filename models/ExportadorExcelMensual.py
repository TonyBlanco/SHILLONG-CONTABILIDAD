# -*- coding: utf-8 -*-
"""
models/ExportadorExcelMensual.py — MOTOR DE EXPORTACIÓN v3.7.2
-----------------------------------------------------------------
Genera reportes Excel profesionales con:
- Totales calculados (Debe, Haber y SALDO NETO).
- Formato de moneda.
- Estilos (Negritas, colores).
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side


class ExportadorExcelMensual:
    
    @staticmethod
    def _estilar_cabecera(ws, columnas):
        """Aplica estilo azul profesional a la cabecera."""
        thin = Side(border_style="thin", color="000000")
        border = Border(left=thin, right=thin, top=thin, bottom=thin)
        fill = PatternFill(
            start_color="1e3a8a",
            end_color="1e3a8a",
            fill_type="solid"
        )  # Azul oscuro
        font = Font(color="FFFFFF", bold=True)
        
        for col_num, nombre in enumerate(columnas, 1):
            cell = ws.cell(row=1, column=col_num, value=nombre)
            cell.fill = fill
            cell.font = font
            cell.alignment = Alignment(horizontal="center")
            cell.border = border
            
            # Anchos aproximados
            ancho = 15
            if "Concepto" in nombre:
                ancho = 40
            if "Cuenta" in nombre:
                ancho = 20
            if "Nombre" in nombre:
                ancho = 30
            ws.column_dimensions[
                openpyxl.utils.get_column_letter(col_num)
            ].width = ancho

    @staticmethod
    def _formato_moneda(ws, row, cols_indices):
        """Aplica formato #,##0.00 a las celdas indicadas."""
        for col in cols_indices:
            cell = ws.cell(row=row, column=col)
            cell.number_format = "#,##0.00"

    # ============================================================
    #  EXPORTACIÓN GENERAL — FORMATO LIBRO TEST
    # ============================================================
    @staticmethod
    def exportar_general(ruta_archivo, datos, periodo_str):
        """
        Exporta el listado detallado en el formato oficial:
        Fecha | Cuenta | Categoría | Concepto | Debe | Haber | Saldo | Banco | Documento
        """
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Libro Mensual"

        # Encabezado EXACTO como el Libro TEST
        headers = [
            "Fecha",
            "Cuenta",
            "Categoría",
            "Concepto",
            "Debe",
            "Haber",
            "Saldo",
            "Banco",
            "Documento",
        ]
        ExportadorExcelMensual._estilar_cabecera(ws, headers)

        row_idx = 2
        total_debe = 0.0
        total_haber = 0.0

        for m in datos:
            debe = float(m.get("debe", 0) or 0)
            haber = float(m.get("haber", 0) or 0)
            saldo = float(m.get("saldo", 0) or 0)

            total_debe += debe
            total_haber += haber

            row = [
                m.get("fecha"),                    # 1 Fecha
                str(m.get("cuenta")),              # 2 Cuenta
                m.get("categoria", ""),            # 3 Categoría
                m.get("concepto"),                 # 4 Concepto
                debe,                              # 5 Debe
                haber,                             # 6 Haber
                saldo,                             # 7 Saldo
                m.get("banco"),                    # 8 Banco
                m.get("documento"),                # 9 Documento
            ]

            for col_idx, val in enumerate(row, 1):
                ws.cell(row=row_idx, column=col_idx, value=val)

            # Debe, Haber, Saldo → columnas 5,6,7
            ExportadorExcelMensual._formato_moneda(ws, row_idx, [5, 6, 7])
            row_idx += 1

        # Fila de TOTALES
        ws.cell(row=row_idx, column=1, value="TOTALES DEL PERIODO").font = Font(
            bold=True
        )
        ws.cell(row=row_idx, column=5, value=total_debe).font = Font(bold=True)
        ws.cell(row=row_idx, column=6, value=total_haber).font = Font(bold=True)
        ws.cell(
            row=row_idx,
            column=7,
            value=total_haber - total_debe,
        ).font = Font(
            bold=True,
            color="FF0000" if (total_haber - total_debe) < 0 else "000000",
        )

        ExportadorExcelMensual._formato_moneda(ws, row_idx, [5, 6, 7])

        try:
            wb.save(ruta_archivo)
            return True
        except Exception as e:
            raise e

    # ============================================================
    #  EXPORTACIÓN AGRUPADA (NO SE TOCA)
    # ============================================================
    @staticmethod
    def exportar_agrupado(ruta_archivo, grupos_data, periodo_str, titulo_agrupacion):
        """
        Exporta agrupando por Categoría o Cuenta.
        grupos_data: Diccionario { "NombreGrupo": [lista_movimientos] }
        """
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Resumen Agrupado"

        headers = [
            titulo_agrupacion,
            "Fecha",
            "Documento",
            "Concepto",
            "Cuenta",
            "Debe",
            "Haber",
            "Saldo",
        ]
        ExportadorExcelMensual._estilar_cabecera(ws, headers)

        row_idx = 2

        gran_total_debe = 0.0
        gran_total_haber = 0.0

        # Iterar grupos
        from openpyxl.styles import PatternFill

        for nombre_grupo, movimientos in grupos_data.items():
            # Cabecera de grupo
            cell_group = ws.cell(row=row_idx, column=1, value=f"{nombre_grupo.upper()}")
            cell_group.font = Font(bold=True, size=12, color="1e3a8a")
            ws.merge_cells(
                start_row=row_idx,
                start_column=1,
                end_row=row_idx,
                end_column=8,
            )
            ws.cell(row=row_idx, column=1).fill = PatternFill(
                start_color="e2e8f0", end_color="e2e8f0", fill_type="solid"
            )
            row_idx += 1

            subtotal_debe = 0.0
            subtotal_haber = 0.0
            saldo_acumulado_grupo = 0.0

            for m in movimientos:
                d = float(m.get("debe", 0) or 0)
                h = float(m.get("haber", 0) or 0)
                subtotal_debe += d
                subtotal_haber += h
                saldo_acumulado_grupo += (h - d)

                ws.cell(row=row_idx, column=2, value=m.get("fecha"))
                ws.cell(row=row_idx, column=3, value=m.get("documento"))
                ws.cell(row=row_idx, column=4, value=m.get("concepto"))
                ws.cell(row=row_idx, column=5, value=str(m.get("cuenta")))
                ws.cell(row=row_idx, column=6, value=d)
                ws.cell(row=row_idx, column=7, value=h)
                ws.cell(row=row_idx, column=8, value=saldo_acumulado_grupo)

                ExportadorExcelMensual._formato_moneda(ws, row_idx, [6, 7, 8])
                row_idx += 1

            # Pie de grupo (Subtotales)
            ws.cell(
                row=row_idx, column=1, value=f"TOTAL {nombre_grupo}"
            ).font = Font(bold=True)
            ws.cell(row=row_idx, column=6, value=subtotal_debe).font = Font(bold=True)
            ws.cell(row=row_idx, column=7, value=subtotal_haber).font = Font(bold=True)

            # Saldo neto del grupo
            neto_grupo = subtotal_haber - subtotal_debe
            cell_saldo = ws.cell(row=row_idx, column=8, value=neto_grupo)
            cell_saldo.font = Font(
                bold=True, color="FF0000" if neto_grupo < 0 else "008000"
            )

            ExportadorExcelMensual._formato_moneda(ws, row_idx, [6, 7, 8])

            # Línea de separación visual
            for c in range(1, 9):
                ws.cell(row=row_idx, column=c).border = Border(
                    bottom=Side(style="thick")
                )

            row_idx += 2  # Espacio

            gran_total_debe += subtotal_debe
            gran_total_haber += subtotal_haber

        # GRAN TOTAL FINAL
        ws.cell(row=row_idx, column=1, value="TOTAL REPORTE").font = Font(
            bold=True, size=14
        )
        ws.cell(row=row_idx, column=6, value=gran_total_debe).font = Font(
            bold=True, size=12
        )
        ws.cell(row=row_idx, column=7, value=gran_total_haber).font = Font(
            bold=True, size=12
        )

        gran_neto = gran_total_haber - gran_total_debe
        cell_gran_saldo = ws.cell(row=row_idx, column=8, value=gran_neto)
        cell_gran_saldo.font = Font(
            bold=True, size=12, color="FF0000" if gran_neto < 0 else "008000"
        )

        ExportadorExcelMensual._formato_moneda(ws, row_idx, [6, 7, 8])

        try:
            wb.save(ruta_archivo)
            return True
        except Exception as e:
            raise e
