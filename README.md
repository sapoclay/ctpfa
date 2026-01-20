# ⚡ Cualquier Tiempo Pasado Fue Anterior ⚡

Una web retro rápida con estética años 80-90 y un cliente de escritorio para gestionar el contenido.

<img width="768" height="768" alt="logo" src="https://github.com/user-attachments/assets/2c1fa5f4-57fb-4f0b-a94f-0581cc25b582" />

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    CUALQUIER TIEMPO PASADO FUE ANTERIOR                       ║
║                         Tu portal de nostalgia digital                        ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

## 📋 Descripción

Este proyecto consiste en dos partes:

1. **Web estática retro**: Una página web ultra rápida con diseño inspirado en los años 80-90, con efectos neón, scanlines CRT y estética synthwave.

2. **Cliente de escritorio (CMS)**: Una aplicación Python con interfaz gráfica para crear, editar y publicar artículos desde tu ordenador.

## ✨ Características

### Web
- 🚀 **Ultra rápida**: HTML y CSS puro, sin JavaScript innecesario
- 🎨 **Estética retro**: Colores neón, efecto scanlines, tipografía monoespaciada
- 📱 **Responsive**: Se adapta a cualquier dispositivo
- 🔒 **Sin dependencias**: No requiere CDN ni frameworks externos
- ⚡ **Optimizada**: Carga instantánea

### Cliente de escritorio
- ✍️ **Editor de artículos**: Con soporte para Markdown básico
- 📤 **Publicación SFTP**: Sube artículos directamente al servidor
- 🎬 **Animación retro**: Visualización del proceso de subida
- 💾 **Persistencia**: Guarda configuración y artículos localmente
- 🗑️ **Gestión completa**: Crear, editar, eliminar (local y remoto)

## 📁 Estructura del proyecto

```
webRetro/
├── index.html              # Página principal
├── articulo.html           # Plantilla de artículo de ejemplo
├── css/
│   ├── style.css           # Estilos principales
│   └── article.css         # Estilos para artículos
├── admin/                  # Cliente de escritorio (NO subir al servidor)
│   ├── retro_cms.py        # Aplicación principal
│   ├── run_app.py          # Lanzador con entorno virtual
│   ├── requirements.txt    # Dependencias Python
│   ├── config.json         # Configuración del servidor
│   ├── README.md           # Documentación del cliente
│   ├── Img/
│   │   └── logo.png        # Logo de la aplicación
│   └── articles/           # Artículos guardados localmente
│       └── index.json      # Índice de artículos
└── README.md               # Este archivo
```

## 🚀 Instalación

### Requisitos previos
- Python 3.8 o superior
- Servidor web con acceso SFTP/SSH

### Paso 1: Subir la web al servidor

Sube **solo** estos archivos a tu servidor web:

```bash
scp -r index.html articulo.html css/ usuario@tuservidor:/var/www/html/webRetro/
```

**NO subas** la carpeta `admin/` al servidor.

### Paso 2: Configurar el cliente en tu equipo

```bash
# Copia la carpeta admin a tu equipo
cp -r admin/ ~/ctpfa-cms/

# Navega a la carpeta
cd ~/ctpfa-cms/

# Ejecuta el cliente (crea entorno virtual automáticamente)
python3 run_app.py
```

El script `run_app.py` automáticamente:
1. Crea un entorno virtual `.venv`
2. Instala las dependencias (`paramiko`, `Pillow`)
3. Lanza la aplicación

## 🖥️ Uso del cliente

### Primera configuración

1. Abre el cliente: `python3 run_app.py`
2. Ve a **Archivo → Configuración** o pulsa el botón **⚙ Config**
3. Introduce los datos de tu servidor:
   - **Host**: IP o dominio (ej: `midominio.com`)
   - **Puerto**: Normalmente `22`
   - **Usuario**: Tu usuario SSH
   - **Contraseña**: Tu contraseña SSH
   - **Ruta remota**: `/var/www/html/webRetro`
4. Pulsa **💾 Guardar**

### Crear un artículo

1. Pulsa **+ Nuevo**
2. Rellena los campos:
   - **Título**: Nombre del artículo
   - **Subtítulo**: Descripción breve
   - **Categoría**: Selecciona una categoría
   - **Tags**: Etiquetas separadas por comas
   - **Contenido**: Escribe usando Markdown
