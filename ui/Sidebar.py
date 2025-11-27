from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal


class Sidebar(QWidget):
    # Señal para cambiar la vista en MainWindow
    change_view = Signal(str)

    def __init__(self):
        super().__init__()
        self._build_ui()

    # ============================================================
    # UI PRINCIPAL
    # ============================================================
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(15)

        # Título
        titulo = QLabel("MENÚ")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #1e293b;
        """)
        layout.addWidget(titulo)

        layout.addSpacing(15)

        # BOTONES
        layout.addWidget(self._crear_boton("🏠 Dashboard", "dashboard"))
        layout.addWidget(self._crear_boton("📝 Registrar", "registrar"))
        layout.addWidget(self._crear_boton("📘 Libro Mensual", "libro_mensual"))
        layout.addWidget(self._crear_boton("⏳ Pendientes", "pendientes"))
        layout.addWidget(self._crear_boton("🧾 Cierre Mensual", "cierre"))
        layout.addWidget(self._crear_boton("📊 Informes", "informes"))
        layout.addWidget(self._crear_boton("🛠 Herramientas", "herramientas"))

        layout.addStretch()

        firma = QLabel("SHILLONG v3")
        firma.setAlignment(Qt.AlignCenter)
        firma.setStyleSheet("color: #94a3b8; font-size: 12px;")
        layout.addWidget(firma)

    # ============================================================
    # CREAR BOTÓN
    # ============================================================
    def _crear_boton(self, texto, vista):
        btn = QPushButton(texto)
        btn.setProperty("vista", vista)

        btn.setStyleSheet("""
            QPushButton {
                padding: 12px;
                text-align: left;
                border-radius: 6px;
                background: #e2e8f0;
                font-size: 15px;
            }
            QPushButton:hover {
                background: #cbd5e1;
            }
        """)

        btn.clicked.connect(lambda _, v=vista: self._emitir_cambio(v))
        return btn

    # ============================================================
    # EMITIR SEÑAL
    # ============================================================
    def _emitir_cambio(self, vista):
        self.change_view.emit(vista)