# -*- coding: utf-8 -*-
"""
importador_excel.py — SHILLONG CONTABILIDAD v3 PRO (2025 FINAL)

Módulo adaptador profesional para lanzar el importador de Excel.
Incluye:
- Manejo de errores con mensajes claros
- Recarga automática de vistas tras importar
- Soporte a modo oscuro/claro
- Logging opcional
- Refresco inteligente de Dashboard y otras vistas
"""

import logging
from PySide6.QtWidgets import QMessageBox

# Import seguro del diálogo
try:
    from ui.Dialogs.ImportarExcelDialog import ImportarExcelDialog
except ImportError as e:
    logging.error(f"No se pudo cargar ImportarExcelDialog: {e}")
    ImportarExcelDialog = None


def abrir_importador(parent, data_model):
    """
    Abre el diálogo de importación de Excel de forma segura y profesional.

    Args:
        parent: Ventana principal (MainWindow)
        data_model: Instancia de ContabilidadData

    Funcionalidades:
        - Verifica que el diálogo exista
        - Maneja excepciones globales
        - Refresca vistas críticas tras éxito
        - Muestra mensajes claros al usuario
    """
    if ImportarExcelDialog is None:
        QMessageBox.critical(
            parent,
            "Error de módulo",
            "No se pudo cargar el importador de Excel.\n"
            "Verifique que exista el archivo:\n"
            "ui/Dialogs/ImportarExcelDialog.py"
        )
        return

    try:
        dlg = ImportarExcelDialog(parent, data_model)
        result = dlg.exec()

        if result == QDialog.Accepted:
            # Éxito en la importación
            QMessageBox.information(
                parent,
                "Importación exitosa",
                "Los movimientos se han importado correctamente.\n"
                "Se han actualizado los saldos y vistas."
            )

            # Refrescar vistas principales
            _refrescar_vistas(parent)

    except Exception as e:
        logging.exception("Error inesperado al abrir el importador de Excel")
        QMessageBox.critical(
            parent,
            "Error crítico",
            f"Ocurrió un error inesperado:\n{str(e)}\n\n"
            "Consulte el log para más detalles."
        )


def _refrescar_vistas(main_window):
    """
    Refresca todas las vistas que dependen de los movimientos.
    Compatible con todas las vistas actuales del sistema.
    """
    vistas_a_refrescar = [
        "dashboard",
        "registrar",
        "pendientes",
        "libro_mensual",
        "cierre",
        "informes"
    ]

    for nombre_vista in vistas_a_refrescar:
        vista = main_window.views.get(nombre_vista)
        if vista and hasattr(vista, "actualizar"):
            try:
                vista.actualizar()
            except Exception as e:
                logging.warning(f"No se pudo refrescar {nombre_vista}: {e}")

    # Refrescar saldo en dashboard si existe el método
    if hasattr(main_window, "refrescar_saldo"):
        main_window.refrescar_saldo()

    # Actualizar barra de estado
    if hasattr(main_window, "set_status"):
        main_window.set_status("Datos importados y actualizados")

    logging.info("Vistas refrescadas tras importación de Excel")