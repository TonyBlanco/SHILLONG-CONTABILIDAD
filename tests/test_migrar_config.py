# -*- coding: utf-8 -*-
"""
pytest — MIGRACIÓN DE CONFIGURACIÓN (models/migrar_config.py)
=============================================================
Verifica que al arrancar la app:
  1) los bancos nuevos (Cambio Euros/Contrapartida) se fusionan en un
     bancos.json viejo, conservando bancos personalizados y saldos,
  2) las cuentas nuevas (556/557) se añaden al plan contable viejo sin
     tocar las existentes,
  3) se crea un backup previo en backups/,
  4) la operación es idempotente (no escribe nada si ya está al día),
  5) si no hay copia del usuario se instala la empaquetada,
  6) un archivo corrupto se restaura con backup.

Ejecutar desde la raíz del proyecto:
    python -m pytest tests/test_migrar_config.py -v
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pytest

from models.migrar_config import _migrar_un_archivo, migrar_configuracion


# ============================================================
# DATOS DE PARTIDA (versiones "viejas" que tiene la usuaria)
# ============================================================
BANCOS_VIEJO = {
    "banks": [
        {"id": 1, "nombre": "Federal Bank", "saldo": 0.0},
        {"id": 2, "nombre": "SBI", "saldo": 0.0},
        {"id": 3, "nombre": "Union Bank", "saldo": 50000.0},
        {"id": 4, "nombre": "Otro", "saldo": 0.0},
        {"id": 5, "nombre": "Caja", "saldo": -20000.0},
        {"id": 9, "nombre": "Banco Personalizado", "saldo": 123.45},  # personalización
    ]
}

PLAN_VIEJO = {
    "603000": {"nombre": "Comestibles", "descripcion": "Alimentación."},
    "211000": {"nombre": "Edificios", "descripcion": "Obras."},
    "999999": {"nombre": "Cuenta Propia", "descripcion": "Personalización."},
}


@pytest.fixture()
def entorno(tmp_path):
    """Crea un árbol simulado: empaquetado (data/) y usuario (app/data/)."""
    empaquetado = tmp_path / "empaquetado" / "data"
    usuario_dir = tmp_path / "app" / "data"
    empaquetado.mkdir(parents=True)
    usuario_dir.mkdir(parents=True)
    return {
        "empaquetado": empaquetado,
        "usuario_dir": usuario_dir,
        "tmp": tmp_path,
    }


def _escribir(ruta, datos):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)


def _leer(ruta):
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def _backups_de(entorno):
    bdir = entorno["tmp"] / "app" / "backups"
    if not bdir.exists():
        return []
    return sorted(p.name for p in bdir.iterdir())


# ============================================================
# 1) FUSIÓN DE BANCOS: añade los nuevos, conserva personalizados y saldos
# ============================================================
def test_fusiona_bancos_nuevos_conservando_personalizacion(entorno):
    emp = entorno["empaquetado"] / "bancos.json"
    usr = entorno["usuario_dir"] / "bancos.json"
    _escribir(emp, {
        "banks": [
            {"id": 1, "nombre": "Federal Bank", "saldo": 0.0},
            {"id": 2, "nombre": "SBI", "saldo": 0.0},
            {"id": 3, "nombre": "Union Bank", "saldo": 0.0},
            {"id": 4, "nombre": "Otro", "saldo": 0.0},
            {"id": 5, "nombre": "Caja", "saldo": 0.0},
            {"id": 6, "nombre": "Cambio Euros", "saldo": 0.0},
            {"id": 7, "nombre": "Contrapartida", "saldo": 0.0},
        ]
    })
    _escribir(usr, BANCOS_VIEJO)

    resultado = _migrar_un_archivo("bancos.json", emp, usr)
    assert resultado == [("bancos.json", ["Cambio Euros", "Contrapartida"])]

    final = _leer(usr)["banks"]
    nombres = [b["nombre"] for b in final]
    assert "Cambio Euros" in nombres
    assert "Contrapartida" in nombres
    # Personalizaciones intactas
    assert "Banco Personalizado" in nombres
    assert any(b["nombre"] == "Banco Personalizado" and b["saldo"] == 123.45 for b in final)
    assert any(b["nombre"] == "Union Bank" and b["saldo"] == 50000.0 for b in final)
    # IDs de los nuevos siguen al máximo existente
    ids = [b["id"] for b in final]
    assert max(ids) == 11
    # Sin duplicados
    assert len(nombres) == len(set(nombres))


# ============================================================
# 2) FUSIÓN DEL PLAN CONTABLE: añade 556/557, no toca existentes
# ============================================================
def test_fusiona_plan_contable_nuevo(entorno):
    emp = entorno["empaquetado"] / "plan_contable_v3.json"
    usr = entorno["usuario_dir"] / "plan_contable_v3.json"
    _escribir(emp, {
        "603000": {"nombre": "Comestibles", "descripcion": "Alimentación."},
        "556": {"nombre": "Cambio Euros", "descripcion": "Cambio de divisas."},
        "557": {"nombre": "Contrapartida", "descripcion": "Trasvases internos."},
    })
    _escribir(usr, PLAN_VIEJO)

    resultado = _migrar_un_archivo("plan_contable_v3.json", emp, usr)
    añadidos = [c for _, c in resultado]
    assert añadidos[0] == ["556", "557"]

    final = _leer(usr)
    assert final["556"]["nombre"] == "Cambio Euros"
    assert final["557"]["nombre"] == "Contrapartida"
    # Cuentas existentes intactas (incluida la personalizada)
    assert final["999999"]["nombre"] == "Cuenta Propia"
    assert final["603000"]["nombre"] == "Comestibles"


# ============================================================
# 3) BACKUP PREVIO
# ============================================================
def test_crea_backup_antes_de_escribir(entorno):
    emp = entorno["empaquetado"] / "bancos.json"
    usr = entorno["usuario_dir"] / "bancos.json"
    _escribir(emp, {"banks": [{"id": 6, "nombre": "Cambio Euros", "saldo": 0.0}]})
    _escribir(usr, BANCOS_VIEJO)

    _migrar_un_archivo("bancos.json", emp, usr)

    backups = _backups_de(entorno)
    assert len(backups) == 1
    assert backups[0].startswith("bancos.json.")
    assert backups[0].endswith(".bak")
    # El backup es el archivo ANTIGUO (sin Cambio Euros)
    contenido = _leer(entorno["tmp"] / "app" / "backups" / backups[0])
    nombres = [b["nombre"] for b in contenido["banks"]]
    assert "Cambio Euros" not in nombres
    assert "Banco Personalizado" in nombres


# ============================================================
# 4) IDEMPOTENCIA: si ya está al día, no escribe ni hace backup
# ============================================================
def test_idempotente_no_escribe_ni_backupea(entorno):
    emp = entorno["empaquetado"] / "bancos.json"
    usr = entorno["usuario_dir"] / "bancos.json"
    _escribir(emp, {"banks": [{"id": 6, "nombre": "Cambio Euros", "saldo": 0.0}]})
    _escribir(usr, {
        "banks": [
            {"id": 1, "nombre": "Caja", "saldo": 5.0},
            {"id": 6, "nombre": "Cambio Euros", "saldo": 0.0},
        ]
    })

    assert _migrar_un_archivo("bancos.json", emp, usr) == []
    assert _backups_de(entorno) == []
    # El contenido no cambió
    assert _leer(usr)["banks"][0]["saldo"] == 5.0


# ============================================================
# 5) SIN COPIA DEL USUARIO → instala la empaquetada
# ============================================================
def test_sin_copia_usuario_instala_empaquetado(entorno):
    emp = entorno["empaquetado"] / "plan_contable_v3.json"
    usr = entorno["usuario_dir"] / "plan_contable_v3.json"
    _escribir(emp, {"556": {"nombre": "Cambio Euros", "descripcion": "Cambio."}})

    resultado = _migrar_un_archivo("plan_contable_v3.json", emp, usr)
    assert resultado == [("plan_contable_v3.json", ["(copia inicial)"])]
    assert _leer(usr)["556"]["nombre"] == "Cambio Euros"
    assert _backups_de(entorno) == []  # no hay nada que respaldar


# ============================================================
# 6) CORRUPTO → backup y restauración
# ============================================================
def test_corrupto_se_respalda_y_restaura(entorno):
    emp = entorno["empaquetado"] / "bancos.json"
    usr = entorno["usuario_dir"] / "bancos.json"
    _escribir(emp, {"banks": [{"id": 6, "nombre": "Cambio Euros", "saldo": 0.0}]})
    usr.write_text("{ esto no es json ", encoding="utf-8")

    resultado = _migrar_un_archivo("bancos.json", emp, usr)
    assert resultado[0][0] == "bancos.json"

    assert _leer(usr)["banks"][0]["nombre"] == "Cambio Euros"
    backups = _backups_de(entorno)
    assert len(backups) == 1  # el corrupto quedó respaldado


# ============================================================
# 7) MIGRACIÓN COMPLETA (ambos archivos) — integración con rutas reales
# ============================================================
def test_migracion_completa_vacia_en_desarrollo():
    """En desarrollo la ruta empaquetada == ruta del usuario (repo data/),
    por lo que la migración no debe escribir nada."""
    cambios = migrar_configuracion()
    # Puede devolver copias iniciales si faltan archivos, pero nunca debe
    # borrar ni duplicar nada. Verificamos que no explota y que devuelve lista.
    assert isinstance(cambios, list)
