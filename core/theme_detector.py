import winreg

def windows_is_dark():
    """Devuelve True si Windows está en modo oscuro."""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        )
        # AppsUseLightTheme = 0 → DARK
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        return value == 0
    except:
        return False  # Si falla, assume modo claro
