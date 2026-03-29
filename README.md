# SHILLONG CONTABILIDAD v3.8.3 PRO

Sistema contable profesional de gestión comunitaria. Diseñado para comunidades, ONGs y centros educativos que requieren un sistema ágil, multimoneda y con reportes financieros de alto nivel, pero con una interfaz humana y accesible.

## 🌟 Novedades de la Versión 3.8 PRO

Esta versión introduce una arquitectura blindada y funcionalidades de Inteligencia de Negocio (BI):

### 📊 Inteligencia de Negocio (BI) y Reportes
- **Cierre Anual Evolutivo ("La Sábana")**: Generación automática de matrices Excel con la evolución de gastos mes a mes (Enero-Diciembre).
- **Control Presupuestario**: Comparativa visual (semáforos rojo/verde) entre lo presupuestado y la realidad.
- **Top Gastos (Pareto)**: Ranking automático de las cuentas con mayor impacto financiero.
- **Exportador Nativo**: Motor propio basado en openpyxl que genera Excels estilizados con colores corporativos, fórmulas y formatos de moneda.

### ✨ Módulo "Herramientas & Luz"
Un toque único para humanizar el software:
- **Inspiración Diaria**: Widget integrado que ofrece Salmos aleatorios y los 72 Nombres de Dios en hebreo para meditación diaria.
- **Gestión de Sistema**: Copias de seguridad (Backup/Restore) y gestión de temas (Claro/Oscuro) en un clic.

### 🆘 Centro de Ayuda Integrado
- **Guía Interactiva**: Manual de usuario completo dentro de la aplicación (HelpView), con secciones desplegables explicativas.
- **Onboarding**: Explicación paso a paso de cómo registrar, cerrar mes y gestionar datos.

## 🚀 Características Principales

### 🔹 Gestión Contable
- **Dashboard Dinámico**: KPIs en tiempo real (Ingresos, Gastos, Saldo) y gráficos de distribución (Donut Charts).
- **Registro Inteligente**: Autocompletado de cuentas y validación semántica (ej: escribir "luz" sugiere la cuenta correcta).
- **Libros Oficiales**: Diario General, Libro Mensual y Gestión de Pendientes.

### 🔹 Importación/Exportación
- **Importador Excel Blindado**: Detecta cabeceras, limpia datos sucios y valida duplicados antes de importar.
- **Salida Profesional**: Todos los informes se exportan a Excel (.xlsx) listos para imprimir o auditar.

### 🔹 Administración sin Código (v3.8.3+)
- **Gestión de Bancos/Cajas**: GUI completa (Herramientas → Gestionar Bancos) para agregar, editar o eliminar bancos sin tocar JSON. Los cambios se aplican al instante.
- **Configuración 100% externa**: añadir un banco nuevo no requiere recompilar ni modificar código Python.
- **Asignación automática de cuenta contable**: `cuenta_banco` (57xx) se asigna al guardar movimientos nuevos, leyendo el mapeo de `bancos.json`.

### 🔹 Arquitectura Técnica (Robusta)
- **Rutas Inteligentes (utils/rutas.py)**: Sistema híbrido que detecta si corre en script .py o ejecutable .exe compilado, evitando errores de rutas o pérdida de recursos.
- **DPI Safe**: Interfaz escalable que se ve nítida en pantallas 4K y monitores antiguos.
- **Datos JSON**: Base de datos ligera, portable y fácil de respaldar (`shillong_{año}.json`). El año se detecta automáticamente — funciona en 2027+ sin cambios de código.

## 📂 Estructura del Proyecto
D:\ShillongV3
├── main.py # Punto de entrada (Launcher)
├── importador_excel.py # Helper de importación (Raíz)
├── core/ # Configuraciones globales y versión
├── data/ # Base de datos JSON (Persistente)
│ ├── shillong_{año}.json     # Año dinámico
│ ├── bancos.json              # Fuente de verdad bancos + cuentas 57xx
│ └── plan_contable_v3.json
├── models/ # Lógica de Negocio
│ ├── ContabilidadData.py # Motor de datos (CRUD)
│ ├── ExportadorExcel... # Motor de reportes openpyxl
│ └── ...
├── ui/ # Interfaz Gráfica (Vistas)
│ ├── MainWindow.py           # Ventana Principal (Coordinador)
│ ├── Sidebar.py              # Menú Lateral Inteligente
│ ├── HelpView.py             # Centro de Ayuda
│ ├── ToolsView.py            # Herramientas y Sistema
│ ├── Dialogs/
│ │   ├── GestorBancosDialog.py   # Gestión de bancos (NUEVO v3.8.3)
│ │   ├── SaldosInicialesDialog.py
│ │   └── ...
│ └── ...
├── utils/ # Utilidades
│ └── rutas.py # Gestor de rutas (Dev vs Prod)
├── BUILD_NOTES.md  # Notas técnicas para build/CI
└── assets/         # Iconos y recursos gráficos

## 🛠 Compilación (Build)

El proyecto incluye un script de automatización para generar el instalador final (.exe).

### Requisitos
- Python 3.10+
- `pip install -r requirements.txt` (PySide6, pandas, openpyxl)
- Inno Setup 6 (para el instalador)

### Generar Ejecutable
Ejecutar el script de PowerShell en la raíz:
.\build_full.ps1
Este script:
- Limpia compilaciones anteriores.
- Ejecuta PyInstaller usando `SHILLONG_v3_PRO.spec` (configuración blindada).
- Empaqueta carpetas `data`, `assets` y `themes`.
- Ejecuta Inno Setup para crear el instalador final en `Output/`.

## 👨‍💻 Autor y Créditos
Desarrollado con ❤️ y mucho código por " @TonyBlanco". Versión 3.8 PRO - Edición Especial 2026.

## 📜 Licencia
MIT License — Libre uso personal y comercial.

