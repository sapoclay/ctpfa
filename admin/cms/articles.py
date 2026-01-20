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
