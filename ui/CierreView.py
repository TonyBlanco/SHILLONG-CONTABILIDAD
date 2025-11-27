from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFrame, QMessageBox
)
from PySide6.QtCore import Qt


class CierreView(QWidget):
    """
    Vista de Cierres y Ajustes Contables
    SHILLONG CONTABILIDAD v3 – PySide6
    """

    def __init__(self, data=None):
        super().__init__()
        self.data = data  # Instancia futura de ContabilidadData
        self._build_ui()

    # ------------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Título
        titulo = QLabel("🪙 Cierres y Ajustes Contables")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(titulo)

        # Tarjeta blanca
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
        card_layout.setSpacing(10)

        # Texto explicativo
        texto = QLabel(
            "Los asientos de ajuste permiten corregir y equilibrar las cuentas "
            "sin afectar el saldo real de caja.\n\n"
            "Se usan cuando:\n"
            "— Hay amortizaciones.\n"
            "— Hay regularizaciones de inventario.\n"
            "— Hay clasificaciones incorrectas.\n"
            "— Se ajustan cuentas del ejercicio.\n\n"
            "Estos movimientos NO modifican la caja, pero sí el Balance."
        )
        texto.setWordWrap(True)
        texto.setStyleSheet("font-size: 14px;")
        card_layout.addWidget(texto)

        # Botón para registrar ajuste (placeholder)
        btn = QPushButton("➕ Registrar Asiento de Ajuste")
        btn.setStyleSheet("""
            QPushButton {
                background: #2563eb;
                color: white;
                padding: 10px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #1e40af;
            }
        """)
        btn.clicked.connect(self._ajuste_manual)

        card_layout.addWidget(btn, alignment=Qt.AlignLeft)

        layout.addWidget(card)

    # ------------------------------------------------------------
    def _ajuste_manual(self):
        """
        Por ahora solo muestra un mensaje informativo.
        En la versión avanzada, abrirá un formulario para registrar ajustes.
        """
        QMessageBox.information(
            self,
            "Ajuste manual",
            "El formulario para registrar asientos de ajuste\n"
            "aún no está implementado.\n\n"
            "En SHILLONG v3 Pro podrás:\n"
            "✔ Seleccionar fecha\n"
            "✔ Elegir cuenta contable\n"
            "✔ Escribir concepto\n"
            "✔ Registrar importe Debe / Haber\n"
            "✔ Registrar en el archivo mensual correspondiente",
        )
