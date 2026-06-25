# -*- coding: utf-8 -*-
"""
models/ExportadorModeloEvolutivo.py

Fills the official blank template ("Modelo evolutivo presupuestario 26 - blank.xlsx")
with real data from totales_exactos, preserving the original formatting exactly.

Public API:
  exportar_modelo_evolutivo(ruta_archivo, totales_exactos, cuentas_by_section,
                             anio, periodo_str, nombre_por_cuenta, ruta_plantilla)

Column layout in template (1-based):
  C(3) = account code  D(4) = name  E(5) = MES CORRIENTE  F(6) = BANCO
  G(7) = CAJA  H(8) = MESES ANTERIORES  I(9) = SUMA ACUMULADO
  J(10) = PRESUPUESTO  K(11) = DIFERENCIA
"""

import shutil
import datetime
import re
from pathlib import Path
import openpyxl

# Column indices (1-based, matching template layout)
COL_CUENTA      = 3
COL_NOMBRE      = 4
COL_CORRIENTE   = 5   # MES CORRIENTE  = cur_banco + cur_caja
COL_BANCO       = 6
COL_CAJA        = 7
COL_ANTERIORES  = 8   # MESES ANTERIORES = prev_total
COL_ACUMULADO   = 9   # SUMA ACUMULADO  = corriente + anteriores
COL_PRESUPUESTO = 10
COL_DIFERENCIA  = 11  # PRESUPUESTO - ACUMULADO

TOTAL_LABELS = {"SUMA TOTAL GASTOS", "SUMA TOTAL INGRESOS", "INVERSIONES"}


def _normalizar_codigo(v):
    """Convert any template account code format to 6-digit string, e.g. '629.2' -> '629200'."""
    if v is None:
        return None
    s = str(int(v)) if isinstance(v, (int, float)) else str(v).strip()
    s = re.sub(r"\D", "", s)
    if not s.isdigit():
        return None
    return s.ljust(6, "0")[:6]


def _parse_template_code(v):
    """Return normalized code plus interpretation mode for template rows.

    Mode rules:
    - "exact": dotted/comma formats like 602.40 mean the concrete account 602400.
    - "group": dashed formats like 602-400 mean the parent/group row for 6024xx.
    - "auto": fallback for plain numeric codes, preserving the historical rollup logic.
    """
    if v is None:
        return None, "auto"

    raw = str(int(v)) if isinstance(v, (int, float)) else str(v).strip()
    codigo = _normalizar_codigo(raw)
    if not codigo:
        return None, "auto"

    if "-" in raw:
        return codigo, "group"
    if "." in raw or "," in raw:
        return codigo, "exact"
    return codigo, "auto"


def _group_prefix(codigo):
    codigo = str(codigo).strip()
    if codigo.endswith("000") and len(codigo) > 3:
        return codigo[:-3]
    if codigo.endswith("00") and len(codigo) > 2:
        return codigo[:-2]
    return codigo


def _has_descendants(codigo, candidate_codes):
    pref = _group_prefix(codigo)
    for candidate in candidate_codes:
        cta = str(candidate).strip()
        if len(cta) != len(str(codigo)):
            continue
        if cta != str(codigo) and cta.startswith(pref):
            return True
    return False


def _resolve_template_mode(raw_code, normalized_code, sheet_codes, candidate_codes):
    raw = str(raw_code or "").strip()
    if not normalized_code:
        return "auto"

    if "-" in raw:
        return "group"

    parts = [p for p in re.split(r"[.,]", raw) if p]
    has_separator = any(sep in raw for sep in (".", ","))

    # A dotted/comma row is exact if the same normalized code also exists as a plain row.
    if has_separator:
        for other_raw, other_norm in sheet_codes:
            if other_norm != normalized_code:
                continue
            other_txt = str(other_raw or "").strip()
            if other_txt == raw:
                continue
            if not any(sep in other_txt for sep in (".", ",", "-")):
                return "exact"

    # Three decimal digits usually map to explicit leaves like 602.401 -> 602401.
    if has_separator and any(len(p) >= 3 for p in parts[1:]):
        return "exact"

    if _has_descendants(normalized_code, candidate_codes):
        return "group"

    if has_separator:
        return "exact"
    return "auto"


