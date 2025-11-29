# -*- coding: utf-8 -*-
"""
HelpView.py — SHILLONG CONTABILIDAD v3.6 PRO
Módulo de Ayuda y Documentación Avanzada.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame,
    QToolBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class HelpView(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- HEADER ---
        header = QFrame()
        header.setStyleSheet("background-color: #ffffff; border-bottom: 1px solid #cbd5e1;")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(40, 30, 40, 30)
        
        lbl_titulo = QLabel("🆘 Guía del Usuario y Soporte")
        lbl_titulo.setStyleSheet("font-size: 28px; font-weight: 800; color: #1e293b; font-family: 'Segoe UI'; border: none;")
        
        lbl_subtitulo = QLabel("Manual completo de Shillong Contabilidad v3.6 PRO Desarrollado con ❤️ y mucho código por Mr. Ego"  )
        lbl_subtitulo.setStyleSheet("font-size: 16px; color: #64748b; margin-top: 5px; border: none;")
        
        header_layout.addWidget(lbl_titulo)
        header_layout.addWidget(lbl_subtitulo)
        layout.addWidget(header)

        # --- CONTENIDO SCROLL ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea { background-color: #f1f5f9; border: none; }
            QScrollBar:vertical { width: 10px; background: #f1f5f9; }
        """)
        
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #f1f5f9;") 
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(40, 30, 40, 40)
        content_layout.setSpacing(20)

        # ACORDEÓN
        toolbox = QToolBox()
        toolbox.setStyleSheet("""
            QToolBox { background: transparent; }
            QToolBox::tab {
                background: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 5px;
                color: #1e293b;
                font-weight: bold;
                font-size: 15px;
                padding-left: 10px;
            }
            QToolBox::tab:selected {
                background: #2563eb;
                color: #ffffff;
                border: 1px solid #1d4ed8;
            }
        """)

        # -------------------------------------------------------------
        # 1. INTRODUCCIÓN
        # -------------------------------------------------------------
        html_intro = """
        <h3 style="color:#2563eb;">Bienvenida a su Sistema Contable</h3>
        <p style="font-size:14px; color:#334155;">
            Shillong Contabilidad ha sido diseñado para gestionar las cuentas de la comunidad de manera fácil,
            profesional y segura. No necesita ser experta en informática para usarlo.
        </p>
        <p style="font-size:14px; color:#334155;">
            <b>¿Cómo me muevo?</b><br>
            A la izquierda tiene una barra blanca con todos los menús. Pulse en cualquier botón para cambiar de pantalla.
            El botón que está azul es donde se encuentra ahora mismo.
        </p>
        """
        self._agregar_seccion(toolbox, "1. Introducción y Bienvenida", html_intro)

        # -------------------------------------------------------------
        # 2. REGISTRAR OPERACIONES
        # -------------------------------------------------------------
        html_registrar = """
        <h3 style="color:#16a34a;">Registrar: El corazón del sistema</h3>
        <p style="font-size:14px; color:#334155;">
            Aquí es donde se introducen los datos día a día.
        </p>
        <ol style="font-size:14px; color:#334155;">
            <li><b>Fecha:</b> Se pone automáticamente en 'hoy', pero puede cambiarla.</li>
            <li><b>Concepto:</b> Describa el gasto (ej: 'Compra Mercadona', 'Recibo Luz').</li>
            <li><b>Cuenta:</b> Escriba para buscar. Ejemplo: si escribe 'alim', el sistema sugerirá 'Alimentación'.</li>
            <li><b>Importe:</b> 
                <ul>
                    <li>Use <b>Debe</b> para GASTOS (salidas de dinero).</li>
                    <li>Use <b>Haber</b> para INGRESOS (entradas de dinero).</li>
                </ul>
            </li>
            <li><b>Banco:</b> Elija de dónde salió el dinero (Caja, Banco, etc.).</li>
        </ol>
        <p style="font-size:14px; color:#334155;">
            Al pulsar <b>Guardar</b>, el movimiento queda grabado para siempre en el archivo seguro.
        </p>
        """
        self._agregar_seccion(toolbox, "2. Cómo Registrar Gastos e Ingresos", html_registrar)

        # -------------------------------------------------------------
        # 3. LIBROS Y CONSULTAS
        # -------------------------------------------------------------
        html_libros = """
        <h3 style="color:#d97706;">Consultando sus datos</h3>
        <p style="font-size:14px; color:#334155;">
            El programa ofrece tres formas de ver la información:
        </p>
        <ul style="font-size:14px; color:#334155;">
            <li><b>📘 Diario General:</b> Es el historial completo. Aquí ve TODO lo que ha pasado, ordenado por fecha.
                Úselo para buscar un movimiento específico ("¿Cuándo pagué aquella factura?").</li>
            <li><b>📑 Libro Mensual:</b> Es un resumen del mes. Le muestra gráficos y totales.
                Es ideal para ver cómo va el mes en curso.</li>
            <li><b>⏳ Pendientes:</b> Si marcó algún movimiento como "Pendiente" al registrarlo, aparecerá aquí
                para recordarle que debe pagarlo o cobrarlo.</li>
        </ul>
        """
        self._agregar_seccion(toolbox, "3. Libros: Diario, Mensual y Pendientes", html_libros)

        # -------------------------------------------------------------
        # 4. CIERRES E INFORMES (EXCEL)
        # -------------------------------------------------------------
        html_informes = """
        <h3 style="color:#7c3aed;">Cierres e Informes Oficiales</h3>
        <p style="font-size:14px; color:#334155;">
            Esta es la parte más potente. El programa genera los Excel por usted.
        </p>
        <ul style="font-size:14px; color:#334155;">
            <li><b>🔒 Cierre Mensual:</b> Úselo a fin de mes. Revise que todo cuadre y pulse "Exportar Excel".
                Generará un archivo con el formato oficial, colores y saldos calculados.</li>
            <li><b>📅 Cierre Anual:</b> Úselo a fin de año. El botón "Exportar Evolutivo" crea una
                'Sábana' gigante con todos los meses en columnas para ver la evolución anual.</li>
            <li><b>📈 Informes BI:</b> Aquí encontrará rankings (Top Gastos) y comparativas de presupuesto.</li>
        </ul>
        """
        self._agregar_seccion(toolbox, "4. Cierres Mensuales y Anuales (Excel)", html_informes)

        # -------------------------------------------------------------
        # 5. DATOS Y SEGURIDAD (TÉCNICO)
        # -------------------------------------------------------------
        html_tecnico = """
        <h3 style="color:#dc2626;">¿Dónde están mis datos?</h3>
        <p style="font-size:14px; color:#334155;">
            El sistema guarda todo en una carpeta llamada <b>'data'</b> dentro de la instalación.
        </p>
        <ul style="font-size:14px; color:#334155;">
            <li><b>Archivo Principal:</b> <code>shillong_2026.json</code> (Aquí están todos sus movimientos).</li>
            <li><b>Bancos:</b> <code>bancos.json</code> (Guarda los saldos iniciales).</li>
            <li><b>Plan Contable:</b> <code>plan_contable_v3.json</code> (Nombres de las cuentas).</li>
        </ul>
        <p style="font-size:14px; color:#334155;">
            <b>¡Importante! Copias de Seguridad:</b><br>
            Vaya a la sección <b>Sistema</b> y pulse "Crear Backup". Esto creará un archivo ZIP con todos sus datos.
            Guarde ese ZIP en un pendrive o en la nube regularmente por seguridad.
        </p>
        """
        self._agregar_seccion(toolbox, "5. Datos, Archivos y Seguridad", html_tecnico)

        # -------------------------------------------------------------
        # 6. HERRAMIENTAS ESPIRITUALES
        # -------------------------------------------------------------
        html_spirit = """
        <h3 style="color:#0ea5e9;">Alimento para el Alma</h3>
        <p style="font-size:14px; color:#334155;">
            Porque este trabajo también requiere paz mental, hemos incluido en <b>Herramientas</b>:
        </p>
        <ul style="font-size:14px; color:#334155;">
            <li><b>Salmos:</b> Una palabra bíblica de aliento seleccionada al azar.</li>
            <li><b>Nombres de Dios:</b> Meditaciones breves con los 72 Nombres en hebreo para momentos de necesidad.</li>
        </ul>
        """
        self._agregar_seccion(toolbox, "6. Inspiración Diaria", html_spirit)

        content_layout.addWidget(toolbox)
        content_layout.addStretch() 
        
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

    def _agregar_seccion(self, toolbox, titulo, html_content):
        page = QWidget()
        page.setStyleSheet("background-color: white;") 
        
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(20, 20, 20, 20)
        
        label = QLabel()
        label.setTextFormat(Qt.RichText)
        label.setText(html_content)
        label.setWordWrap(True)
        label.setStyleSheet("border: none; background-color: transparent;")
        label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        scroll_interno = QScrollArea()
        scroll_interno.setWidget(label)
        scroll_interno.setWidgetResizable(True)
        scroll_interno.setFrameShape(QFrame.NoFrame)
        scroll_interno.setStyleSheet("background-color: white; border: none;")
        
        page_layout.addWidget(scroll_interno)
        
        toolbox.addItem(page, titulo)