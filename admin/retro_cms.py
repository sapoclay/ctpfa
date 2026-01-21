#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════╗
║  CTPFA CMS - Cliente de Escritorio                            ║
║  Gestiona artículos de tu web retro desde tu ordenador        ║
║                                                               ║
║  Este archivo es el punto de entrada principal.               ║
║  El código está modularizado en el paquete 'cms/':            ║
║    - cms/theme.py       → Tema visual retro                   ║
║    - cms/dialogs.py     → Ventanas de diálogo                 ║
║    - cms/config.py      → Gestión de configuración            ║
║    - cms/articles.py    → Gestión de artículos                ║
║    - cms/html_generator.py → Generación de HTML               ║
║    - cms/uploader.py    → Subida FTP/SFTP                     ║
║    - cms/app.py         → Aplicación principal                ║
╚═══════════════════════════════════════════════════════════════╝
"""

import os

# Importar desde el paquete modularizado
from cms import RetroCMSApp


def main():
    """Punto de entrada principal"""
    # Crear directorios necesarios
    os.makedirs("articles", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    
    app = RetroCMSApp()
    app.run()


if __name__ == "__main__":
    main()
