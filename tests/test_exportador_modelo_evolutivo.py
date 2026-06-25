import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PySide6.QtWidgets import QApplication

from models.ExportadorModeloEvolutivo import _parse_template_code, _resolve_template_mode, _rollup
from ui.InformesView import InformesView


class _MockData:
    def __init__(self):
        self.cuentas = {}
        self.movimientos = []


class TestModeloEvolutivoTemplateCodes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_parse_template_code_distinguishes_group_and_exact(self):
        self.assertEqual(_parse_template_code("602-400"), ("602400", "group"))
        self.assertEqual(_parse_template_code("602.40"), ("602400", "exact"))

    def test_resolve_template_mode_uses_sheet_context(self):
        sheet_codes = [
            ("602400", "602400"),
            ("602.40", "602400"),
            ("602.401", "602401"),
            ("650.10", "650100"),
            ("650.11", "650110"),
            ("758.00", "758000"),
            ("758.1", "758100"),
            ("759", "759000"),
            ("759.10", "759100"),
        ]
        candidate_codes = {code for _, code in sheet_codes}

        self.assertEqual(_resolve_template_mode("602.40", "602400", sheet_codes, candidate_codes), "exact")
        self.assertEqual(_resolve_template_mode("650.10", "650100", sheet_codes, candidate_codes), "group")
        self.assertEqual(_resolve_template_mode("758.00", "758000", sheet_codes, candidate_codes), "group")
        self.assertEqual(_resolve_template_mode("759.10", "759100", sheet_codes, candidate_codes), "exact")

    def test_rollup_group_and_exact_do_not_collide(self):
        totales = {
            "602400": {"cur_banco": 7651.0, "cur_caja": 0.0, "prev_total": 0.0},
            "602401": {"cur_banco": 120.0, "cur_caja": 0.0, "prev_total": 0.0},
            "602403": {"cur_banco": 80.0, "cur_caja": 0.0, "prev_total": 0.0},
        }

        self.assertEqual(_rollup("602400", totales, mode="exact"), (7651.0, 0.0, 0.0))
        self.assertEqual(_rollup("602400", totales, mode="group"), (7851.0, 0.0, 0.0))

    def test_informes_view_uses_same_group_vs_exact_rule(self):
        view = InformesView(_MockData())
        codigos = {"602400", "602401", "602403", "650100", "650110", "758000", "758100", "759000", "759100"}
        totales = {
            "602400": {"cur_banco": 7651.0, "cur_caja": 0.0, "prev_total": 0.0},
            "602401": {"cur_banco": 120.0, "cur_caja": 0.0, "prev_total": 0.0},
            "602403": {"cur_banco": 80.0, "cur_caja": 0.0, "prev_total": 0.0},
            "650110": {"cur_banco": 2995.0, "cur_caja": 0.0, "prev_total": 0.0},
            "758100": {"cur_banco": 297852.0, "cur_caja": 0.0, "prev_total": 0.0},
            "759100": {"cur_banco": 6000.0, "cur_caja": 0.0, "prev_total": 0.0},
        }
        sheet_codes = [
            ("602400", "602400"),
            ("602.40", "602400"),
            ("602.401", "602401"),
            ("650.10", "650100"),
            ("650.11", "650110"),
            ("758.00", "758000"),
            ("758.1", "758100"),
            ("759", "759000"),
            ("759.10", "759100"),
        ]

        cuenta_grupo, mode_grupo = view._parsear_codigo_template("602-400", codigos)
        cuenta_exacta, mode_exacto = view._parsear_codigo_template("602.40", codigos)
        _, mode_65010 = view._parsear_codigo_template("650.10", codigos)
        _, mode_75800 = view._parsear_codigo_template("758.00", codigos)
        _, mode_75910 = view._parsear_codigo_template("759.10", codigos)

        mode_grupo = view._resolver_modo_codigo_template("602-400", cuenta_grupo, sheet_codes, codigos)
        mode_exacto = view._resolver_modo_codigo_template("602.40", cuenta_exacta, sheet_codes, codigos)
        mode_65010 = view._resolver_modo_codigo_template("650.10", "650100", sheet_codes, codigos)
        mode_75800 = view._resolver_modo_codigo_template("758.00", "758000", sheet_codes, codigos)
        mode_75910 = view._resolver_modo_codigo_template("759.10", "759100", sheet_codes, codigos)

        self.assertEqual(
            view._rollup_sisters(cuenta_grupo, totales, mode=mode_grupo),
            {"cur_banco": 7851.0, "cur_caja": 0.0, "prev_total": 0.0},
        )
        self.assertEqual(
            view._rollup_sisters(cuenta_exacta, totales, mode=mode_exacto),
            {"cur_banco": 7651.0, "cur_caja": 0.0, "prev_total": 0.0},
        )
        self.assertEqual(mode_65010, "group")
        self.assertEqual(mode_75800, "group")
        self.assertEqual(mode_75910, "exact")


if __name__ == "__main__":
    unittest.main()
