# -*- coding: utf-8 -*-
import os
import json
from pathlib import Path

def _config_dir():
    base = os.getenv('LOCALAPPDATA') or str(Path.home())
    path = Path(base) / "ShillongContabilidad"
    path.mkdir(parents=True, exist_ok=True)
    return path

def _config_file():
    return _config_dir() / "config.json"

def load_config():
    f = _config_file()
    if not f.exists():
        return {}
    try:
        return json.loads(f.read_text(encoding='utf-8'))
    except Exception:
        return {}

def save_config(cfg: dict):
    f = _config_file()
    f.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding='utf-8')

def get(key, default=None):
    cfg = load_config()
    return cfg.get(key, default)

def set(key, value):
    cfg = load_config()
    cfg[key] = value
    save_config(cfg)
