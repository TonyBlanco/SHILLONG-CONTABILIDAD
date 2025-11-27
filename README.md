SHILLONG CONTABILIDAD v3 PRO

Sistema contable completo en PySide6 + JSON + Excel, diseñado para comunidades, ONGs o pequeñas instituciones con necesidades reales de contabilidad, multimoneda y reportes profesionales.

📌 Características principales
✔ Interfaz moderna y modular (PySide6)

Dashboard dinámico

Registro de movimientos con autocompletado inteligente de cuentas

Libro mensual multimoneda

Vista de pendientes (cuentas por pagar)

Informes diarios con exportación a Excel

Cierres y ajustes contables

Herramientas del sistema (cambios de archivo, backup, temas)

✔ Motor contable profesional

Plan contable completo v3

Motor de cuentas con validación semántica concepto ↔ cuenta

Reglas automáticas para conceptos contables (inteligencia semántica)

✔ Importación y exportación Excel

Importador Excel con detección de cabeceras, validación y limpieza automática

Exportador general y exportador profesional con estilo PRO

✔ Sistema de datos robusto

Archivo contable en JSON con soporte multimoneda (INR / EUR / USD)

Funciones avanzadas: top cuentas anuales, trimestres, ingresos por moneda, etc.

🗂 Estructura del Proyecto
/ui
   ├── MainWindow.py
   ├── Sidebar.py
   ├── HeaderBar.py
   ├── DashboardView.py
   ├── RegistrarView.py
   ├── LibroMensualView.py
   ├── PendientesView.py
   ├── InformesView.py
   ├── CierreView.py
   ├── ToolsView.py
   └── Dialogs/
         └── ImportarExcelDialog.py

/models
   ├── ContabilidadData.py
   ├── cuentas_motor.py
   ├── importador_excel.py
   ├── exportador_excel.py
   └── ...

/data
   ├── bancos.json
   ├── plan_contable_v3.json
   ├── reglas_conceptos.json
   └── shillong_2026.json

main.py
requirements.txt
README.md

🚀 Instalación
1. Clonar el repositorio
git clone https://github.com/TonyBlanco/SHILLONG-CONTABILIDAD.git
cd shillong-contabilidad-v3

2. Instalar dependencias
pip install -r requirements.txt


(Usa PySide6, pandas, openpyxl según requirements.txt )

3. Ejecutar la aplicación
python main.py

🧠 Cómo funciona el sistema
🔹 MainWindow – el núcleo del programa

Registra todas las vistas, carga el archivo contable y gestiona temas visuales, backups, importación/exportación y navegación .

🔹 ContabilidadData – modelo de datos multimoneda

Se encarga de cargar el JSON, registrar movimientos y generar estadísticas contables profesionales .

🔹 Motor de Cuentas

Autocompletado inteligente y validación semántica usando reglas_conceptos.json .

🔹 Importador Excel PRO

El módulo más avanzado:

detecta cabeceras reales,

corrige filas basura,

valida cuentas y conceptos,

rellena fechas automáticamente,

importa solo movimientos limpios.


🔹 Vistas de usuario

Cada vista tiene su módulo independiente: Dashboard, Libro Mensual, Pendientes, Informes, Herramientas…

📦 JSONs incluidos

bancos.json: listado de bancos + caja

plan_contable_v3.json: plan contable completo v3

reglas_conceptos.json: reglas automáticas de validación

shillong_2026.json: archivo contable de ejemplo con movimientos reales

🛠 Build para EXE (PyInstaller)

Ejemplo de comando:

pyinstaller --noconfirm --clean ^
  --add-data "data;data" ^
  --add-data "themes;themes" ^
  --add-data "core;core" ^
  --windowed ^
  main.py

📜 Licencia

MIT License — Libre uso comercial y privado.

🧑‍💻 Author / Autor

SHILLONG v3 PRO
Designed & Developed by Tony Blanco

