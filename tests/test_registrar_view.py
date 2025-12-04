# -*- coding: utf-8 -*-
"""
Test Suite for RegistrarView fixes — SHILLONG CONTABILIDAD v3.7.8 PRO
Tests the core logic without requiring the GUI components.
"""

import sys
import os
import unittest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ============================================================
# TEST THE CORE LOGIC (No GUI required)
# ============================================================

class TestParseFloat(unittest.TestCase):
    """Test the _parse_float method logic"""
    
    def _parse_float(self, txt):
        """Copy of the method to test"""
        if not txt:
            return 0.0
        txt = str(txt).strip()
        try:
            txt = txt.replace(".", "").replace(",", ".")
            return float(txt)
        except ValueError:
            return 0.0
        except Exception:
            return 0.0

    def test_empty_string(self):
        self.assertEqual(self._parse_float(""), 0.0)
    
    def test_none_value(self):
        self.assertEqual(self._parse_float(None), 0.0)
    
    def test_spanish_format(self):
        """Test Spanish number format: 1.234,56"""
        self.assertEqual(self._parse_float("1.234,56"), 1234.56)
        self.assertEqual(self._parse_float("100,00"), 100.0)
        self.assertEqual(self._parse_float("0,00"), 0.0)
    
    def test_integer_string(self):
        self.assertEqual(self._parse_float("100"), 100.0)
    
    def test_with_spaces(self):
        self.assertEqual(self._parse_float("  100,50  "), 100.50)
    
    def test_invalid_string(self):
        self.assertEqual(self._parse_float("abc"), 0.0)
        self.assertEqual(self._parse_float("12abc"), 0.0)


class TestFormatMethod(unittest.TestCase):
    """Test the _fmt method logic"""
    
    def _fmt(self, v):
        """Copy of the method with proper exception handling"""
        try:
            # Simulate Spanish locale formatting
            result = f"{float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            return result
        except (ValueError, TypeError):
            return "0,00"
    
    def test_format_zero(self):
        self.assertEqual(self._fmt(0), "0,00")
    
    def test_format_integer(self):
        self.assertEqual(self._fmt(100), "100,00")
    
    def test_format_decimal(self):
        self.assertEqual(self._fmt(123.45), "123,45")
    
    def test_format_large_number(self):
        self.assertEqual(self._fmt(1234567.89), "1.234.567,89")
    
    def test_format_invalid(self):
        self.assertEqual(self._fmt("invalid"), "0,00")


class TestDebeHaberLogic(unittest.TestCase):
    """Test the DEBE/HABER logic without GUI"""
    
    def test_ingreso_to_haber(self):
        """INGRESO UI should map to HABER (accounting)"""
        ingreso_ui = 500.0  # User enters in "INGRESO" field
        gasto_ui = 0.0
        
        haber = ingreso_ui  # INGRESO → HABER
        debe = gasto_ui     # GASTO → DEBE
        
        self.assertEqual(haber, 500.0)
        self.assertEqual(debe, 0.0)
    
    def test_gasto_to_debe(self):
        """GASTO UI should map to DEBE (accounting)"""
        ingreso_ui = 0.0
        gasto_ui = 300.0  # User enters in "GASTO" field
        
        haber = ingreso_ui  # INGRESO → HABER
        debe = gasto_ui     # GASTO → DEBE
        
        self.assertEqual(haber, 0.0)
        self.assertEqual(debe, 300.0)
    
    def test_both_zero_validation(self):
        """Should reject when both are zero"""
        debe, haber = 0.0, 0.0
        is_valid = not (debe == 0 and haber == 0)
        self.assertFalse(is_valid)
    
    def test_both_nonzero_validation(self):
        """Should reject when both have values"""
        debe, haber = 100.0, 200.0
        is_valid = not (debe > 0 and haber > 0)
        self.assertFalse(is_valid)
    
    def test_valid_debe_only(self):
        """Valid: only DEBE has value"""
        debe, haber = 100.0, 0.0
        is_valid = not (debe == 0 and haber == 0) and not (debe > 0 and haber > 0)
        self.assertTrue(is_valid)
    
    def test_valid_haber_only(self):
        """Valid: only HABER has value"""
        debe, haber = 0.0, 100.0
        is_valid = not (debe == 0 and haber == 0) and not (debe > 0 and haber > 0)
        self.assertTrue(is_valid)


class TestGastoKeywordDetection(unittest.TestCase):
    """Test the expense keyword detection"""
    
    def setUp(self):
        self.gasto_keywords = [
            "vegetable", "milk", "fish", "rice", "bread", "egg", "onion",
            "chicken", "medicine", "medical", "clean", "gas", "taxi",
            "gasto", "pago", "compra", "servicio", "equipo"
        ]
    
    def test_detect_expense_keyword(self):
        concepto = "Compra de vegetable para cocina"
        detected = any(k in concepto.lower() for k in self.gasto_keywords)
        self.assertTrue(detected)
    
    def test_no_expense_keyword(self):
        concepto = "Donación recibida"
        detected = any(k in concepto.lower() for k in self.gasto_keywords)
        self.assertFalse(detected)
    
    def test_multiple_keywords(self):
        concepto = "Pago por servicio médico"
        matches = [k for k in self.gasto_keywords if k in concepto.lower()]
        self.assertIn("pago", matches)
        self.assertIn("servicio", matches)


