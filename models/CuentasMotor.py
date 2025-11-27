# -*- coding: utf-8 -*-
"""
Motor de Cuentas v3 — Versión Final (COMPATIBLE CON EXE)
==================================================
✔ Compatible con plan_contable_v3.json
✔ Compatible con reglas_conceptos.json
✔ Funciona en desarrollo y en .exe
✔ Usa ruta_recurso() para PyInstaller
"""

import json
from utils.rutas import ruta_recurso


class MotorCuentas:

    def __init__(self):
        self.cuentas = {}
        self.reglas = {}
        self.subcategorias = {
            "Huevos": "Huevos",
            "Leche": "Leche",
            "Pan": "Panadería",
            "Verduras": "Verduras",
            "Carne": "Carne",
            "Pollo": "Pollo",
            "Café": "Café",
        }

        # Cargar datos usando rutas compatibles con EXE
        self._cargar()
        self._cargar_reglas()

    # ---------------------------------------------------------
    def _cargar(self):
        """Carga el plan contable completo v3."""
        path = ruta_recurso("data/plan_contable_v3.json")
        if not path.exists():
            print(f"ADVERTENCIA: No se encontró {path}")
            return

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.cuentas = {
            codigo: datos
            for codigo, datos in data.items()
        }

    # ---------------------------------------------------------
    def _cargar_reglas(self):
        """Carga reglas_conceptos.json con validación."""
        path = ruta_recurso("data/reglas_conceptos.json")
        if not path.exists():
            print("ADVERTENCIA: No se encontró reglas_conceptos.json. Validación desactivada.")
            self.reglas = {}
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                self.reglas = json.load(f)
        except Exception as e:
            print(f"ERROR cargando reglas_conceptos.json: {e}")
            self.reglas = {}

    # ---------------------------------------------------------
    def listar_codigos(self):
        return sorted(self.cuentas.keys())

    # ---------------------------------------------------------
    def get_nombre(self, codigo):
        return self.cuentas.get(str(codigo), {}).get("nombre", "Cuenta sin nombre")

    # ---------------------------------------------------------
    def get_descripcion(self, codigo):
        return self.cuentas.get(str(codigo), {}).get("descripcion", "")

    # ---------------------------------------------------------
    def get_combo_display(self, codigo):
        nombre = self.get_nombre(codigo)
        return f"{codigo} – {nombre}"

    # ---------------------------------------------------------
    def todas_las_opciones(self):
        lista = []
        for codigo in self.listar_codigos():
            lista.append(self.get_combo_display(codigo))
        for sub in self.subcategorias:
            lista.append(f"SUB – {sub}")
        return lista

    # ---------------------------------------------------------
    def filtrar(self, texto):
        texto = texto.lower().strip()
        if not texto:
            return self.todas_las_opciones()
        return [item for item in self.todas_las_opciones() if texto in item.lower()]

    # ---------------------------------------------------------
    def es_subcategoria(self, valor):
        return valor.startswith("SUB – ")

    # ---------------------------------------------------------
    def extraer_nombre_subcategoria(self, valor):
        return valor.replace("SUB – ", "").strip()

    # ---------------------------------------------------------
    def es_concepto_valido(self, codigo, concepto):
        codigo = str(codigo).strip()
        if codigo not in self.reglas:
            return True
        concepto = concepto.lower()
        return any(palabra.lower() in concepto for palabra in self.reglas[codigo].get("permitidos", []))