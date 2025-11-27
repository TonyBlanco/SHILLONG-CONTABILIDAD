# -*- coding: utf-8 -*-
"""
LIBRO MENSUAL — SHILLONG CONTABILIDAD v3.2 PRO++ (FORMATO FINAL PERFECTO)
"""

from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QFrame,
    QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextDocument, QColor
from PySide6.QtPrintSupport import QPrinter, QPrintPreviewDialog, QPrintDialog
from PySide6.QtCharts import QChart, QChartView, QBarCategoryAxis, QValueAxis, QBarSet, QBarSeries

import datetime
import json

from models.ExportadorExcelMensual import ExportadorExcelMensual


class LibroMensualView(QWidget):

    def __init__(self, data):
        super().__init__()
        self.data = data
        hoy = datetime.date.today()
        self.mes_actual = hoy.month
        self.año_actual = hoy.year
        self.bancos = self._cargar_bancos()
        self._build_ui()
        self.actualizar()

    def _cargar_bancos(self):
        try:
            with open("data/bancos.json", "r", encoding="utf-8") as f:
                return ["Todos"] + [b["nombre"] for b in json.load(f).get("banks", [])]
        except:
            return ["Todos", "Caja"]

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        titulo = QLabel("LIBRO MENSUAL — V.3.2 PRO++")
        titulo.setStyleSheet("font-size: 28px; font-weight: 800; color: #0f172a;")
        layout.addWidget(titulo)

        filtros = QHBoxLayout()
        filtros.addWidget(QLabel("Mes:"))
        self.cbo_mes = QComboBox()
        self.cbo_mes.addItems(["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"])
        self.cbo_mes.setCurrentIndex(self.mes_actual - 1)
        filtros.addWidget(self.cbo_mes)

        filtros.addWidget(QLabel("Año:"))
        self.cbo_año = QComboBox()
        for a in range(2020, 2036): self.cbo_año.addItem(str(a))
        self.cbo_año.setCurrentText(str(self.año_actual))
        filtros.addWidget(self.cbo_año)

        filtros.addWidget(QLabel("Categoría:"))
        self.cbo_categoria = QComboBox()
        self.cbo_categoria.addItems(["Todas", "FOOD", "MEDICINE", "HYGIENE", "SALARY", "ONLINE", "THERAPEUTIC", "DIET", "OTROS"])
        filtros.addWidget(self.cbo_categoria)

        filtros.addWidget(QLabel("Estado:"))
        self.cbo_estado = QComboBox()
        self.cbo_estado.addItems(["Todos", "pagado", "pendiente"])
        filtros.addWidget(self.cbo_estado)

        filtros.addWidget(QLabel("Banco:"))
        self.cbo_banco = QComboBox()
        self.cbo_banco.addItems(self.bancos)
        filtros.addWidget(self.cbo_banco)

        filtros.addWidget(QLabel("Tipo:"))
        self.cbo_tipo = QComboBox()
        self.cbo_tipo.addItems(["Todos", "Solo gastos", "Solo ingresos"])
        filtros.addWidget(self.cbo_tipo)

        filtros.addStretch()

        for w in [self.cbo_mes, self.cbo_año, self.cbo_categoria, self.cbo_estado, self.cbo_banco, self.cbo_tipo]:
            w.currentIndexChanged.connect(self.actualizar)

        btn_preview = QPushButton("Vista previa")
        btn_preview.clicked.connect(self.vista_previa)
        btn_print = QPushButton("Imprimir")
        btn_print.clicked.connect(self.imprimir)
        btn_export = QPushButton("Exportar Excel")
        btn_export.clicked.connect(self.exportar_excel)

        filtros.addWidget(btn_preview)
        filtros.addWidget(btn_print)
        filtros.addWidget(btn_export)
        layout.addLayout(filtros)

        cards = QHBoxLayout()
        self.card_gasto = self._crear_card("Gasto INR")
        self.lbl_gasto = self._crear_valor_card(self.card_gasto)
        cards.addWidget(self.card_gasto)
        self.card_ingreso = self._crear_card("Ingreso INR")
        self.lbl_ingreso = self._crear_valor_card(self.card_ingreso)
        cards.addWidget(self.card_ingreso)
        self.card_saldo = self._crear_card("Saldo")
        self.lbl_saldo = self._crear_valor_card(self.card_saldo)
        cards.addWidget(self.card_saldo)
        layout.addLayout(cards)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(10)
        self.tabla.setHorizontalHeaderLabels([
            "Cuenta","Nombre Cuenta","Fecha","Concepto","Debe INR","Haber INR",
            "Saldo Acum.","Banco","Estado","Documento"
        ])
        layout.addWidget(self.tabla)

        self.lbl_resumen = QLabel()
        self.lbl_resumen.setStyleSheet("font-size: 18px; font-weight: bold; color: #1e293b;")
        self.lbl_resumen.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_resumen)

        self.chart_view = QChartView()
        self.chart_view.setMinimumHeight(300)
        layout.addWidget(self.chart_view)

    def _crear_card(self, titulo):
        card = QFrame()
        card.setStyleSheet("background:#fff; border:1px solid #d1d5db; border-radius:12px; padding:10px;")
        card.setMinimumHeight(120)
        v = QVBoxLayout(card)
        lbl = QLabel(titulo)
        lbl.setStyleSheet("font-size:15px; font-weight:bold; color:#475569;")
        v.addWidget(lbl)
        return card

    def _crear_valor_card(self, card):
        lbl = QLabel("0,00")
        lbl.setStyleSheet("font-size:28px; font-weight:800; margin-top:8px;")
        card.layout().addWidget(lbl)
        return lbl

    def _fmt(self, n):
        return f"{float(n):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def _categoria_de_cuenta(self, cuenta):
        try:
            with open("data/reglas_conceptos.json", "r", encoding="utf-8") as f:
                reglas = json.load(f)
        except:
            reglas = {}
        cuenta_str = str(cuenta).strip()
        if cuenta_str in reglas:
            cat = reglas[cuenta_str].get("categoria", "").upper()
            mapeo = {"COMESTIBLES Y BEBIDAS": "FOOD", "FARMACIA Y MATERIAL SANITARIO": "MEDICINE",
                     "MATERIAL DE LIMPIEZA": "HYGIENE", "LAVANDERÍA": "HYGIENE", "ASEO PERSONAL": "HYGIENE",
                     "SUELDOS Y SALARIOS": "SALARY", "TELEFONÍA E INTERNET": "ONLINE"}
            return mapeo.get(cat, "OTROS")
        try:
            c = int(cuenta)
            if 600000 <= c <= 609999: return "FOOD"
            if 610000 <= c <= 619999: return "MEDICINE"
            if 620000 <= c <= 629999: return "HYGIENE"
            if 750000 <= c <= 759999: return "SALARY"
            if 770000 <= c <= 779999: return "ONLINE"
            if 780000 <= c <= 789999: return "THERAPEUTIC"
            if 790000 <= c <= 799999: return "DIET"
        except: pass
        return "OTROS"

    def _aplicar_filtros(self, movimientos):
        cat = self.cbo_categoria.currentText()
        estado = self.cbo_estado.currentText().lower()
        banco = self.cbo_banco.currentText()
        tipo = self.cbo_tipo.currentText()
        filtrados = []
        for m in movimientos:
            if cat != "Todas" and self._categoria_de_cuenta(m.get("cuenta")) != cat: continue
            if estado != "todos" and m.get("estado", "").lower() != estado: continue
            if banco != "Todos" and m.get("banco", "") != banco: continue
            if tipo == "Solo gastos" and float(m.get("debe", 0)) == 0: continue
            if tipo == "Solo ingresos" and float(m.get("haber", 0)) == 0: continue
            filtrados.append(m)
        return filtrados

    def actualizar(self):
        mes = self.cbo_mes.currentIndex() + 1
        año = int(self.cbo_año.currentText())
        movimientos = self.data.movimientos_por_mes(mes, año)
        filtrados = self._aplicar_filtros(movimientos)

        gasto = sum(float(m.get("debe", 0)) for m in filtrados)
        ingreso = sum(float(m.get("haber", 0)) for m in filtrados)
        saldo = ingreso - gasto

        self.lbl_gasto.setText(self._fmt(gasto))
        self.lbl_gasto.setStyleSheet("font-size:28px; font-weight:800; color:#dc2626;")
        self.lbl_ingreso.setText(self._fmt(ingreso))
        self.lbl_ingreso.setStyleSheet("font-size:28px; font-weight:800; color:#16a34a;")
        self.lbl_saldo.setText(self._fmt(saldo))
        self.lbl_saldo.setStyleSheet(f"font-size:28px; font-weight:800; color:{'#dc2626' if saldo<0 else '#16a34a'};")
        self.lbl_resumen.setText(f"GASTO TOTAL: {self._fmt(gasto)}   |   INGRESO TOTAL: {self._fmt(ingreso)}   |   SALDO: {self._fmt(saldo)}")

        self.tabla.setRowCount(0)
        saldo_acum = 0
        for m in filtrados:
            debe = float(m.get("debe", 0))
            haber = float(m.get("haber", 0))
            saldo_acum += haber - debe
            fila = [
                str(m.get("cuenta", "")),
                self.data.obtener_nombre_cuenta(m.get("cuenta")),
                m.get("fecha", ""),
                m.get("concepto", ""),
                self._fmt(debe),
                self._fmt(haber),
                self._fmt(saldo_acum),
                m.get("banco", ""),
                m.get("estado", ""),
                m.get("documento", "")
            ]
            self.tabla.insertRow(self.tabla.rowCount())
            for col, valor in enumerate(fila):
                item = QTableWidgetItem(str(valor))
                self.tabla.setItem(self.tabla.rowCount()-1, col, item)
        self.tabla.resizeColumnsToContents()
        self._crear_grafico(filtrados)

    def _crear_grafico(self, movimientos):
        series = QBarSeries()
        set_gasto = QBarSet("Gasto por categoría")
        cats = ["FOOD","MEDICINE","HYGIENE","SALARY","ONLINE","THERAPEUTIC","DIET","OTROS"]
        valores = [sum(float(m.get("debe", 0)) for m in movimientos if self._categoria_de_cuenta(m.get("cuenta")) == c) for c in cats]
        set_gasto.append(valores)
        series.append(set_gasto)
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Gasto por categoría (INR)")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        axis_x = QBarCategoryAxis()
        axis_x.append(cats)
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        axis_y = QValueAxis()
        axis_y.setLabelFormat("%.0f")
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        self.chart_view.setChart(chart)

    def _generar_html(self, mes, año):
        movimientos = self.data.movimientos_por_mes(mes, año)
        filtrados = self._aplicar_filtros(movimientos)
        html = """
        <html><head><style>
            body {font-family: Arial; margin:40px;}
            h1 {text-align:center; font-size:24px; margin-bottom:30px;}
            table {width:100%; border-collapse:collapse; margin:20px 0;}
            th {background:#e5e7eb; padding:12px; text-align:center; border:2px solid #000; white-space:nowrap;}
            td {padding:8px; border:1px solid #000; white-space:nowrap;}
            .num {text-align:right;}
            .total {font-weight:bold;}
            .total-td {background:#FFF2CC;}
        </style></head><body>
        """
        html += f"<h1>LIBRO MENSUAL — {self.cbo_mes.currentText()} {año}</h1>"
        html += "<table><tr><th>Cuenta</th><th>Nombre Cuenta</th><th>Fecha</th><th>Concepto</th><th>Debe</th><th>Haber</th><th>Saldo</th><th>Banco</th><th>Estado</th><th>Documento</th></tr>"
        saldo_acum = total_debe = total_haber = 0
        for m in filtrados:
            debe = float(m.get("debe", 0))
            haber = float(m.get("haber", 0))
            saldo_acum += haber - debe
            total_debe += debe
            total_haber += haber
            html += f"<tr><td>{m.get('cuenta','')}</td><td>{self.data.obtener_nombre_cuenta(m.get('cuenta'))}</td><td>{m.get('fecha','')}</td><td>{m.get('concepto','')}</td><td class='num'>{debe:,.2f}</td><td class='num'>{haber:,.2f}</td><td class='num'>{saldo_acum:,.2f}</td><td>{m.get('banco','')}</td><td>{m.get('estado','')}</td><td>{m.get('documento','')}</td></tr>"

        html += f"""
        <tr class='total'>
            <td></td><td></td><td></td><td></td><td></td>
            <td class='total-td'>TOTAL GASTO:</td>
            <td class='total-td num'>{total_debe:,.2f}</td>
            <td></td><td></td><td></td>
        </tr>
        <tr class='total'>
            <td></td><td></td><td></td><td></td><td></td>
            <td class='total-td'>TOTAL INGRESO:</td>
            <td class='total-td num'>{total_haber:,.2f}</td>
            <td></td><td></td><td></td>
        </tr>
        <tr class='total'>
            <td></td><td></td><td></td><td></td><td></td>
            <td class='total-td'>SALDO FINAL:</td>
            <td class='total-td num'>{saldo_acum:,.2f}</td>
            <td></td><td></td><td></td>
        </tr>
        """
        html += "</table></body></html>"
        return html

    def vista_previa(self):
        mes = self.cbo_mes.currentIndex() + 1
        año = int(self.cbo_año.currentText())
        html = self._generar_html(mes, año)
        printer = QPrinter(QPrinter.HighResolution)
        preview = QPrintPreviewDialog(printer, self)
        preview.paintRequested.connect(lambda p: self._imprimir_html(p, html))
        preview.exec()

    def imprimir(self):
        mes = self.cbo_mes.currentIndex() + 1
        año = int(self.cbo_año.currentText())
        html = self._generar_html(mes, año)
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec():
            self._imprimir_html(printer, html)

    def _imprimir_html(self, printer, html):
        doc = QTextDocument()
        doc.setHtml(html)
        doc.print_(printer)

    def exportar_excel(self):
        ruta, _ = QFileDialog.getSaveFileName(self, "Exportar Libro Mensual", "Libro_Mensual.xlsx", "Excel (*.xlsx)")
        if not ruta:
            return
        mes = self.cbo_mes.currentIndex() + 1
        año = int(self.cbo_año.currentText())
        movimientos = self.data.movimientos_por_mes(mes, año)
        filtrados = self._aplicar_filtros(movimientos)
        datos = []
        saldo_acum = 0
        for m in filtrados:
            debe = float(m.get("debe", 0))
            haber = float(m.get("haber", 0))
            saldo_acum += haber - debe
            datos.append({
                "cuenta": str(m.get("cuenta", "")),
                "nombre_cuenta": self.data.obtener_nombre_cuenta(m.get("cuenta")),
                "fecha": m.get("fecha", ""),
                "concepto": m.get("concepto", ""),
                "debe": debe,
                "haber": haber,
                "saldo_acumulado": saldo_acum,
                "banco": m.get("banco", ""),
                "estado": m.get("estado", ""),
                "documento": m.get("documento", "")
            })
        try:
            ExportadorExcelMensual.exportar(ruta, datos)
            QMessageBox.information(self, "OK", "Exportado correctamente")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))