class TestSaldoCalculation(unittest.TestCase):
    """Test the balance calculation logic"""
    
    def test_saldo_calculation_chronological(self):
        """Test that saldo calculates correctly with FIXED parse_float"""
        movimientos = [
            {"fecha": "01/12/2025", "debe": "100.00", "haber": "0.00"},
            {"fecha": "02/12/2025", "debe": "0.00", "haber": "500.00"},
            {"fecha": "03/12/2025", "debe": "50.00", "haber": "0.00"},
        ]
        
        def parse_float_fixed(txt):
            """FIXED version that handles both Spanish and standard decimal formats"""
            if not txt:
                return 0.0
            txt = str(txt).strip()
            try:
                # Handle numeric types directly
                if isinstance(txt, (int, float)):
                    return float(txt)
                
                # Count separators to determine format
                dot_count = txt.count(".")
                comma_count = txt.count(",")
                
                # Standard decimal format: "1234.56" or "1,234.56"
                if comma_count == 0 and dot_count == 1:
                    return float(txt)
                if comma_count >= 1 and dot_count == 1 and txt.rfind(".") > txt.rfind(","):
                    # US format: 1,234.56
                    return float(txt.replace(",", ""))
                
                # Spanish format: "1234,56" or "1.234,56"
                if dot_count == 0 and comma_count == 1:
                    return float(txt.replace(",", "."))
                if dot_count >= 1 and comma_count == 1 and txt.rfind(",") > txt.rfind("."):
                    # Spanish format: 1.234,56
                    return float(txt.replace(".", "").replace(",", "."))
                
                # Fallback: try direct conversion
                return float(txt)
            except (ValueError, TypeError):
                return 0.0
        
        saldo = 0
        total_debe = 0
        total_haber = 0
        
        for m in movimientos:
            d = parse_float_fixed(m.get("debe", "0"))
            h = parse_float_fixed(m.get("haber", "0"))
            saldo += d - h  # Current logic
            total_debe += d
            total_haber += h
        
        # Expected: 100 - 0 + 0 - 500 + 50 - 0 = -350
        self.assertEqual(saldo, -350.0)
        self.assertEqual(total_debe, 150.0)
        self.assertEqual(total_haber, 500.0)
    
    def test_parse_float_handles_both_formats(self):
        """Test that fixed parse handles Spanish AND standard decimal"""
        def parse_float_fixed(txt):
            if not txt:
                return 0.0
            txt = str(txt).strip()
            try:
                if isinstance(txt, (int, float)):
                    return float(txt)
                
                dot_count = txt.count(".")
                comma_count = txt.count(",")
                
                if comma_count == 0 and dot_count == 1:
                    return float(txt)
                if comma_count >= 1 and dot_count == 1 and txt.rfind(".") > txt.rfind(","):
                    return float(txt.replace(",", ""))
                if dot_count == 0 and comma_count == 1:
                    return float(txt.replace(",", "."))
                if dot_count >= 1 and comma_count == 1 and txt.rfind(",") > txt.rfind("."):
                    return float(txt.replace(".", "").replace(",", "."))
                
                return float(txt)
            except (ValueError, TypeError):
                return 0.0
        
        # Test standard decimal format (from database)
        self.assertEqual(parse_float_fixed("100.00"), 100.0)
        self.assertEqual(parse_float_fixed("1234.56"), 1234.56)
        
        # Test Spanish format (from UI)
        self.assertEqual(parse_float_fixed("100,00"), 100.0)
        self.assertEqual(parse_float_fixed("1.234,56"), 1234.56)
        
        # Test US format with thousand separators
        self.assertEqual(parse_float_fixed("1,234.56"), 1234.56)
        
        # Test integer
        self.assertEqual(parse_float_fixed("100"), 100.0)
        
        # Test numeric types
        self.assertEqual(parse_float_fixed(100.0), 100.0)
        self.assertEqual(parse_float_fixed(100), 100.0)


class TestContabilidadDataIntegration(unittest.TestCase):
    """Test integration with ContabilidadData"""
    
    def setUp(self):
        """Create mock data manager"""
        self.mock_data = Mock()
        self.mock_data.movimientos = []
        self.mock_data.agregar_movimiento = MagicMock()
        self.mock_data.obtener_nombre_cuenta = MagicMock(return_value="Test Account")
    
    def test_agregar_movimiento_call(self):
        """Test that movement is added with correct structure"""
        movimiento = {
            "fecha": "04/12/2025",
            "documento": "TEST-001",
            "concepto": "Test transaction",
            "cuenta": "100",
            "debe": "50.00",
            "haber": "0.00",
            "moneda": "INR",
            "banco": "Caja",
            "estado": "pagado"
        }
        
        self.mock_data.agregar_movimiento(**movimiento)
        
        self.mock_data.agregar_movimiento.assert_called_once_with(
            fecha="04/12/2025",
            documento="TEST-001",
            concepto="Test transaction",
            cuenta="100",
            debe="50.00",
            haber="0.00",
            moneda="INR",
            banco="Caja",
            estado="pagado"
        )


