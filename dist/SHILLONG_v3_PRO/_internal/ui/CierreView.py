# -*- coding: utf-8 -*-
"""
CierreView.py — SHILLONG CONTABILIDAD v3.7.6 PRO
---------------------------------------------------------
Cierre Anual Blindado:
- Exportaciones Anuales completas (General, Categoría, Cuenta).
- Categorización Inteligente (AI).
- Tabla Resumen Mensual.
---------------------------------------------------------
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QPushButton, QTableWidget, QTableWidgetItem, QFrame, 
    QHeaderView, QMessageBox, QFileDialog, QMenu
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont

import datetime
from collections import defaultdict

# Intentamos importar el motor de exportación
try:
    from models.ExportadorExcelMensual import ExportadorExcelMensual
except ImportError:
    ExportadorExcelMensual = None

class CierreView(QWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.año_actual = datetime.date.today().year
        
        self.reglas_cache = self._cargar_reglas()
        
        self._build_ui()
        self.actualizar()

    def _cargar_reglas(self):
        import json, os
        try:
            if os.path.exists("data/reglas_conceptos.json"):
                with open("data/reglas_conceptos.json", "r", encoding="utf-8") as f:
                    return json.load(f)
        except (IOError, json.JSONDecodeError):
            pass
        return {}

    # --- CATEGORIZACIÓN INTELIGENTE (IGUAL QUE EN LIBRO MENSUAL) ---
    def _categoria_de_cuenta(self, cuenta):
        cuenta_str = str(cuenta).split(" ")[0].strip()
        
        # 1. Reglas aprendidas
        if cuenta_str in self.reglas_cache:
            cat = self.reglas_cache[cuenta_str].get("categoria", "").upper()
            mapeo = {
                "COMESTIBLES Y BEBIDAS": "FOOD", "ALIMENTACIÓN": "FOOD",
                "FARMACIA Y MATERIAL SANITARIO": "MEDICINE", "FARMACIA": "MEDICINE",
                "MEDICAMENTOS": "MEDICINE", "MATERIAL DE LIMPIEZA": "HYGIENE", 
                "LIMPIEZA": "HYGIENE", "LAVANDERÍA": "HYGIENE", "HIGIENE": "HYGIENE",
                "ASEO PERSONAL": "HYGIENE", "SUELDOS Y SALARIOS": "SALARY", 
                "NOMINAS": "SALARY", "TELEFONÍA E INTERNET": "ONLINE", 
                "INTERNET": "ONLINE", "TELEFONO": "ONLINE", 
                "TERAPIAS": "THERAPEUTIC", "DIETA": "DIET"
            }
            if cat in mapeo: return mapeo[cat]
            return cat

        # 2. Fallback numérico
        try:
            c = int(cuenta_str)
            if 600000 <= c <= 609999: return "MEDICINE"
            if 603000 <= c <= 603999: return "FOOD"
            if 602400 <= c <= 602499: return "HYGIENE"
            if 620401 <= c <= 620499: return "HYGIENE"
            if 640000 <= c <= 649999: return "SALARY"
            if 629200 <= c <= 629299: return "ONLINE"
        except (ValueError, TypeError):
            pass
        
        return "OTROS"

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # --- HEADER ---
        header = QHBoxLayout()
        lbl_titulo = QLabel("📅 Cierre Anual del Ejercicio")
        lbl_titulo.setStyleSheet("font-size: 28px; font-weight: 800; color: #1e293b;")
        header.addWidget(lbl_titulo)
        header.addStretch()
        
        # --- BOTÓN MENÚ DESPLEGABLE ---
        self.btn_exportar_menu = QPushButton("📊 Exportar Anual ▼")
        self.btn_exportar_menu.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; color: white; font-weight: bold; 
                padding: 10px 20px; border-radius: 8px; font-size: 14px;
            }
            QPushButton:hover { background-color: #1d4ed8; }
            QPushButton::menu-indicator { image: none; }
        """)
        
        self.menu_exportar = QMenu(self)
        self.menu_exportar.addAction("📈 Excel Evolutivo (Matriz Mensual)", self._exportar_evolutivo)
        self.menu_exportar.addSeparator()
        self.menu_exportar.addAction("📑 Excel Detallado (Todo el Año)", self._exportar_general_anual)
        self.menu_exportar.addAction("📂 Excel Anual por Categorías", self._exportar_categorias_anual)
        self.menu_exportar.addAction("🔢 Excel Anual por Cuentas", self._exportar_cuentas_anual)
        
        self.btn_exportar_menu.setMenu(self.menu_exportar)
        self.btn_exportar_menu.setCursor(Qt.PointingHandCursor)
        header.addWidget(self.btn_exportar_menu)
        
        layout.addLayout(header)

        # --- FILTRO AÑO ---
        filtro_layout = QHBoxLayout()
        filtro_layout.addWidget(QLabel("Seleccionar Año Fiscal:"))
        self.cbo_año = QComboBox()
        for a in range(2020, 2036):
            self.cbo_año.addItem(str(a))
        self.cbo_año.setCurrentText(str(self.año_actual))
        self.cbo_año.currentTextChanged.connect(self.actualizar)
        filtro_layout.addWidget(self.cbo_año)
        filtro_layout.addStretch()
        layout.addLayout(filtro_layout)

        # --- TARJETAS KPI (Resumen Anual) ---
        kpi_layout = QHBoxLayout()
        self.kpi_ingresos = self._crear_kpi("INGRESOS ANUALES", "#16a34a")
        self.kpi_gastos = self._crear_kpi("GASTOS ANUALES", "#dc2626")
        self.kpi_resultado = self._crear_kpi("RESULTADO EJERCICIO", "#2563eb")
        
        kpi_layout.addWidget(self.kpi_ingresos)
        kpi_layout.addWidget(self.kpi_gastos)
        kpi_layout.addWidget(self.kpi_resultado)
        layout.addLayout(kpi_layout)

        # --- TABLA RESUMEN MENSUAL ---
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["Mes", "Ingresos", "Gastos", "Saldo Mensual"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setStyleSheet("""
            QTableWidget { font-size: 14px; gridline-color: #e2e8f0; }
            QHeaderView::section { background: #f8fafc; padding: 8px; font-weight: bold; border: none; }
        """)
        layout.addWidget(self.tabla)

    def _crear_kpi(self, titulo, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white; border: 1px solid #e2e8f0; border-radius: 12px;
                border-left: 6px solid {color};
            }}
        """)
        vbox = QVBoxLayout(card)
        lbl_tit = QLabel(titulo)
        lbl_tit.setStyleSheet("color: #64748b; font-weight: bold; font-size: 12px;")
        
        lbl_val = QLabel("0.00")
        lbl_val.setStyleSheet(f"color: {color}; font-weight: 800; font-size: 32px;")
        
        vbox.addWidget(lbl_tit)
        vbox.addWidget(lbl_val)
        card.valor_lbl = lbl_val
        return card

    def actualizar(self):
        try:
            año = int(self.cbo_año.currentText())
        except (ValueError, TypeError):
            return
        
        total_ingresos = 0
        total_gastos = 0
        
        self.tabla.setRowCount(0)
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                 "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

        for i, nombre_mes in enumerate(meses):
            num_mes = i + 1
            # Usar data.movimientos_por_mes (asumimos que existe y filtra bien)
            # Si quieres hacerlo robusto manual:
            movs = self._filtrar_movimientos_robust(num_mes, año)
            
            ing = sum(float(m.get("haber", 0)) for m in movs)
            gas = sum(float(m.get("debe", 0)) for m in movs)
            sal = ing - gas
            
            total_ingresos += ing
            total_gastos += gas
            
            row = self.tabla.rowCount()
            self.tabla.insertRow(row)
            
            self.tabla.setItem(row, 0, QTableWidgetItem(nombre_mes))
            
            item_ing = QTableWidgetItem(f"{ing:,.2f}")
            item_ing.setForeground(QColor("#16a34a"))
            item_ing.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabla.setItem(row, 1, item_ing)
            
            item_gas = QTableWidgetItem(f"{gas:,.2f}")
            item_gas.setForeground(QColor("#dc2626"))
            item_gas.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabla.setItem(row, 2, item_gas)
            
            item_sal = QTableWidgetItem(f"{sal:,.2f}")
            item_sal.setFont(QFont("Arial", 9, QFont.Bold))
            item_sal.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabla.setItem(row, 3, item_sal)

        # Actualizar KPIs
        self.kpi_ingresos.valor_lbl.setText(f"{total_ingresos:,.2f}")
        self.kpi_gastos.valor_lbl.setText(f"{total_gastos:,.2f}")
        resultado = total_ingresos - total_gastos
        self.kpi_resultado.valor_lbl.setText(f"{resultado:,.2f}")
        
        color_res = "#16a34a" if resultado >= 0 else "#dc2626"
        self.kpi_resultado.valor_lbl.setStyleSheet(f"color: {color_res}; font-weight: 800; font-size: 32px;")

    def _filtrar_movimientos_robust(self, mes, año):
        """Filtrado manual robusto que soporta fechas con guiones y barras."""
        filtrados = []
        for m in self.data.movimientos:
            f_str = str(m.get("fecha", ""))
            try:
                if "/" in f_str: d, mm, a = map(int, f_str.split("/"))
                elif "-" in f_str:
                    parts = list(map(int, f_str.split("-")))
                    if parts[0] > 1000: a, mm, d = parts
                    else: d, mm, a = parts
                else: continue
                
                if mm == mes and a == año:
                    filtrados.append(m)
            except (ValueError, IndexError):
                continue
        return filtrados

    # ============================================================
    # EXPORTACIONES (NUEVAS Y POTENTES)
    # ============================================================
    
    def _recopilar_datos_anuales(self):
        """Recopila y enriquece TODOS los movimientos del año seleccionado."""
        año = int(self.cbo_año.currentText())
        datos_prep = []
        saldo = 0
        
        # Recorremos todos los meses para asegurar orden cronológico o filtrar todo de golpe
        todos_movs = []
        for m in self.data.movimientos:
            f_str = str(m.get("fecha", ""))
            try:
                if "/" in f_str: d, mm, a = map(int, f_str.split("/"))
                elif "-" in f_str:
                    parts = list(map(int, f_str.split("-")))
                    if parts[0] > 1000: a, mm, d = parts
                    else: d, mm, a = parts
                else: continue
                
                if a == año:
                    todos_movs.append(m)
            except (ValueError, IndexError):
                continue
            
        # Ordenar (opcional)
        # todos_movs.sort(...) 

        for m in todos_movs:
            d = float(m.get("debe", 0))
            h = float(m.get("haber", 0))
            saldo += h - d
            
            item = m.copy()
            item["saldo"] = saldo
            item["categoria"] = self._categoria_de_cuenta(m.get("cuenta"))
            item["nombre_cuenta"] = self.data.obtener_nombre_cuenta(m.get("cuenta"))
            datos_prep.append(item)
            
        return datos_prep

    def _exportar_base(self, modo):
        if ExportadorExcelMensual is None:
            QMessageBox.critical(self, "Error", "Motor de exportación no disponible.")
            return

        año = self.cbo_año.currentText()
        nombres = {
            "general": f"Anual_Detallado_{año}.xlsx",
            "categoria": f"Anual_Categorias_{año}.xlsx",
            "cuenta": f"Anual_Cuentas_{año}.xlsx"
        }
        
        archivo, _ = QFileDialog.getSaveFileName(self, "Guardar Excel Anual", nombres[modo], "Excel (*.xlsx)")
        if not archivo: return

        datos = self._recopilar_datos_anuales()
        periodo = f"EJERCICIO {año}"

        try:
            if modo == "general":
                ExportadorExcelMensual.exportar_general(archivo, datos, periodo)
            elif modo == "categoria":
                g = defaultdict(list)
                for x in datos: g[x["categoria"]].append(x)
                ExportadorExcelMensual.exportar_agrupado(archivo, dict(sorted(g.items())), periodo, "Categoría")
            elif modo == "cuenta":
                g = defaultdict(list)
                for x in datos: g[f"{x['cuenta']} - {x['nombre_cuenta']}"].append(x)
                ExportadorExcelMensual.exportar_agrupado(archivo, dict(sorted(g.items())), periodo, "Cuenta")
                
            QMessageBox.information(self, "Éxito", f"Reporte Anual '{modo}' generado.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _exportar_general_anual(self): self._exportar_base("general")
    def _exportar_categorias_anual(self): self._exportar_base("categoria")
    def _exportar_cuentas_anual(self): self._exportar_base("cuenta")

    def _exportar_evolutivo(self):
        """Exporta la matriz de evolución mensual (El original)."""
        año = int(self.cbo_año.currentText())
        archivo, _ = QFileDialog.getSaveFileName(self, "Guardar Evolutivo", f"Evolutivo_{año}.xlsx", "Excel (*.xlsx)")
        
        if not archivo: return
        if ExportadorExcelMensual is None:
            return

        # Preparar datos matriz
        matriz = defaultdict(lambda: [0.0]*12)
        nombres = {}
        
        # Reutilizamos la lógica de recopilación para no repetir bucles feos
        # Pero el evolutivo necesita estructura específica, así que lo hacemos manual rápido
        for m in range(1, 13):
            movs = self._filtrar_movimientos_robust(m, año)
            for x in movs:
                if float(x.get("debe", 0)) > 0:
                    cta = str(x.get("cuenta", "S/N"))
                    nombres[cta] = self.data.obtener_nombre_cuenta(cta)
                    matriz[cta][m-1] += float(x["debe"])
        
        datos = {k: (nombres.get(k, ""), v, sum(v)) for k, v in matriz.items()}
        
        try:
            # Asumimos que el motor tiene 'exportar_evolutivo_anual', si no, habría que añadirlo
            # Si falla, es porque el motor no tiene este método específico.
            if hasattr(ExportadorExcelMensual, "exportar_evolutivo_anual"):
                ExportadorExcelMensual.exportar_evolutivo_anual(archivo, dict(sorted(datos.items())), año)
                QMessageBox.information(self, "Éxito", "Evolutivo generado.")
            else:
                QMessageBox.warning(self, "Aviso", "El motor no soporta exportación de matriz evolutiva.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))