# -*- coding: utf-8 -*-
"""
migrar_banco_57xx.py — SHILLONG CONTABILIDAD
----------------------------------------------
Añade el campo 'cuenta_banco' (código 57xx) a cada movimiento
basándose en el nombre del banco usado.

El mapa se construye DINÁMICAMENTE desde data/bancos.json (campo 'cuenta_contable').
Para agregar un banco nuevo, solo hay que editarlo en bancos.json — sin tocar este script.

Uso:
    python tools/migrar_banco_57xx.py               # migra shillong_{año}.json
    python tools/migrar_banco_57xx.py backup.json   # migra archivo especificado
"""

import json
import sys
import shutil
from pathlib import Path
from datetime import datetime


def _cargar_mapa_bancos(ruta_bancos="data/bancos.json"):
    """
    Lee bancos.json y construye el mapa nombre -> cuenta_contable.
    Incluye variantes en minúscula para comparación robusta.
    """
    path = Path(ruta_bancos)
    if not path.exists():
        print(f"⚠️  No se encontró {path}, usando mapa vacío.")
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    mapa = {}
    for b in data.get("banks", []):
        nombre = b.get("nombre", "").strip()
        codigo = b.get("cuenta_contable", "").strip()
        if nombre and codigo:
            mapa[nombre] = codigo
            mapa[nombre.lower()] = codigo
    return mapa


def migrar(ruta_archivo: str):
    path = Path(ruta_archivo)
    if not path.exists():
        print(f"ERROR: No existe el archivo '{path}'")
        sys.exit(1)

    # Mapa dinámico desde bancos.json
    BANCO_A_CUENTA = _cargar_mapa_bancos()
    print(f"   Bancos cargados de bancos.json: {len(BANCO_A_CUENTA) // 2}")

    # Backup de seguridad
    backup = path.with_suffix(path.suffix + ".pre_57xx.bak")
    if not backup.exists():
        shutil.copy2(path, backup)
        print(f"✅ Backup guardado: {backup.name}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    movimientos = data if isinstance(data, list) else data.get("movimientos", [])

    actualizados  = 0
    sin_mapa      = set()

    for m in movimientos:
        banco_nombre = m.get("banco", "").strip()

        # Buscar primero con caso exacto, luego lowercase
        codigo = BANCO_A_CUENTA.get(banco_nombre) or BANCO_A_CUENTA.get(banco_nombre.lower())

        if codigo:
            if m.get("cuenta_banco") != codigo:
                m["cuenta_banco"] = codigo
                actualizados += 1
        else:
            if banco_nombre:
                sin_mapa.add(banco_nombre)
            m.setdefault("cuenta_banco", "")   # campo vacío para no perder el campo

    # Guardar
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"\n📂 Archivo: {path.name}")
    print(f"   Movimientos totales : {len(movimientos)}")
    print(f"   Actualizados        : {actualizados}")
    if sin_mapa:
        print(f"   ⚠️  Bancos sin mapa  : {sorted(sin_mapa)}")
    else:
        print("   ✔ Todos los bancos mapeados correctamente")


if __name__ == "__main__":
    año = datetime.now().year
    archivos = sys.argv[1:] if len(sys.argv) > 1 else [
        f"data/shillong_{año}.json",
    ]
    for archivo in archivos:
        migrar(archivo)
    print("\n✅ Migración completada.")
