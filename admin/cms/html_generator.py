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
            <p class="footer-copy">© 2026 Cualquier Tiempo Pasado Fue Anterior - Todos los derechos reservados</p>
            <p class="footer-info">Optimizado para Netscape Navigator 4.0+ | Resolución: 800x600</p>
            <p class="footer-text">════════════════════════════════════════════════════════</p>
        </div>
    </footer>

    <script>
        // Sistema de cambio de tema
        (function() {
            const themeToggle = document.getElementById('themeToggle');
            const icon = themeToggle.querySelector('.icon');
            const label = themeToggle.querySelector('.label');
            
            // Cargar tema guardado o usar oscuro por defecto
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
        date_formatted = date_obj.strftime("%d de %B, %Y")
        
        # Obtener autor de la configuración
        author = "Admin"
        if self.config:
            author_config = self.config.get("site", "author")
            if isinstance(author_config, str) and author_config:
                author = author_config
        
        template = Template(self.ARTICLE_TEMPLATE)
        return template.safe_substitute(
            title=article['title'],
            subtitle=article.get('subtitle', ''),
            category=article['category'].upper(),
            date=date_formatted,
            author=author,
            reading_time=reading_time,
            content=content,
            tags=tags_html
        )
    
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
            date_formatted = date_obj.strftime("%d/%m/%Y")
            
            template = Template(self.CARD_TEMPLATE)
            cards.append(template.safe_substitute(
                title=art['title'],
                category=art['category'].upper(),
                date=date_formatted,
                excerpt=excerpt,
                filename=f"{art['id']}.html"
            ))
        
        return '\n\n'.join(cards)
    
    def generate_index_html(self, articles):
        """Genera el index.html completo con los artículos publicados"""
        cards_html = self.generate_index_cards(articles)
        
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
                <p class="hero-desc">Tu fuente de nostalgia digital desde 1989</p>
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
                        <p><span class="prompt">C:\\CTPFA></span> ABOUT.EXE</p>
                        <p class="terminal-text">
                            ╔════════════════════════════════════════╗<br>
                            ║  CTPFA - EST. 1989                     ║<br>
                            ╠════════════════════════════════════════╣<br>
                            ║  Somos un portal dedicado a preservar  ║<br>
                            ║  la memoria de la era dorada de la     ║<br>
                            ║  tecnología y la cultura pop.          ║<br>
                            ║                                        ║<br>
                            ║  Desde los primeros ordenadores hasta  ║<br>
                            ║  los clásicos del cine y la música,    ║<br>
                            ║  aquí encontrarás todo lo retro.       ║<br>
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
            <p class="footer-copy">© 2026 Cualquier Tiempo Pasado Fue Anterior - Todos los derechos reservados</p>
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
        """Procesa el contenido con formato básico"""
        lines = content.split('\n')
        html_lines = []
        in_list = False
        in_code = False
        
        for line in lines:
            line = line.strip()
            
            # Bloques de código
            if line.startswith('```'):
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
            
            # Headers
            if line.startswith('## '):
                html_lines.append(f'<h2>╔═══ {line[3:].upper()} ═══╗</h2>')
            elif line.startswith('### '):
                html_lines.append(f'<h3>★ {line[4:].upper()} ★</h3>')
            # Listas
            elif line.startswith('- ') or line.startswith('* '):
                if not in_list:
                    html_lines.append('<ul class="retro-list">')
                    in_list = True
                html_lines.append(f'<li>► {line[2:]}</li>')
            # Citas
            elif line.startswith('> '):
                html_lines.append(f'<blockquote class="retro-quote"><p>{line[2:]}</p></blockquote>')
            # Párrafos normales
            elif line:
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                # Procesar negritas y cursivas
                line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
                line = re.sub(r'\*(.+?)\*', r'<em>\1</em>', line)
                html_lines.append(f'<p>{line}</p>')
            elif in_list:
                html_lines.append('</ul>')
                in_list = False
        
        if in_list:
            html_lines.append('</ul>')
        if in_code:
            html_lines.append('</pre>')
        
        return '\n                '.join(html_lines)