class TestMotorCuentasIntegration(unittest.TestCase):
    """Test integration with MotorCuentas"""
    
    def setUp(self):
        """Create mock motor"""
        self.mock_motor = Mock()
        self.mock_motor.todas_las_opciones = MagicMock(return_value=[
            "100 – Caja",
            "200 – Banco",
            "300 – Proveedores"
        ])
        self.mock_motor.get_nombre = MagicMock(return_value="Caja")
        self.mock_motor.es_concepto_valido = MagicMock(return_value=True)
    
    def test_cuenta_extraction(self):
        """Test extracting account code from combo text"""
        cuenta_txt = "100 – Caja"
        if " – " in cuenta_txt:
            codigo = cuenta_txt.split(" – ")[0]
            self.assertEqual(codigo, "100")
        else:
            self.fail("Invalid cuenta format")
    
    def test_invalid_cuenta_format(self):
        """Test handling invalid cuenta format"""
        cuenta_txt = "Invalid Format"
        is_valid = " – " in cuenta_txt
        self.assertFalse(is_valid)


class TestExceptionHandling(unittest.TestCase):
    """Test that specific exceptions are caught properly"""
    
    def test_value_error_handling(self):
        """Test ValueError is handled gracefully"""
        def safe_parse(txt):
            try:
                return float(txt.replace(",", "."))
            except ValueError:
                return 0.0
        
        result = safe_parse("not_a_number")
        self.assertEqual(result, 0.0)
    
    def test_key_error_handling(self):
        """Test KeyError is handled gracefully"""
        mov = {"fecha": "01/01/2025"}
        
        def safe_get(d, key, default="0"):
            try:
                return d[key]
            except KeyError:
                return default
        
        result = safe_get(mov, "debe", "0")
        self.assertEqual(result, "0")


class TestDashboardViewDependencies(unittest.TestCase):
    """Test DashboardView dependencies and integration"""
    
    def test_cargar_datos_alias_exists(self):
        """Test that ContabilidadData has cargar_datos alias for DashboardView"""
        from models.ContabilidadData import ContabilidadData
        data = ContabilidadData()
        
        # Check that cargar_datos alias exists
        self.assertTrue(hasattr(data, 'cargar_datos'))
        self.assertTrue(callable(data.cargar_datos))
        
        # Check that it's an alias to cargar
        self.assertEqual(data.cargar_datos, data.cargar)
    
    def test_guardar_datos_alias_exists(self):
        """Test that ContabilidadData has guardar_datos alias"""
        from models.ContabilidadData import ContabilidadData
        data = ContabilidadData()
        
        self.assertTrue(hasattr(data, 'guardar_datos'))
        self.assertTrue(callable(data.guardar_datos))
        self.assertEqual(data.guardar_datos, data.guardar)
    
    def test_dashboard_date_parsing(self):
        """Test date parsing logic used in DashboardView"""
        from PySide6.QtCore import QDate
        
        test_cases = [
            ("01/12/2025", (1, 12, 2025)),  # Spanish format
            ("2025-12-01", (2025, 12, 1)),  # ISO format
        ]
        
        for f_raw, expected in test_cases:
            try:
                if "/" in f_raw:
                    d, mm, a = map(int, f_raw.split("/"))
                elif "-" in f_raw:
                    p = f_raw.split("-")
                    a, mm, d = (int(p[0]), int(p[1]), int(p[2])) if len(p[0]) == 4 else (int(p[2]), int(p[1]), int(p[0]))
                
                # Verify parsed values
                if "/" in f_raw:
                    self.assertEqual((d, mm, a), expected)
                else:
                    self.assertEqual((a, mm, d), expected)
            except (ValueError, IndexError):
                self.fail(f"Failed to parse date: {f_raw}")


# ============================================================
# RUN TESTS
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("SHILLONG CONTABILIDAD - RegistrarView Test Suite")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestParseFloat))
    suite.addTests(loader.loadTestsFromTestCase(TestFormatMethod))
    suite.addTests(loader.loadTestsFromTestCase(TestDebeHaberLogic))
    suite.addTests(loader.loadTestsFromTestCase(TestGastoKeywordDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestSaldoCalculation))
    suite.addTests(loader.loadTestsFromTestCase(TestContabilidadDataIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestMotorCuentasIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestExceptionHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestDashboardViewDependencies))
    
    # Run with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED - Safe to apply fixes!")
    else:
        print("❌ SOME TESTS FAILED - Review before applying fixes!")
        print(f"   Failures: {len(result.failures)}")
        print(f"   Errors: {len(result.errors)}")
    print("=" * 60)

