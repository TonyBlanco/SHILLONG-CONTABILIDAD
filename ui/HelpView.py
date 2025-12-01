# -*- coding: utf-8 -*-
"""
HelpView.py — SHILLONG CONTABILIDAD v3.7.1 PRO
Manual de usuario actualizado con IA y herramientas de reparación.
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
        
        lbl_subtitulo = QLabel(
            'Manual completo de Shillong Contabilidad v3.7.1 PRO\n'
            'Incluye instrucciones para las nuevas funciones inteligentes.'
        )
        lbl_subtitulo.setStyleSheet("font-size: 14px; color: #64748b; margin-top: 8px; font-weight: 500;")
        lbl_subtitulo.setWordWrap(True)
        
        header_layout.addWidget(lbl_titulo)
        header_layout.addWidget(lbl_subtitulo)
        layout.addWidget(header)

        # --- CONTENIDO SCROLL ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea { background-color: #f1f5f9; border: none; }
            QScrollBar:vertical { width: 12px; background: #f1f5f9; border-radius: 6px; }
            QScrollBar::handle:vertical { background: #cbd5e1; border-radius: 6px; }
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
                padding-left: 15px;
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
        <h3 style="color:#2563eb;">Bienvenida a su Sistema Contable Inteligente</h3>
        <p style="font-size:14px; color:#334155;">
            Shillong Contabilidad v3.7 no es solo una calculadora; es un asistente que aprende de usted.
            Ahora incluye detección automática de errores y aprendizaje de conceptos nuevos.
        </p>
        """
        self._agregar_seccion(toolbox, "1. Introducción y Novedades", html_intro)

        # -------------------------------------------------------------
        # 2. CÓMO ENSEÑAR AL SISTEMA (NUEVO)
        # -------------------------------------------------------------
        html_ia = """
        <h3 style="color:#8b5cf6;">🧠 El Botón Violeta: Auto-Aprendizaje</h3>
        <p style="font-size:14px; color:#334155;">
            <b>Problema:</b> A veces compra productos nuevos (ej: "Masala Dosa", "Nuevas medicinas") y el Excel sale desordenado porque el sistema no sabe qué son.
        </p>
        <p style="font-size:14px; color:#334155;">
            <b>Solución:</b> 
            <ol>
                <li>Registre sus gastos normalmente (aunque sean conceptos nuevos).</li>
                <li>Vaya a <b>Herramientas</b>.</li>
                <li>Pulse el botón violeta <b>"🧠 Auto-Aprender Conceptos"</b>.</li>
            </ol>
            El sistema revisará todo lo que ha escrito, aprenderá que "Masala Dosa" es comida (porque usted lo puso en la cuenta de comida) y la próxima vez lo clasificará automáticamente.
        </p>
        """
        self._agregar_seccion(toolbox, "2. Inteligencia Artificial (Enseñar conceptos nuevos)", html_ia)

        # -------------------------------------------------------------
        # 3. SOLUCIÓN DE ERRORES (NUEVO)
        # -------------------------------------------------------------
        html_fix = """
        <h3 style="color:#db2777;">🔧 El Botón Rosa: Reparación de Emergencia</h3>
        <p style="font-size:14px; color:#334155;">
            <b>¿Cuándo usarlo?</b><br>
            Si ve que su saldo en el banco es enorme e irreal, o si los gráficos dicen que tiene muchos "Ingresos" cuando en realidad solo ha tenido gastos.
        </p>
        <p style="font-size:14px; color:#334155;">
            <b>¿Qué hace?</b><br>
            Esto ocurre si al importar un Excel los gastos se pusieron en la columna "Haber" por error. 
            Al pulsar el botón rosa en <b>Herramientas</b>, el sistema busca todos esos errores y los invierte automáticamente.
        </p>
        """
        self._agregar_seccion(toolbox, "3. Solución de Problemas (Saldo incorrecto)", html_fix)

        # -------------------------------------------------------------
        # 4. IMPORTACIÓN DE EXCEL
        # -------------------------------------------------------------
        html_import = """
        <h3 style="color:#0d9488;">Importar desde Banco (Excel)</h3>
        <p style="font-size:14px; color:#334155;">
            Puede cargar el extracto del banco directamente. El archivo Excel debe tener una fila de títulos con:
        </p>
        <table border="1" cellspacing="0" cellpadding="5" style="border-collapse:collapse; width:100%; font-size:13px; color:#334155; border-color:#cbd5e1;">
            <tr style="background-color:#e2e8f0;">
                <th>Columna</th>
                <th>Nombres Aceptados</th>
            </tr>
            <tr>
                <td><b>Fecha</b></td>
                <td>fecha, date</td>
            </tr>
            <tr>
                <td><b>Concepto</b></td>
                <td>concepto, descripción, detalle, narration</td>
            </tr>
            <tr>
                <td><b>Importe</b></td>
                <td>debe, gasto, withdrawal, debit (para salidas)<br>haber, ingreso, deposit, credit (para entradas)</td>
            </tr>
        </table>
        <p style="font-size:13px; color:#64748b; margin-top:10px;">
            * Si su banco pone todo en una sola columna con signo menos (-), el sistema intentará entenderlo, pero es mejor separarlo en Debe/Haber.
        </p>
        """
        self._agregar_seccion(toolbox, "4. Importación de Extractos Bancarios", html_import)

        # -------------------------------------------------------------
        # 5. CIERRE Y EXPORTACIÓN
        # -------------------------------------------------------------
        html_cierre = """
        <h3 style="color:#2563eb;">Finalizar el Mes</h3>
        <ul style="font-size:14px; color:#334155;">
            <li><b>Dashboard:</b> Revise que el saldo "Caja" coincida con el dinero real en la caja física.</li>
            <li><b>Cierre Mensual:</b> Vaya a esta pantalla para ver el resumen.</li>
            <li><b>Exportar:</b> Use el botón azul "Exportar como..." para sacar el <b>Libro Diario Mensual</b> en Excel para la auditoría.</li>
        </ul>
        """
        self._agregar_seccion(toolbox, "5. Cierre Mensual y Reportes", html_cierre)

        # -------------------------------------------------------------
        # 6. COPIAS DE SEGURIDAD
        # -------------------------------------------------------------
        html_backup = """
        <h3 style="color:#ea580c;">Seguridad de Datos</h3>
        <p style="font-size:14px; color:#334155;">
            <b>¡Muy Importante!</b><br>
            Haga una copia de seguridad (Backup) al menos una vez al mes.
            Vaya a <b>Herramientas > Backup</b> y guarde el archivo generado en un pendrive o enviéselo por correo a usted misma.
        </p>
        """
        self._agregar_seccion(toolbox, "6. Copias de Seguridad (Backups)", html_backup)

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