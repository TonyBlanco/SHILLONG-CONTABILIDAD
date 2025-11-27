# -*- coding: utf-8 -*-
"""
Motor de Cuentas v3 — Versión Final
==================================================
✔ Compatible con plan_contable_v3.json
✔ Compatible con reglas_conceptos.json
✔ Lee: código → {nombre, descripcion}
✔ Validación concepto ↔ cuenta contable
✔ Devuelve lista de cuentas: "600000 – Compra de farmacia"
✔ Obtiene descripción oficial
✔ Mantiene SUB-categorías opcionales
✔ 100% compatible con RegistrarView v3
"""

import json
from pathlib import Path


class MotorCuentas:

    def __init__(self, archivo_json="data/plan_contable_v3.json"):
        self.archivo_json = Path(archivo_json)
        self.cuentas = {}
        self.reglas = {}  # reglas concepto ↔ cuenta
        self.subcategorias = {
            "Huevos": "Huevos",
            "Leche": "Leche",
            "Pan": "Panadería",
            "Verduras": "Verduras",
            "Carne": "Carne",
            "Pollo": "Pollo",
            "Café": "Café",
        }

        # Cargar datos
        self._cargar()          # plan contable
        self._cargar_reglas()   # reglas concepto-cuenta


    # ---------------------------------------------------------
    def _cargar(self):
        """Carga el plan contable completo v3."""
        if not self.archivo_json.exists():
            raise FileNotFoundError(f"No existe {self.archivo_json}")

        with self.archivo_json.open("r", encoding="utf-8") as f:
            data = json.load(f)

        # data = {"622000": {"nombre": "...", "descripcion": "..."}}
        self.cuentas = {
            codigo: datos
            for codigo, datos in data.items()
        }


    # ---------------------------------------------------------
    def _cargar_reglas(self):
        """Carga reglas_conceptos.json con validación."""
        ruta_reglas = Path("data/reglas_conceptos.json")

        if not ruta_reglas.exists():
            print("⚠ ADVERTENCIA: No se encontró reglas_conceptos.json. Validación desactivada.")
            self.reglas = {}
            return

        try:
            with ruta_reglas.open("r", encoding="utf-8") as f:
                self.reglas = json.load(f)
        except Exception as e:
            print(f"⚠ ERROR cargando reglas_conceptos.json: {e}")
            self.reglas = {}


    # ---------------------------------------------------------
    def listar_codigos(self):
        """Devuelve solo los códigos ordenados."""
        return sorted(self.cuentas.keys())


    # ---------------------------------------------------------
    def get_nombre(self, codigo):
        """Devuelve nombre contable."""
        return self.cuentas.get(codigo, {}).get("nombre", "")


    # ---------------------------------------------------------
    def get_descripcion(self, codigo):
        """Devuelve descripción contable oficial."""
        return self.cuentas.get(codigo, {}).get("descripcion", "")


    # ---------------------------------------------------------
    def get_combo_display(self, codigo):
        """Para mostrar en la UI: '600000 – Compra farmacia'."""
        nombre = self.get_nombre(codigo)
        return f"{codigo} – {nombre}"


    # ---------------------------------------------------------
    def todas_las_opciones(self):
        """
        Devuelve:
        ✔ lista completa de cuentas contables
        ✔ subcategorías (si deseas mantenerlas)
        """
        lista = []

        # Cuentas oficiales
        for codigo in self.listar_codigos():
            lista.append(self.get_combo_display(codigo))

        # Subcategorías adicionales
        for sub in self.subcategorias:
            lista.append(f"SUB – {sub}")

        return lista


    # ---------------------------------------------------------
    def filtrar(self, texto):
        """Filtro inteligente para autocompletar."""
        texto = texto.lower().strip()
        if texto == "":
            return self.todas_las_opciones()

        resultados = []
        for item in self.todas_las_opciones():
            if texto in item.lower():
                resultados.append(item)

        return resultados


    # ---------------------------------------------------------
    def es_subcategoria(self, valor):
        return valor.startswith("SUB – ")


    # ---------------------------------------------------------
    def extraer_nombre_subcategoria(self, valor):
        return valor.replace("SUB – ", "").strip()


    # ---------------------------------------------------------
    # VALIDACIÓN DE CONCEPTO SEGÚN REGLAS OFICIALES
    # ---------------------------------------------------------
    def es_concepto_valido(self, codigo, concepto):
        """
        Valida que el concepto coincide con la naturaleza
        de la cuenta contable según reglas_conceptos.json.
        """

        codigo = codigo.strip()

        # Si no hay reglas → se acepta
        if codigo not in self.reglas:
            return True

        concepto = concepto.lower()

        # Comprobar coincidencia con palabras clave
        for palabra in self.reglas[codigo]["permitidos"]:
            if palabra.lower() in concepto:
                return True

        # Si no coincide ninguna → no es válido
        return False
