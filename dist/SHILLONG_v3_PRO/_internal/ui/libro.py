# -*- coding: utf-8 -*-
"""
LIBRO MENSUAL — SHILLONG CONTABILIDAD v3
Reporte profesional estilo Excel
Multimoneda (desactivado) + Bancos
"""

from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextDocument

import datetime

from models.exportador_excel import ExportadorExcel
from models.BankManager import BankManager


class LibroMensualView(QWidget):

    def __init__(self, data):
        super().__init__()

        self.data = data

        hoy = datetime.date.today()
        self.mes_actual = hoy.month
        self.año_actual = hoy.year

        self._build_ui()
        self.actualizar()

    # ==============================================================
    #   UI PRINCIPAL
    # ==============================================================
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        titulo = QLabel("LIBRO MENSUAL — V.3")
        titulo.setStyleSheet("font-size: 28px; font-weight: 800; color: #0f172a;")
        layout.addWidget(titulo)

        # -------------------------------
        # FILTROS + BOTONES
        # -------------------------------
        box = QHBoxLayout()

        self.cbo_mes = QComboBox()
        self.cbo_mes.addItems([
            "Enero","Febrero","Marzo","Abril","Mayo","Junio",
            "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
        ])
        self.cbo_mes.setCurrentIndex(self.mes_actual - 1)

        self.cbo_año = QComboBox()
        for a in range(2023, 2035):
            self.cbo_año.addItem(str(a))
        self.cbo_año.setCurrentText(str(self.año_actual))

        self.cbo_mes.currentIndexChanged.connect(self.actualizar)
        self.cbo_año.currentIndexChanged.connect(self.actualizar)

        btn_preview = QPushButton("📄 Vista previa")
        btn_preview.clicked.connect(self.vista_previa)

        btn_print = QPushButton("🖨 Imprimir")
        btn_print.clicked.connect(self.imprimir)

        btn_exportar = QPushButton("⬇ Exportar a Excel")
        btn_exportar.clicked.connect(self.exportar_excel)

        box.addWidget(QLabel("Mes:"))
        box.addWidget(self.cbo_mes)
        box.addSpacing(20)
        box.addWidget(QLabel("Año:"))
        box.addWidget(self.cbo_año)
        box.addStretch()
        box.addWidget(btn_preview)
        box.addWidget(btn_print)
        box.addWidget(btn_exportar)

        layout.addLayout(box)

        # -------------------------------
        # TARJETAS
        # -------------------------------
        cards = QHBoxLayout()

        self.card_gasto = self._crear_card("Gasto INR (mes)")
        self.lbl_gasto = self._crear_valor_card(self.card_gasto)
        cards.addWidget(self.card_gasto)

        self.card_ingreso = self._crear_card("Ingreso INR (mes)")
        self.lbl_ingreso = self._crear_valor_card(self.card_ingreso)
        cards.addWidget(self.card_ingreso)

        self.card_total = self._crear_card("Total categorías")
        self.lbl_total = self._crear_valor_card(self.card_total)
        cards.addWidget(self.card_total)

        layout.addLayout(cards)

        # -------------------------------
        # TABLA PREVIA
        # -------------------------------
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(11)
        self.tabla.setHorizontalHeaderLabels([
            "Fecha","Documento","Concepto","Cuenta",
            "Nombre Cuenta","Debe INR","Haber",
            "Estado","Banco","Saldo","Categoría"
        ])
        layout.addWidget(self.tabla)

    # ==============================================================
    #   CARDS
    # ==============================================================
    def _crear_card(self, titulo):
        card = QFrame()
        card.setStyleSheet("""
            background: #ffffff;
            border: 1px solid #d1d5db;
            border-radius: 12px;
            padding: 10px;
        """)
        card.setMinimumHeight(120)

        layout = QVBoxLayout(card)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet("""
            font-size: 15px;
            font-weight: bold;
            color: #475569;
        """)

        layout.addWidget(lbl_titulo)
        return card

    def _crear_valor_card(self, card):
        lbl = QLabel("0,00")
        lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        lbl.setStyleSheet("""
            font-size: 28px;
            font-weight: 800;
            margin-top: 8px;
        """)
        card.layout().addWidget(lbl)
        return lbl

    def _set_card(self, label, valor):
        txt = self._fmt(valor)
        color = "#dc2626" if valor < 0 else "#16a34a"
        label.setStyleSheet(f"""
            font-size: 28px;
            font-weight: 800;
            color: {color};
        """)
        label.setText(txt)

    # ==============================================================
    #   FORMATO CONTABLE ESPAÑOL
    # ==============================================================
    def _fmt(self, num):
        try:
            return f"{float(num):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except:
            return str(num)

    # ==============================================================
    #   CATEGORÍAS OFICIALES
    # ==============================================================
    def _categoria_de_cuenta(self, cuenta):
        try:
            c = int(cuenta)
        except:
            return "OTROS"

        if 600000 <= c <= 609999:
            return "FOOD"
        if 610000 <= c <= 619999:
            return "MEDICINE"
        if 620000 <= c <= 629999:
            return "HYGIENE"
        if 750000 <= c <= 759999:
            return "SALARY"
        if 770000 <= c <= 779999:
            return "ONLINE"
        if 780000 <= c <= 789999:
            return "THERAPEUTIC"
        if 790000 <= c <= 799999:
            return "DIET"

        return "OTROS"

    # ==============================================================
    #   AGRUPAR MOVIMIENTOS
    # ==============================================================
    def _agrupar_por_categoria(self, movimientos):
        grupos = {
            "FOOD": [], "MEDICINE": [], "HYGIENE": [],
            "SALARY": [], "ONLINE": [], "THERAPEUTIC": [],
            "DIET": [], "OTROS": []
        }

        for m in movimientos:
            cat = self._categoria_de_cuenta(m.get("cuenta"))
            grupos[cat].append(m)

        return grupos

    # ==============================================================
    #   TOTALES
    # ==============================================================
    def _totales_categoria(self, lista):
        total_gasto = 0
        total_ingreso = 0
        saldo = 0

        for m in lista:
            debe = float(m.get("debe", 0))
            haber = float(m.get("haber", 0))
            total_gasto += debe
            total_ingreso += haber
            saldo += (haber - debe)

        return total_gasto, total_ingreso, saldo

    # ==============================================================
    #   PREVISUALIZACIÓN EN TABLA
    # ==============================================================
    def _cargar_tabla_preview(self, movimientos):
        self.tabla.setRowCount(len(movimientos))

        for i, m in enumerate(movimientos):
            fila = [
                m.get("fecha", ""),
                m.get("documento", ""),
                m.get("concepto", ""),
                str(m.get("cuenta", "")),
                self.data.obtener_nombre_cuenta(m.get("cuenta")),
                self._fmt(m.get("debe", 0)),
                self._fmt(m.get("haber", 0)),
                m.get("estado", ""),
                m.get("banco", ""),
                self._fmt(m.get("saldo", 0)),
                self._categoria_de_cuenta(m.get("cuenta"))
            ]

            for j, valor in enumerate(fila):
                item = QTableWidgetItem(str(valor))
                if j == 5:
                    item.setForeground(Qt.red)
                if j == 6:
                    item.setForeground(Qt.darkGreen)

                self.tabla.setItem(i, j, item)

        self.tabla.resizeColumnsToContents()

    # ==============================================================
    #   ACTUALIZAR VISTA
    # ==============================================================
    def actualizar(self):
        mes = self.cbo_mes.currentIndex() + 1
        año = int(self.cbo_año.currentText())

        movimientos = self.data.movimientos_por_mes(mes, año)
        grupos = self._agrupar_por_categoria(movimientos)

        gasto_total = sum(self._totales_categoria(grupos[c])[0] for c in grupos)
        ingreso_total = sum(self._totales_categoria(grupos[c])[1] for c in grupos)

        self._set_card(self.lbl_gasto, gasto_total)
        self._set_card(self.lbl_ingreso, ingreso_total)
        self._set_card(self.lbl_total, ingreso_total - gasto_total)

        self._cargar_tabla_preview(movimientos)

    # ==============================================================
    #   GENERAR HTML ESTILO EXCEL
    # ==============================================================
    def _generar_html(self, mes, año):
        movimientos = self.data.movimientos_por_mes(mes, año)
        grupos = self._agrupar_por_categoria(movimientos)

        html = """ 
        <html>
        <head>
            <style>
                body {
                    font-family: Arial;
                    font-size: 13px;
                }
                h1 {
                    text-align:center;
                    font-size: 24px;
                }
                h2 {
                    margin-top: 30px;
                    background: #f0f0f0;
                    padding: 6px;
                    border: 1px solid #333;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 8px;
                }
                th {
                    background: #dbe3f0;
                    padding: 6px;
                    border: 1px solid #333;
                    font-weight: bold;
                    text-align: center;
                }
                td {
                    border: 1px solid #333;
                    padding: 4px;
                }
                .num {
                    text-align: right;
                }
                .total-row {
                    background: #222;
                    color: white;
                    font-weight: bold;
                }
                .subtotal {
                    background: #9fbcd7;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
        """

        html += f"<h1>LIBRO MENSUAL — {self.cbo_mes.currentText()} {año}</h1>"

        # ----- FUNCIÓN PARA BLOQUE -----
        def bloque_categoria(nombre, lista):
            nonlocal html

            html += f"<h2>{nombre}</h2>"

            if not lista:
                html += "<i>No hay movimientos en esta categoría.</i>"
                return (0, 0, 0)

            html += """
            <table>
                <tr>
                    <th>Fecha</th>
                    <th>Documento</th>
                    <th>Concepto</th>
                    <th>Cuenta</th>
                    <th>Nombre Cuenta</th>
                    <th>Debe</th>
                    <th>Haber</th>
                    <th>Banco</th>
                    <th>Saldo</th>
                </tr>
            """

            saldo = 0
            total_gasto = 0
            total_ingreso = 0

            for m in lista:
                debe = float(m.get("debe", 0))
                haber = float(m.get("haber", 0))
                saldo += haber - debe

                total_gasto += debe
                total_ingreso += haber

                html += f"""
                <tr>
                    <td>{m.get('fecha','')}</td>
                    <td>{m.get('documento','')}</td>
                    <td>{m.get('concepto','')}</td>
                    <td>{m.get('cuenta','')}</td>
                    <td>{self.data.obtener_nombre_cuenta(m.get('cuenta'))}</td>
                    <td class="num">{debe:,.2f}</td>
                    <td class="num">{haber:,.2f}</td>
                    <td>{m.get('banco','')}</td>
                    <td class="num">{saldo:,.2f}</td>
                </tr>
                """

            html += f"""
            <tr class="subtotal">
                <td colspan="5">SUBTOTAL {nombre}</td>
                <td class="num">{total_gasto:,.2f}</td>
                <td class="num">{total_ingreso:,.2f}</td>
                <td></td>
                <td class="num">{saldo:,.2f}</td>
            </tr>
            </table>
            """

            return total_gasto, total_ingreso, saldo

        # ----- CREAR BLOQUES -----
        totales_finales = {}
        for cat in ["FOOD","MEDICINE","HYGIENE","SALARY","ONLINE","THERAPEUTIC","DIET"]:
            totales_finales[cat] = bloque_categoria(cat, grupos[cat])

        # ----- RESUMEN FINAL -----
        html += """
        <h2>RESUMEN FINAL</h2>
        <table>
        <tr><th>Categoría</th><th>Total Gasto</th><th>Total Ingreso</th><th>Saldo</th></tr>
        """

        gasto_total = 0
        ingreso_total = 0
        saldo_total = 0

        for cat, (g, i, s) in totales_finales.items():
            gasto_total += g
            ingreso_total += i
            saldo_total += s

            html += f"""
            <tr>
                <td>{cat}</td>
                <td class="num">{g:,.2f}</td>
                <td class="num">{i:,.2f}</td>
                <td class="num">{s:,.2f}</td>
            </tr>
            """

        html += f"""
        <tr class="total-row">
            <td>TOTAL GENERAL</td>
            <td class="num">{gasto_total:,.2f}</td>
            <td class="num">{ingreso_total:,.2f}</td>
            <td class="num">{saldo_total:,.2f}</td>
        </tr>
        </table>
        </body>
        </html>
        """

        return html

    # ==============================================================
    #   VISTA PREVIA (PDF-LIKE)
    # ==============================================================
    def vista_previa(self):
        from PySide6.QtPrintSupport import QPrinter, QPrintPreviewDialog

        mes = self.cbo_mes.currentIndex() + 1
        año = int(self.cbo_año.currentText())
        html = self._generar_html(mes, año)

        printer = QPrinter()
        preview = QPrintPreviewDialog(printer, self)

        preview.paintRequested.connect(
            lambda p: self._imprimir_documento(p, html)
        )

        preview.exec()

    # ==============================================================
    #   IMPRIMIR
    # ==============================================================
    def imprimir(self):
        from PySide6.QtPrintSupport import QPrinter, QPrintDialog

        mes = self.cbo_mes.currentIndex() + 1
        año = int(self.cbo_año.currentText())
        html = self._generar_html(mes, año)

        printer = QPrinter()
        dialog = QPrintDialog(printer, self)

        if dialog.exec():
            self._imprimir_documento(printer, html)

    # ==============================================================
    #   MÉTODO INTERNO PARA IMPRIMIR HTML
    # ==============================================================
    def _imprimir_documento(self, printer, html):
        doc = QTextDocument()
        doc.setHtml(html)
        doc.print_(printer)

    # ==============================================================
    #   EXPORTAR A EXCEL (CORREGIDO)
    # ==============================================================
    def exportar_excel(self):
        from PySide6.QtWidgets import QFileDialog, QMessageBox

        ruta, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Libro Mensual",
            "LibroMensual.xlsx",
            "Excel (*.xlsx)"
        )

        if not ruta:
            return

        mes = self.cbo_mes.currentIndex() + 1
        año = int(self.cbo_año.currentText())

        datos = self.data.movimientos_por_mes(mes, año)

        try:
            ExportadorExcel.exportar(ruta, datos)
        except Exception as e:
            QMessageBox.warning(self, "Error exportando", str(e))
