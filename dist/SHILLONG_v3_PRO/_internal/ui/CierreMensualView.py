# -*- coding: utf-8 -*-
"""
CierreMensualView — SHILLONG CONTABILIDAD v3.6 PRO
Versión Premium con:
- KPIs modernas
- Gráficos
- Asientos de cierre
- Anomalías
- Buscador
- Exportador Excel
- PDF estándar
- PDF Azul Oficial
- Libro Diario Mensual
- EXCEL por categorías y por cuentas
- Botón azul SHILLONG con menú "Exportar como..."
"""

import datetime
import json
import csv
from collections import defaultdict

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QComboBox, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QLineEdit, QFileDialog,
    QMessageBox, QFrame, QTextEdit, QMenu
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPainter, QBrush, QPen
from PySide6.QtPrintSupport import QPrinter, QPrintPreviewDialog, QPrintDialog
from PySide6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QLineSeries, QValueAxis, QBarCategoryAxis

# Importamos el nuevo exportador basado en openpyxl
try:
    from models.ExportadorExcelMensual import ExportadorExcelMensual
except ImportError:
    ExportadorExcelMensual = None

class CierreMensualView(QWidget):

    COLORES = {
        "FOOD": "#fef3c7", "MEDICINE": "#ffe4e6", "HYGIENE": "#e0f2fe",
        "SALARY": "#ede9fe", "ONLINE": "#cffafe", "THERAPEUTIC": "#fae8ff",
        "DIET": "#dcfce7", "OTROS": "#ffffff"
    }

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.hoy = datetime.date.today()
        self.mes_actual = self.hoy.month
        self.año_actual = self.hoy.year
        self.bancos = self._cargar_bancos()
        self.cuentas = self._cargar_cuentas()
        self._build_ui()
        self.actualizar()

    # ============================================================
    # CARGA DE BANCOS Y CUENTAS
    # ============================================================
    def _cargar_bancos(self):
        try:
            with open("data/bancos.json", "r", encoding="utf-8") as f:
                return ["Todos"] + [b["nombre"] for b in json.load(f).get("banks", [])]
        except:
            return ["Todos", "Caja"]

    def _cargar_cuentas(self):
        cuentas = ["Todas"]
        try:
            with open("data/plan_contable_v3.json", "r", encoding="utf-8") as f:
                plan = json.load(f)
                cuentas.extend([f"{k} – {v['nombre']}" for k, v in plan.items()])
        except:
            pass
        return cuentas

    def _categoria_de_cuenta(self, cuenta):
        try:
            with open("data/reglas_conceptos.json", "r", encoding="utf-8") as f:
                reglas = json.load(f)
        except:
            reglas = {}
        
        cuenta_str = str(cuenta).strip()
        if cuenta_str in reglas:
            cat = reglas[cuenta_str].get("categoria", "").upper()
            mapeo = {
                "COMESTIBLES Y BEBIDAS": "FOOD", "FARMACIA Y MATERIAL SANITARIO": "MEDICINE",
                "MATERIAL DE LIMPIEZA": "HYGIENE", "LAVANDERÍA": "HYGIENE", "ASEO PERSONAL": "HYGIENE",
                "SUELDOS Y SALARIOS": "SALARY", "TELEFONÍA E INTERNET": "ONLINE"
            }
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
        except:
            pass
        return "OTROS"

    # ============================================================
    # INTERFAZ PRINCIPAL
    # ============================================================
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        titulo = QLabel("📆 CIERRE MENSUAL — SHILLONG CONTABILIDAD v3.6 PRO")
        titulo.setStyleSheet("font-size: 28px; font-weight: 800; color: #0f172a;")
        layout.addWidget(titulo)

        # -------------------------
        # BOTONES (MOVIDO A LA PARTE SUPERIOR)
        # -------------------------
        btn_layout = QHBoxLayout()
        # Si prefieres que estén a la izquierda, quita la siguiente línea (addStretch)
        btn_layout.addStretch()

        self.btn_preview = QPushButton("Vista previa PDF")
        self.btn_print = QPushButton("Imprimir PDF")
        self.btn_export = QPushButton("Exportar Excel")
        self.btn_asientos = QPushButton("Generar Asientos")
        self.btn_guardar = QPushButton("Guardar Cierre")
        self.btn_bloquear = QPushButton("Bloquear Mes")
        self.btn_desbloquear = QPushButton("Desbloquear Mes")

        for btn in [self.btn_preview, self.btn_print, self.btn_export, self.btn_asientos,
                    self.btn_guardar, self.btn_bloquear, self.btn_desbloquear]:
            btn_layout.addWidget(btn)

        # -------------------------
        # BOTÓN EXPANDIDO "📤 Exportar como… ▼"
        # -------------------------
        self.btn_exportar_menu = QPushButton("📤 Exportar como… ▼")
        self.btn_exportar_menu.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                padding: 10px 18px;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1d4ed8; }
        """)

        # Menú desplegable
        self.menu_exportar = QMenu(self)

        # ACCIONES DEL MENÚ
        self.menu_exportar.addAction("PDF estándar", self._exportar_pdf_estandar)
        self.menu_exportar.addAction("PDF Azul (oficial)", self._exportar_pdf_azul)
        self.menu_exportar.addAction("Excel general", self._exportar_excel_general)
        self.menu_exportar.addAction("Excel por categorías", self._exportar_excel_categorias)
        self.menu_exportar.addAction("Excel por cuentas", self._exportar_excel_cuentas)
        self.menu_exportar.addAction("Libro diario mensual", self._exportar_excel_libro_mensual)

        # Mostrar menú al pulsar
        self.btn_exportar_menu.clicked.connect(
            lambda: self.menu_exportar.exec(self.btn_exportar_menu.mapToGlobal(self.btn_exportar_menu.rect().bottomLeft()))
        )

        btn_layout.addWidget(self.btn_exportar_menu)
        layout.addLayout(btn_layout)

        # -------------------------
        # FILTROS
        # -------------------------
        filtros = QGridLayout()
        filtros.addWidget(QLabel("Mes:"), 0, 0)
        self.cbo_mes = QComboBox()
        self.cbo_mes.addItems([
            "Enero","Febrero","Marzo","Abril","Mayo","Junio",
            "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
        ])
        self.cbo_mes.setCurrentIndex(self.mes_actual - 1)
        filtros.addWidget(self.cbo_mes, 0, 1)

        filtros.addWidget(QLabel("Año:"), 0, 2)
        self.cbo_año = QComboBox()
        for a in range(2020, 2036):
            self.cbo_año.addItem(str(a))
        self.cbo_año.setCurrentText(str(self.año_actual))
        filtros.addWidget(self.cbo_año, 0, 3)

        filtros.addWidget(QLabel("Banco:"), 0, 4)
        self.cbo_banco = QComboBox()
        self.cbo_banco.addItems(self.bancos)
        filtros.addWidget(self.cbo_banco, 0, 5)

        filtros.addWidget(QLabel("Cuenta:"), 1, 0)
        self.cbo_cuenta = QComboBox()
        self.cbo_cuenta.addItems(self.cuentas)
        filtros.addWidget(self.cbo_cuenta, 1, 1, 1, 2)

        filtros.addWidget(QLabel("Categoría:"), 1, 3)
        self.cbo_categoria = QComboBox()
        self.cbo_categoria.addItems(["Todas", "FOOD", "MEDICINE", "HYGIENE", "SALARY", "ONLINE", "THERAPEUTIC", "DIET", "OTROS"])
        filtros.addWidget(self.cbo_categoria, 1, 4)

        filtros.addWidget(QLabel("Tipo:"), 1, 5)
        self.cbo_tipo = QComboBox()
        self.cbo_tipo.addItems(["Todos", "Solo gastos", "Solo ingresos"])
        filtros.addWidget(self.cbo_tipo, 1, 6)

        for w in [self.cbo_mes, self.cbo_año, self.cbo_banco, self.cbo_cuenta, self.cbo_categoria, self.cbo_tipo]:
            w.currentIndexChanged.connect(self.actualizar)

        layout.addLayout(filtros)

        # -------------------------
        # KPIs
        # -------------------------
        kpi_layout = QHBoxLayout()
        self.card_gasto = self._crear_kpi_card("Total Gastos", "0,00", "#dc2626")
        self.card_ingreso = self._crear_kpi_card("Total Ingresos", "0,00", "#16a34a")
        self.card_saldo = self._crear_kpi_card("Saldo Final", "0,00", "#2563eb")
        kpi_layout.addWidget(self.card_gasto)
        kpi_layout.addWidget(self.card_ingreso)
        kpi_layout.addWidget(self.card_saldo)
        layout.addLayout(kpi_layout)

        # -------------------------
        # BUSCADOR
        # -------------------------
        self.buscador = QLineEdit()
        self.buscador.setPlaceholderText("Buscar en cierre mensual...")
        self.buscador.textChanged.connect(self.actualizar)
        layout.addWidget(self.buscador)

        # -------------------------
        # TABLA
        # -------------------------
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(11)
        self.tabla.setHorizontalHeaderLabels([
            "Fecha","Documento","Concepto","Cuenta","Nombre Cuenta",
            "Debe","Haber","Banco","Estado","Saldo Acum.","Categoría"
        ])
        layout.addWidget(self.tabla)

        # -------------------------
        # GRÁFICOS
        # -------------------------
        graficos = QHBoxLayout()
        self.chart_categoria = QChartView()
        self.chart_evolucion = QChartView()
        graficos.addWidget(self.chart_categoria)
        graficos.addWidget(self.chart_evolucion)
        layout.addLayout(graficos)

        # -------------------------
        # ANOMALÍAS
        # -------------------------
        self.anomalias = QTextEdit()
        self.anomalias.setMaximumHeight(120)
        self.anomalias.setReadOnly(True)
        layout.addWidget(QLabel("Anomalías detectadas:"))
        layout.addWidget(self.anomalias)

        # (La sección de botones original que estaba aquí ha sido movida arriba)

        # Conectar botones originales
        self.btn_preview.clicked.connect(self.vista_previa)
        self.btn_print.clicked.connect(self.imprimir)
        self.btn_export.clicked.connect(self.exportar_excel)
        self.btn_asientos.clicked.connect(self._generar_asientos_cierre)
        self.btn_guardar.clicked.connect(self._guardar_cierre)
        self.btn_bloquear.clicked.connect(self._bloquear_mes)
        self.btn_desbloquear.clicked.connect(self._desbloquear_mes)

    # ============================================================
    # LÓGICA DE NEGOCIO Y AYUDAS
    # ============================================================

    def _crear_kpi_card(self, titulo, valor, color):
        card = QFrame()
        card.setStyleSheet("background:#fff; border:1px solid #d1d5db; border-radius:12px; padding:20px;")
        card.setMinimumHeight(140)
        v = QVBoxLayout(card)
        lbl_tit = QLabel(titulo)
        lbl_tit.setStyleSheet("font-size:16px; font-weight:bold; color:#475569;")
        lbl_val = QLabel(valor)
        lbl_val.setStyleSheet(f"font-size:36px; font-weight:800; color:{color};")
        v.addWidget(lbl_tit)
        v.addWidget(lbl_val)
        card.valor = lbl_val
        return card

    def _fmt(self, n):
        return f"{float(n):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def _aplicar_filtros(self, movimientos):
        mes = self.cbo_mes.currentIndex() + 1
        año = int(self.cbo_año.currentText())
        banco = self.cbo_banco.currentText()
        cuenta = self.cbo_cuenta.currentText().split(" – ")[0] if " – " in self.cbo_cuenta.currentText() else None
        categoria = self.cbo_categoria.currentText()
        tipo = self.cbo_tipo.currentText()
        texto = self.buscador.text().lower()

        filtrados = []
        for m in movimientos:
            try:
                # Asumimos formato dd/mm/yyyy
                parts = m.get("fecha", "").split("/")
                if len(parts) == 3:
                    m_mes, m_año = int(parts[1]), int(parts[2])
                else:
                    continue # Formato fecha invalido

                if m_mes != mes or m_año != año:
                    continue
            except:
                continue

            if banco != "Todos" and m.get("banco", "") != banco:
                continue
            if cuenta and str(m.get("cuenta", "")) != cuenta:
                continue
            if categoria != "Todas" and self._categoria_de_cuenta(m.get("cuenta")) != categoria:
                continue
            if tipo == "Solo gastos" and float(m.get("debe", 0)) == 0:
                continue
            if tipo == "Solo ingresos" and float(m.get("haber", 0)) == 0:
                continue

            if texto:
                valores = [
                    str(v).lower() for v in m.values()
                ] + [self.data.obtener_nombre_cuenta(m.get("cuenta", "")).lower()]
                if not any(texto in v for v in valores):
                    continue

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

        self.card_gasto.valor.setText(self._fmt(gasto))
        self.card_ingreso.valor.setText(self._fmt(ingreso))
        self.card_saldo.valor.setText(self._fmt(saldo))

        color = "#16a34a" if saldo >= 0 else "#dc2626"
        self.card_saldo.valor.setStyleSheet(f"font-size:36px; font-weight:800; color:{color};")

        self.tabla.setRowCount(0)
        saldo_acum = 0
        for m in filtrados:
            debe = float(m.get("debe", 0))
            haber = float(m.get("haber", 0))
            saldo_acum += haber - debe
            cat = self._categoria_de_cuenta(m.get("cuenta"))
            color_row = QColor(self.COLORES.get(cat, "#ffffff"))

            fila = [
                m.get("fecha", ""),
                m.get("documento", ""),
                m.get("concepto", ""),
                str(m.get("cuenta", "")),
                self.data.obtener_nombre_cuenta(m.get("cuenta")),
                self._fmt(debe),
                self._fmt(haber),
                m.get("banco", ""),
                m.get("estado", ""),
                self._fmt(saldo_acum),
                cat
            ]

            self.tabla.insertRow(self.tabla.rowCount())
            for col, valor in enumerate(fila):
                item = QTableWidgetItem(str(valor))
                item.setBackground(color_row)
                if col == 5 and debe > 0:
                    item.setForeground(QColor("#dc2626"))
                if col == 6 and haber > 0:
                    item.setForeground(QColor("#16a34a"))
                self.tabla.setItem(self.tabla.rowCount()-1, col, item)

        self._graficos(filtrados)
        self._detectar_anomalias(filtrados)

    # ============================================================
    # GRÁFICOS
    # ============================================================
    def _graficos(self, movimientos):
        # Gráfico por categoría
        cats = ["FOOD","MEDICINE","HYGIENE","SALARY","ONLINE","THERAPEUTIC","DIET","OTROS"]
        valores = [sum(float(m.get("debe", 0)) for m in movimientos if self._categoria_de_cuenta(m.get("cuenta")) == c) for c in cats]
        set1 = QBarSet("Gastos")
        set1.append(valores)
        series = QBarSeries()
        series.append(set1)
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Gastos por categoría")
        axis_x = QBarCategoryAxis()
        axis_x.append(cats)
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        axis_y = QValueAxis()
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        self.chart_categoria.setChart(chart)

        # Evolución 3 meses
        series_line = QLineSeries()
        series_line.setName("Saldo")
        for offset in range(-2, 1):
            m = self.mes_actual + offset
            a = self.año_actual
            if m <= 0:
                m, a = 12, a-1
            if m > 12:
                m, a = 1, a+1
            
            # Nota: Esto requiere que data.movimientos_por_mes exista y funcione
            try:
                movs = self.data.movimientos_por_mes(m, a)
                saldo = sum(float(x.get("haber", 0)) - float(x.get("debe", 0)) for x in movs)
                series_line.append(offset, saldo)
            except:
                series_line.append(offset, 0)
                
        chart2 = QChart()
        chart2.addSeries(series_line)
        chart2.setTitle("Evolución Saldo (3 meses)")
        self.chart_evolucion.setChart(chart2)

    # ============================================================
    # ANOMALÍAS
    # ============================================================
    def _detectar_anomalias(self, movimientos):
        anomalias = []
        docs = [m.get("documento", "") for m in movimientos]
        duplicados = {x for x in docs if docs.count(x) > 1 and x}
        if duplicados:
            anomalias.append(f"Documentos duplicados: {', '.join(duplicados)}")

        for m in movimientos:
            if float(m.get("debe", 0)) == 0 and float(m.get("haber", 0)) == 0:
                anomalias.append(f"Movimiento sin importe: {m.get('documento')}")
            if m.get("estado", "").lower() == "pendiente":
                anomalias.append(f"Movimiento pendiente: {m.get('documento')}")

        self.anomalias.setText("\n".join(anomalias) if anomalias else "Ninguna anomalía detectada")


    # ============================================================
    # EXPORTAR EXCEL GENERAL (COMPATIBILIDAD)
    # ============================================================
    def exportar_excel(self):
        """Exporta el Excel General usando el nuevo motor"""
        archivo, _ = QFileDialog.getSaveFileName(
            self, "Exportar Excel", "Movimientos.xlsx", "Excel (*.xlsx)"
        )
        if not archivo:
            return

        if ExportadorExcelMensual is None:
            QMessageBox.critical(self, "Error", "No se encontró el módulo models.ExportadorExcelMensual o falta openpyxl")
            return

        mes = self.cbo_mes.currentIndex() + 1
        año = int(self.cbo_año.currentText())
        movimientos = self._aplicar_filtros(
            self.data.movimientos_por_mes(mes, año)
        )
        
        # Preparamos datos con saldo acumulado
        datos_prep = []
        saldo = 0
        for m in movimientos:
            debe = float(m.get("debe", 0))
            haber = float(m.get("haber", 0))
            saldo += haber - debe
            # Añadimos la categoria para el reporte
            m_copy = m.copy()
            m_copy["categoria"] = self._categoria_de_cuenta(m.get("cuenta"))
            m_copy["saldo"] = saldo
            datos_prep.append(m_copy)

        try:
            ExportadorExcelMensual.exportar_general(archivo, datos_prep, f"{self.cbo_mes.currentText()} {año}")
            QMessageBox.information(self, "OK", "Excel generado correctamente con formato profesional.")
        except Exception as e:
            QMessageBox.critical(self, "Error exportando Excel", str(e))
    

    # ============================================================
    # EXPORTACIONES DEL MENÚ (AHORA IMPLEMENTADAS CON OPENPYXL)
    # ============================================================
    def _exportar_pdf_estandar(self):
        self._exportar_pdf()

    def _exportar_pdf_azul(self):
        self._exportar_pdf_azul_oficial()

    def _exportar_excel_general(self):
        self.exportar_excel()

    def _exportar_excel_categorias(self):
        """Genera Excel Agrupado por Categoría"""
        archivo, _ = QFileDialog.getSaveFileName(
            self, "Exportar por Categorías", "Resumen_Categorias.xlsx", "Excel (*.xlsx)"
        )
        if not archivo: return

        if ExportadorExcelMensual is None: return

        mes = self.cbo_mes.currentIndex() + 1
        año = int(self.cbo_año.currentText())
        movimientos = self._aplicar_filtros(self.data.movimientos_por_mes(mes, año))
        
        # Agrupar
        grupos = defaultdict(list)
        for m in movimientos:
            cat = self._categoria_de_cuenta(m.get("cuenta"))
            grupos[cat].append(m)

        try:
            ExportadorExcelMensual.exportar_agrupado(archivo, grupos, f"{self.cbo_mes.currentText()} {año}", "Categoría")
            QMessageBox.information(self, "Éxito", "Excel por categorías generado.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _exportar_excel_cuentas(self):
        """Genera Excel Agrupado por Cuentas"""
        archivo, _ = QFileDialog.getSaveFileName(
            self, "Exportar por Cuentas", "Resumen_Cuentas.xlsx", "Excel (*.xlsx)"
        )
        if not archivo: return

        if ExportadorExcelMensual is None: return

        mes = self.cbo_mes.currentIndex() + 1
        año = int(self.cbo_año.currentText())
        movimientos = self._aplicar_filtros(self.data.movimientos_por_mes(mes, año))
        
        # Agrupar
        grupos = defaultdict(list)
        for m in movimientos:
            cta = str(m.get("cuenta", ""))
            nombre = self.data.obtener_nombre_cuenta(cta)
            label = f"{cta} - {nombre}"
            grupos[label].append(m)
        
        # Ordenar claves
        grupos_ord = dict(sorted(grupos.items()))

        try:
            ExportadorExcelMensual.exportar_agrupado(archivo, grupos_ord, f"{self.cbo_mes.currentText()} {año}", "Cuenta")
            QMessageBox.information(self, "Éxito", "Excel por cuentas generado.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _exportar_excel_libro_mensual(self):
        # El libro mensual es básicamente el general
        self.exportar_excel()

    def _bloquear_mes(self):
        QMessageBox.information(self, "Bloqueo", f"Mes de {self.cbo_mes.currentText()} bloqueado.")

    def _desbloquear_mes(self):
        QMessageBox.information(self, "Desbloqueo", f"Mes de {self.cbo_mes.currentText()} desbloqueado.")

    # ============================================================
    # PDF ESTÁNDAR
    # ============================================================
    def _exportar_pdf(self):
        archivo, _ = QFileDialog.getSaveFileName(
            self, "Guardar PDF", "", "Archivos PDF (*.pdf)"
        )
        if not archivo:
            return

        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(archivo)

        painter = QPainter()
        if not painter.begin(printer):
            QMessageBox.critical(self, "Error", "No se pudo iniciar la impresión en PDF.")
            return

        painter.setFont(QFont("Arial", 11))

        y = 100

        # Título
        painter.setFont(QFont("Arial", 18, QFont.Bold))
        painter.drawText(100, y, "Cierre Mensual — SHILLONG v3.6 PRO")
        y += 60

        # KPIs
        painter.setFont(QFont("Arial", 13))
        painter.drawText(100, y, f"Ingresos: {self.card_ingreso.valor.text()}")
        y += 30
        painter.drawText(100, y, f"Gastos:  {self.card_gasto.valor.text()}")
        y += 30
        painter.drawText(100, y, f"Saldo Final: {self.card_saldo.valor.text()}")
        y += 50

        # Tabla
        painter.setFont(QFont("Arial", 10))
        for row in range(self.tabla.rowCount()):
            linea = []
            for col in range(self.tabla.columnCount()):
                item = self.tabla.item(row, col)
                linea.append(item.text() if item else "")
            
            # Simple prevención de desborde de página
            if y > printer.height() - 100:
                printer.newPage()
                y = 100
                
            painter.drawText(100, y, " | ".join(linea))
            y += 20

        painter.end()

    # ============================================================
    # PDF AZUL OFICIAL (nuevo)
    # ============================================================
    def _exportar_pdf_azul_oficial(self):
        archivo, _ = QFileDialog.getSaveFileName(
            self, "Guardar PDF Azul Oficial", "", "Archivos PDF (*.pdf)"
        )
        if not archivo:
            return

        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(archivo)
        printer.setPageMargins(20, 20, 20, 20, QPrinter.Millimeter)

        painter = QPainter()
        if not painter.begin(printer):
            QMessageBox.critical(self, "Error", "No se pudo iniciar la impresión en PDF.")
            return

        painter.setFont(QFont("Arial", 14))

        y = 80

        # Encabezado azul
        painter.setBrush(QColor("#1e3a8a"))
        painter.setPen(QPen(QColor("#1e3a8a")))
        painter.drawRect(0, y - 50, printer.width(), 50)
        painter.setPen(QColor("white"))
        painter.setFont(QFont("Arial", 20, QFont.Bold))
        painter.drawText(50, y - 15, "CIERRE MENSUAL — SHILLONG PRO")

        y += 20

        # Información del mes
        painter.setPen(Qt.black)
        painter.setFont(QFont("Arial", 12))
        painter.drawText(50, y, f"Mes: {self.cbo_mes.currentText()} {self.cbo_año.currentText()}")
        y += 30

        # Título de tabla
        painter.setPen(Qt.white)
        painter.setBrush(QColor("#1d4ed8"))
        painter.drawRect(0, y, printer.width(), 30)
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        painter.drawText(50, y + 20, "TABLA DE MOVIMIENTOS (OFICIAL)")
        y += 50

        # Cabecera azul de la tabla
        header_bg = QColor("#1e40af")
        painter.setBrush(header_bg)
        painter.setPen(Qt.white)
        painter.drawRect(0, y, printer.width(), 28)
        painter.drawText(50, y + 20, "Fecha")
        painter.drawText(150, y + 20, "Doc")
        painter.drawText(250, y + 20, "Concepto")
        painter.drawText(500, y + 20, "Cuenta")
        painter.drawText(620, y + 20, "Debe")
        painter.drawText(720, y + 20, "Haber")
        painter.drawText(820, y + 20, "Saldo")

        y += 40

        # Cuerpo de la tabla
        painter.setFont(QFont("Arial", 10))
        painter.setPen(Qt.black)

        movimientos = self._aplicar_filtros(self.data.movimientos_por_mes(
            self.cbo_mes.currentIndex() + 1,
            int(self.cbo_año.currentText())
        ))

        saldo = 0

        for m in movimientos:
            if y > printer.height() - 80:
                printer.newPage()
                y = 80
                # Redibujar cabecera en nueva página si se desea (opcional)

            fecha = m.get("fecha", "")
            doc = m.get("documento", "")
            conc = m.get("concepto", "")
            cta = str(m.get("cuenta", ""))
            debe = float(m.get("debe", 0))
            haber = float(m.get("haber", 0))
            saldo += haber - debe

            painter.drawText(50, y, fecha)
            painter.drawText(150, y, doc)
            painter.drawText(250, y, conc[:25])
            painter.drawText(500, y, cta)
            painter.drawText(620, y, f"{debe:,.2f}")
            painter.drawText(720, y, f"{haber:,.2f}")
            painter.drawText(820, y, f"{saldo:,.2f}")

            y += 25

        painter.end()

    # ============================================================
    # IMPRIMIR PDF DIRECTO (COMPATIBILIDAD)
    # ============================================================
    def imprimir(self):
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec():
            self._render_preview_pdf(printer)

    # ============================================================
    # VISTA PREVIA PDF (COMPATIBILIDAD)
    # ============================================================
    def vista_previa(self):
        printer = QPrinter(QPrinter.HighResolution)
        preview = QPrintPreviewDialog(printer, self)
        preview.paintRequested.connect(lambda p: self._render_preview_pdf(p))
        preview.exec()

    # ============================================================
    # RENDER DEL PDF ESTÁNDAR (USADO POR IMPRIMIR Y PREVIEW)
    # ============================================================
    def _render_preview_pdf(self, printer):
        painter = QPainter()
        if not painter.begin(printer):
             return
             
        painter.setFont(QFont("Arial", 12))
        y = 80

        # Título
        painter.setFont(QFont("Arial", 16, QFont.Bold))
        painter.drawText(50, y, "Cierre Mensual — SHILLONG PRO")
        y += 40

        # Cabecera
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.drawText(
            50, y,
            "Fecha        Doc            Concepto           Cuenta       Debe        Haber        Saldo"
        )
        y += 20

        painter.setFont(QFont("Arial", 9))

        movimientos = self._aplicar_filtros(
            self.data.movimientos_por_mes(
                self.cbo_mes.currentIndex() + 1,
                int(self.cbo_año.currentText())
            )
        )

        saldo = 0

        for m in movimientos:
            # Salto de página
            if y > printer.height() - 80:
                printer.newPage()
                y = 80

            fecha = m.get("fecha", "")
            doc = m.get("documento", "")
            conc = m.get("concepto", "")[:25]
            cta = str(m.get("cuenta", ""))
            debe = float(m.get("debe", 0))
            haber = float(m.get("haber", 0))
            saldo += haber - debe

            line = (
                f"{fecha}   {doc}   {conc:25s}   {cta}   "
                f"{debe:,.2f}   {haber:,.2f}   {saldo:,.2f}"
            )
            painter.drawText(50, y, line)
            y += 20
        
        painter.end()

    # ============================================================
    # GENERAR ASIENTOS DE CIERRE
    # ============================================================
    def _generar_asientos_cierre(self):
        """
        Genera los asientos automáticos de cierre:
        - Traslada gastos a Resultado del Ejercicio
        - Traslada ingresos a Resultado del Ejercicio
        - Cierra el Resultado del Ejercicio contra Capital
        """
        mes = self.cbo_mes.currentIndex() + 1
        año = int(self.cbo_año.currentText())
        movimientos = self._aplicar_filtros(self.data.movimientos_por_mes(mes, año))

        if not movimientos:
            QMessageBox.information(self, "Asientos", "No hay movimientos en este mes.")
            return

        # Calcular totales
        total_gastos = sum(float(m.get("debe", 0)) for m in movimientos if float(m.get("debe", 0)) > 0)
        total_ingresos = sum(float(m.get("haber", 0)) for m in movimientos if float(m.get("haber", 0)) > 0)
        resultado = total_ingresos - total_gastos

        fecha_cierre = f"31/{mes:02d}/{año}"

        # === 1. Asiento de gastos → Resultado ===
        if total_gastos > 0:
            self.data.agregar_movimiento(
                fecha=fecha_cierre,
                documento="CIERRE-GASTOS",
                concepto="Cierre de cuentas de gasto",
                cuenta="129000",  # Resultado del ejercicio (pérdidas)
                debe=0,
                haber=total_gastos,
                moneda="INR",
                banco="Caja",
                estado="pagado"
            )
            self.data.agregar_movimiento(
                fecha=fecha_cierre,
                documento="CIERRE-GASTOS",
                concepto="Cierre de cuentas de gasto",
                cuenta="600000",  # Grupo de gastos (ajustar si usas 6xxxxx)
                debe=total_gastos,
                haber=0,
                moneda="INR",
                banco="Caja",
                estado="pagado"
            )

        # === 2. Asiento de ingresos → Resultado ===
        if total_ingresos > 0:
            self.data.agregar_movimiento(
                fecha=fecha_cierre,
                documento="CIERRE-INGRESOS",
                concepto="Cierre de cuentas de ingreso",
                cuenta="129000",
                debe=total_ingresos,
                haber=0,
                moneda="INR",
                banco="Caja",
                estado="pagado"
            )
            self.data.agregar_movimiento(
                fecha=fecha_cierre,
                documento="CIERRE-INGRESOS",
                concepto="Cierre de cuentas de ingreso",
                cuenta="700000",  # Grupo de ingresos (ajustar si usas 7xxxxx)
                debe=0,
                haber=total_ingresos,
                moneda="INR",
                banco="Caja",
                estado="pagado"
            )

        # === 3. Cierre del Resultado del Ejercicio contra Capital ===
        if resultado != 0:
            cuenta_capital = "100000"  # Ajusta según tu plan contable
            concepto_res = "Beneficio" if resultado > 0 else "Pérdida"
            self.data.agregar_movimiento(
                fecha=fecha_cierre,
                documento="CIERRE-RESULTADO",
                concepto=f"{concepto_res} del ejercicio → Capital",
                cuenta="129000",
                debe=abs(resultado) if resultado < 0 else 0,
                haber=abs(resultado) if resultado > 0 else 0,
                moneda="INR",
                banco="Caja",
                estado="pagado"
            )
            self.data.agregar_movimiento(
                fecha=fecha_cierre,
                documento="CIERRE-RESULTADO",
                concepto=f"{concepto_res} del ejercicio → Capital",
                cuenta=cuenta_capital,
                debe=abs(resultado) if resultado > 0 else 0,
                haber=abs(resultado) if resultado < 0 else 0,
                moneda="INR",
                banco="Caja",
                estado="pagado"
            )

        QMessageBox.information(
            self,
            "Asientos generados",
            f"Se han creado los asientos de cierre del mes {self.cbo_mes.currentText()} {año}\n\n"
            f"• Gastos: {total_gastos:,.2f} INR\n"
            f"• Ingresos: {total_ingresos:,.2f} INR\n"
            f"• Resultado: {resultado:,.2f} INR {'(Beneficio)' if resultado > 0 else '(Pérdida)'}"
        )

        self.actualizar()  # Refresca la vista

    # ============================================================
    # GUARDAR CIERRE
    # ============================================================
    def _guardar_cierre(self):
        """
        Guarda un archivo JSON con el cierre del mes seleccionado
        (útil para auditoría y respaldo oficial)
        """
        mes = self.cbo_mes.currentText()
        año = self.cbo_año.currentText()
        nombre_default = f"Cierre_Mensual_{mes}_{año}.json"

        ruta, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Cierre Mensual",
            nombre_default,
            "Archivos JSON (*.json)"
        )
        if not ruta:
            return

        movimientos = self._aplicar_filtros(
            self.data.movimientos_por_mes(self.cbo_mes.currentIndex() + 1, int(año))
        )

        # Información del cierre
        total_gastos = sum(float(m.get("debe", 0)) for m in movimientos)
        total_ingresos = sum(float(m.get("haber", 0)) for m in movimientos)
        saldo_final = total_ingresos - total_gastos

        cierre_data = {
            "shillong_version": "3.6.0",
            "fecha_generacion": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
            "periodo": f"{mes} {año}",
            "total_ingresos": total_ingresos,
            "total_gastos": total_gastos,
            "resultado": saldo_final,
            "movimientos": movimientos
        }

        try:
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(cierre_data, f, indent=4, ensure_ascii=False)
            QMessageBox.information(
                self,
                "Cierre guardado",
                f"Cierre mensual guardado correctamente:\n{ruta}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar:\n{e}")