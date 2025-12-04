# -*- coding: utf-8 -*-
"""
SHILLONG CONTABILIDAD v3.7.8 PRO — Update Checker
--------------------------------------------------
Checks for updates from GitHub releases and notifies users.
"""

import requests
import json
import os
from pathlib import Path

# Import version comparison safely
try:
    from packaging.version import parse as parse_version
except ImportError:
    parse_version = None

# Current app version
APP_VERSION = "3.7.8"

# GitHub API URL for releases
GITHUB_API_URL = "https://api.github.com/repos/TonyBlanco/SHILLONG-CONTABILIDAD/releases/latest"

# Cache file to avoid repeated API calls
CACHE_FILE = Path("data/update_cache.json")
CACHE_DURATION_HOURS = 6  # Check every 6 hours


def clean_version(v_str):
    """
    Clean version string by removing common prefixes and characters.
    Handles formats like: v3.7.8, 3.7.7_4.3.2, 3.7.8-PRO, etc.
    """
    if not v_str:
        return "0.0.0"
    # Remove 'v' or 'V' prefix
    v_str = v_str.lstrip('v').lstrip('V')
    # Remove quotes and whitespace
    v_str = v_str.replace("'", "").replace('"', "").strip()
    # Remove any suffix like "-PRO", "-beta", etc. for comparison
    if "-" in v_str:
        v_str = v_str.split("-")[0]
    # Remove underscore suffix (e.g., 3.7.7_4.3.2 -> 3.7.7)
    if "_" in v_str:
        v_str = v_str.split("_")[0]
    return v_str


def get_local_version():
    """Get the current installed version."""
    return APP_VERSION


def _load_cache():
    """Load cached update check result."""
    try:
        if CACHE_FILE.exists():
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cache = json.load(f)
                # Check if cache is still valid
                import time
                cached_time = cache.get("timestamp", 0)
                if time.time() - cached_time < (CACHE_DURATION_HOURS * 3600):
                    return cache
    except (IOError, json.JSONDecodeError):
        pass
    return None


def _save_cache(data):
    """Save update check result to cache."""
    try:
        import time
        data["timestamp"] = time.time()
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except IOError:
        pass


def check_for_updates(force=False):
    """
    Check if a new version is available on GitHub.
    
    Args:
        force: If True, bypass cache and check immediately
        
    Returns:
        tuple: (update_available: bool, remote_version: str, download_url: str, release_notes: str)
    """
    local_version = get_local_version()
    
    # Check cache first (unless forced)
    if not force:
        cache = _load_cache()
        if cache:
            return (
                cache.get("update_available", False),
                cache.get("remote_version", local_version),
                cache.get("download_url"),
                cache.get("release_notes", "")
            )
    
    # Check if packaging is available
    if parse_version is None:
        print("[Updater] WARNING: 'packaging' module not installed. Install with: pip install packaging")
        return False, local_version, None, ""
    
    try:
        # Make API request to GitHub
        headers = {"Accept": "application/vnd.github.v3+json"}
        response = requests.get(GITHUB_API_URL, headers=headers, timeout=10)
        response.raise_for_status()
        release_data = response.json()
        
        # Get version tag
        raw_tag = release_data.get("tag_name", "0.0.0")
        remote_version = clean_version(raw_tag)
        local_version_clean = clean_version(local_version)
        
        # Get release notes
        release_notes = release_data.get("body", "No release notes available.")
        
        # Get download URL (prefer .exe installer)
        download_url = None
        for asset in release_data.get("assets", []):
            asset_name = asset.get("name", "").lower()
            if asset_name.endswith(".exe") or "setup" in asset_name or "installer" in asset_name:
                download_url = asset.get("browser_download_url")
                break
        
        # Fallback to release page if no .exe found
        if not download_url:
            download_url = release_data.get("html_url", "https://github.com/TonyBlanco/SHILLONG-CONTABILIDAD/releases")
        
        # Compare versions
        try:
            update_available = parse_version(remote_version) > parse_version(local_version_clean)
        except Exception:
            # Manual comparison fallback
            update_available = remote_version != local_version_clean
        
        # Cache the result
        result = {
            "update_available": update_available,
            "remote_version": remote_version,
            "local_version": local_version,
            "download_url": download_url,
            "release_notes": release_notes[:500] if release_notes else ""  # Limit notes length
        }
        _save_cache(result)
        
        return update_available, remote_version, download_url, release_notes
        
    except requests.exceptions.Timeout:
        print("[Updater] Connection timeout while checking for updates.")
        return False, local_version, None, ""
    except requests.exceptions.ConnectionError:
        print("[Updater] No internet connection. Cannot check for updates.")
        return False, local_version, None, ""
    except requests.exceptions.HTTPError as e:
        print(f"[Updater] HTTP error: {e}")
        return False, local_version, None, ""
    except (ValueError, KeyError) as e:
        print(f"[Updater] Error parsing update data: {e}")
        return False, local_version, None, ""


def get_update_info():
    """
    Get formatted update information for display.
    
    Returns:
        dict with keys: available, local_version, remote_version, download_url, message
    """
    local_version = get_local_version()
    update_available, remote_version, download_url, release_notes = check_for_updates()
    
    if update_available:
        message = f"🎉 Nueva versión disponible: v{remote_version}\n\nVersión actual: v{local_version}"
        if release_notes:
            message += f"\n\n📋 Notas de la versión:\n{release_notes[:300]}..."
    else:
        message = f"✅ Estás usando la última versión: v{local_version}"
    
    return {
        "available": update_available,
        "local_version": local_version,
        "remote_version": remote_version,
        "download_url": download_url,
        "message": message,
        "release_notes": release_notes
    }


# For backwards compatibility
def check_updates():
    """Alias for check_for_updates() for backwards compatibility."""
    available, version, url, _ = check_for_updates()
    return available, version, url


if __name__ == "__main__":
    # Test the updater
    print("=== SHILLONG Update Checker ===")
    print(f"Current version: {get_local_version()}")
    print("Checking for updates...")
    
    info = get_update_info()
    print(info["message"])
    
    if info["available"]:
        print(f"\nDownload: {info['download_url']}")
