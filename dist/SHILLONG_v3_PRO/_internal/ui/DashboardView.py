# -*- coding: utf-8 -*-
"""
DashboardView — SHILLONG CONTABILIDAD v3 PRO
Dashboard principal con tarjetas, gráficas y tablas
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt
from PySide6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis, QLineSeries
from PySide6.QtGui import QColor, QPainter

import datetime
import json
from pathlib import Path


class DashboardView(QWidget):

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.hoy = datetime.date.today()
        self.mes = self.hoy.month
        self.año = self.hoy.year
        self.bancos = self._cargar_bancos()
        self._build_ui()
        self.actualizar()

    def _cargar_bancos(self):
        try:
            with open("data/bancos.json", "r", encoding="utf-8") as f:
                return json.load(f).get("banks", [])
        except:
            return []

    def _fmt(self, n):
        return f"{float(n):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def _build_ui(self):
        self.setStyleSheet("background:#f1f5f9; font-family:Segoe UI, Arial;")
        main = QVBoxLayout(self)
        main.setSpacing(20)
        main.setContentsMargins(30, 20, 30, 20)

        # Tarjetas superiores
        cards = QHBoxLayout()
        cards.setSpacing(20)

        self.card_gasto = self._crear_card("Gasto del mes", "0,00", "#dc2626")
        self.card_ingreso = self._crear_card("Ingreso del mes", "0,00", "#16a34a")
        self.card_saldo = self._crear_card("Saldo del mes", "0,00", "#2563eb")
        self.card_bancos = self._crear_card("Saldo total bancos", "0,00", "#7c3aed")

        cards.addWidget(self.card_gasto)
        cards.addWidget(self.card_ingreso)
        cards.addWidget(self.card_saldo)
        cards.addWidget(self.card_bancos)
        main.addLayout(cards)

        # Gráficas y tablas
        row1 = QHBoxLayout()
        row1.setSpacing(20)

        # Gráfica gasto por categoría
        chart1 = self._crear_chart("Gasto por categoría — Mes actual")
        self.view_categoria = QChartView(chart1)
        self.view_categoria.setMinimumHeight(320)
        self.view_categoria.setRenderHint(QPainter.Antialiasing)
        row1.addWidget(self.view_categoria, 2)

        # Tabla Top 5 mes
        self.tabla_mes = self._crear_tabla("Top 5 cuentas — Mes actual")
        row1.addWidget(self.tabla_mes, 1)

        main.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(20)

        # Gráfica anual
        chart2 = self._crear_chart("Gastos mensuales — Año " + str(self.año))
        self.view_anual = QChartView(chart2)
        self.view_anual.setMinimumHeight(320)
        self.view_anual.setRenderHint(QPainter.Antialiasing)
        row2.addWidget(self.view_anual, 2)

        col_der = QVBoxLayout()
        col_der.setSpacing(20)

        # Tabla Top 5 año
        self.tabla_año = self._crear_tabla("Top 5 cuentas — Año " + str(self.año))
        col_der.addWidget(self.tabla_año)

        # Estado de bancos
        self.tabla_bancos = self._crear_tabla_bancos()
        col_der.addWidget(self.tabla_bancos)

        row2.addLayout(col_der, 1)
        main.addLayout(row2)

    def _crear_card(self, titulo, valor, color):
        frame = QFrame()
        frame.setStyleSheet(f"""
            background:#ffffff; border-radius:12px; border:1px solid #e2e8f0;
            padding:16px; min-width:200px;
        """)
        layout = QVBoxLayout(frame)
        lbl_tit = QLabel(titulo)
        lbl_tit.setStyleSheet("font-size:14px; color:#64748b;")
        lbl_val = QLabel(valor)
        lbl_val.setStyleSheet(f"font-size:28px; font-weight:800; color:{color};")
        layout.addWidget(lbl_tit)
        layout.addWidget(lbl_val)
        return frame

    def _crear_chart(self, titulo):
        chart = QChart()
        chart.setTitle(titulo)
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        return chart

    def _crear_tabla(self, titulo):
        frame = QFrame()
        frame.setStyleSheet("background:#ffffff; border-radius:12px; border:1px solid #e2e8f0;")
        layout = QVBoxLayout(frame)
        lbl = QLabel(titulo)
        lbl.setStyleSheet("font-size:15px; font-weight:bold; padding:12px; color:#1e293b;")
        tabla = QTableWidget(5, 3)
        tabla.setHorizontalHeaderLabels(["Cuenta", "Nombre", "Gasto"])
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        tabla.setStyleSheet("QTableWidget {font-size:13px;}")
        layout.addWidget(lbl)
        layout.addWidget(tabla)
        return frame

    def _crear_tabla_bancos(self):
        frame = QFrame()
        frame.setStyleSheet("background:#ffffff; border-radius:12px; border:1px solid #e2e8f0;")
        layout = QVBoxLayout(frame)
        lbl = QLabel("Estado de bancos")
        lbl.setStyleSheet("font-size:15px; font-weight:bold; padding:12px; color:#1e293b;")
        tabla = QTableWidget(len(self.bancos), 2)
        tabla.setHorizontalHeaderLabels(["Banco", "Saldo"])
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(lbl)
        layout.addWidget(tabla)
        return frame

    def _categoria_de_cuenta(self, cuenta):
        try:
            with open("data/reglas_conceptos.json", "r", encoding="utf-8") as f:
                reglas = json.load(f)
        except:
            reglas = {}

        cat = reglas.get(str(cuenta), {}).get("categoria", "").upper()
        mapeo = {
            "COMESTIBLES Y BEBIDAS": "FOOD", "FARMACIA Y MATERIAL SANITARIO": "MEDICINE",
            "MATERIAL DE LIMPIEZA": "HYGIENE", "LAVANDERÍA": "HYGIENE", "ASEO PERSONAL": "HYGIENE",
            "SUELDOS Y SALARIOS": "SALARY", "TELEFONÍA E INTERNET": "ONLINE",
            "ODONTOLOGÍA": "THERAPEUTIC", "OFTALMOLOGÍA": "THERAPEUTIC"
        }
        if cat in mapeo.values():
            return cat
        return mapeo.get(cat, "OTROS")

    def actualizar(self):
        # Totales del mes
        mov_mes = self.data.movimientos_por_mes(self.mes, self.año)
        gasto_mes = sum(float(m.get("debe", 0)) for m in mov_mes)
        ingreso_mes = sum(float(m.get("haber", 0)) for m in mov_mes)
        saldo_mes = ingreso_mes - gasto_mes

        saldo_bancos = sum(b.get("saldo", 0) for b in self.bancos)

        # Actualizar tarjetas
        self.card_gasto.layout().itemAt(1).widget().setText(self._fmt(gasto_mes))
        self.card_ingreso.layout().itemAt(1).widget().setText(self._fmt(ingreso_mes))
        self.card_saldo.layout().itemAt(1).widget().setText(self._fmt(saldo_mes))
        self.card_saldo.layout().itemAt(1).widget().setStyleSheet(
            f"font-size:28px; font-weight:800; color:{'#dc2626' if saldo_mes<0 else '#16a34a'};"
        )
        self.card_bancos.layout().itemAt(1).widget().setText(self._fmt(saldo_bancos))

        # Gráfica por categoría
        cats = ["FOOD","MEDICINE","HYGIENE","SALARY","ONLINE","THERAPEUTIC","DIET","OTROS"]
        valores = []
        for cat in cats:
            total = sum(float(m.get("debe", 0)) for m in mov_mes if self._categoria_de_cuenta(m.get("cuenta")) == cat)
            valores.append(total)

        set_cat = QBarSet("Gasto")
        set_cat.append(valores)
        set_cat.setBrush(QColor("#3b82f6"))

        chart_cat = self.view_categoria.chart()
        chart_cat.removeAllSeries()
        series_cat = QBarSeries()
        series_cat.append(set_cat)
        chart_cat.addSeries(series_cat)

        axis_x_cat = QBarCategoryAxis()
        axis_x_cat.append(cats)
        chart_cat.setAxisX(axis_x_cat, series_cat)

        axis_y_cat = QValueAxis()
        axis_y_cat.setLabelFormat("%.0f")
        chart_cat.setAxisY(axis_y_cat, series_cat)

        # Gráfica anual
        meses = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
        gastos_anual = []
        for m in range(1, 13):
            mov = self.data.movimientos_por_mes(m, self.año)
            gastos_anual.append(sum(float(x.get("debe", 0)) for x in mov))

        set_anual = QBarSet("Gasto")
        set_anual.append(gastos_anual)
        set_anual.setBrush(QColor("#10b981"))

        chart_anual = self.view_anual.chart()
        chart_anual.removeAllSeries()
        series_anual = QBarSeries()
        series_anual.append(set_anual)
        chart_anual.addSeries(series_anual)

        axis_x_anual = QBarCategoryAxis()
        axis_x_anual.append(meses)
        chart_anual.setAxisX(axis_x_anual, series_anual)

        axis_y_anual = QValueAxis()
        axis_y_anual.setLabelFormat("%.0f")
        chart_anual.setAxisY(axis_y_anual, series_anual)

        # Top 5 mes
        resumen = {}
        for m in mov_mes:
            cuenta = str(m.get("cuenta"))
            resumen[cuenta] = resumen.get(cuenta, 0) + float(m.get("debe", 0))
        top_mes = sorted(resumen.items(), key=lambda x: x[1], reverse=True)[:5]

        tabla_mes = self.tabla_mes.findChild(QTableWidget)
        tabla_mes.setRowCount(0)
        for cuenta, total in top_mes:
            nombre = self.data.obtener_nombre_cuenta(cuenta)
            fila = tabla_mes.rowCount()
            tabla_mes.insertRow(fila)
            tabla_mes.setItem(fila, 0, QTableWidgetItem(cuenta))
            tabla_mes.setItem(fila, 1, QTableWidgetItem(nombre))
            tabla_mes.setItem(fila, 2, QTableWidgetItem(self._fmt(total)))

        # Top 5 año
        top_año = self.data.get_top_cuentas_anuales(self.año, 5)
        tabla_año = self.tabla_año.findChild(QTableWidget)
        tabla_año.setRowCount(0)
        for cuenta, nombre, total in top_año:
            fila = tabla_año.rowCount()
            tabla_año.insertRow(fila)
            tabla_año.setItem(fila, 0, QTableWidgetItem(cuenta))
            tabla_año.setItem(fila, 1, QTableWidgetItem(nombre))
            tabla_año.setItem(fila, 2, QTableWidgetItem(self._fmt(total)))

        # Estado bancos
        tabla_bancos = self.tabla_bancos.findChild(QTableWidget)
        tabla_bancos.setRowCount(0)
        for b in self.bancos:
            fila = tabla_bancos.rowCount()
            tabla_bancos.insertRow(fila)
            item_nombre = QTableWidgetItem(b.get("nombre", ""))
            item_saldo = QTableWidgetItem(self._fmt(b.get("saldo", 0)))
            color = "#16a34a" if b.get("saldo", 0) >= 0 else "#dc2626"
            item_saldo.setForeground(QColor(color))
            tabla_bancos.setItem(fila, 0, item_nombre
                                 )
            tabla_bancos.setItem(fila, 1, item_saldo)