def _rollup(codigo, totales_exactos, mode="auto"):
    """Sum accounts whose 6-char code shares the same meaningful prefix.

    Parent accounts like '600000' (ends in 000) roll up all 600xxx children.
    Leaf accounts like '628030' match exactly.
    """
    codigo = str(codigo).strip()
    if mode == "exact":
        pref = codigo
        exact_match = True
    elif mode == "group":
        exact_match = False
        if codigo.endswith("000") and len(codigo) > 3:
            pref = codigo[:-3]
        elif codigo.endswith("00") and len(codigo) > 2:
            pref = codigo[:-2]
        else:
            pref = codigo
    elif codigo.endswith("000") and len(codigo) > 3:
        pref = codigo[:-3]   # "600000" → "600", "628000" → "628"
        exact_match = False
    elif codigo.endswith("00") and len(codigo) > 2:
        pref = codigo[:-2]   # "629000" → "6290"
        exact_match = False
    else:
        pref = codigo         # "628030" → exact match
        exact_match = True

    cur_banco = cur_caja = prev_total = 0.0
    for cta, vals in totales_exactos.items():
        cta_s = str(cta)
        if len(cta_s) != len(codigo):
            continue
        if exact_match and cta_s != pref:
            continue
        if not exact_match and not cta_s.startswith(pref):
            continue
        cur_banco  += float(vals.get("cur_banco",  0) or 0)
        cur_caja   += float(vals.get("cur_caja",   0) or 0)
        prev_total += float(vals.get("prev_total", 0) or 0)
    return cur_banco, cur_caja, prev_total


def _fill_row(ws, row, cur_banco, cur_caja, prev_total):
    """Write computed values into the data columns of a template row."""
    corriente  = round(cur_banco + cur_caja, 2)
    acumulado  = round(corriente + prev_total, 2)
    try:
        presupuesto = float(ws.cell(row, COL_PRESUPUESTO).value or 0)
    except (TypeError, ValueError):
        presupuesto = 0.0
    diferencia  = round(presupuesto - acumulado, 2)

    ws.cell(row, COL_CORRIENTE).value  = corriente
    ws.cell(row, COL_BANCO).value      = round(cur_banco,  2)
    ws.cell(row, COL_CAJA).value       = round(cur_caja,   2)
    ws.cell(row, COL_ANTERIORES).value = round(prev_total, 2)
    ws.cell(row, COL_ACUMULADO).value  = acumulado
    ws.cell(row, COL_DIFERENCIA).value = diferencia

    return corriente, cur_banco, cur_caja, prev_total, acumulado


def exportar_modelo_evolutivo(ruta_archivo, totales_exactos, cuentas_by_section,
                               anio, periodo_str="", nombre_por_cuenta=None,
                               ruta_plantilla=None):
    """
    Fill the blank template with real data and save to ruta_archivo.
    Falls back to a minimal programmatic layout if no template is available.
    """
    if ruta_plantilla and Path(ruta_plantilla).exists():
        return _exportar_desde_plantilla(
            ruta_archivo, totales_exactos, anio, periodo_str, ruta_plantilla
        )
    return _exportar_programatico(
        ruta_archivo, totales_exactos, cuentas_by_section,
        anio, periodo_str, nombre_por_cuenta
    )


# ──────────────────────────────────────────────────────────────────────────────
# Template-fill path  (preferred — preserves the original format exactly)
# ──────────────────────────────────────────────────────────────────────────────

