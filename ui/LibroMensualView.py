# -*- coding: utf-8 -*-
"""
LibroMensualView.py — SHILLONG CONTABILIDAD v3.7.2 PRO
---------------------------------------------------------
FIX: Restaurado menú "Exportar como..." con 3 opciones:
1. General
2. Por Categorías
3. Por Cuentas
---------------------------------------------------------
"""

from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QFrame,
    QFileDialog, QMessageBox, QHeaderView, QMenu
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QTextDocument
from PySide6.QtPrintSupport import QPrinter, QPrintPreviewDialog, QPrintDialog

import datetime
import json
import os
from collections import defaultdict

# Intentamos importar el motor de Excel
try:
    from models.ExportadorExcelMensual import ExportadorExcelMensual
except ImportError:
    ExportadorExcelMensual = None

class LibroMensualView(QWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.hoy = datetime.date.today()
        self.mes_actual = self.hoy.month
        self.año_actual = self.hoy.year
        
        self.bancos = self._cargar_bancos()
        self.reglas_cache = self._cargar_reglas()
        
        self._build_ui()
        self.actualizar()

    def _cargar_bancos(self):
        try:
            with open("data/bancos.json", "r", encoding="utf-8") as f:
                return ["Todos"] + [b["nombre"] for b in json.load(f).get("banks", [])]
        except:
            return ["Todos", "Caja"]

    def _cargar_reglas(self):
        try:
            if os.path.exists("data/reglas_conceptos.json"):
                with open("data/reglas_conceptos.json", "r", encoding="utf-8") as f:
                    return json.load(f)
        except: pass
        return {}

    # --- LÓGICA DE CATEGORÍAS (ROBUSTA) ---
    def _categoria_de_cuenta(self, cuenta):
        # 1. Limpieza del input
        cuenta_str = str(cuenta).split(" ")[0].strip()
        
        # 2. Búsqueda directa en reglas (Cache)
        if cuenta_str in self.reglas_cache:
            cat_original = self.reglas_cache[cuenta_str].get("categoria", "")
            cat_upper = cat_original.upper()
            
            # Mapeo de categorías en español a códigos internos en inglés
            mapeo = {
                "COMESTIBLES Y BEBIDAS": "FOOD", "ALIMENTACIÓN": "FOOD",
                "FARMACIA Y MATERIAL SANITARIO": "MEDICINE", "FARMACIA": "MEDICINE",
                "MEDICAMENTOS": "MEDICINE",
                "MATERIAL DE LIMPIEZA": "HYGIENE", "LIMPIEZA": "HYGIENE", 
                "LAVANDERÍA": "HYGIENE", "HIGIENE": "HYGIENE", "ASEO PERSONAL": "HYGIENE",
                "SUELDOS Y SALARIOS": "SALARY", "NOMINAS": "SALARY",
                "TELEFONÍA E INTERNET": "ONLINE", "INTERNET": "ONLINE", 
                "TELEFONO": "ONLINE",
                "TERAPIAS": "THERAPEUTIC", "DIETA": "DIET"
            }
            
            if cat_upper in mapeo: return mapeo[cat_upper]
            return cat_original

        # 3. Fallback por rangos numéricos
        try:
            c = int(cuenta_str)
            if 600000 <= c <= 609999: return "MEDICINE"
            if 603000 <= c <= 603999: return "FOOD"
            if 602400 <= c <= 602499: return "HYGIENE"
            if 620401 <= c <= 620499: return "HYGIENE"
            if 640000 <= c <= 649999 or (750000 <= c <= 759999): return "SALARY"
            if 629200 <= c <= 629299: return "ONLINE"
        except: 
            pass
            
        return "OTROS"

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # HEADER
        h_layout = QHBoxLayout()
        lbl_titulo = QLabel("📖 Libro Diario Mensual")
        lbl_titulo.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e3a8a;")
        h_layout.addWidget(lbl_titulo)
        h_layout.addStretch()

        btn_preview = QPushButton("📄 Vista Previa")
        btn_preview.clicked.connect(self.vista_previa)
        
        btn_print = QPushButton("🖨️ Imprimir")
        btn_print.clicked.connect(self.imprimir)

        # --- BOTÓN RESTAURADO: MENÚ DESPLEGABLE ---
        self.btn_exportar_menu = QPushButton("📤 Exportar como… ▼")
        self.btn_exportar_menu.setStyleSheet("""
            QPushButton {
                background-color: #16a34a; color: white; font-weight: bold;
                padding: 6px 15px; border-radius: 6px;
            }
            QPushButton:hover { background-color: #15803d; }
            QPushButton::menu-indicator { image: none; }
        """)
        
        # Menú
        self.menu_exportar = QMenu(self)
        self.menu_exportar.addAction("📊 Excel Detallado (General)", self._exportar_excel_general)
        self.menu_exportar.addSeparator()
        self.menu_exportar.addAction("📂 Excel por Categorías", self._exportar_excel_categorias)
        self.menu_exportar.addAction("🔢 Excel por Cuentas", self._exportar_excel_cuentas)
        
        # Asignar menú al botón (o usar clic para mostrarlo)
        self.btn_exportar_menu.setMenu(self.menu_exportar)

        for b in [btn_preview, btn_print, self.btn_exportar_menu]:
            b.setCursor(Qt.PointingHandCursor)
            b.setMinimumHeight(35)
            if not b.styleSheet():
                b.setStyleSheet("padding: 5px 15px; border-radius: 6px; background: #f1f5f9; border: 1px solid #cbd5e1;")
            h_layout.addWidget(b)

        layout.addLayout(h_layout)

        # FILTROS
        filtros = QFrame()
        filtros.setStyleSheet("background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px;")
        f_layout = QHBoxLayout(filtros)
        f_layout.setContentsMargins(10, 10, 10, 10)
        
        self.cbo_mes = QComboBox()
        self.cbo_mes.addItems(["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"])
        self.cbo_mes.setCurrentIndex(self.mes_actual - 1)
        
        self.cbo_año = QComboBox()
        self.cbo_año.addItems([str(x) for x in range(2020, 2036)])
        self.cbo_año.setCurrentText(str(self.año_actual))
        
        self.cbo_banco = QComboBox()
        self.cbo_banco.addItems(self.bancos)

        btn_ver = QPushButton("🔄 Actualizar")
        btn_ver.setStyleSheet("background:#3b82f6; color:white; font-weight:bold; padding:5px 15px; border-radius:4px;")
        btn_ver.clicked.connect(self.actualizar)

        f_layout.addWidget(QLabel("Mes:"))
        f_layout.addWidget(self.cbo_mes)
        f_layout.addSpacing(15)
        f_layout.addWidget(QLabel("Año:"))
        f_layout.addWidget(self.cbo_año)
        f_layout.addSpacing(15)
        f_layout.addWidget(QLabel("Banco:"))
        f_layout.addWidget(self.cbo_banco)
        f_layout.addSpacing(15)
        f_layout.addWidget(btn_ver)
        f_layout.addStretch()
        layout.addWidget(filtros)

        # CARDS
        cards = QHBoxLayout()
        self.card_gasto = self._crear_card("Total Gastos", "#ef4444")
        self.card_ingreso = self._crear_card("Total Ingresos", "#10b981")
        self.card_saldo = self._crear_card("Saldo del Mes", "#3b82f6")
        cards.addWidget(self.card_gasto)
        cards.addWidget(self.card_ingreso)
        cards.addWidget(self.card_saldo)
        layout.addLayout(cards)

        # TABLA
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(11)
        self.tabla.setHorizontalHeaderLabels([
            "Fecha", "Doc", "Concepto", "Cuenta", "Nombre", 
            "Debe", "Haber", "Saldo", "Banco", "Estado", "Categoría"
        ])
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setStyleSheet("QHeaderView::section { background-color: #f1f5f9; font-weight: bold; border: none; padding: 6px; }")
        layout.addWidget(self.tabla)

    def _crear_card(self, titulo, color):
        card = QFrame()
        card.setStyleSheet(f"background: white; border: 1px solid #e2e8f0; border-radius: 10px; border-left: 5px solid {color};")
        card.setMinimumHeight(80)
        l = QVBoxLayout(card)
        l.addWidget(QLabel(titulo))
        lbl_val = QLabel("0.00")
        lbl_val.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {color};")
        lbl_val.setObjectName("val")
        l.addWidget(lbl_val)
        return card

    def _update_card(self, card, valor):
        lbl = card.findChild(QLabel, "val")
        if lbl: lbl.setText(f"{valor:,.2f}")

    def actualizar(self):
        mes = self.cbo_mes.currentIndex() + 1
        año = int(self.cbo_año.currentText())
        banco_filtro = self.cbo_banco.currentText()
        
        movs = self.data.movimientos_por_mes(mes, año)
        
        self.tabla.setRowCount(0)
        saldo_acum = 0
        total_debe = 0
        total_haber = 0
        
        for m in movs:
            if banco_filtro != "Todos" and m.get("banco") != banco_filtro:
                continue
                
            row = self.tabla.rowCount()
            self.tabla.insertRow(row)
            
            try: debe = float(m.get("debe", 0))
            except: debe = 0.0
            try: haber = float(m.get("haber", 0))
            except: haber = 0.0
            
            total_debe += debe
            total_haber += haber
            saldo_acum += haber - debe
            
            cat = self._categoria_de_cuenta(m.get("cuenta"))
            nombre_cuenta = self.data.obtener_nombre_cuenta(m.get("cuenta"))

            items = [
                m.get("fecha", ""), m.get("documento", ""), m.get("concepto", ""),
                str(m.get("cuenta", "")), nombre_cuenta,
                f"{debe:,.2f}", f"{haber:,.2f}", f"{saldo_acum:,.2f}",
                m.get("banco", ""), m.get("estado", ""), cat
            ]

            for c, val in enumerate(items):
                it = QTableWidgetItem(str(val))
                if c in [5,6,7]: 
                    it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    if c == 7: it.setFont(QFont("Arial", 9, QFont.Bold))
                
                if c == 10:
                    if val == "OTROS": it.setForeground(QColor("#94a3b8"))
                    else: it.setForeground(QColor("#16a34a"))
                    it.setFont(QFont("Arial", 9, QFont.Bold))

                self.tabla.setItem(row, c, it)

        self._update_card(self.card_gasto, total_debe)
        self._update_card(self.card_ingreso, total_haber)
        self._update_card(self.card_saldo, total_haber - total_debe)

    # ============================================================
    # MÉTODOS DE EXPORTACIÓN RESTAURADOS
    # ============================================================
    def _exportar_excel_general(self):
        self._exportar_excel_base("general")

    def _exportar_excel_categorias(self):
        self._exportar_excel_base("categoria")

    def _exportar_excel_cuentas(self):
        self._exportar_excel_base("cuenta")

    def _exportar_excel_base(self, modo):
        """Método centralizado para exportar los 3 tipos de reportes."""
        if ExportadorExcelMensual is None:
            QMessageBox.critical(self, "Error", "Falta el módulo ExportadorExcelMensual.")
            return

        # Pedir ruta
        nombres = {
            "general": f"Libro_{self.cbo_mes.currentText()}.xlsx",
            "categoria": f"Resumen_Categorias_{self.cbo_mes.currentText()}.xlsx",
            "cuenta": f"Resumen_Cuentas_{self.cbo_mes.currentText()}.xlsx"
        }
        
        ruta, _ = QFileDialog.getSaveFileName(self, "Exportar Excel", nombres[modo], "Excel (*.xlsx)")
        if not ruta: return

        # Recopilar datos filtrados
        mes = self.cbo_mes.currentIndex() + 1
        año = int(self.cbo_año.currentText())
        banco_filtro = self.cbo_banco.currentText()
        
        movs_raw = self.data.movimientos_por_mes(mes, año)
        datos_prep = []
        saldo = 0
        
        for m in movs_raw:
            if banco_filtro != "Todos" and m.get("banco") != banco_filtro: continue
            
            d = float(m.get("debe", 0))
            h = float(m.get("haber", 0))
            saldo += h - d
            
            item = m.copy()
            item["saldo"] = saldo
            item["categoria"] = self._categoria_de_cuenta(m.get("cuenta"))
            item["nombre_cuenta"] = self.data.obtener_nombre_cuenta(m.get("cuenta"))
            datos_prep.append(item)

        try:
            periodo = f"{self.cbo_mes.currentText()} {año}"
            
            if modo == "general":
                ExportadorExcelMensual.exportar_general(ruta, datos_prep, periodo)
                
            elif modo == "categoria":
                # Agrupar por categoría
                grupos = defaultdict(list)
                for x in datos_prep: grupos[x["categoria"]].append(x)
                # Ordenar por nombre de categoría
                grupos_ord = dict(sorted(grupos.items()))
                ExportadorExcelMensual.exportar_agrupado(ruta, grupos_ord, periodo, "Categoría")
                
            elif modo == "cuenta":
                # Agrupar por Cuenta
                grupos = defaultdict(list)
                for x in datos_prep: 
                    clave = f"{x['cuenta']} - {x['nombre_cuenta']}"
                    grupos[clave].append(x)
                # Ordenar por número de cuenta
                grupos_ord = dict(sorted(grupos.items()))
                ExportadorExcelMensual.exportar_agrupado(ruta, grupos_ord, periodo, "Cuenta")

            QMessageBox.information(self, "Éxito", f"Reporte '{modo}' generado correctamente.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Fallo al exportar: {e}")

    # ============================================================
    # IMPRESIÓN Y PDF
    # ============================================================
    def _generar_html(self):
        mes = self.cbo_mes.currentText()
        año = self.cbo_año.currentText()
        html = f"<html><head><style>body{{font-family:Arial;}} table{{width:100%;border-collapse:collapse;}} th{{background:#eee;}} td,th{{border:1px solid #ccc;padding:5px;}} .num{{text-align:right;}}</style></head><body><h1>Libro {mes} {año}</h1><table><tr><th>Fecha</th><th>Concepto</th><th>Cuenta</th><th>Debe</th><th>Haber</th></tr>"
        for r in range(self.tabla.rowCount()):
            html += f"<tr><td>{self.tabla.item(r,0).text()}</td><td>{self.tabla.item(r,2).text()}</td><td>{self.tabla.item(r,3).text()}</td><td class='num'>{self.tabla.item(r,5).text()}</td><td class='num'>{self.tabla.item(r,6).text()}</td></tr>"
        html += "</table></body></html>"
        return html

    def vista_previa(self):
        printer = QPrinter(QPrinter.HighResolution)
        preview = QPrintPreviewDialog(printer, self)
        preview.paintRequested.connect(lambda p: QTextDocument().setHtml(self._generar_html()) or QTextDocument().print_(p))
        preview.exec()

    def imprimir(self):
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec():
            doc = QTextDocument()
            doc.setHtml(self._generar_html())
            doc.print_(printer)