# -*- coding: utf-8 -*-
import requests
import json
import sys

# Importar parse_version de forma segura
try:
    from packaging.version import parse as parse_version
except ImportError:
    parse_version = None 

# Importar versión local
try:
    from .version import VERSION as VERSION_LOCAL 
except ImportError:
    VERSION_LOCAL = "0.0.0" 

# URL de la API (Correcta)
GITHUB_API_URL = "https://api.github.com/repos/TonyBlanco/SHILLONG-CONTABILIDAD/releases/latest" 

def clean_version(v_str):
    """
    Limpia la cadena de versión de caracteres comunes que causan errores.
    Elimina 'v', comillas simples/dobles y espacios.
    """
    if not v_str: return "0.0.0"
    # Eliminar 'v' o 'V' al inicio
    v_str = v_str.lstrip('v').lstrip('V')
    # Eliminar comillas y espacios que puedan haberse colado
    v_str = v_str.replace("'", "").replace('"', "").strip()
    return v_str

def check_for_updates():
    """
    Compara la versión local con el último Release etiquetado en GitHub.
    """
    if parse_version is None:
        print("ADVERTENCIA: 'packaging' no instalado.")
        return False, VERSION_LOCAL, None
        
    try:
        # Consulta a GitHub
        response = requests.get(GITHUB_API_URL, timeout=5)
        response.raise_for_status()
        remote_data = response.json()
        
        # 1. Obtener el tag crudo
        raw_tag = remote_data.get("tag_name", "0.0.0")
        
        # 2. LIMPIEZA AGRESIVA DE LAS VERSIONES
        remote_version_clean = clean_version(raw_tag)
        local_version_clean = clean_version(VERSION_LOCAL)
        
        # Obtener URL de descarga
        download_url = None
        for asset in remote_data.get("assets", []):
            if asset.get("name", "").endswith(".exe"):
                download_url = asset.get("browser_download_url")
                break
        
        if not download_url:
             download_url = remote_data.get("html_url", "No se encontró el instalador.")

        # 3. Comparación segura
        if parse_version(remote_version_clean) > parse_version(local_version_clean):
            return True, remote_version_clean, download_url
        else:
            return False, local_version_clean, None
            
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")
        return False, VERSION_LOCAL, None
    except Exception as e:
        # Esto captura el error que veías en la imagen
        print(f"Error procesando la actualización: {e}")
        return False, VERSION_LOCAL, None