def _exportar_desde_plantilla(ruta_archivo, totales_exactos, anio, periodo_str, ruta_plantilla):
    dest = Path(ruta_archivo)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ruta_plantilla, dest)

    wb = openpyxl.load_workbook(dest)
    ws = wb.active

    # Update date cell (template row 4, col G)
    try:
        ws.cell(4, 7).value = datetime.date(anio, 12, 31)
    except Exception:
        pass

    # Exact base totals from JSON by section.
    section_totals = {s: [0.0, 0.0, 0.0, 0.0] for s in ("6", "7", "2")}
    # [corriente, banco, caja, anteriores]
    for cta, vals in totales_exactos.items():
        cta_s = str(cta).strip()
        if not cta_s or cta_s[0] not in section_totals:
            continue
        banco = float(vals.get("cur_banco", 0) or 0)
        caja = float(vals.get("cur_caja", 0) or 0)
        prev = float(vals.get("prev_total", 0) or 0)
        t = section_totals[cta_s[0]]
        t[0] += banco + caja
        t[1] += banco
        t[2] += caja
        t[3] += prev

    current_section = None
    sheet_codes = []
    candidate_codes = set(str(cta).strip() for cta in totales_exactos.keys())

    for row in range(1, ws.max_row + 1):
        code_raw = ws.cell(row, COL_CUENTA).value
        code_norm = _normalizar_codigo(code_raw)
        if code_norm:
            sheet_codes.append((code_raw, code_norm))
            candidate_codes.add(code_norm)

    for row in range(1, ws.max_row + 1):
        code_raw  = ws.cell(row, COL_CUENTA).value
        label_d   = str(ws.cell(row, COL_NOMBRE).value or "").strip()
        code_str  = str(code_raw or "").strip()
        # Section header: C is literal "CUENTAS..." OR a formula (=+C61) with section keyword in D
        cuenta_hdr = (
            code_str.upper().startswith("CUENTAS") or
            (code_str.startswith("=") and
             any(k in label_d.upper() for k in ("GASTOS", "INGRESOS", "INVER")))
        )

        # Section header rows have "CUENTAS" in col C — skip them and update section
        if cuenta_hdr:
            if "GASTOS"     in label_d: current_section = "6"
            elif "INGRESOS" in label_d: current_section = "7"
            elif "INVER"    in label_d: current_section = "2"
            continue

        # Total rows: col D in TOTAL_LABELS, col C does NOT start with "CUENTAS"
        if label_d in TOTAL_LABELS and current_section:
            t = section_totals[current_section]
            corriente  = round(t[0], 2)
            acumulado  = round(t[0] + t[3], 2)
            try:
                presupuesto = float(ws.cell(row, COL_PRESUPUESTO).value or 0)
            except (TypeError, ValueError):
                presupuesto = 0.0
            ws.cell(row, COL_CORRIENTE).value  = corriente
            ws.cell(row, COL_BANCO).value      = round(t[1], 2)
            ws.cell(row, COL_CAJA).value       = round(t[2], 2)
            ws.cell(row, COL_ANTERIORES).value = round(t[3], 2)
            ws.cell(row, COL_ACUMULADO).value  = acumulado
            ws.cell(row, COL_DIFERENCIA).value = round(float(presupuesto) - acumulado, 2)
            continue

        # Data rows: account code in col C
        codigo, _ = _parse_template_code(code_raw)
        if not codigo or not current_section:
            continue
        if not codigo.isdigit() or codigo[0] not in ("6", "7", "2"):
            continue
        if codigo[0] != current_section:
            continue
        mode = _resolve_template_mode(code_raw, codigo, sheet_codes, candidate_codes)

        cur_banco, cur_caja, prev_total = _rollup(codigo, totales_exactos, mode=mode)
        _fill_row(ws, row, cur_banco, cur_caja, prev_total)

    wb.save(dest)
    return True


# ──────────────────────────────────────────────────────────────────────────────
# Fallback: minimal programmatic layout (used only when template is missing)
# ──────────────────────────────────────────────────────────────────────────────

