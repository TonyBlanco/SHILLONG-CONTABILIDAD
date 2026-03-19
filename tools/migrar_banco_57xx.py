# -*- coding: utf-8 -*-
"""
migrar_banco_57xx.py — SHILLONG CONTABILIDAD
----------------------------------------------
Añade el campo 'cuenta_banco' (código 57xx) a cada movimiento
basándose en el nombre del banco usado.

Uso:
    python tools/migrar_banco_57xx.py               # migra shillong_2026.json
    python tools/migrar_banco_57xx.py backup.json   # migra archivo especificado
"""

import json
import sys
import shutil
from pathlib import Path

# ── MAPA BANCO NOMBRE → CÓDIGO 57xx ─────────────────────────────────────────
# Construido a partir de bancos.json + plan_contable_v3.json
BANCO_A_CUENTA = {
    "Caja":                        "570",
    "SBI- Sr sindhu":              "5721",
    "sbi- sr sindhu":              "5721",
    "Federal Bank sr Sindhu":      "5722",
    "federal bank sr sindhu":      "5722",
    "Federal Bank- sr Juliana":    "5723",
    "federal bank- sr juliana":    "5723",
    "Federal Bank sr Shairilin":   "5724",
    "federal bank sr shairilin":   "5724",
    "Union Bank, sr Elisa":        "5725",
    "union bank, sr elisa":        "5725",
    "Union Bank":                  "5725",   # nombre abreviado en algunos registros
    "union bank":                  "5725",
    "Post- office sr Sindhu":      "5741",
    "post- office sr sindhu":      "5741",
    "Post-office sr Shairilin":    "5742",
    "post-office sr shairilin":    "5742",
}


def migrar(ruta_archivo: str):
    path = Path(ruta_archivo)
    if not path.exists():
        print(f"ERROR: No existe el archivo '{path}'")
        sys.exit(1)

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
    archivos = sys.argv[1:] if len(sys.argv) > 1 else [
        "backups/backup_2026-03-18.json",
        "data/shillong_2026.json",
    ]
    for archivo in archivos:
        migrar(archivo)
    print("\n✅ Migración completada.")
