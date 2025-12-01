# -*- coding: utf-8 -*-
"""
ImportarExcelDialog.py — SHILLONG CONTABILIDAD v3.6 PRO
Versión DIRECTA: Sin preguntas intermedias que bloqueen la importación.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QProgressBar
)
from PySide6.QtCore import Qt
import csv
import datetime

# Intentamos importar openpyxl
try:
    import openpyxl
except ImportError:
    openpyxl = None

class ImportarExcelDialog(QDialog):
    def __init__(self, parent, data_manager):
        super().__init__(parent)
        self.setWindowTitle("📥 Importar Movimientos")
        self.resize(850, 550)
        self.data_manager = data_manager
        self.datos_leidos = [] 
        
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Info
        lbl_info = QLabel(
            "<b>Instrucciones:</b> Seleccione su archivo CSV o Excel.<br>"
            "El sistema buscará automáticamente las columnas necesarias.<br>"
            "Al pulsar 'Confirmar', los datos se guardarán inmediatamente."
        )
        lbl_info.setWordWrap(True)
        lbl_info.setStyleSheet("color: #334155; font-size: 13px; background: #f1f5f9; padding: 10px; border-radius: 5px;")
        layout.addWidget(lbl_info)

        # Botón selección
        btn_layout = QHBoxLayout()
        self.btn_select = QPushButton("📂 Seleccionar Archivo...")
        self.btn_select.setCursor(Qt.PointingHandCursor)
        self.btn_select.setStyleSheet("""
            QPushButton { background-color: #2563eb; color: white; padding: 10px 20px; border-radius: 6px; font-weight: bold; font-size: 14px; }
            QPushButton:hover { background-color: #1d4ed8; }
        """)
        self.btn_select.clicked.connect(self._seleccionar_archivo)
        btn_layout.addWidget(self.btn_select)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Tabla Preview
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(8)
        self.tabla.setHorizontalHeaderLabels(["Fecha", "Doc", "Concepto", "Cuenta", "Debe", "Haber", "Banco", "Estado"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setStyleSheet("QHeaderView::section { background-color: #f8fafc; padding: 4px; border: none; font-weight: bold; }")
        layout.addWidget(self.tabla)

        # Progreso
        self.progress = QProgressBar()
        self.progress.setTextVisible(True)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # Botones finales
        actions = QHBoxLayout()
        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet("font-weight: bold; color: #0f172a;")
        actions.addWidget(self.lbl_status)
        actions.addStretch()
        
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.clicked.connect(self.reject)
        
        self.btn_import = QPushButton("✅ IMPORTAR AHORA")
        self.btn_import.setCursor(Qt.PointingHandCursor)
        self.btn_import.setStyleSheet("""
            QPushButton { background-color: #16a34a; color: white; padding: 10px 20px; border-radius: 6px; font-weight: bold; }
            QPushButton:hover { background-color: #15803d; }
            QPushButton:disabled { background-color: #cbd5e1; color: #94a3b8; }
        """)
        self.btn_import.setEnabled(False)
        self.btn_import.clicked.connect(self._procesar_importacion)

        actions.addWidget(self.btn_cancel)
        actions.addWidget(self.btn_import)
        layout.addLayout(actions)

    def _seleccionar_archivo(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Abrir Archivo", "", "Archivos de Datos (*.csv *.xlsx *.xls)")
        if not archivo: return

        self.lbl_status.setText("Analizando archivo...")
        self.datos_leidos = []
        
        try:
            if archivo.endswith(".csv"):
                self._leer_csv(archivo)
            elif archivo.endswith((".xlsx", ".xls")):
                if openpyxl:
                    self._leer_excel(archivo)
                else:
                    QMessageBox.warning(self, "Falta Librería", "Para leer Excel necesita instalar openpyxl. Use CSV por ahora.")
                    return
            else:
                return

            self._llenar_tabla_preview()
            
            if self.datos_leidos:
                self.btn_import.setEnabled(True)
                self.lbl_status.setText(f"✅ Listo para importar {len(self.datos_leidos)} movimientos.")
            else:
                self.btn_import.setEnabled(False)
                self.lbl_status.setText("⚠️ No se encontraron datos válidos.")

        except Exception as e:
            QMessageBox.critical(self, "Error Crítico", f"Error al leer el archivo:\n{str(e)}")
            self.lbl_status.setText("Error de lectura.")

    def _leer_csv(self, ruta):
        try:
            with open(ruta, 'r', encoding='utf-8', errors='replace') as f:
                sample = f.read(2048)
                dialect = csv.Sniffer().sniff(sample)
        except:
            dialect = 'excel'

        with open(ruta, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.reader(f, dialect)
            rows = list(reader)
            self._parsear_filas(rows)

    def _leer_excel(self, ruta):
        wb = openpyxl.load_workbook(ruta, data_only=True)
        ws = wb.active
        rows = []
        for row in ws.iter_rows(values_only=True):
            rows.append([str(c).strip() if c is not None else "" for c in row])
        self._parsear_filas(rows)

    def _parsear_filas(self, rows):
        header_map = {}
        start_index = -1
        
        # BUSCAR CABECERA
        for i, row in enumerate(rows):
            row_lower = [str(x).lower().strip() for x in row]
            if "fecha" in row_lower and "cuenta" in row_lower:
                start_index = i
                for col_idx, val in enumerate(row_lower):
                    if "fecha" in val: header_map["fecha"] = col_idx
                    elif "doc" in val: header_map["documento"] = col_idx
                    elif "concepto" in val: header_map["concepto"] = col_idx
                    elif "cuenta" in val: header_map["cuenta"] = col_idx
                    elif "debe" in val or "cargo" in val: header_map["debe"] = col_idx
                    elif "haber" in val or "abono" in val: header_map["haber"] = col_idx
                    elif "banco" in val: header_map["banco"] = col_idx
                    elif "estado" in val: header_map["estado"] = col_idx
                break
        
        if start_index == -1:
            raise Exception("No se encontró la fila de cabeceras (Busqué 'Fecha' y 'Cuenta').")

        # PROCESAR DATOS
        for i in range(start_index + 1, len(rows)):
            row = rows[i]
            if not row or len(row) <= header_map.get("fecha", 0): continue
            
            try:
                def get(k): 
                    idx = header_map.get(k)
                    return str(row[idx]).strip() if idx is not None and idx < len(row) else ""

                fecha_raw = get("fecha")
                if not fecha_raw: continue

                # Normalizar Fecha
                fecha_fmt = fecha_raw
                if "-" in fecha_raw and len(fecha_raw.split("-")) == 3: 
                    parts = fecha_raw.split(" ")[0].split("-")
                    if len(parts[0]) == 4:
                        fecha_fmt = f"{parts[2]}/{parts[1]}/{parts[0]}"
                
                # Normalizar importes
                debe = float(get("debe").replace(",", ".") or 0)
                haber = float(get("haber").replace(",", ".") or 0)

                if debe == 0 and haber == 0: continue

                mov = {
                    "fecha": fecha_fmt,
                    "documento": get("documento"),
                    "concepto": get("concepto"),
                    "cuenta": get("cuenta").split(" ")[0],
                    "debe": debe,
                    "haber": haber,
                    "banco": get("banco") or "Caja",
                    "estado": get("estado").lower() or "pagado",
                    "moneda": "INR"
                }
                self.datos_leidos.append(mov)

            except Exception as e:
                print(f"Fila {i} ignorada: {e}")

    def _llenar_tabla_preview(self):
        self.tabla.setRowCount(len(self.datos_leidos))
        for i, m in enumerate(self.datos_leidos):
            self.tabla.setItem(i, 0, QTableWidgetItem(m["fecha"]))
            self.tabla.setItem(i, 1, QTableWidgetItem(m["documento"]))
            self.tabla.setItem(i, 2, QTableWidgetItem(m["concepto"]))
            self.tabla.setItem(i, 3, QTableWidgetItem(m["cuenta"]))
            self.tabla.setItem(i, 4, QTableWidgetItem(f"{m['debe']:.2f}"))
            self.tabla.setItem(i, 5, QTableWidgetItem(f"{m['haber']:.2f}"))
            self.tabla.setItem(i, 6, QTableWidgetItem(m["banco"]))
            self.tabla.setItem(i, 7, QTableWidgetItem(m["estado"]))

    def _procesar_importacion(self):
        """
        Versión simplificada: Sin pregunta SI/NO. 
        Guarda directamente y muestra progreso.
        """
        if not self.datos_leidos: return
        
        # Bloquear botón para no doble clic
        self.btn_import.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setMaximum(len(self.datos_leidos))
        self.lbl_status.setText("Guardando datos...")
        
        # 1. Añadir a memoria
        for i, mov in enumerate(self.datos_leidos):
            self.data_manager.agregar_movimiento(
                fecha=mov["fecha"],
                documento=mov["documento"],
                concepto=mov["concepto"],
                cuenta=mov["cuenta"],
                debe=mov["debe"],
                haber=mov["haber"],
                moneda=mov["moneda"],
                banco=mov["banco"],
                estado=mov["estado"]
            )
            self.progress.setValue(i + 1)
        
        # 2. Forzar escritura en disco (usando el método seguro que creamos antes)
        if hasattr(self.data_manager, "guardar_datos"):
            self.data_manager.guardar_datos()
        elif hasattr(self.data_manager, "save_data"):
            self.data_manager.save_data()
        elif hasattr(self.data_manager, "guardar"):
            self.data_manager.guardar()
            
        # 3. Éxito
        QMessageBox.information(self, "¡Completado!", f"Se han importado {len(self.datos_leidos)} movimientos correctamente.")
        self.accept()