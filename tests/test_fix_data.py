import unittest
import json
import os
from pathlib import Path
from unittest.mock import patch, mock_open

# Add the parent directory to the path to allow importing fix_data
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models.fix_data import reparar_json

class TestFixData(unittest.TestCase):

    def setUp(self):
        """Set up a temporary directory for test files."""
        self.test_dir = Path("tests/temp_data")
        self.test_dir.mkdir(exist_ok=True)
        self.addCleanup(self.cleanup_test_dir)

    def cleanup_test_dir(self):
        """Remove the temporary directory and its contents."""
        for f in self.test_dir.glob("*"):
            f.unlink()
        self.test_dir.rmdir()

    def create_mock_json(self, file_name, data):
        """Helper to create a JSON file in the temp directory."""
        path = self.test_dir / file_name
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        return path

    def test_no_changes_needed(self):
        """Test with a file where all data is correct."""
        mock_data = {
            "movimientos": [
                {"cuenta": "603000", "debe": 50.0, "haber": 0.0, "saldo": -50.0, "concepto": "Gasto correcto"},
                {"cuenta": "700000", "debe": 0.0, "haber": 100.0, "saldo": 100.0, "concepto": "Ingreso correcto"}
            ]
        }
        mock_file_path = self.create_mock_json("correct_data.json", mock_data)

        # Keep original data for comparison
        original_data = mock_data.copy()

        with patch('builtins.print') as mock_print:
            reparar_json(mock_file_path)

        with open(mock_file_path, "r", encoding="utf-8") as f:
            repaired_data = json.load(f)

        self.assertEqual(original_data, repaired_data, "The file should not have been modified.")
        mock_print.assert_any_call("\n👍 Todo parece correcto. No se encontraron errores de Debe/Haber.")

    def test_fix_debe_haber_error(self):
        """Test a file with a clear debe/haber error that needs fixing."""
        mock_data = {
            "movimientos": [
                {"cuenta": "603000", "debe": 0.0, "haber": 75.0, "saldo": 75.0, "concepto": "Gasto mal registrado"}
            ]
        }
        mock_file_path = self.create_mock_json("error_data.json", mock_data)

        with patch('builtins.print'):
            reparar_json(mock_file_path)

        with open(mock_file_path, "r", encoding="utf-8") as f:
            repaired_data = json.load(f)

        repaired_mov = repaired_data["movimientos"][0]
        self.assertEqual(repaired_mov["debe"], 75.0)
        self.assertEqual(repaired_mov["haber"], 0.0)
        self.assertEqual(repaired_mov["saldo"], -75.0, "Saldo should be inverted after correction.")

    def test_mixed_data_only_fixes_error(self):
        """Test that only incorrect entries are modified."""
        mock_data = {
            "movimientos": [
                {"cuenta": "603000", "debe": 50.0, "haber": 0.0, "saldo": -50.0, "concepto": "Gasto correcto"},
                {"cuenta": "604000", "debe": 0.0, "haber": 120.0, "saldo": 120.0, "concepto": "Gasto mal registrado"},
                {"cuenta": "700000", "debe": 0.0, "haber": 200.0, "saldo": 200.0, "concepto": "Ingreso correcto"}
            ]
        }
        mock_file_path = self.create_mock_json("mixed_data.json", mock_data)

        with patch('builtins.print'):
            reparar_json(mock_file_path)

        with open(mock_file_path, "r", encoding="utf-8") as f:
            repaired_data = json.load(f)
        
        # Correct expense entry should be unchanged
        self.assertEqual(repaired_data["movimientos"][0]["debe"], 50.0)
        self.assertEqual(repaired_data["movimientos"][0]["haber"], 0.0)

        # Incorrect expense entry should be fixed
        self.assertEqual(repaired_data["movimientos"][1]["debe"], 120.0)
        self.assertEqual(repaired_data["movimientos"][1]["haber"], 0.0)
        self.assertEqual(repaired_data["movimientos"][1]["saldo"], -120.0)
        
        # Correct income entry should be unchanged
        self.assertEqual(repaired_data["movimientos"][2]["debe"], 0.0)
        self.assertEqual(repaired_data["movimientos"][2]["haber"], 200.0)

    def test_ignores_non_gasto_accounts(self):
        """Test that an income account (e.g., starting with '7') with haber > 0 is not modified."""
        mock_data = {
            "movimientos": [
                {"cuenta": "705000", "debe": 0.0, "haber": 500.0, "saldo": 500.0, "concepto": "Donación"}
            ]
        }
        mock_file_path = self.create_mock_json("income_data.json", mock_data)
        original_data = mock_data.copy()

        with patch('builtins.print'):
            reparar_json(mock_file_path)

        with open(mock_file_path, "r", encoding="utf-8") as f:
            repaired_data = json.load(f)

        self.assertEqual(original_data, repaired_data, "Income accounts should not be 'repaired'.")

    def test_ignores_non_gasto_accounts(self):
        """Test that an entry with a non-numeric account name is not modified by this repair function."""
        mock_data = {
            "movimientos": [
                {"cuenta": "Teléfonos", "debe": 0.0, "haber": 99.0, "saldo": 99.0, "concepto": "Gasto con cuenta corrupta"}
            ]
        }
        mock_file_path = self.create_mock_json("corrupt_cuenta.json", mock_data)
        original_data = mock_data.copy()

        with patch('builtins.print'):
            reparar_json(mock_file_path)

        with open(mock_file_path, "r", encoding="utf-8") as f:
            repaired_data = json.load(f)

        self.assertEqual(original_data, repaired_data, "The script should not modify entries where the account is not a numeric ID.")


if __name__ == '__main__':
    unittest.main()
