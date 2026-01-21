"""
Generación de HTML para CTPFA CMS
"""

import re
from datetime import datetime
from string import Template


class HTMLGenerator:
    """Genera HTML a partir de los artículos"""
    
    ARTICLE_TEMPLATE = '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="${subtitle} - Cualquier Tiempo Pasado Fue Anterior">
    <title>${title} | Cualquier Tiempo Pasado Fue Anterior</title>
    <link rel="stylesheet" href="css/style.css">
    <link rel="stylesheet" href="css/article.css">
</head>
<body>
    <div class="scanlines"></div>
    
    <header class="header">
        <div class="header-content">
            <a href="index.html" class="logo">
                <span class="logo-text">CTPFA</span>
                <span class="logo-zone">·</span>
            </a>
            <nav class="nav">
                <a href="index.html" class="nav-link">INICIO</a>
                <a href="index.html#articulos" class="nav-link active">ARTÍCULOS</a>
                <a href="index.html#about" class="nav-link">ABOUT</a>
                <a href="index.html#contacto" class="nav-link">CONTACTO</a>
                <button class="theme-toggle" id="themeToggle" aria-label="Cambiar tema">
                    <span class="icon">☀</span>
                    <span class="label">CLARO</span>
                </button>
            </nav>
        </div>
    </header>

    <main>
        <article class="article">
            <header class="article-header">
                <div class="article-meta">
                    <span class="article-category">${category}</span>
                    <span class="article-date">${date}</span>
                    <span class="article-author">✍ ${author}</span>
                    <span class="article-reading">⏱ ${reading_time} min lectura</span>
                </div>
                <h1 class="article-title">${title}</h1>
                <p class="article-subtitle">${subtitle}</p>
            </header>

            <div class="article-content">
                ${content}
            </div>

            <footer class="article-footer">
                <div class="article-tags">
                    ${tags}
                </div>
                <div class="article-nav">
                    <a href="index.html#articulos" class="btn-back">[ ← VOLVER A ARTÍCULOS ]</a>
                </div>
            </footer>
        </article>
    </main>

            <footer class="footer">
        <div class="footer-content">
            <p class="footer-text">════════════════════════════════════════════════════════</p>
            <p class="footer-copy">© 2026 Cualquier Tiempo Pasado Fue Anterior - Ni derechos ni torcidos</p>
            <div class="footer-links">
                <a href="#" id="downloadMd" class="footer-link">[ ↓ DESCARGAR .MD ]</a>
            </div>
            <p class="footer-info">Optimizado para Netscape Navigator 4.0+ | Resolución: 800x600</p>
            <p class="footer-text">════════════════════════════════════════════════════════</p>
        </div>
    </footer>

    <script>
        // Sistema de cambio de tema y Descarga MD
        (function() {
            // TEMA
            const themeToggle = document.getElementById('themeToggle');
            const icon = themeToggle.querySelector('.icon');
            const label = themeToggle.querySelector('.label');
            
            const savedTheme = localStorage.getItem('ctpfa-theme') || 'dark';
            document.documentElement.setAttribute('data-theme', savedTheme);
            updateButton(savedTheme);
            
            themeToggle.addEventListener('click', function() {
                const currentTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                
                document.documentElement.setAttribute('data-theme', newTheme);
                localStorage.setItem('ctpfa-theme', newTheme);
                updateButton(newTheme);
            });
            
            function updateButton(theme) {
                if (theme === 'dark') {
                    icon.textContent = '☀';
                    label.textContent = 'CLARO';
                } else {
                    icon.textContent = '☾';
                    label.textContent = 'OSCURO';
                }
            }

            // DESCARGA MARKDOWN
            const downloadBtn = document.getElementById('downloadMd');
            if (downloadBtn) {
                downloadBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    
                    try {
                        const script = document.getElementById('ctpfa-data');
                        if (!script) {
                            alert('Error: Datos no encontrados');
                            return;
                        }
                        
                        const data = JSON.parse(script.textContent);
                        
                        // Construir contenido Markdown
                        const frontmatter = [
                            '---',
                            `title: ${data.title}`,
                            `category: ${data.category}`,
                            `tags: ${(data.tags || []).join(', ')}`,
                            `date: ${data.created}`,
                            '---',
                            '',
                            ''
                        ].join('\\n');
                        
                        const mdContent = frontmatter + data.content;
                        
                        // Crear Blob y descargar
                        const blob = new Blob([mdContent], { type: 'text/markdown' });
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = (data.id || 'article') + '.md';
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        URL.revokeObjectURL(url);
                        
                    } catch (err) {
                        console.error(err);
                        alert('Error al generar la descarga');
                    }
                });
            }
        })();
    </script>