def _exportar_programatico(ruta_archivo, totales_exactos, cuentas_by_section,
                            anio, periodo_str, nombre_por_cuenta):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    BURDEOS = "8C0052"
    wb = Workbook()
    ws = wb.active
    ws.title = "Modelo Evolutivo"

    fill_h = PatternFill(start_color=BURDEOS, end_color=BURDEOS, fill_type="solid")
    fill_t = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
    font_h = Font(bold=True, color="FFFFFF")
    centro = Alignment(horizontal="center", vertical="center")
    borde  = Border(
        left=Side(style="thin"), right=Side(style="thin"),
        top=Side(style="thin"),  bottom=Side(style="thin")
    )

    SEC_HEADERS = {
        "6": ["CUENTA", "NOMBRE", "MES CORRIENTE", "BANCO", "CAJA",
              "GASTO MESES ANTERIORES", "SUMA DE GASTO ACUMULADO",
              f"PRESUPUESTO {anio}", "DIFERENCIA"],
        "7": ["CUENTA", "NOMBRE", "MES CORRIENTE", "BANCO", "CAJA",
              "INGRESOS MESES ANTERIORES", "SUMA DE INGRESO ACUMULADO",
              f"PRESUPUESTO {anio}", "DIFERENCIA"],
        "2": ["CUENTA", "NOMBRE", "MES CORRIENTE", "BANCO", "CAJA",
              "INVERSIONES MESES ANTER.", "SUMA DE GASTO ACUMULADO",
              f"PRESUPUESTO {anio}", "DIFERENCIA"],
    }
    SEC_TOTALS = {"6": "SUMA TOTAL GASTOS", "7": "SUMA TOTAL INGRESOS", "2": "INVERSIONES"}

    row = 1
    # Title
    ws.merge_cells(start_row=row, start_column=3, end_row=row, end_column=11)
    c = ws.cell(row, 3, "CUENTAS DE COMUNIDAD DE SHILLONG")
    c.font = font_h; c.fill = fill_h; c.alignment = centro
    ws.cell(row, 6, "FECHA:"); ws.cell(row, 7, datetime.date(anio, 12, 31))
    row += 4   # match template offset (row 4 in template = data row)

    for sec in ("6", "7", "2"):
        headers  = SEC_HEADERS[sec]
        n_cols   = len(headers)
        tot_lbl  = SEC_TOTALS[sec]
        cuentas  = cuentas_by_section.get(sec, [])

        # Header row
        for ci, h in enumerate(headers, start=3):
            c = ws.cell(row, ci, h)
            c.fill = fill_h; c.font = font_h; c.border = borde
            c.alignment = centro
            ws.column_dimensions[get_column_letter(ci)].width = 20
        row += 2

        t_corr = t_banco = t_caja = t_ant = 0.0

        for cta in cuentas:
            nombre = ""
            if callable(nombre_por_cuenta):
                try: nombre = nombre_por_cuenta(cta)
                except Exception: pass
            elif isinstance(nombre_por_cuenta, dict):
                nombre = nombre_por_cuenta.get(cta, "")

            b, ca, pr = _rollup(cta, totales_exactos)
            corr = round(b + ca, 2); acum = round(corr + pr, 2)

            vals = [cta, nombre, corr, round(b,2), round(ca,2), round(pr,2), acum, 0.0, -acum]
            for ci, v in enumerate(vals, start=3):
                c = ws.cell(row, ci, v)
                c.border = borde
                if ci >= 5:
                    c.number_format = "#,##0.00"
                    c.alignment = Alignment(horizontal="right")
            t_corr += corr; t_banco += b; t_caja += ca; t_ant += pr
            row += 1

        # Total row
        t_acum = round(t_corr + t_ant, 2)
        ws.cell(row, COL_NOMBRE, tot_lbl).font = Font(bold=True)
        for ci, v in [(5, round(t_corr,2)), (6, round(t_banco,2)),
                      (7, round(t_caja,2)), (8, round(t_ant,2)), (9, t_acum)]:
            c = ws.cell(row, ci, v)
            c.fill = fill_t; c.number_format = "#,##0.00"
        row += 2

    dest = Path(ruta_archivo)
    dest.parent.mkdir(parents=True, exist_ok=True)
    wb.save(dest)
    return True
