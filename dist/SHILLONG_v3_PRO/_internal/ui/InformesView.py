# -*- coding: utf-8 -*-
"""
InformesView — SHILLONG CONTABILIDAD v3.6 PRO
Centro de Inteligencia de Negocio (BI)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QComboBox, QFrame, QFileDialog, QMessageBox, QGridLayout
)
from PySide6.QtCore import Qt
import datetime
import json
from collections import defaultdict
from pathlib import Path

# Importamos el motor actualizado
try:
    from models.ExportadorExcelMensual import ExportadorExcelMensual
except ImportError:
    ExportadorExcelMensual = None

class InformesView(QWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.año_actual = datetime.date.today().year
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)

        # Título
        lbl_titulo = QLabel("📊 Informes Avanzados & BI")
        lbl_titulo.setStyleSheet("font-size: 28px; font-weight: bold; color: #0f172a;")
        layout.addWidget(lbl_titulo)

        # Selector de Año
        panel_filtro = QHBoxLayout()
        panel_filtro.addWidget(QLabel("Seleccionar Año Fiscal:"))
        self.cbo_año = QComboBox()
        for a in range(2020, 2031):
            self.cbo_año.addItem(str(a))
        self.cbo_año.setCurrentText(str(self.año_actual))
        panel_filtro.addWidget(self.cbo_año)
        panel_filtro.addStretch()
        layout.addLayout(panel_filtro)

        # Grid de Botones
        grid = QGridLayout()
        grid.setSpacing(20)

        # 1. Evolutivo
        btn_evolutivo = self._crear_boton_informe(
            "📈 Evolutivo Anual (Matriz)",
            "Genera una sábana Excel con todos los meses en columnas.",
            "#2563eb"
        )
        btn_evolutivo.clicked.connect(self._generar_evolutivo)
        grid.addWidget(btn_evolutivo, 0, 0)

        # 2. Presupuesto (AHORA ACTIVO)
        btn_presupuesto = self._crear_boton_informe(
            "📉 Control Presupuestario",
            "Comparativa: Presupuesto vs. Realidad (Semáforo de desviación).",
            "#059669"
        )
        btn_presupuesto.clicked.connect(self._generar_control_presupuestario)
        grid.addWidget(btn_presupuesto, 0, 1)

        # 3. Top Gastos
        btn_top = self._crear_boton_informe(
            "🏆 Top 10 Gastos",
            "Ranking de cuentas (Pareto 80/20).",
            "#d97706"
        )
        btn_top.clicked.connect(self._generar_top_gastos)
        grid.addWidget(btn_top, 1, 0)

        layout.addLayout(grid)
        layout.addStretch()

    def _crear_boton_informe(self, titulo, desc, color):
        btn = QPushButton()
        layout = QVBoxLayout(btn)
        lbl_t = QLabel(titulo)
        lbl_t.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color};")
        lbl_d = QLabel(desc)
        lbl_d.setStyleSheet("font-size: 13px; color: #64748b;")
        lbl_d.setWordWrap(True)
        layout.addWidget(lbl_t)
        layout.addWidget(lbl_d)
        btn.setStyleSheet(f"QPushButton {{ background-color: white; border: 2px solid #e2e8f0; border-radius: 15px; padding: 15px; text-align: left; }} QPushButton:hover {{ border-color: {color}; background-color: #f8fafc; }}")
        btn.setMinimumHeight(120)
        return btn

    def _generar_evolutivo(self):
        año = int(self.cbo_año.currentText())
        archivo, _ = QFileDialog.getSaveFileName(self, "Guardar Evolutivo", f"Evolutivo_{año}.xlsx", "Excel (*.xlsx)")
        
        if not archivo or ExportadorExcelMensual is None: return

        matriz = defaultdict(lambda: [0.0]*12)
        nombres_cuenta = {}

        for mes in range(1, 13):
            movs = self.data.movimientos_por_mes(mes, año)
            for m in movs:
                if float(m.get("debe", 0)) > 0:
                    cta = str(m.get("cuenta", "Desconocida"))
                    nombres_cuenta[cta] = self.data.obtener_nombre_cuenta(cta)
                    matriz[cta][mes-1] += float(m["debe"])

        datos_finales = {cta: (nombres_cuenta.get(cta, "S/N"), v, sum(v)) for cta, v in matriz.items()}
        
        try:
            ExportadorExcelMensual.exportar_evolutivo_anual(archivo, dict(sorted(datos_finales.items())), año)
            QMessageBox.information(self, "Éxito", f"Evolutivo {año} generado.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _generar_control_presupuestario(self):
        """Genera el reporte comparativo Presupuesto vs Realidad"""
        año = int(self.cbo_año.currentText())
        
        # 1. Cargar archivo de presupuesto
        ruta_json = Path(f"data/presupuesto_{año}.json")
        if not ruta_json.exists():
            QMessageBox.warning(self, "Falta Presupuesto", f"No se encontró el archivo de presupuesto:\n{ruta_json}\n\nPor favor crea este archivo o renombra 'presupuesto_2025.json' si corresponde.")
            return

        try:
            with open(ruta_json, "r", encoding="utf-8") as f:
                presupuesto = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Error JSON", f"Error leyendo presupuesto: {e}")
            return

        # 2. Calcular Realidad (Gasto Anual)
        gasto_real = defaultdict(float)
        # Recorremos TODOS los movimientos del año (mes 1 a 12)
        for mes in range(1, 13):
            movs = self.data.movimientos_por_mes(mes, año)
            for m in movs:
                if float(m.get("debe", 0)) > 0:
                    cta = str(m.get("cuenta", "")).strip()
                    gasto_real[cta] += float(m["debe"])

        # 3. Cruzar datos (Solo cuentas que tengan presupuesto o gasto)
        todas_cuentas = set(presupuesto.keys()) | set(gasto_real.keys())
        datos_informe = []

        for cta in todas_cuentas:
            ppt = float(presupuesto.get(cta, 0))
            real = gasto_real.get(cta, 0)
            diff = ppt - real  # Positivo = Ahorro, Negativo = Sobregasto
            pct = ((real - ppt) / ppt * 100) if ppt != 0 else 0
            
            # Filtro opcional: ignorar cuentas sin movimiento y sin presupuesto
            if ppt == 0 and real == 0: continue

            datos_informe.append({
                "cuenta": cta,
                "nombre": self.data.obtener_nombre_cuenta(cta),
                "ppt": ppt,
                "real": real,
                "diff": diff, # Diferencia monetaria
                "pct": pct    # Desviación porcentual
            })

        datos_informe.sort(key=lambda x: x["cuenta"])

        # 4. Exportar
        archivo, _ = QFileDialog.getSaveFileName(self, "Guardar Control Presupuestario", f"Presupuesto_vs_Real_{año}.xlsx", "Excel (*.xlsx)")
        if not archivo: return

        try:
            ExportadorExcelMensual.exportar_presupuesto_vs_real(archivo, datos_informe, año)
            QMessageBox.information(self, "Éxito", "Informe de Control Presupuestario generado.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _generar_top_gastos(self):
        """Genera el Ranking de Gastos (Pareto)"""
        año = int(self.cbo_año.currentText())
        
        # 1. Calcular Gasto Total por Cuenta
        gasto_por_cuenta = defaultdict(float)
        total_anual = 0.0
        
        for mes in range(1, 13):
            movs = self.data.movimientos_por_mes(mes, año)
            for m in movs:
                if float(m.get("debe", 0)) > 0:
                    cta = str(m.get("cuenta", "")).strip()
                    importe = float(m["debe"])
                    gasto_por_cuenta[cta] += importe
                    total_anual += importe

        if total_anual == 0:
            QMessageBox.information(self, "Info", f"No hay gastos registrados en {año}.")
            return

        # 2. Ordenar y seleccionar Top
        ranking = []
        # Convertimos a lista y ordenamos por importe descendente
        cuentas_ordenadas = sorted(gasto_por_cuenta.items(), key=lambda x: x[1], reverse=True)
        
        # Tomamos todas (o limitamos a top 50 para no hacer eterno el excel, aquí todas)
        for i, (cta, importe) in enumerate(cuentas_ordenadas, 1):
            if importe > 0:
                ranking.append({
                    "rank": i,
                    "cuenta": cta,
                    "nombre": self.data.obtener_nombre_cuenta(cta),
                    "importe": importe
                })

        # 3. Exportar
        archivo, _ = QFileDialog.getSaveFileName(self, "Guardar Top Gastos", f"Ranking_Gastos_{año}.xlsx", "Excel (*.xlsx)")
        if not archivo: return
        
        if ExportadorExcelMensual is None:
            QMessageBox.critical(self, "Error", "Falta el módulo ExportadorExcelMensual.")
            return

        try:
            ExportadorExcelMensual.exportar_ranking(archivo, ranking, año, total_anual)
            QMessageBox.information(self, "Éxito", f"Ranking de Gastos {año} generado correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))