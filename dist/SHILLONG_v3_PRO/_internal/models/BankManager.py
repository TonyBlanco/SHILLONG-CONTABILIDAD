# models/BankManager.py – VERSIÓN DEFINITIVA 2025

import json
from pathlib import Path
from utils.rutas import ruta_recurso


class BankManager:
    def __init__(self):
        self.archivo = ruta_recurso("data/bancos.json")
        self.bancos = self._cargar()

    def _cargar(self):
        if not self.archivo.exists():
            return []
        try:
            with open(self.archivo, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("banks", [])
        except (IOError, json.JSONDecodeError):
            return []

    def _guardar(self):
        with open(self.archivo, "w", encoding="utf-8") as f:
            json.dump({"banks": self.bancos}, f, indent=2, ensure_ascii=False)

    def listar(self):
        return self.bancos

    def get_nombre(self, bank_id):
        for b in self.bancos:
            if b["id"] == bank_id:
                return b["nombre"]
        return "Desconocido"

    def get_saldo(self, bank_id):
        """SALDO REAL: calculado desde movimientos + saldo inicial"""
        from models.ContabilidadData import ContabilidadData
        data = ContabilidadData()

        # Saldo inicial del banco
        saldo_inicial = 0.0
        for b in self.bancos:
            if b["id"] == bank_id:
                saldo_inicial = float(b.get("saldo", 0.0))
                break

        # Movimientos pagados
        saldo_movimientos = 0.0
        nombre_banco = self.get_nombre(bank_id)
        for m in data.movimientos:
            if m.get("banco") == nombre_banco and m.get("estado", "").lower() == "pagado":
                saldo_movimientos += float(m.get("haber", 0)) - float(m.get("debe", 0))

        return saldo_inicial + saldo_movimientos

    def get_saldo_total(self):
        """Saldo total de todos los bancos (real)"""
        total = 0.0
        for banco in self.bancos:
            total += self.get_saldo(banco["id"])
        return total

    def actualizar_saldo_inicial(self, bank_id, nuevo_saldo):
        """Solo para ajustar saldo inicial manualmente"""
        for b in self.bancos:
            if b["id"] == bank_id:
                b["saldo"] = float(nuevo_saldo)
                self._guardar()
                return True
        return False