from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTableView, QFrame, QFileDialog, QMessageBox
)
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt
from datetime import datetime
import pandas as pd


class InformesView(QWidget):
    """
    Informes y exportaciones — SHILLONG CONTABILIDAD v3 (PySide6)
    Muestra movimientos por fecha y permite exportar el Libro Diario a Excel.
    """

    def __init__(self, data=None):
        super().__init__()
        self.data = data
        self._build_ui()
        self._crear_modelo()

    # ------------------------------------------------------------
    # CONSTRUCCIÓN DE LA INTERFAZ
    # ------------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        titulo = QLabel("📊 Informes y Exportaciones")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(titulo)

        # Caja blanca tipo tarjeta
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #d1d5db;
                border-radius: 8px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(12)

        # -----------------------------------------------
        # Fila superior: Fecha + botones
        # -----------------------------------------------
        top = QHBoxLayout()

        top.addWidget(QLabel("Fecha (dd/mm/aaaa):"))

        self.entry_fecha = QLineEdit()
        self.entry_fecha.setPlaceholderText("01/01/2026")
        self.entry_fecha.setText(datetime.now().strftime("%d/%m/%Y"))
        self.entry_fecha.setFixedWidth(140)
        top.addWidget(self.entry_fecha)

        btn_mostrar = QPushButton("Mostrar")
        btn_mostrar.clicked.connect(self.cargar_informe)
        top.addWidget(btn_mostrar)

        btn_exportar = QPushButton("Exportar a Excel")
        btn_exportar.clicked.connect(self.exportar_excel)
        top.addWidget(btn_exportar)

        top.addStretch()
        card_layout.addLayout(top)

        # -----------------------------------------------
        # Tabla
        # -----------------------------------------------
        self.tabla = QTableView()
        self.tabla.setStyleSheet("""
            QTableView {
                background: white;
                border: 1px solid #d1d5db;
                font-size: 14px;
            }
        """)
        card_layout.addWidget(self.tabla)

        layout.addWidget(card)

        # Totales
        self.label_totales = QLabel("Totales: Debe = 0.00 | Haber = 0.00")
        self.label_totales.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(self.label_totales)

    # ------------------------------------------------------------
    def _crear_modelo(self):
        self.modelo = QStandardItemModel()
        self.modelo.setHorizontalHeaderLabels([
            "Fecha", "Documento", "Concepto", "Cuenta",
            "Debe", "Haber", "Saldo", "Estado"
        ])
        self.tabla.setModel(self.modelo)

    # ------------------------------------------------------------
    def cargar_informe(self):
        """Carga los movimientos de la fecha proporcionada."""
        if not self.data:
            print("⚠ InformesView: Sin modelo de datos conectado.")
            return

        fecha = self.entry_fecha.text().strip()

        try:
            movimientos = self.data.movimientos_por_fecha(fecha)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Fecha inválida:\n{e}")
            return

        self._crear_modelo()

        total_debe = 0.0
        total_haber = 0.0

        for m in movimientos:
            debe = float(m.get("debe", 0) or 0)
            haber = float(m.get("haber", 0) or 0)

            fila = [
                m.get("fecha", ""),
                m.get("documento", ""),
                m.get("concepto", ""),
                m.get("cuenta", ""),
                f"{debe:.2f}" if debe else "",
                f"{haber:.2f}" if haber else "",
                f"{float(m.get('saldo', 0)):.2f}",
                m.get("estado", "")
            ]

            items = [QStandardItem(str(x)) for x in fila]
            for it in items:
                it.setEditable(False)
            self.modelo.appendRow(items)

            total_debe += debe
            total_haber += haber

        self.label_totales.setText(
            f"Totales: Debe = {total_debe:,.2f} | Haber = {total_haber:,.2f}"
        )

        self.tabla.resizeColumnsToContents()

    # ------------------------------------------------------------
    def exportar_excel(self):
        """Exporta el informe diario a un archivo Excel."""
        if self.modelo.rowCount() == 0:
            QMessageBox.warning(self, "Sin datos", "No hay datos para exportar.")
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar informe",
            f"Libro Diario {self.entry_fecha.text().replace('/', '-')}.xlsx",
            "Archivos Excel (*.xlsx)"
        )

        if not save_path:
            return

        # Convertir modelo a DataFrame
        headers = [self.modelo.horizontalHeaderItem(i).text() for i in range(self.modelo.columnCount())]
        data = []

        for row in range(self.modelo.rowCount()):
            fila = []
            for col in range(self.modelo.columnCount()):
                fila.append(self.modelo.item(row, col).text())
            data.append(fila)

        df = pd.DataFrame(data, columns=headers)

        try:
            df.to_excel(save_path, index=False)
            QMessageBox.information(self, "Éxito", f"Informe exportado en:\n{save_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo:\n{e}")
