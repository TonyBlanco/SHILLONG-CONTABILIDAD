import sys
import json
import datetime
from pathlib import Path

# Ensure project root is on sys.path (this script lives in tools/)
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Simulate PyInstaller _MEIPASS so ruta_recurso() points to dist/_internal
sys._MEIPASS = r'D:\ShillongV3\dist\SHILLONG_v3_PRO\_internal'

from PySide6.QtWidgets import QApplication
from ui.InformesView import InformesView

class MockData:
    def __init__(self):
        with open('data/shillong_2026.json', 'r', encoding='utf-8') as f:
            d = json.load(f)
            self.movimientos = d.get('movimientos', [])
            self.cuentas = d.get('cuentas', {})

app = QApplication([])

data = MockData()
iv = InformesView(data)

# Set up to export sisters model (same as test_informes)
iv.cbo_tipo.setCurrentIndex(5)
iv.fecha_ini.setDate(datetime.date(2025, 11, 1))
iv.fecha_fin.setDate(datetime.date(2026, 1, 31))

iv._exportar_excel_modelo_sisters('test_out_frozen.xlsx')
print('Done exporting test_out_frozen.xlsx')
