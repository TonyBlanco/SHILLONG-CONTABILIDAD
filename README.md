# ✅ **README.md — SHILLONG CONTABILIDAD v3 PRO (versión final)**

```markdown
# SHILLONG CONTABILIDAD v3 PRO  
Sistema contable profesional en **PySide6 + JSON + Excel**, diseñado para comunidades, ONGs, centros educativos y pequeñas instituciones que requieren un sistema ágil, rápido, multimoneda y con reportes contables claros y modernos.

---

## 📌 Características principales

### ✔ Interfaz moderna (PySide6)
- Dashboard dinámico  
- Registro de movimientos con **autocompletado inteligente**  
- Validación semántica concepto ↔ cuenta  
- Libro mensual multimoneda  
- Vista de pendientes  
- Informes con exportación a Excel  
- Cierres contables automáticos  
- Herramientas del sistema (temas, backup, archivos)

### ✔ Motor contable profesional
- Plan contable completo v3  
- Motor de cuentas con inteligencia semántica  
- Reglas automáticas basadas en `reglas_conceptos.json`  
- Aprendizaje automático de conceptos nuevos  

### ✔ Importación y exportación Excel PRO
- Detección automática de cabeceras  
- Limpieza de filas basura  
- Validación de cuentas y conceptos  
- Corrección automática de fechas  
- Importación segura sin duplicados  
- Exportador profesional estilizado  

### ✔ Sistema de datos robusto
- Archivo contable JSON con soporte **multimoneda (INR / EUR / USD)**  
- Cálculos avanzados:  
  - top cuentas anuales  
  - análisis trimestral  
  - ingresos por moneda  
  - totales de bancos  
  - resumen mensual profesional  

---

## 📁 Estructura oficial del proyecto

```

📁 ShillongV3/
│
├── main.py
│
├── 📁 ui/
│     ├── MainWindow.py
│     ├── RegistrarView.py
│     ├── LibroMensualView.py
│     ├── CierreMensualView.py
│     ├── PendientesView.py
│     ├── DashboardView.py
│     ├── InformesView.py
│     ├── Sidebar.py
│     ├── HeaderBar.py
│     └── ToolsView.py
│
├── 📁 models/
│     ├── ContabilidadData.py
│     ├── BankManager.py
│     ├── CuentasMotor.py
│     ├── importador_excel.py
│     ├── exportador_excel.py
│     └── plan_contable_v3.json
│
├── 📁 data/
│     ├── shillong_2026.json
│     ├── bancos.json
│     ├── plan_contable_v3.json
│     ├── reglas_conceptos.json
│     └── (otros JSON necesarios)
│
├── 📁 themes/
│     ├── light.qss
│     ├── dark.qss
│
├── 📁 core/
│     ├── updater.py
│     ├── styles.qss
│     └── **init**.py
│
├── 📁 utils/
│     └── rutas.py
│
└── requirements.txt


## 🚀 Instalación

### 1️⃣ Clonar el repositorio
```bash
git clone https://github.com/TonyBlanco/SHILLONG-CONTABILIDAD.git
cd shillong-contabilidad-v3
````

### 2️⃣ Instalar dependencias

```bash
pip install -r requirements.txt
```

Requiere:

* PySide6
* pandas
* openpyxl
* json
* pathlib

### 3️⃣ Ejecutar la aplicación

```bash
python main.py


## 🧠 Cómo funciona el sistema

### 🔹 MainWindow — El núcleo

Gestiona:

* navegación entre vistas
* carga de JSON
* temas light/dark
* backup y restauración
* importación/exportación Excel

### 🔹 ContabilidadData — Motor de datos

* carga JSON
* registra movimientos
* calcula totales
* soporta multimoneda
* genera estadísticas profesionales

### 🔹 MotorCuentas — Inteligencia semántica

* autocompletado inteligente
* validación de conceptos
* aprendizaje automático
* uso de `reglas_conceptos.json`

### 🔹 Importador Excel PRO

* detecta encabezados reales
* limpia datos sucios
* valida conceptos y cuentas
* convierte fechas
* evita duplicados

### 🔹 Vistas de usuario

Cada vista es independiente (MVC):

* RegistrarView
* LibroMensualView
* CierreMensualView
* PendientesView
* DashboardView
* InformesView
* ToolsView

---

## 📦 Archivos JSON incluidos

| Archivo                 | Descripción                      |
| ----------------------- | -------------------------------- |
| `bancos.json`           | Listado de bancos + Caja         |
| `plan_contable_v3.json` | Plan contable oficial v3         |
| `reglas_conceptos.json` | Reglas de validación semántica   |
| `shillong_2026.json`    | Archivo contable real de ejemplo |

---

## 🛠 Build para EXE (PyInstaller)

Ejemplo PRO:

```bash
pyinstaller main.py ^
 --clean ^
 --windowed ^
 --noconfirm ^
 --onefile ^
 --name "SHILLONG_CONTABILIDAD_v3_PRO" ^
 --add-data "ui;ui" ^
 --add-data "models;models" ^
 --add-data "core;core" ^
 --add-data "themes;themes" ^
 --add-data "data;data"
```

---

## 📜 Licencia

**MIT License** — Libre uso personal y comercial.

---

## 🧑‍💻 Author / Autor

**SHILLONG v3 PRO**
Designed & Developed by **Tony Blanco**

````

---

# ✅ ¿AHORA QUÉ HACES?

1️⃣ Crea un archivo nuevo:  
`README.md`

2️⃣ Copia todo este contenido.  

3️⃣ Haz commit y push:

```bash
git add README.md
git commit -m "Actualizado README profesional"
git push
````


