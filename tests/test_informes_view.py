import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QApplication, QTableWidget

from ui.InformesView import InformesView


class MockData:
    def __init__(self):
        self.cuentas = {
            "211000": {"nombre": "Edificios"},
            "602100": {"nombre": "Combustibles"},
        }
        self.movimientos = [
            {
                "fecha": "10/01/2026",
                "cuenta": "211000",
                "debe": 100.0,
                "haber": 0.0,
                "nombre_cuenta": "Edificios",
                "banco": "Caja",
            },
            {
                "fecha": "20/05/2026",
                "cuenta": "211000",
                "debe": 0.0,
                "haber": 40.0,
                "nombre_cuenta": "Edificios",
                "banco": "BBVA",
            },
            {
                "fecha": "15/06/2026",
                "cuenta": "602100",
                "debe": 70.0,
                "haber": 0.0,
                "nombre_cuenta": "Combustibles",
                "banco": "Caja",
            },
        ]

    def obtener_nombre_cuenta(self, cuenta):
        return self.cuentas.get(str(cuenta), {}).get("nombre", "")


class TestInformesView(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.view = InformesView(MockData())

    def test_reporte_por_cuentas_filtra_cuenta_con_separador_largo(self):
        self.view.cbo_tipo.setCurrentIndex(4)
        self.view.fecha_ini.setDate(QDate(2026, 1, 1))
        self.view.fecha_fin.setDate(QDate(2026, 5, 31))
        self.view.cbo_cuenta.setCurrentText("211000 — Edificios")

        datos = self.view._obtener_datos_reporte_por_cuentas()

        self.assertEqual(len(datos), 1)
        self.assertEqual(datos[0][0], "211000")
        self.assertEqual(len(datos[0][2]), 2)

    def test_ruta_exporte_por_defecto_usa_reportes_y_nombre_del_informe(self):
        self.view.cbo_tipo.setCurrentIndex(6)
        self.view.fecha_ini.setDate(QDate(2026, 1, 1))
        self.view.fecha_fin.setDate(QDate(2026, 6, 30))

        ruta = Path(self.view._ruta_exporte_por_defecto())

        self.assertEqual(ruta.parent.name, "reportes")
        self.assertEqual(ruta.name, "CashFlow_Mensual_20260101_20260630.xlsx")

    def test_balance_sumas_saldos_respeta_rango_fechas(self):
        self.view.cbo_tipo.setCurrentIndex(2)
        self.view.fecha_ini.setDate(QDate(2026, 1, 1))
        self.view.fecha_fin.setDate(QDate(2026, 5, 31))

        self.view._limpiar_vista()
        self.view._mostrar_sumas_saldos()

        tabla = self.view.contenedor_layout.itemAt(0).widget()
        self.assertIsInstance(tabla, QTableWidget)
        self.assertEqual(tabla.rowCount(), 2)
        self.assertEqual(tabla.item(0, 0).text(), "211000")
        self.assertEqual(tabla.item(0, 2).text(), "100.0")
        self.assertEqual(tabla.item(0, 3).text(), "40.0")

    def test_flujo_caja_mensual_agrupa_por_mes(self):
        self.view.cbo_tipo.setCurrentIndex(6)
        self.view.fecha_ini.setDate(QDate(2026, 1, 1))
        self.view.fecha_fin.setDate(QDate(2026, 6, 30))

        self.view._limpiar_vista()
        self.view._mostrar_flujo_caja_mensual()

        tabla = self.view.contenedor_layout.itemAt(0).widget()
        self.assertIsInstance(tabla, QTableWidget)
        self.assertEqual(tabla.rowCount(), 4)
        self.assertEqual(tabla.item(0, 0).text(), "Enero 2026")
        self.assertEqual(tabla.item(0, 1).text(), "0.0")
        self.assertEqual(tabla.item(0, 2).text(), "0.0")
        self.assertEqual(tabla.item(0, 3).text(), "0.0")
        self.assertEqual(tabla.item(0, 4).text(), "100.0")
        self.assertEqual(tabla.item(1, 0).text(), "Mayo 2026")
        self.assertEqual(tabla.item(1, 1).text(), "40.0")
        self.assertEqual(tabla.item(1, 2).text(), "0.0")
        self.assertEqual(tabla.item(1, 3).text(), "0.0")
        self.assertEqual(tabla.item(1, 4).text(), "0.0")
        self.assertEqual(tabla.item(2, 0).text(), "Junio 2026")
        self.assertEqual(tabla.item(2, 4).text(), "70.0")
        self.assertEqual(tabla.item(3, 0).text(), "TOTAL")

        tabla_bancos = self.view.contenedor_layout.itemAt(2).widget()
        self.assertIsInstance(tabla_bancos, QTableWidget)
        self.assertEqual(tabla_bancos.rowCount(), 3)
        self.assertEqual(tabla_bancos.item(0, 0).text(), "Enero 2026")
        self.assertEqual(tabla_bancos.item(0, 1).text(), "Caja")
        self.assertEqual(tabla_bancos.item(0, 3).text(), "100.0")
        self.assertEqual(tabla_bancos.item(1, 1).text(), "BBVA")
        self.assertEqual(tabla_bancos.item(1, 2).text(), "40.0")



if __name__ == "__main__":
    unittest.main()
