from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTableView
)
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt


class DiarioView(QWidget):
    """
    Vista del Libro Diario — SHILLONG v3 (PySide6)
    Muestra movimientos filtrados por fecha, incluyendo BANCO.
    """

    def __init__(self, data=None):
        super().__init__()

        self.data = data    # Se integra luego con ContabilidadData
        self._build_ui()

    # -------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        # Título
        titulo = QLabel("📘 Libro Diario – Movimientos por Fecha")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(titulo)

        # ------------------------------------------
        # PANEL SUPERIOR (FECHA + BOTÓN)
        # ------------------------------------------
        top = QHBoxLayout()
        top.addWidget(QLabel("Fecha (dd/mm/aaaa):"))

        self.entry_fecha = QLineEdit()
        self.entry_fecha.setPlaceholderText("01/01/2026")
        self.entry_fecha.setFixedWidth(140)
        top.addWidget(self.entry_fecha)

        btn = QPushButton("Mostrar")
        btn.clicked.connect(self.cargar_movimientos)
        top.addWidget(btn)

        top.addStretch()
        layout.addLayout(top)

        # ------------------------------------------
        # TABLA
        # ------------------------------------------
        self.tabla = QTableView()
        self.tabla.setStyleSheet("""
            QTableView {
                background: white;
                border: 1px solid #d1d5db;
                font-size: 14px;
            }
        """)

        layout.addWidget(self.tabla)

        # Modelo vacío inicial
        self._crear_modelo_tabla()

    # -------------------------------------------------------
    def _crear_modelo_tabla(self):
        """Modelo base vacío"""
        self.modelo = QStandardItemModel()
        self.modelo.setHorizontalHeaderLabels([
            "Fecha", "Documento", "Concepto", "Cuenta",
            "Debe", "Haber", "Saldo", "Estado", "Banco"
        ])
        self.tabla.setModel(self.modelo)

    # -------------------------------------------------------
    def cargar_movimientos(self):
        """Carga movimientos desde ContabilidadData filtrando por fecha."""

        fecha = self.entry_fecha.text().strip()

        if not self.data:
            print("⚠ DiarioView: No hay modelo de datos conectado todavía.")
            return

        try:
            movimientos = self.data.movimientos_por_fecha(fecha)
        except Exception as e:
            print(f"Error leyendo movimientos: {e}")
            return

        self._crear_modelo_tabla()

        for mov in movimientos:
            fila = [
                str(mov.get("fecha", "")),
                str(mov.get("documento", "")),
                str(mov.get("concepto", "")),
                str(mov.get("cuenta", "")),
                f"{float(mov.get('debe', 0)):.2f}",
                f"{float(mov.get('haber', 0)):.2f}",
                f"{float(mov.get('saldo', 0)):.2f}",
                str(mov.get("estado", "")),
                str(mov.get("banco", ""))     # ← NUEVO
            ]

            items = [QStandardItem(x) for x in fila]
            for it in items:
                it.setEditable(False)

            self.modelo.appendRow(items)

        self.tabla.resizeColumnsToContents()
