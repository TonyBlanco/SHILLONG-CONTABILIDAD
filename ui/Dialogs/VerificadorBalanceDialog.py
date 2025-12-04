# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
    QLabel, QHeaderView, QTableWidgetItem, QAbstractItemView, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

class VerificadorBalanceDialog(QDialog):
    """Ventana para mostrar y corregir inconsistencias Debe/Haber."""
    
    def __init__(self, data, errores_encontrados, parent=None):
        super().__init__(parent)
        self.data = data
        self.errores = errores_encontrados
        self.setWindowTitle("🛠️ Auditoría y Corrección de Movimientos")
        self.resize(1000, 700)
        
        self._build_ui()
        self._cargar_errores()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        
        # Título y mensaje
        self.lbl_info = QLabel(f"❌ Se encontraron **{len(self.errores)}** inconsistencias. Edite 'Debe' o 'Haber' para corregir:")
        self.lbl_info.setStyleSheet("font-size: 16px; font-weight: bold; color: #dc2626;")
        layout.addWidget(self.lbl_info)
        
        # Tabla de errores
        self.tabla = QTableWidget(0, 7)
        self.tabla.setHorizontalHeaderLabels([
            "Index JSON", "Fecha", "Documento", "Concepto", "Debe", "Haber", "Tipo de Error"
        ])
        # Permitir edición en columnas de Debe y Haber (índices 4 y 5)
        self.tabla.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.AnyKeyPressed)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch) # Concepto
        layout.addWidget(self.tabla)
        
        # Botones
        h_layout = QHBoxLayout()
        self.btn_guardar = QPushButton("💾 Aplicar Correcciones y Guardar DB")
        self.btn_guardar.setStyleSheet("background-color: #059669; color: white; padding: 10px;")
        self.btn_cancelar = QPushButton("Cancelar")
        
        h_layout.addStretch()
        h_layout.addWidget(self.btn_guardar)
        h_layout.addWidget(self.btn_cancelar)
        layout.addLayout(h_layout)
        
        self.btn_guardar.clicked.connect(self._aplicar_correcciones)
        self.btn_cancelar.clicked.connect(self.reject)

    def _cargar_errores(self):
        self.tabla.setRowCount(len(self.errores))
        
        for row, error in enumerate(self.errores):
            # Columna 0: Índice real en el JSON
            idx_item = QTableWidgetItem(str(error["index"]))
            self.tabla.setItem(row, 0, idx_item)
            
            # Columna 1-3: Datos de visualización
            self.tabla.setItem(row, 1, QTableWidgetItem(error["movimiento"].get("fecha", "")))
            self.tabla.setItem(row, 2, QTableWidgetItem(error["movimiento"].get("documento", "")))
            self.tabla.setItem(row, 3, QTableWidgetItem(error["movimiento"].get("concepto", "")))
            
            # Columna 4 y 5: Debe y Haber (Editables)
            debe_item = QTableWidgetItem(str(error["movimiento"].get("debe", "0.00")))
            haber_item = QTableWidgetItem(str(error["movimiento"].get("haber", "0.00")))
            debe_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            haber_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabla.setItem(row, 4, debe_item)
            self.tabla.setItem(row, 5, haber_item)

            # Columna 6: Error
            error_item = QTableWidgetItem(error["error"])
            error_item.setForeground(QColor("#dc2626"))
            self.tabla.setItem(row, 6, error_item)

    def _aplicar_correcciones(self):
        """Aplica los cambios hechos en la tabla al modelo de datos."""
        try:
            cambios_aplicados = 0
            for row in range(self.tabla.rowCount()):
                json_index = int(self.tabla.item(row, 0).text())
                
                # Obtener nuevos valores (Deben ser números válidos)
                nuevo_debe_str = self.tabla.item(row, 4).text().replace(',', '.')
                nuevo_haber_str = self.tabla.item(row, 5).text().replace(',', '.')
                
                nuevo_debe = float(nuevo_debe_str)
                nuevo_haber = float(nuevo_haber_str)
                
                # Aplicar las correcciones al JSON original si hay cambio
                mov = self.data.movimientos[json_index]
                if float(mov["debe"]) != nuevo_debe or float(mov["haber"]) != nuevo_haber:
                    
                    # ⚠️ Re-validar antes de guardar
                    if nuevo_debe > 0 and nuevo_haber > 0:
                        raise ValueError(f"Fila {row+1}: Debe y Haber no pueden coexistir. (Debe={nuevo_debe}, Haber={nuevo_haber})")
                    
                    if nuevo_debe == 0 and nuevo_haber == 0:
                         raise ValueError(f"Fila {row+1}: Debe o Haber debe ser mayor que cero.")

                    # Guardar en la estructura de datos
                    mov["debe"] = f"{nuevo_debe:.2f}"
                    mov["haber"] = f"{nuevo_haber:.2f}"
                    cambios_aplicados += 1

            if cambios_aplicados > 0:
                self.data.guardar() # Suponemos que existe un método para guardar el JSON
                QMessageBox.information(self, "Éxito", f"Se aplicaron {cambios_aplicados} correcciones y se guardó la base de datos.")
            
            self.accept()
            
        except ValueError as e:
            QMessageBox.critical(self, "Error de Validación", f"Error al procesar los datos: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error de Guardado", f"Ocurrió un error inesperado: {e}")