</body>
</html>'''

    CARD_TEMPLATE = '''                <article class="card">
                    <div class="card-header">
                        <span class="card-category">${category}</span>
                        <span class="card-date">${date}</span>
                    </div>
                    <h3 class="card-title">${title}</h3>
                    <p class="card-excerpt">${excerpt}</p>
                    <a href="${filename}" class="card-link">[ LEER MÁS → ]</a>
                </article>'''

    def __init__(self, articles_manager, config=None):
        self.am = articles_manager
        self.config = config
    
    def generate_article_html(self, article):
        """Genera el HTML de un artículo"""
        # Procesar contenido (markdown básico a HTML)
        content = self.process_content(article['content'])
        
        # Calcular tiempo de lectura
        words = len(article['content'].split())
        reading_time = max(1, words // 200)
        
        # Generar tags HTML
        tags_html = '\n                    '.join([
            f'<span class="tag">#{tag.upper()}</span>' 
            for tag in article.get('tags', [])
        ])
        
        # Formatear fecha
        date_obj = datetime.strptime(article['created'], "%Y-%m-%d %H:%M")
        date_formatted = date_obj.strftime("%d-%m-%Y")
        
        # Obtener autor de la configuración
        author = "Admin"
        if self.config:
            author_config = self.config.get("site", "author")
            if isinstance(author_config, str) and author_config:
                author = author_config
        
        # Preparar datos JSON para incrustar (para importación sin pérdidas)
        import json
        article_data = article.copy()
        # Asegurar que no hay datos sensibles si los hubiera (en este caso no, pero buena práctica)
        json_data = json.dumps(article_data, ensure_ascii=False)
        
        template = Template(self.ARTICLE_TEMPLATE)
        # Inyectar el script con datos JSON antes del cierre del body
        # Como no tenemos una variable para eso en el template original, lo añadiremos
        # modificando el template on-the-fly o simplemente concatenando, 
        # pero es más limpio modificar el TEMPLATE si es posible.
        # Dado que el template es una constante de clase, lo mejor es inyectar el script
        # al final del contenido o modificar el template para incluir una variable ${json_data}
        # Sin embargo, el template actual no tiene esa variable logica.
        # Estrategia: Reemplazar </body> con el script + </body>
        
        html = template.safe_substitute(
            title=article['title'],
            subtitle=article.get('subtitle', ''),
            category=article['category'].upper(),
            date=date_formatted,
            author=author,
            reading_time=reading_time,
            content=content,
            tags=tags_html
        )
        
        # Inyectar script de datos
        script_tag = f'<script type="application/json" id="ctpfa-data">{json_data}</script>'
        return html.replace('</body>', f'{script_tag}\n</body>')
    
    def strip_markdown(self, text):
        """Elimina el formato markdown del texto para generar texto plano"""
        # Eliminar negritas y cursivas
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'__(.+?)__', r'\1', text)
        text = re.sub(r'_(.+?)_', r'\1', text)
        # Eliminar headers
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        # Eliminar marcadores de lista
        text = re.sub(r'^[\-\*]\s+', '', text, flags=re.MULTILINE)
        # Eliminar citas
        text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
        # Eliminar bloques de código
        text = re.sub(r'```[\s\S]*?```', '', text)
        text = re.sub(r'`(.+?)`', r'\1', text)
        # Eliminar enlaces [texto](url)
        text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
        # Eliminar imágenes ![alt](url)
        text = re.sub(r'!\[.*?\]\(.+?\)', '', text)
        # Limpiar espacios múltiples y saltos de línea
        text = re.sub(r'\n+', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def generate_index_cards(self, articles):
        """Genera las tarjetas para el index"""
        cards = []
        for art in sorted(articles, key=lambda x: x['created'], reverse=True):
            full_article = self.am.get_article(art['id'])
            if not full_article or not full_article.get('published', False):
                continue
            
            # Crear excerpt (limpiar markdown primero)
            content = self.strip_markdown(full_article['content'])
            excerpt = content[:150].rsplit(' ', 1)[0] + '...'
            
            # Formatear fecha
            date_obj = datetime.strptime(art['created'], "%Y-%m-%d %H:%M")
            date_formatted = date_obj.strftime("%d-%m-%Y")
            
            template = Template(self.CARD_TEMPLATE)
            cards.append(template.safe_substitute(
                title=art['title'],
                category=art['category'].upper(),
                date=date_formatted,
                excerpt=excerpt,
                filename=f"{art['id']}.html"
            ))
        
        return '\n\n'.join(cards)
    
    def generate_tag_cloud(self, articles):
        """Genera la nube de etiquetas HTML"""
        # Contar tags
        tag_counts = {}
        for art in articles:
            full_article = self.am.get_article(art['id'])
            if full_article and full_article.get('published', False):
                for tag in full_article.get('tags', []):
                    clean_tag = tag.strip().upper()
                    if clean_tag:
                        tag_counts[clean_tag] = tag_counts.get(clean_tag, 0) + 1
        
        if not tag_counts:
            return ""
            
        # Generar HTML con tamaños relativos
        max_count = max(tag_counts.values())
        min_count = min(tag_counts.values())
        diff = max_count - min_count if max_count > min_count else 1
        
        tags_html = []
        for tag, count in sorted(tag_counts.items()):
            # Tamaño entre 0.8rem y 2.0rem
            size = 0.8 + ((count - min_count) / diff) * 1.2
            tags_html.append(
                f'<span style="font-size: {size:.1f}rem" class="cloud-tag" title="{count} artículos">#{tag}</span>'
            )
            
        return f'''
        <section id="temas" class="tag-cloud">
            <h2 class="section-title">
                <span class="title-deco">▓▓▓</span>
                TEMAS
                <span class="title-deco">▓▓▓</span>
            </h2>
            <div class="cloud-content">
                {' '.join(tags_html)}
            </div>
        </section>'''

    def generate_index_html(self, articles):
        """Genera el index.html completo con los artículos publicados"""
        cards_html = self.generate_index_cards(articles)
        tag_cloud_html = self.generate_tag_cloud(articles)
        
        # Contar artículos publicados
        published_count = 0
        for art in articles:
            full_article = self.am.get_article(art['id'])
            if full_article and full_article.get('published', False):
                published_count += 1
        
        # Timestamp para evitar caché
        cache_buster = datetime.now().strftime("%Y%m%d%H%M%S")
        
        return f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Cualquier Tiempo Pasado Fue Anterior - Artículos de los años 80 y 90">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <title>⚡ Cualquier Tiempo Pasado Fue Anterior ⚡</title>
    <link rel="stylesheet" href="css/style.css?v={cache_buster}">
    <style>
        .tag-cloud {{
            padding: 4rem 2rem;
            background: var(--bg-secondary);
            text-align: center;
        }}
        .cloud-content {{
            max_width: 800px;
            margin: 2rem auto;
            line-height: 2.5;
        }}
        .cloud-tag {{
            color: var(--neon-cyan);
            margin: 0 0.5rem;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
            cursor: default;
        }}
        .cloud-tag:hover {{
            color: var(--neon-pink);
            text-shadow: 0 0 10px var(--neon-pink);
            transform: scale(1.1);
        }}
    </style>
</head>
<body>
    <div class="scanlines"></div>
    
    <header class="header">
        <div class="header-content">
            <h1 class="logo">
                <span class="logo-text">CTPFA</span>
                <span class="logo-zone">·</span>
            </h1>
            <nav class="nav">
                <a href="#" class="nav-link active">INICIO</a>
                <a href="#articulos" class="nav-link">ARTÍCULOS</a>
                <a href="#about" class="nav-link">ABOUT</a>
                <a href="#contacto" class="nav-link">CONTACTO</a>
                <button class="theme-toggle" id="themeToggle" aria-label="Cambiar tema">
                    <span class="icon">☀</span>
                    <span class="label">CLARO</span>
                </button>
            </nav>
        </div>
    </header>

    <main>
        <section class="hero">
            <div class="hero-content">
                <p class="hero-subtitle">※ BIENVENIDO AL PORTAL ※</p>
                <h2 class="hero-title">CUALQUIER TIEMPO PASADO FUE ANTERIOR</h2>
                <p class="hero-desc">Tomando malas de decisiones desde 1982</p>
                <div class="hero-stats">
                    <div class="stat">
                        <span class="stat-num">{published_count}</span>
                        <span class="stat-label">ARTÍCULOS</span>
                    </div>
                    <div class="stat">
                        <span class="stat-num">64K</span>
                        <span class="stat-label">VISITAS</span>
                    </div>
                    <div class="stat">
                        <span class="stat-num">1337</span>
                        <span class="stat-label">USUARIOS</span>
                    </div>
                </div>
            </div>
        </section>

        {tag_cloud_html}

        <section id="articulos" class="articles">
            <h2 class="section-title">
                <span class="title-deco">▓▓▓</span>
                ÚLTIMOS ARTÍCULOS
                <span class="title-deco">▓▓▓</span>
            </h2>
            
            <div class="articles-grid">
{cards_html}
            </div>
        </section>

        <section id="about" class="about">
            <div class="about-content">
                <div class="terminal">
                    <div class="terminal-header">
                        <span class="terminal-btn"></span>
                        <span class="terminal-btn"></span>
                        <span class="terminal-btn"></span>
                        <span class="terminal-title">ABOUT.TXT</span>
                    </div>
                    <div class="terminal-body">
                        <p><span class="prompt">C:\\CTPFA></span> ABOUT-y0.EXE</p>
                        <p class="terminal-text">
                            ╔════════════════════════════════════════╗<br>
                            ║  CTPFA - EST. 1982                     ║<br>
                            ╠════════════════════════════════════════╣<br>
                            ║  Esto es un portal dedicado a preservar║<br>
                            ║  la memoria de la era dorada de cuando ║<br>
                            ║  las cosas se hacían divertidas.       ║<br>
                            ║                                        ║<br>
                            ║  Desde los primeros ordenadores hasta  ║<br>
                            ║  los apuntes de seguridad informática, ║<br>
                            ║  aquí encontrarás todo esto y más ...  ║<br>
                            ║  hasta que me canse                    ║<br>
                            ╚════════════════════════════════════════╝
                        </p>
                        <p><span class="prompt">C:\\CTPFA></span> <span class="cursor">█</span></p>
                    </div>
                </div>
            </div>
        </section>

        <section id="contacto" class="contact">
            <h2 class="section-title">
                <span class="title-deco">▓▓▓</span>
                CONTACTO
                <span class="title-deco">▓▓▓</span>
            </h2>
            <form class="contact-form" action="#" method="post">
                <div class="form-group">
                    <label for="nombre">NOMBRE:</label>
                    <input type="text" id="nombre" name="nombre" required>
                </div>
                <div class="form-group">
                    <label for="email">E-MAIL:</label>
                    <input type="email" id="email" name="email" required>
                </div>
                <div class="form-group">
                    <label for="mensaje">MENSAJE:</label>
                    <textarea id="mensaje" name="mensaje" rows="5" required></textarea>
                </div>
                <button type="submit" class="btn-submit">[ ENVIAR TRANSMISIÓN ]</button>
            </form>
        </section>
    </main>

    <footer class="footer">
        <div class="footer-content">
            <p class="footer-text">════════════════════════════════════════════════════════</p>
            <p class="footer-copy">© 2026 Cualquier Tiempo Pasado Fue Anterior - Ni derechos ni ná</p>
            <p class="footer-info">Optimizado para Netscape Navigator 4.0+ | Resolución: 800x600</p>
            <p class="footer-counter">
                <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='88' height='31'%3E%3Crect fill='%23000' width='88' height='31'/%3E%3Ctext x='44' y='20' text-anchor='middle' fill='%2300ff00' font-family='monospace' font-size='12'%3E{published_count:06d}%3C/text%3E%3C/svg%3E" alt="Contador de visitas" width="88" height="31">
            </p>
            <p class="footer-text">════════════════════════════════════════════════════════</p>
        </div>
    </footer>

    <script>
        // Sistema de cambio de tema
        (function() {{
            const themeToggle = document.getElementById('themeToggle');
            const icon = themeToggle.querySelector('.icon');
            const label = themeToggle.querySelector('.label');
            
            // Cargar tema guardado o usar oscuro por defecto
            const savedTheme = localStorage.getItem('ctpfa-theme') || 'dark';
            document.documentElement.setAttribute('data-theme', savedTheme);
            updateButton(savedTheme);
            
            themeToggle.addEventListener('click', function() {{
                const currentTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                
                document.documentElement.setAttribute('data-theme', newTheme);
                localStorage.setItem('ctpfa-theme', newTheme);
                updateButton(newTheme);
            }});
            
            function updateButton(theme) {{
                if (theme === 'dark') {{
                    icon.textContent = '☀';
                    label.textContent = 'CLARO';
                }} else {{
                    icon.textContent = '☾';
                    label.textContent = 'OSCURO';
                }}
            }}
        }})();
    </script>
</body>
</html>'''
    
    def process_content(self, content):
        """Procesa el contenido con formato básico.

        Comportamiento:
        - Las líneas se agrupan en párrafos separados por una línea en blanco.
        - Los saltos de línea simples dentro de un párrafo se convierten en `<br>`.
        - Conserva listas, encabezados, bloques de código y citas.
        """
        raw_lines = content.split('\n')
        html_lines = []
        in_list = False
        in_code = False

        # Buffer para agrupar líneas de un mismo párrafo
        para_buf = []

        def flush_paragraph():
            nonlocal para_buf
            if not para_buf:
                return
            # Unir líneas del párrafo según reglas de Markdown:
            # - Una línea simple se une con un espacio
            # - Si una línea termina con dos espacios, se interpreta como <br>
            parts = []
            for i, pl in enumerate(para_buf):
                if pl.endswith('  '):
                    parts.append(pl.rstrip())
                    parts.append('<br>')
                else:
                    parts.append(pl)
                    # Añadir espacio entre líneas si no es la última y si la siguiente no empieza con <
                    if i != len(para_buf) - 1:
                        parts.append(' ')

            para_text = ''.join(parts).strip()
            # Aplicar formatos inline
            para_text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', para_text)
            para_text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', para_text)
            html_lines.append(f'<p>{para_text}</p>')
            para_buf = []

        for raw in raw_lines:
            line = raw.rstrip('\r')

            # Bloques de código
            if line.strip().startswith('```'):
                # Antes de entrar/salir de código, vaciar párrafo pendiente
                flush_paragraph()
                if in_code:
                    html_lines.append('</pre>')
                    in_code = False
                else:
                    html_lines.append('<pre class="code-block">')
                    in_code = True
                continue

            if in_code:
                html_lines.append(line)
                continue

            stripped = line.strip()

            # Línea en blanco => final de párrafo o lista
            if stripped == '':
                flush_paragraph()
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                continue

            # Headers
            if stripped.startswith('## '):
                flush_paragraph()
                html_lines.append(f'<h2>╔═══ {stripped[3:].upper()} ═══╗</h2>')
                continue
            elif stripped.startswith('### '):
                flush_paragraph()
                html_lines.append(f'<h3>★ {stripped[4:].upper()} ★</h3>')
                continue

            # Listas
            if stripped.startswith('- ') or stripped.startswith('* '):
                # Si había un párrafo abierto, cerrarlo
                flush_paragraph()
                if not in_list:
                    html_lines.append('<ul class="retro-list">')
                    in_list = True
                html_lines.append(f'<li>► {stripped[2:]}</li>')
                continue

            # Citas
            if stripped.startswith('> '):
                flush_paragraph()
                html_lines.append(f'<blockquote class="retro-quote"><p>{stripped[2:]}</p></blockquote>')
                continue

            # Texto normal -> acumular en buffer de párrafo
            # Mantener el texto tal cual (sin .strip()) pero quitar espacios finales
            para_line = line
            para_buf.append(para_line)

        # Fin del bucle: vaciar buffers abiertos
        flush_paragraph()
        if in_list:
            html_lines.append('</ul>')
        if in_code:
            html_lines.append('</pre>')

        # Añadir una línea en blanco adicional entre bloques para que
        # en el HTML generado haya una separación visual (línea en blanco)
        return '\n\n                '.join(html_lines)