3. Pulsa **Guardar** para guardarlo localmente

### Publicar un artículo

1. Carga o crea el artículo que quieres publicar
2. Pulsa el botón **Publicar**
3. Confirma la publicación
4. El artículo se subirá al servidor y el `index.html` se actualizará automáticamente
5. Disfruta de la animación retro de transmisión 😎

> **Nota**: "Guardar" solo guarda en local, "Publicar" sube al servidor.

### Eliminar artículos

- Si el artículo está publicado, te preguntará si quieres eliminarlo también del servidor
- Los artículos no publicados solo se eliminan localmente

## ✍️ Formato Markdown

El editor soporta Markdown básico:

```markdown
## Título de sección
Se convierte en: ╔═══ TÍTULO DE SECCIÓN ═══╗

### Subtítulo  
Se convierte en: ★ SUBTÍTULO ★

**texto en negrita**
*texto en cursiva*

- Elemento de lista (se convierte en ► Elemento)

> Cita con estilo retro

` ` `
Bloque de código
` ` `
```

## 🎨 Personalización

### Colores

Los colores se definen en `css/style.css` mediante variables CSS:

```css
:root {
    --neon-pink: #ff00ff;
    --neon-cyan: #00ffff;
    --neon-green: #00ff00;
    --neon-yellow: #ffff00;
    --dark-bg: #0a0a0a;
    --dark-purple: #1a0a2e;
}
```

### Categorías

Las categorías disponibles se definen en `retro_cms.py`:

```python
CATEGORIES = [
    "TECNOLOGÍA", "VIDEOJUEGOS", "MÚSICA", "CINE", 
    "INTERNET", "HARDWARE", "SOFTWARE", "CULTURA"
]
```

### Logo

Coloca tu logo en `admin/Img/logo.png`. Se mostrará con un borde verde neón en la ventana "Acerca de".

## 🔒 Seguridad

- Las credenciales se guardan en `config.json` (solo en tu equipo local)
- **NUNCA** subas `config.json` a repositorios públicos
- Se recomienda usar claves SSH en lugar de contraseñas
- La carpeta `admin/` nunca debe estar en el servidor web

## 📦 Dependencias

### Web
- Ninguna (HTML + CSS puro)

### Cliente de escritorio
- Python 3.8+
- paramiko (conexión SFTP)
- Pillow (carga de imágenes)
- tkinter (incluido en Python)

## 🗂️ Flujo de trabajo

```
┌─────────────────────┐                      ┌─────────────────────┐
│   TU EQUIPO LOCAL   │                      │   SERVIDOR WEB      │
│                     │                      │                     │
│  ┌───────────────┐  │      SFTP/SSH        │  ┌───────────────┐  │
│  │  retro_cms.py │  │ ──────────────────►  │  │  index.html   │  │
│  │               │  │  Genera HTML y sube  │  │  articulo.html│  │
│  │  articles/    │  │                      │  │  css/         │  │
│  │  config.json  │  │                      │  │  *.html       │  │
│  └───────────────┘  │                      │  └───────────────┘  │
│                     │                      │                     │
│   Escribes y        │                      │   Los usuarios      │
│   gestionas         │                      │   ven la web        │
│   artículos         │                      │   ultra rápida      │
└─────────────────────┘                      └─────────────────────┘
```

## 🐛 Solución de problemas

### Error de Firefox en Linux (Snap)
Si al abrir enlaces aparece un error de `GTK_PATH`, el cliente ya incluye un fix automático.

### No se conecta al servidor
- Verifica que el puerto SSH (22) esté abierto
- Comprueba que las credenciales sean correctas
- Asegúrate de que la ruta remota existe

### No aparece el logo
- Verifica que existe `admin/Img/logo.png`
- El archivo debe ser PNG con transparencia para mejor resultado

## 📜 Licencia

© 2026 Cualquier Tiempo Pasado Fue Anterior

## 🔗 Enlaces

- **Repositorio**: [https://github.com/sapoclay/ctpfa](https://github.com/sapoclay/ctpfa)

---

```
════════════════════════════════════════════════════════════════════════════════
                    Hecho con 💾 y ☕ - Optimizado para Netscape Navigator 4.0+
════════════════════════════════════════════════════════════════════════════════
```
