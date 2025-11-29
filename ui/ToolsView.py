# -*- coding: utf-8 -*-
"""
ToolsView.py — SHILLONG CONTABILIDAD v3.6 PRO
Incluye:
- Selector de Tema
- Utilidades de Sistema
- ✨ Módulo "Inspiración Diaria" (Salmos + 72 Nombres de Dios)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QMessageBox, QFrame, QGraphicsDropShadowEffect
)
from PySide6.QtGui import QIcon, QFont, QColor
from PySide6.QtCore import Qt, QSize
import os
import random

class ToolsView(QWidget):

    # Base de datos de Inspiración (Salmos + Nombres de Dios)
    INSPIRACION = [
        # --- SALMOS ---
        ("Salmo 23:1", "El Señor es mi pastor, nada me falta: en verdes praderas me hace recostar.", ""),
        ("Salmo 27:1", "El Señor es mi luz y mi salvación, ¿a quién temeré?", ""),
        ("Salmo 91:4", "Con sus plumas te cubrirá, y debajo de sus alas estarás seguro.", ""),
        ("Salmo 121:1-2", "Levanto mis ojos a los montes: ¿de dónde me vendrá el auxilio? El auxilio me viene del Señor.", ""),
        ("Salmo 46:1", "Dios es nuestro amparo y fortaleza, nuestro pronto auxilio en las tribulaciones.", ""),
        # --- 72 NOMBRES DE DIOS (Selección) ---
        ("Nombre #1 - VEHU", "Viaje en el tiempo, arrepentimiento, eliminar el pasado doloroso.", "והו"),
        ("Nombre #2 - YELI", "Recuperar la energía, vitalidad, despertar la chispa divina.", "ילי"),
        ("Nombre #3 - SIT", "Haciendo milagros, rompiendo las leyes de la naturaleza.", "סיט"),
        ("Nombre #4 - ALEM", "Eliminar pensamientos negativos, paz mental.", "עלם"),
        ("Nombre #5 - MAHASH", "Curación, sanación física y espiritual.", "מהש"),
        ("Nombre #6 - LELA", "Estado de sueño, mensajes en sueños, profecía.", "ללה"),
        ("Nombre #10 - ALAD", "Protección contra el mal de ojo y la envidia.", "אלד"),
        ("Nombre #12 - HAHASH", "Amor incondicional, despertar el amor al prójimo.", "ההע"),
        ("Nombre #18 - KALI", "Fertilidad, creatividad, dar a luz proyectos.", "כלי"),
        ("Nombre #25 - NITH", "Decir la verdad, coraje para hablar, sinceridad.", "נתה"),
        ("Nombre #26 - HAA", "Orden en el caos, poner orden en la vida.", "האא"),
        ("Nombre #32 - VASAR", "Recuerdos, memoria, recordar lecciones de vida.", "ושר"),
        ("Nombre #45 - SAMECH", "Prosperidad, sustento, éxito económico.", "סאל"),
        ("Nombre #49 - VEHU", "Felicidad, gratitud, apreciar lo que se tiene.", "והו"), # Repetido con otro matiz en algunas tradiciones
        ("Nombre #58 - YEYAL", "Dejar ir, soltar, liberar ataduras.", "ייל"),
        ("Nombre #68 - CHAVU", "Contactar con almas que partieron, elevación.", "חבו")
    ]

    def __init__(self, main):
        super().__init__()
        self.main = main

        # RUTA ABSOLUTA A LOS ICONOS PNG
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.icon_path = os.path.join(base, "assets", "icons")
        if not os.path.exists(self.icon_path):
             self.icon_path = os.path.join(base, "ui", "assets", "icons")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(25)

        # TÍTULO
        header = QLabel("🛠️ Herramientas & Luz")
        header.setStyleSheet("font-size: 28px; font-weight: 800; color: #1e293b;")
        layout.addWidget(header)

        # -------------------------------------------------------------
        # 1. ✨ SECCIÓN INSPIRACIÓN (WIDGET DIVINO)
        # -------------------------------------------------------------
        self._setup_salmo_widget(layout)

        # -------------------------------------------------------------
        # 2. TEMA VISUAL
        # -------------------------------------------------------------
        layout.addWidget(QLabel("🎨 Personalización Visual"))
        panel_tema = self._crear_panel_tema()
        layout.addWidget(panel_tema)

        # -------------------------------------------------------------
        # 3. ACCIONES DE SISTEMA
        # -------------------------------------------------------------
        layout.addWidget(QLabel("💾 Gestión de Datos"))
        panel_datos = self._crear_panel_datos()
        layout.addWidget(panel_datos)

        layout.addStretch()
        
        # Iniciar con un mensaje aleatorio
        self._cambiar_mensaje()

    # =====================================================================
    #  WIDGET INSPIRACIÓN
    # =====================================================================
    def _setup_salmo_widget(self, layout):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #fefce8; /* Amarillo papiro */
                border: 1px solid #fde047;
                border-radius: 15px;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)

        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(25, 25, 25, 25)

        # Título pequeña
        lbl_top = QLabel("✨ Luz del Día")
        lbl_top.setStyleSheet("color: #d97706; font-weight: bold; font-size: 12px; text-transform: uppercase;")
        lbl_top.setAlignment(Qt.AlignCenter)
        vbox.addWidget(lbl_top)

        # Texto Hebreo (Grande y centrado)
        self.lbl_hebreo = QLabel("")
        self.lbl_hebreo.setAlignment(Qt.AlignCenter)
        self.lbl_hebreo.setStyleSheet("font-size: 40px; font-weight: bold; color: #1e3a8a; font-family: 'Times New Roman'; margin-top: 5px;")
        vbox.addWidget(self.lbl_hebreo)

        # Texto del Mensaje
        self.lbl_mensaje = QLabel("...")
        self.lbl_mensaje.setWordWrap(True)
        self.lbl_mensaje.setAlignment(Qt.AlignCenter)
        self.lbl_mensaje.setStyleSheet("font-size: 18px; font-style: italic; color: #451a03; font-family: 'Georgia'; margin: 10px 0;")
        vbox.addWidget(self.lbl_mensaje)

        # Referencia (Cita o Nombre)
        self.lbl_cita = QLabel("...")
        self.lbl_cita.setAlignment(Qt.AlignCenter)
        self.lbl_cita.setStyleSheet("font-size: 14px; font-weight: bold; color: #92400e;")
        vbox.addWidget(self.lbl_cita)

        # Botón refrescar
        btn_refresh = QPushButton("🙏 Nueva Luz")
        btn_refresh.setCursor(Qt.PointingHandCursor)
        btn_refresh.setStyleSheet("""
            QPushButton {
                background: transparent; color: #b45309; font-weight: bold; border: 1px solid #b45309;
                border-radius: 15px; padding: 5px 15px; margin-top: 10px;
            }
            QPushButton:hover { background: #fff7ed; }
        """)
        btn_refresh.setFixedWidth(150)
        btn_refresh.clicked.connect(self._cambiar_mensaje)
        
        hbox_btn = QHBoxLayout()
        hbox_btn.addStretch()
        hbox_btn.addWidget(btn_refresh)
        hbox_btn.addStretch()
        vbox.addLayout(hbox_btn)

        layout.addWidget(card)

    def _cambiar_mensaje(self):
        cita, texto, hebreo = random.choice(self.INSPIRACION)
        
        self.lbl_hebreo.setText(hebreo) # Si es salmo, estará vacío y no ocupa espacio
        self.lbl_hebreo.setVisible(bool(hebreo)) # Ocultar si no hay hebreo
        
        self.lbl_mensaje.setText(f"“{texto}”")
        self.lbl_cita.setText(f"— {cita}")

    # =====================================================================
    #  PANELES DE HERRAMIENTAS
    # =====================================================================
    def _crear_panel_tema(self):
        frame = QFrame()
        frame.setStyleSheet("background: white; border-radius: 10px; border: 1px solid #e2e8f0;")
        h = QHBoxLayout(frame)
        h.setContentsMargins(15, 15, 15, 15)
        
        btn_claro = QPushButton("🌞 Modo Claro")
        btn_claro.clicked.connect(lambda: self._aplicar_tema("light"))
        self._estilar_btn(btn_claro, "#0ea5e9")

        btn_oscuro = QPushButton("🌙 Modo Oscuro")
        btn_oscuro.clicked.connect(lambda: self._aplicar_tema("dark"))
        self._estilar_btn(btn_oscuro, "#334155")

        h.addWidget(btn_claro)
        h.addWidget(btn_oscuro)
        return frame

    def _crear_panel_datos(self):
        frame = QFrame()
        frame.setStyleSheet("background: white; border-radius: 10px; border: 1px solid #e2e8f0;")
        h = QHBoxLayout(frame)
        h.setContentsMargins(15, 15, 15, 15)

        btn_backup = QPushButton("📦 Crear Backup")
        btn_backup.clicked.connect(self._accion_backup)
        self._estilar_btn(btn_backup, "#16a34a")

        btn_restore = QPushButton("♻️ Restaurar")
        btn_restore.clicked.connect(self._accion_restore)
        self._estilar_btn(btn_restore, "#ea580c")

        h.addWidget(btn_backup)
        h.addWidget(btn_restore)
        return frame

    def _estilar_btn(self, btn, color):
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color}; color: white; font-weight: bold;
                padding: 10px 15px; border-radius: 6px; border: none;
            }}
            QPushButton:hover {{ opacity: 0.9; }}
        """)

    # =====================================================================
    #  CONEXIONES CON MAINWINDOW
    # =====================================================================
    def _aplicar_tema(self, tema):
        if hasattr(self.main, "aplicar_tema"):
            self.main.aplicar_tema(tema)
        else:
            QMessageBox.information(self, "Tema", f"Tema {tema} seleccionado (Reinicio requerido).")

    def _accion_backup(self):
        if hasattr(self.main, "crear_backup"): self.main.crear_backup()
        elif hasattr(self.main, "create_backup"): self.main.create_backup()
        else: QMessageBox.warning(self, "Error", "Función de backup no encontrada.")

    def _accion_restore(self):
        if hasattr(self.main, "restaurar_backup"): self.main.restaurar_backup()
        elif hasattr(self.main, "restore_backup"): self.main.restore_backup()
        else: QMessageBox.warning(self, "Error", "Función de restaurar no encontrada.")