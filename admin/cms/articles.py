"""
Gestión de artículos para CTPFA CMS
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path


class ArticleManager:
    """Gestiona los artículos localmente"""
    
    def __init__(self, config):
        self.config = config
        self.articles_path = Path(config.get("local", "articles_path"))
        self.articles_path.mkdir(parents=True, exist_ok=True)
        self.index_file = self.articles_path / "index.json"
        self.articles = self.load_index()
    
    def load_index(self):
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"articles": []}
    
    def save_index(self):
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.articles, f, indent=4, ensure_ascii=False)
    
    def create_article(self, data):
        """Crea un nuevo artículo"""
        slug = self.slugify(data['title'])
        filename = f"{slug}.json"
        filepath = self.articles_path / filename
        
        article = {
            "id": slug,
            "title": data['title'],
            "subtitle": data.get('subtitle', ''),
            "category": data['category'],
            "content": data['content'],
            "tags": data.get('tags', []),
            "author": self.config.get("site", "author"),
            "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "modified": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "published": data.get('published', False)
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(article, f, indent=4, ensure_ascii=False)
        
        # Actualizar índice
        self.articles["articles"].append({
            "id": slug,
            "title": data['title'],
            "category": data['category'],
            "created": article['created'],
            "published": data.get('published', False)
        })
        self.save_index()
        
        return article
    
    def update_article(self, article_id, data):
        """Actualiza un artículo existente"""
        filepath = self.articles_path / f"{article_id}.json"
        
        if not filepath.exists():
            raise FileNotFoundError(f"Artículo {article_id} no encontrado")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            article = json.load(f)
        
        article.update(data)
        article['modified'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(article, f, indent=4, ensure_ascii=False)
        
        # Actualizar índice
        for idx, art in enumerate(self.articles["articles"]):
            if art["id"] == article_id:
                self.articles["articles"][idx].update({
                    "title": article['title'],
                    "category": article['category'],
                    "published": article.get('published', False)
                })
                break
        self.save_index()
        
        return article
    
    def get_article(self, article_id):
        """Obtiene un artículo por ID"""
        filepath = self.articles_path / f"{article_id}.json"
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def delete_article(self, article_id):
        """Elimina un artículo"""
        filepath = self.articles_path / f"{article_id}.json"
        if filepath.exists():
            os.remove(filepath)
        
        self.articles["articles"] = [
            a for a in self.articles["articles"] if a["id"] != article_id
        ]
        self.save_index()
    
    def list_articles(self):
        """Lista todos los artículos"""
        return self.articles.get("articles", [])
    
    @staticmethod
    def slugify(text):
        """Convierte texto a slug URL-friendly"""
        text = text.lower()
        text = re.sub(r'[áàäâ]', 'a', text)
        text = re.sub(r'[éèëê]', 'e', text)
        text = re.sub(r'[íìïî]', 'i', text)
        text = re.sub(r'[óòöô]', 'o', text)
        text = re.sub(r'[úùüû]', 'u', text)
        text = re.sub(r'[ñ]', 'n', text)
        text = re.sub(r'[^a-z0-9]+', '-', text)
        text = text.strip('-')
        return text


    def extract_article_data(self, html_content, filename):
        """Extrae los datos del artículo desde el HTML sin guardar."""
        import json
        import re
        
        # Estrategia 1: Buscar JSON incrustado
        json_match = re.search(r'<script type="application/json" id="ctpfa-data">(.*?)</script>', html_content, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                if all(k in data for k in ['title', 'content', 'category']):
                    data['published'] = True
                    # Asegurar ID
                    if 'id' not in data and filename:
                        data['id'] = filename.replace('.html', '')
                    return data
            except json.JSONDecodeError:
                pass

        # Estrategia 2: Parsing Best Effort (Legacy)
        try:
            title_match = re.search(r'<title>(.*?) (?:\||-) .*?</title>', html_content)
            title = title_match.group(1).strip() if title_match else "Sin título"
            
            subtitle_match = re.search(r'<meta name="description" content="(.*?) - .*?">', html_content)
            subtitle = subtitle_match.group(1).strip() if subtitle_match else ""
            
            category_match = re.search(r'<span class="article-category">(.*?)</span>', html_content)
            category = category_match.group(1).strip() if category_match else "GENERAL"
            
            # Intentar encontrar contenido con section o div
            content_match = re.search(r'<(?:section|div) class="article-content">(.*?)</(?:section|div)>', html_content, re.DOTALL)
            html_body = content_match.group(1).strip() if content_match else ""
            
            if not html_body:
                # Intento alternativo si el anterior falló (por ejemplo, si hay etiquetas anidadas)
                content_match = re.search(r'class="article-content">(.*?)</article>', html_content, re.DOTALL)
                if content_match:
                    html_body = content_match.group(1).strip()
                    # Quitar el posible cierre de section/div sobrante
                    html_body = re.sub(r'</(?:section|div)>\s*$', '', html_body)
            
            content = self._html_to_markdown_basic(html_body)
            
            tags = []
            tags_match = re.findall(r'<span class="tag">#(.*?)</span>', html_content)
            if tags_match:
                tags = [t.lower() for t in tags_match]
            
            data = {
                'title': title,
                'subtitle': subtitle,
                'category': category,
                'content': content,
                'tags': tags,
                'published': True,
                'id': filename.replace('.html', '') if filename else None
            }
            return data
            
        except Exception as e:
            print(f"Error extrayendo datos legacy: {e}")
            return None

    def import_article_from_html(self, html_content, filename, overwrite=False):
        """Importa un artículo desde su contenido HTML."""
        data = self.extract_article_data(html_content, filename)
        if data:
            return self.create_or_update_article(data, force_id=data.get('id'), overwrite=overwrite)
        return None

    def create_or_update_article(self, data, force_id=None, overwrite=True):
        """Crea o actualiza un artículo basado en los datos importados"""
        # Si viene con ID (del JSON o filename), usamos ese
        article_id = data.get('id', force_id)
        if not article_id:
             article_id = self.slugify(data['title'])
        
        # Verificar si existe
        filepath = self.articles_path / f"{article_id}.json"
        
        if filepath.exists():
            if not overwrite:
                # No sobreescribir, devolver lo que había o None para indicar que se saltó
                # Devolvemos None para que el caller sepa que no se importó/actualizó
                return None
            return self.update_article(article_id, data)
        else:
            # create_article genera ID nuevo, así que mejor guardamos manualmente
            # para forzar el ID que queremos
            article = {
                "id": article_id,
                "title": data['title'],
                "subtitle": data.get('subtitle', ''),
                "category": data['category'],
                "content": data['content'],
                "tags": data.get('tags', []),
                "author": self.config.get("site", "author"),
                "created": data.get('created', datetime.now().strftime("%Y-%m-%d %H:%M")),
                "modified": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "published": True
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(article, f, indent=4, ensure_ascii=False)
            
            # Actualizar índice
            self.articles["articles"].append({
                "id": article_id,
                "title": data['title'],
                "category": data['category'],
                "created": article['created'],
                "published": True
            })
            self.save_index()
            return article
    def _html_to_markdown_basic(self, html):
        """Convierte HTML básico a Markdown"""
        # Saltos de línea
        text = html.replace('<br>', '\n').replace('<br/>', '\n')
        text = text.replace('</p>', '\n\n').replace('<p>', '')
        
        # Negrita y Cursiva
        text = re.sub(r'<strong>(.*?)</strong>', r'**\1**', text)
        text = re.sub(r'<b>(.*?)</b>', r'**\1**', text)
        text = re.sub(r'<em>(.*?)</em>', r'*\1*', text)
        text = re.sub(r'<i>(.*?)</i>', r'*\1*', text)
        
        # Listas
        text = text.replace('<ul>', '').replace('</ul>', '')
        text = text.replace('<li>', '- ').replace('</li>', '\n')
        
        # Headers
        text = re.sub(r'<h2>.*?(.*?) .*?</h2>', r'## \1', text)
        text = re.sub(r'<h3>.*?(.*?) .*?</h3>', r'### \1', text)
        
        # Citas y Código
        text = re.sub(r'<blockquote.*?><p>(.*?)</p></blockquote>', r'> \1', text)
        text = re.sub(r'<pre.*?>(.*?)</pre>', lambda m: f"```\n{m.group(1)}\n```", text, flags=re.DOTALL)
        
        # Limpieza final
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

