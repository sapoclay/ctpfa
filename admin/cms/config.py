"""
Gestión de configuración para CTPFA CMS
"""

import json
import os

# Configuración por defecto
CONFIG_FILE = "config.json"
ARTICLES_DIR = "articles"


class ConfigManager:
    """Gestiona la configuración del CMS"""
    
    DEFAULT_CONFIG = {
        "server": {
            "protocol": "ftp",
            "host": "",
            "port": 21,
            "username": "",
            "password": "",
            "key_file": "",
            "remote_path": "/var/www/html/webRetro"
        },
        "local": {
            "articles_path": "./articles",
            "templates_path": "./templates"
        },
        "site": {
            "name": "Cualquier Tiempo Pasado Fue Anterior",
            "author": "Admin",
            "auto_index": True
        }
    }
    
    def __init__(self, config_file=CONFIG_FILE):
        self.config_file = config_file
        self.config = self.load()
    
    def load(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self.DEFAULT_CONFIG.copy()
    
    def save(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)
    
    def get(self, *keys):
        """Obtiene un valor de la configuración con fallback a DEFAULT_CONFIG"""
        # Intentar obtener de la configuración cargada
        value = self.config
        found = True
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                found = False
                break
        
        if found:
            return value
            
        # Fallback a DEFAULT_CONFIG
        value = self.DEFAULT_CONFIG
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return value
    
    def set(self, value, *keys):
        d = self.config
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        d[keys[-1]] = value
        self.save()
