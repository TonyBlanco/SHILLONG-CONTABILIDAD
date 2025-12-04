# -*- coding: utf-8 -*-
"""
CierreMensualView — SHILLONG CONTABILIDAD v3.8 PRO
---------------------------------------------------------
Versión corregida con el FORMATO OFICIAL “LIBRO TEST”
para que la pantalla y el Excel coincidan EXACTAMENTE
con el libro mensual perfecto solicitado por las Hermanas.
---------------------------------------------------------
"""

import datetime
import json
from collections import defaultdict

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QComboBox, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QTextEdit, QMenu, QHeaderView,
    QFrame, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QMarginsF
from PySide6.QtGui import QColor, QFont, QPainter, QTextDocument, QPageLayout
from PySide6.QtPrintSupport import QPrinter
from PySide6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis

try:
    from models.ExportadorExcelMensual import ExportadorExcelMensual
except ImportError:
    ExportadorExcelMensual = None


class CierreMensualView(QWidget):

    # ---------------------------------------------------------
    # INIT
    # ---------------------------------------------------------
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.hoy = datetime.date.today()
        self.mes_actual = self.hoy.month
        self.año_actual = self.hoy.year

        self.bancos = self._cargar_bancos()
        self.cuentas = self._cargar_cuentas()
        self.reglas_cache = self._cargar_reglas()

        self._build_ui()
        self.actualizar()

    # ---------------------------------------------------------
    # CARGA DE DATOS
    # ---------------------------------------------------------
    def _cargar_bancos(self):
        try:
            with open("data/bancos.json", "r", encoding="utf-8") as f:
                return ["Todos"] + [b["nombre"] for b in json.load(f).get("banks", [])]
        except (IOError, json.JSONDecodeError, KeyError):
            return ["Todos", "Caja"]

    def _cargar_cuentas(self):
        cuentas = ["Todas"]
        try:
            with open("data/plan_contable_v3.json", "r", encoding="utf-8") as f:
                plan = json.load(f)
                cuentas.extend([f"{k} – {v['nombre']}" for k, v in plan.items()])
        except (IOError, json.JSONDecodeError, KeyError):
            pass
        return cuentas

    def _cargar_reglas(self):
        try:
            with open("data/reglas_conceptos.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError):
            return {}

    # ---------------------------------------------------------
    # CATEGORÍAS
    # ---------------------------------------------------------
    def _categoria_de_cuenta(self, cuenta):
        cuenta_str = str(cuenta).split(" ")[0].strip()

        if cuenta_str in self.reglas_cache:
            cat = self.reglas_cache[cuenta_str].get("categoria", "").upper()

            mapeo = {
                "COMESTIBLES Y BEBIDAS": "FOOD",
                "ALIMENTACIÓN": "FOOD",
                "FARMACIA Y MATERIAL SANITARIO": "MEDICINE",
                "MEDICINA": "MEDICINE",
                "MEDICAMENTOS": "MEDICINE",
                "MATERIAL DE LIMPIEZA": "HYGIENE",
                "LIMPIEZA": "HYGIENE",
                "ASEO PERSONAL": "HYGIENE",
                "LAVANDERÍA": "HYGIENE",
                "SUELDOS Y SALARIOS": "SALARY",
                "TELEFONÍA E INTERNET": "ONLINE",
                "INTERNET": "ONLINE",
                "TELEFONO": "ONLINE",
                "FORMACIÓN": "TRAINING"
            }
            return mapeo.get(cat, cat)

        # Rango contable genérico
        try:
            c = int(cuenta_str)
            if 603000 <= c <= 603999: return "FOOD"
            if 600000 <= c <= 609999: return "MEDICINE"
            if 602400 <= c <= 602499: return "HYGIENE"
            if 629200 <= c <= 629299: return "ONLINE"
        except (ValueError, TypeError):
            pass

        return "OTROS"

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        # ------------------------
        # TÍTULO
        # ------------------------
        h = QHBoxLayout()
        tit = QLabel("📆 Cierre Mensual")
        tit.setStyleSheet("font-size: 28px; font-weight: 900; color: #0f172a;")
        h.addWidget(tit)
        h.addStretch()

        # Botón exportación
        self.btn_exportar_menu = QPushButton("📤 Exportar ▼")
        self.btn_exportar_menu.setStyleSheet(
            "background-color: #2563eb; color: white; font-weight:bold; padding:8px 15px; border-radius:6px;"
        )
        self.menu_exp = QMenu(self)
        self.menu_exp.addAction("📊 Excel General", self._exportar_excel_general)
        self.menu_exp.addAction("📂 Excel por Categorías", self._exportar_excel_categorias)
        self.menu_exp.addAction("🔢 Excel por Cuentas", self._exportar_excel_cuentas)
        self.menu_exp.addSeparator()
        self.menu_exp.addAction("📄 PDF Estándar", self._exportar_pdf_estandar)
        self.menu_exp.addAction("📘 PDF Oficial Azul", self._exportar_pdf_azul)
        self.btn_exportar_menu.setMenu(self.menu_exp)

        h.addWidget(self.btn_exportar_menu)
        layout.addLayout(h)

        # ------------------------
        # FILTROS
        # ------------------------
        filtros = QGridLayout()
        self.cbo_mes = QComboBox()
        self.cbo_mes.addItems([
            "Enero","Febrero","Marzo","Abril","Mayo","Junio",
            "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
        ])
        self.cbo_mes.setCurrentIndex(self.mes_actual - 1)

        self.cbo_año = QComboBox()
        for a in range(2020, 2036):
            self.cbo_año.addItem(str(a))
        self.cbo_año.setCurrentText(str(self.año_actual))

        self.cbo_banco = QComboBox()
        self.cbo_banco.addItems(self.bancos)

        self.cbo_cuenta = QComboBox()
        self.cbo_cuenta.addItems(self.cuentas)

        filtros.addWidget(QLabel("Mes:"), 0, 0)
        filtros.addWidget(self.cbo_mes, 0, 1)
        filtros.addWidget(QLabel("Año:"), 0, 2)
        filtros.addWidget(self.cbo_año, 0, 3)
        filtros.addWidget(QLabel("Banco:"), 1, 0)
        filtros.addWidget(self.cbo_banco, 1, 1)
        filtros.addWidget(QLabel("Cuenta:"), 1, 2)
        filtros.addWidget(self.cbo_cuenta, 1, 3)

        for w in [self.cbo_mes, self.cbo_año, self.cbo_banco, self.cbo_cuenta]:
            w.currentIndexChanged.connect(self.actualizar)

        layout.addLayout(filtros)

        # ------------------------
        # KPI
        # ------------------------
        kpi = QHBoxLayout()
        self.card_gasto = self._kpi("Gastos", "#dc2626")
        self.card_ingreso = self._kpi("Ingresos", "#16a34a")
        self.card_saldo = self._kpi("Saldo", "#2563eb")
        kpi.addWidget(self.card_gasto)
        kpi.addWidget(self.card_ingreso)
        kpi.addWidget(self.card_saldo)
        layout.addLayout(kpi)

        # ------------------------
        # TABLA — FORMATO OFICIAL
        # ------------------------
        self.tabla = QTableWidget(0, 9)
        self.tabla.setHorizontalHeaderLabels([
            "Fecha","Cuenta","Categoría","Concepto",
            "Debe","Haber","Saldo","Banco","Documento"
        ])
        self.tabla.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        layout.addWidget(self.tabla)

        # ------------------------
        # GRÁFICOS + ANOMALÍAS
        # ------------------------
        bot = QHBoxLayout()
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setMinimumHeight(250)
        bot.addWidget(self.chart_view, 2)

        anom = QFrame()
        av = QVBoxLayout(anom)
        av.addWidget(QLabel("⚠️ Anomalías:"))
        self.txt_anom = QTextEdit()
        self.txt_anom.setReadOnly(True)
        av.addWidget(self.txt_anom)
        bot.addWidget(anom, 1)

        layout.addLayout(bot)

    # ---------------------------------------------------------
    # KPI CARD
    # ---------------------------------------------------------
    def _kpi(self, t, c):
        f = QFrame()
        f.setStyleSheet(
            f"background:white; border:1px solid #ddd; "
            f"border-radius:10px; border-left:5px solid {c};"
        )
        v = QVBoxLayout(f)
        l1 = QLabel(t)
        l2 = QLabel("0.00")
        l2.setStyleSheet(
            f"font-size:24px; font-weight:bold; color:{c};"
        )
        l2.setObjectName("val")
        v.addWidget(l1)
        v.addWidget(l2)
        f.val = l2
        return f

    # ---------------------------------------------------------
    # ACTUALIZAR VISTA
    # ---------------------------------------------------------
    def actualizar(self):
        mes = self.cbo_mes.currentIndex() + 1
        año = int(self.cbo_año.currentText())
        banco = self.cbo_banco.currentText()

        cta_filt = None
        if " – " in self.cbo_cuenta.currentText():
            cta_filt = self.cbo_cuenta.currentText().split(" – ")[0]

        movs = self.data.movimientos_por_mes(mes, año)
        self.filtrados = []

        for m in movs:
            if banco != "Todos" and m.get("banco") != banco:
                continue
            if cta_filt and str(m.get("cuenta")) != cta_filt:
                continue
            self.filtrados.append(m)

        gas = sum(float(m.get("debe", 0)) for m in self.filtrados)
        ing = sum(float(m.get("haber", 0)) for m in self.filtrados)

        self.card_gasto.val.setText(f"{gas:,.2f}")
        self.card_ingreso.val.setText(f"{ing:,.2f}")
        self.card_saldo.val.setText(f"{ing - gas:,.2f}")

        # TABLA
        self.tabla.setRowCount(0)
        saldo = 0

        for m in self.filtrados:
            d = float(m.get("debe", 0))
            h = float(m.get("haber", 0))
            saldo += h - d

            cat = self._categoria_de_cuenta(m.get("cuenta"))

            row = [
                m.get("fecha"),
                m.get("cuenta"),
                cat,
                m.get("concepto"),
                f"{d:,.2f}",
                f"{h:,.2f}",
                f"{saldo:,.2f}",
                m.get("banco"),
                m.get("documento")
            ]

            r = self.tabla.rowCount()
            self.tabla.insertRow(r)

            for c, val in enumerate(row):
                it = QTableWidgetItem(str(val))

                if c in [4, 5, 6]:
                    it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

                if c == 2:  # Categoría coloreada
                    it.setForeground(QColor("#0f766e"))
                    it.setFont(QFont("Arial", 9, QFont.Bold))

                self.tabla.setItem(r, c, it)

        self._graficos(self.filtrados)

        # Anomalías
        dups = [
            m.get("documento") for m in self.filtrados
            if m.get("documento") and "SIN-DOC" not in str(m.get("documento"))
        ]
        if len(dups) != len(set(dups)):
            self.txt_anom.setText("⚠️ Documentos duplicados detectados.")
        else:
            self.txt_anom.setText("✅ Todo correcto.")

    # ---------------------------------------------------------
    # GRAFICOS
    # ---------------------------------------------------------
    def _graficos(self, movs):
        cats = defaultdict(float)
        for m in movs:
            if float(m.get("debe", 0)) > 0:
                cats[self._categoria_de_cuenta(m.get("cuenta"))] += float(m.get("debe", 0))

        if not cats:
            self.chart_view.setChart(QChart())
            return

        s = QBarSet("Gasto")
        c = []
        for k, v in cats.items():
            s.append(v)
            c.append(k)

        bs = QBarSeries()
        bs.append(s)
        ch = QChart()
        ch.addSeries(bs)
        ch.setTitle("Gastos por Categoría")
        ax = QBarCategoryAxis()
        ax.append(c)
        ch.addAxis(ax, Qt.AlignBottom)
        bs.attachAxis(ax)
        self.chart_view.setChart(ch)

    # ---------------------------------------------------------
    # PDF (sin cambios, separado del formato libro)
    # ---------------------------------------------------------
    def _exportar_pdf_estandar(self):
        self._render_pdf(azul=False)

    def _exportar_pdf_azul(self):
        self._render_pdf(azul=True)

    # ---------------------------------------------------------
    # EXPORTACIÓN EXCEL — FORMATO LIBRO TEST
    # ---------------------------------------------------------
    def _exportar_excel_general(self):
        self._exportar_excel_base("general")

    def _exportar_excel_categorias(self):
        self._exportar_excel_base("categoria")

    def _exportar_excel_cuentas(self):
        self._exportar_excel_base("cuenta")

    def _exportar_excel_base(self, modo):
        if not ExportadorExcelMensual:
            return

        nombres = {
            "general": "Cierre",
            "categoria": "PorCategorias",
            "cuenta": "PorCuentas"
        }
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Excel",
            f"{nombres[modo]}_{self.cbo_mes.currentText()}.xlsx",
            "Excel (*.xlsx)"
        )
        if not ruta:
            return

        prep = []
        saldo = 0

        # ORDEN OFICIAL
        for m in self.filtrados:
            d = float(m.get("debe", 0))
            h = float(m.get("haber", 0))
            saldo += h - d

            it = {
                "fecha": m.get("fecha"),
                "cuenta": m.get("cuenta"),
                "categoria": self._categoria_de_cuenta(m.get("cuenta")),
                "concepto": m.get("concepto"),
                "debe": d,
                "haber": h,
                "saldo": saldo,
                "banco": m.get("banco"),
                "documento": m.get("documento")
            }

            prep.append(it)

        per = f"{self.cbo_mes.currentText()} {self.cbo_año.currentText()}"

        try:
            if modo == "general":
                ExportadorExcelMensual.exportar_general(ruta, prep, per)

            elif modo == "categoria":
                g = defaultdict(list)
                for x in prep:
                    g[x["categoria"]].append(x)
                ExportadorExcelMensual.exportar_agrupado(
                    ruta, dict(sorted(g.items())), per, "Categoría"
                )

            elif modo == "cuenta":
                g = defaultdict(list)
                for x in prep:
                    g[f"{x['cuenta']} - {x['categoria']}"].append(x)
                ExportadorExcelMensual.exportar_agrupado(
                    ruta, dict(sorted(g.items())), per, "Cuenta"
                )

            QMessageBox.information(self, "OK", "Excel exportado correctamente.")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

