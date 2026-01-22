# ⚡ Cualquier Tiempo Pasado Fue Anterior ⚡

Una web retro rápida con estética años 80-90 y un cliente de escritorio creado con Python para gestionar el contenido.

<img width="768" height="768" alt="logo" src="https://github.com/user-attachments/assets/2c1fa5f4-57fb-4f0b-a94f-0581cc25b582" />

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    CUALQUIER TIEMPO PASADO FUE ANTERIOR                       ║
║                 De cuando tenía menos pelos en las piernas                    ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

## Descripción

Este proyecto consiste en dos partes:

1. **Web estática retro**: Una página web ultra rápida con diseño inspirado en los años 80-90, con efectos neón, scanlines CRT y estética synthwave.

2. **Cliente de escritorio (CMS)**: Una aplicación Python modularizada (paquete `cms/`) con interfaz gráfica para crear, editar y publicar artículos desde tu ordenador.

## Características

### Web
- 🚀 **Rápida**: HTML y CSS puro, "casi" sin JavaScript ni warradas que no se necesitan
- 🎨 **Estética retro**: Colores neón, efecto scanlines, tipografía monoespaciada
- 📱 **Responsive**: Se adapta a cualquier dispositivo
- 🔒 **Sin dependencias**: No requiere CDN ni frameworks externos
- ⚡ **Optimizada**: Carga instantánea

### Cliente de escritorio (CMS)
- ✍️ **Editor avanzado**: Campos para título, subtítulo, categoría, tags y contenido (Markdown)
- 📝 **Soporte Markdown**: Guía integrada y vista previa en navegador
- 📤 **Publicación SFTP/SSH**: Sube artículos y actualiza el índice en el servidor
- 📥 **Importar y descargar**: Importa artículos publicados y descarga todos como archivos Markdown
- 🗑️ **Gestión completa**: Crear, editar, eliminar artículos (local y remoto)
- 💾 **Persistencia local**: Guarda artículos y configuración en JSON
- 🎬 **Animación retro**: Progreso visual y barra de estado
- 🛠️ **Configuración fácil**: Diálogo para datos de servidor y protocolo
- 🧩 **Tooltips y ayuda**: Ayuda contextual y guía de Markdown

## 📁 Estructura del proyecto

```
webRetro/
├── index.html              # Página principal
├── LICENSE                 # Licencia
├── README.md               # Este archivo
├── admin/                  # Cliente de escritorio (NO subir al servidor)
│   ├── retro_cms.py        # Punto de entrada (inicia el paquete `cms`)
│   ├── run_app.py          # Lanzador que crea el venv e instala dependencias
│   ├── requirements.txt    # Dependencias Python
│   ├── config.json         # Configuración del servidor (local)
│   ├── README.md           # Documentación del cliente
│   ├── Img/                # Imágenes del cliente
│   ├── articles/           # Artículos guardados localmente (JSON)
│   │   ├── index.json      # Índice de artículos
│   │   └── ...             # Artículos individuales
│   ├── templates/          # Plantillas (vacío por defecto)
│   └── cms/                # Código modular del cliente (paquete)
│       ├── __init__.py
│       ├── app.py          # Lógica principal y UI
│       ├── articles.py     # Gestión de artículos
│       ├── config.py       # Gestión de configuración
│       ├── dialogs.py      # Diálogos y ventanas
│       ├── html_generator.py # Generador de HTML y JSON
│       ├── markdown_guide.txt # Guía de Markdown
│       ├── theme.py        # Temas y estilos
│       └── uploader.py     # Subida SFTP/FTP
├── articles/               # Carpeta para artículos web (vacía por defecto)
├── css/
│   ├── style.css           # Estilos principales
│   └── article.css         # Estilos para artículos
```

## Instalación

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

Detalles importantes:
- El cliente está modularizado dentro de `admin/cms/` como paquete Python. El punto de entrada sigue siendo `retro_cms.py`, que importa y arranca la clase `RetroCMSApp` desde `cms`.
- `run_app.py` crea un entorno virtual `.venv`, instala las dependencias listadas en `requirements.txt` y ejecuta `retro_cms.py`.

## Uso del cliente

### 1. Configuración inicial

1. Ejecuta el cliente: `python3 run_app.py`
2. Ve a **Archivo → Configuración**
3. Completa los datos de tu servidor (host, puerto, usuario, contraseña, ruta remota)
4. Elige el protocolo (SFTP recomendado)
5. Pulsa **Guardar**

### 2. Crear y editar artículos

1. Pulsa **+ Nuevo** para empezar un borrador
2. Completa los campos: título, subtítulo, categoría, tags y contenido (Markdown)
3. Pulsa **Guardar** para almacenar localmente
4. Puedes editar cualquier artículo guardado desde la lista lateral

### 3. Publicar y sincronizar

1. Selecciona o crea el artículo que quieres publicar
2. Pulsa **Publicar** para subirlo al servidor
3. El índice de la web se actualiza automáticamente
4. Disfruta de la animación retro y barra de estado

### 4. Importar y descargar artículos

- **Importar**: Descarga todos los artículos publicados en el servidor y los añade al cliente
- **Descargar como Markdown**: Exporta todos los artículos publicados como archivos `.md` en la carpeta que elijas

### 5. Eliminar artículos

- Puedes eliminar artículos locales o publicados
- Si el artículo está en el servidor, el cliente te preguntará si deseas borrarlo también remotamente

### 6. Vista previa y ayuda

- Pulsa **Vista previa** para ver el artículo en tu navegador
- Consulta la **Guía de Markdown** desde el menú Ayuda
- Tooltips y mensajes te acompañan en cada acción

## Formato Markdown

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

## Personalización

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

Las categorías disponibles se definen en `admin/cms/app.py` (atributo `RetroCMSApp.CATEGORIES`):

```python
CATEGORIES = [
    "TECNOLOGÍA", "VIDEOJUEGOS", "MÚSICA", "CINE", 
    "INTERNET", "HARDWARE", "SOFTWARE", "CULTURA",
    "GESTIÓN DE INCIDENTES DE SEGURIDAD"
]
```

## Seguridad

- Las credenciales se guardan en `config.json` (solo en tu equipo local)
- **NUNCA** subas `config.json` a repositorios públicos
- Se recomienda usar claves SSH en lugar de contraseñas
- La carpeta `admin/` nunca debe estar en el servidor web

## Dependencias

### Web
- Ninguna (HTML + CSS puro y duro)

### Cliente de escritorio
- Python 3.8+
- paramiko (conexión SFTP)
- Pillow (carga de imágenes)
- tkinter (incluido en Python)

## Flujo de trabajo

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

## Solución de problemas

### Error de Firefox en Linux (Snap)
Si al abrir enlaces aparece un error de `GTK_PATH`, el cliente ya incluye un fix automático.

### No se conecta al servidor
- Verifica que el puerto SSH (22) esté abierto
- Comprueba que las credenciales sean correctas
- Asegúrate de que la ruta remota existe

### No aparece el logo
- Verifica que existe `admin/Img/logo.png`
- El archivo debe ser PNG con transparencia para mejor resultado

## Licencia

2026 Cualquier Tiempo Pasado Fue Anterior

## 🔗 Enlaces

- **Repositorio**: [https://github.com/sapoclay/ctpfa](https://github.com/sapoclay/ctpfa)

---

```
════════════════════════════════════════════════════════════════════════════════
                    Hecho con 💾 y ☕ - Optimizado para Netscape Navigator 4.0+
════════════════════════════════════════════════════════════════════════════════
```
