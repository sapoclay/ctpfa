"""
Aplicación principal del CMS CTPFA
"""

import os
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
from datetime import datetime
from pathlib import Path

from .theme import RetroTheme
from .dialogs import RetroMessageBox
from .config import ConfigManager
from .articles import ArticleManager
from .html_generator import HTMLGenerator
from .uploader import FileUploader, SFTPUploader, build_web_url


class ToolTip:
    """Clase para mostrar tooltips en widgets"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.id = None
        self.x = self.y = 0
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(500, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        # Ajuste retro
        x += 5
        y += 5

        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        from .theme import RetroTheme
        
        label = tk.Label(tw, text=self.text, justify='left',
                       background=RetroTheme.BG_DARK, 
                       foreground=RetroTheme.NEON_YELLOW,
                       relief='solid', borderwidth=1,
                       font=("Courier New", 8))
        label.pack(ipadx=5, ipady=2)

    def hidetip(self):
        tw = self.tooltip_window
        self.tooltip_window = None
        if tw:
            tw.destroy()
class RetroCMSApp:
    """Aplicación principal del CMS"""
    
    CATEGORIES = [
        "TECNOLOGÍA", "VIDEOJUEGOS", "MÚSICA", "CINE", 
        "INTERNET", "HARDWARE", "SOFTWARE", "CULTURA", 
        "GESTIÓN DE INCIDENTES DE SEGURIDAD"
    ]
    

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("⚡ Cualquier Tiempo Pasado Fue Anterior ⚡")
        self.root.geometry("1000x700")
        self.root.configure(bg=RetroTheme.BG_DARK)

        # Inicializar componentes
        self.config = ConfigManager()
        self.articles = ArticleManager(self.config)
        self.generator = HTMLGenerator(self.articles, self.config)

        self.setup_styles()
        self.create_menu()
        self.refresh_article_list()

    def set_status(self, message):
        """Actualiza la barra de estado"""
        if hasattr(self, 'status_var'):
            self.status_var.set(f">> {message}")
        if hasattr(self, 'root'):
            self.root.update_idletasks()
    
    def create_menu(self):
        """Crea el menú superior de la aplicación"""
        menubar = tk.Menu(self.root, bg=RetroTheme.BG_PURPLE, fg=RetroTheme.NEON_CYAN,
                         activebackground=RetroTheme.NEON_PINK, activeforeground=RetroTheme.BG_DARK,
                         font=RetroTheme.FONT_MAIN)
        
        # Menú Archivo
        menu_archivo = tk.Menu(menubar, tearoff=0, bg=RetroTheme.BG_PURPLE, 
                               fg=RetroTheme.NEON_CYAN, activebackground=RetroTheme.NEON_PINK,
                               activeforeground=RetroTheme.BG_DARK, font=RetroTheme.FONT_MAIN)
        menu_archivo.add_command(label="Nuevo artículo", command=self.new_article)
        menu_archivo.add_command(label="Guardar artículo", command=self.save_article)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Importar del servidor", command=self.import_from_server)
        menu_archivo.add_command(label="Descargar como Markdown", command=self.download_as_markdown)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Configuración", command=self.show_config)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self.root.quit)
        menubar.add_cascade(label="Archivo", menu=menu_archivo)
        
        # Menú Ayuda
        menu_ayuda = tk.Menu(menubar, tearoff=0, bg=RetroTheme.BG_PURPLE,
                             fg=RetroTheme.NEON_CYAN, activebackground=RetroTheme.NEON_PINK,
                             activeforeground=RetroTheme.BG_DARK, font=RetroTheme.FONT_MAIN)
        menu_ayuda.add_command(label="Guía de Markdown", command=self.show_markdown_guide)
        menu_ayuda.add_separator()
        menu_ayuda.add_command(label="Acerca de", command=self.show_about)
        menubar.add_cascade(label="Ayuda", menu=menu_ayuda)
        
        self.root.config(menu=menubar)
    
    def show_markdown_guide(self):
          """Muestra la guía de Markdown desde un archivo externo"""
          guide_window = tk.Toplevel(self.root)
          guide_window.title("Guía de Markdown")
          guide_window.geometry("700x700")
          guide_window.configure(bg=RetroTheme.BG_DARK)
          guide_window.transient(self.root)

          frame = ttk.Frame(guide_window, style='Retro.TFrame')
          frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

          ttk.Label(frame, text="═══ GUÍA DE MARKDOWN ═══", 
                      style='Title.TLabel').pack(pady=(0, 15))

          # Leer el archivo de guía
          guide_path = Path(__file__).parent / "markdown_guide.txt"
          try:
                with open(guide_path, "r", encoding="utf-8") as f:
                     guide_text = f.read()
          except Exception as e:
                guide_text = f"No se pudo cargar la guía de Markdown.\n\n{e}"

          text_widget = tk.Text(
                frame, 
                width=80, 
                height=32,
                bg=RetroTheme.BG_PURPLE,
                fg=RetroTheme.NEON_GREEN,
                font=RetroTheme.FONT_MAIN,
                wrap=tk.WORD,
                padx=10,
                pady=10
          )
          text_widget.insert('1.0', guide_text)
          text_widget.config(state=tk.DISABLED)
          text_widget.pack(fill=tk.BOTH, expand=True)

          btn_close = ttk.Button(frame, text="[ CERRAR ]", style='Retro.TButton',
                        command=guide_window.destroy)
          btn_close.pack(pady=(15, 0))
          ToolTip(btn_close, "Cerrar ventana de ayuda")
    
    def show_about(self):
        """Muestra información sobre la aplicación"""
        import webbrowser
        
        about_window = tk.Toplevel(self.root)
        about_window.title("Acerca de")
        about_window.geometry("450x500")
        about_window.configure(bg=RetroTheme.BG_DARK)
        about_window.transient(self.root)
        about_window.resizable(False, False)
        
        frame = ttk.Frame(about_window, style='Retro.TFrame')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Cargar y mostrar logo
        logo_path = Path(__file__).parent.parent / "Img" / "logo.png"

        def download_as_markdown(self):
            """Descarga artículos del servidor como archivos Markdown"""
            server = self.config.get("server")
            if not server.get("host"):
                RetroMessageBox.showerror(self.root, "Error", "Configura el servidor primero")
                return

            dest_dir = filedialog.askdirectory(title="Seleccionar carpeta de destino")
            if not dest_dir:
                return

            def do_download():
                try:
                    import time
                    import os
                    protocol = server.get('protocol', 'ftp').upper()
                    self.anim_add_line(f"> Conectando a {server['host']}...")
                    self.anim_set_status(f"Conectando {protocol}...")
                    uploader = FileUploader(self.config)
                    uploader.connect()
                    self.anim_add_line("  ✓ Conexión establecida")
                    remote_path = server['remote_path']
                    files = uploader.list_files(remote_path)
                    article_files = [f for f in files if f.endswith('.html') and f not in ['index.html', 'articulo.html']]
                    if not article_files:
                        self.anim_add_line("  ! No hay artículos")
                        uploader.disconnect()
                        self.anim_finish(True, "Sin artículos")
                        return
                    total = len(article_files)
                    count = 0
                    self.anim_add_line(f"> Descargando {total} artículos...")
                    for i, filename in enumerate(article_files):
                        self.anim_add_line(f"  [{i+1}/{total}] {filename}")
                        self.anim_update_progress(i, total)
                        remote_file = f"{remote_path}/{filename}"
                        content = uploader.download_string(remote_file)
                        if content:
                            data = self.articles.extract_article_data(content, filename)
                            if data:
                                md_body = data.get('content', '').strip()
                                if not md_body:
                                    md_body = '*[El contenido del artículo está vacío o no se pudo extraer.]*'
                                md_content = f"""---\ntitle: {data.get('title','')}\ncategory: {data.get('category','')}\ntags: {', '.join(data.get('tags', []))}\ndate: {data.get('created', '')}\n---\n\n{md_body}\n"""
                                slug = data.get('id', filename.replace('.html', ''))
                                local_path = os.path.join(dest_dir, f"{slug}.md")
                                with open(local_path, 'w', encoding='utf-8') as f:
                                    f.write(md_content)
                                self.anim_add_line(f"        → Guardado: {slug}.md")
                                count += 1
                            else:
                                self.anim_add_line("        ✗ Error extrayendo datos")
                        else:
                            self.anim_add_line("        ✗ Fallo al descargar")
                        time.sleep(0.1)
                    self.anim_update_progress(total, total)
                    uploader.disconnect()
                    self.anim_finish(True, f"Descargados {count} archivos .md")
                    self.set_status(f"✓ Descarga completada en {dest_dir}")
                except Exception as e:
                    self.anim_finish(False, str(e))
                    self.set_status(f"Error: {str(e)}")


        
        # Frame para botones
        btn_frame = ttk.Frame(frame, style='Retro.TFrame')
        btn_frame.pack(pady=(15, 0))
        
        def open_github():
            """Abre GitHub en el navegador (con fix para Linux/Snap)"""
            # Fix para error de Firefox en Linux con Snap
            if 'GTK_PATH' in os.environ:
                del os.environ['GTK_PATH']
            webbrowser.open("https://github.com/sapoclay/ctpfa")
        
        # Botón GitHub
        btn_github = ttk.Button(btn_frame, text="[ GITHUB ]", style='Retro.TButton',
                  command=open_github)
        btn_github.pack(side=tk.LEFT, padx=5)
        ToolTip(btn_github, "Visitar repositorio del proyecto")
        
        # Botón cerrar
        btn_close = ttk.Button(btn_frame, text="[ CERRAR ]", style='Retro.TButton',
                  command=about_window.destroy)
        btn_close.pack(side=tk.LEFT, padx=5)
        ToolTip(btn_close, "Cerrar ventana")
    
    def setup_styles(self):
        pass
    
    def create_article_list(self, parent):
        """Crea el panel de lista de artículos"""
        list_frame = ttk.Frame(parent, style='Retro.TFrame')
        list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        ttk.Label(list_frame, text="═══ ARTÍCULOS ═══", 
                 style='Retro.TLabel').pack()
        
        # Lista
        self.article_listbox = tk.Listbox(
            list_frame,
            width=35,
            height=25,
            bg=RetroTheme.BG_PURPLE,
            fg=RetroTheme.NEON_CYAN,
            selectbackground=RetroTheme.NEON_PINK,
            selectforeground=RetroTheme.BG_DARK,
            font=RetroTheme.FONT_SMALL,
            borderwidth=2,
            relief=tk.GROOVE
        )
        self.article_listbox.pack(fill=tk.Y, expand=True, pady=5)
        self.article_listbox.bind('<<ListboxSelect>>', self.on_article_select)
        
        # Botones
        btn_frame = ttk.Frame(list_frame, style='Retro.TFrame')
        btn_frame.pack(fill=tk.X, pady=5)
        
        btn_new = ttk.Button(btn_frame, text="+ Nuevo", style='Retro.TButton',
                  command=self.new_article)
        btn_new.pack(side=tk.LEFT, padx=2)
        ToolTip(btn_new, "Crear nuevo borrador")

        btn_del = ttk.Button(btn_frame, text="✕ Eliminar", style='Retro.TButton',
                  command=self.delete_article)
        btn_del.pack(side=tk.LEFT, padx=2)
        ToolTip(btn_del, "Eliminar artículo seleccionado")
    
    def create_editor(self, parent):
        """Crea el panel del editor"""
        editor_frame = ttk.Frame(parent, style='Retro.TFrame')
        editor_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        ttk.Label(editor_frame, text="═══ EDITOR ═══", 
                 style='Retro.TLabel').pack()
        
        # Campos del formulario
        form_frame = ttk.Frame(editor_frame, style='Retro.TFrame')
        form_frame.pack(fill=tk.X, pady=5)
        
        # Título
        ttk.Label(form_frame, text="TÍTULO:", style='Retro.TLabel').grid(
            row=0, column=0, sticky=tk.W, pady=2)
        self.title_var = tk.StringVar()
        self.title_entry = tk.Entry(
            form_frame, textvariable=self.title_var,
            width=60, bg=RetroTheme.BG_PURPLE, fg=RetroTheme.TEXT_PRIMARY,
            insertbackground=RetroTheme.NEON_GREEN, font=RetroTheme.FONT_MAIN
        )
        self.title_entry.grid(row=0, column=1, pady=2, padx=5)
        
        # Subtítulo
        ttk.Label(form_frame, text="SUBTÍTULO:", style='Retro.TLabel').grid(
            row=1, column=0, sticky=tk.W, pady=2)
        self.subtitle_var = tk.StringVar()
        self.subtitle_entry = tk.Entry(
            form_frame, textvariable=self.subtitle_var,
            width=60, bg=RetroTheme.BG_PURPLE, fg=RetroTheme.TEXT_PRIMARY,
            insertbackground=RetroTheme.NEON_GREEN, font=RetroTheme.FONT_MAIN
        )
        self.subtitle_entry.grid(row=1, column=1, pady=2, padx=5)
        
        # Categoría
        ttk.Label(form_frame, text="CATEGORÍA:", style='Retro.TLabel').grid(
            row=2, column=0, sticky=tk.W, pady=2)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(
            form_frame, textvariable=self.category_var,
            values=self.CATEGORIES, state='readonly', width=20
        )
        self.category_combo.grid(row=2, column=1, pady=2, padx=5, sticky=tk.W)
        
        # Tags
        ttk.Label(form_frame, text="TAGS:", style='Retro.TLabel').grid(
            row=3, column=0, sticky=tk.W, pady=2)
        self.tags_var = tk.StringVar()
        self.tags_entry = tk.Entry(
            form_frame, textvariable=self.tags_var,
            width=60, bg=RetroTheme.BG_PURPLE, fg=RetroTheme.TEXT_PRIMARY,
            insertbackground=RetroTheme.NEON_GREEN, font=RetroTheme.FONT_MAIN
        )
        self.tags_entry.grid(row=3, column=1, pady=2, padx=5)
        ttk.Label(form_frame, text="(separados por comas)", 
                 style='Retro.TLabel').grid(row=3, column=2, sticky=tk.W)
        
        # Editor de contenido
        ttk.Label(editor_frame, text="CONTENIDO (usa Markdown):", 
                 style='Retro.TLabel').pack(anchor=tk.W, pady=(10, 2))
        
        self.content_text = scrolledtext.ScrolledText(
            editor_frame,
            width=80,
            height=20,
            bg=RetroTheme.BG_PURPLE,
            fg=RetroTheme.TEXT_PRIMARY,
            insertbackground=RetroTheme.NEON_GREEN,
            font=RetroTheme.FONT_MAIN,
            wrap=tk.WORD
        )
        self.content_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Botones del editor
        edit_btn_frame = ttk.Frame(editor_frame, style='Retro.TFrame')
        edit_btn_frame.pack(fill=tk.X, pady=5)
        
        btn_save = ttk.Button(edit_btn_frame, text="Guardar", style='Retro.TButton',
                  command=self.save_article)
        btn_save.pack(side=tk.LEFT, padx=2)
        ToolTip(btn_save, "Guardar cambios localmente (Ctrl+S)")

        btn_pub = ttk.Button(edit_btn_frame, text="Publicar", style='Retro.TButton',
                  command=self.publish_current_article)
        btn_pub.pack(side=tk.LEFT, padx=2)
        ToolTip(btn_pub, "Subir este artículo al servidor")

        btn_prev = ttk.Button(edit_btn_frame, text="Vista previa", style='Retro.TButton',
                  command=self.preview_article)
        btn_prev.pack(side=tk.LEFT, padx=2)
        ToolTip(btn_prev, "Ver cómo quedará el artículo")

        btn_clear = ttk.Button(edit_btn_frame, text="Limpiar", style='Retro.TButton',
                  command=self.clear_editor)
        btn_clear.pack(side=tk.LEFT, padx=2)
        ToolTip(btn_clear, "Borrar campos del editor")
        
        self.current_article_id = None
    
    def create_status_bar(self, parent):
        """Crea la barra de estado"""
        self.status_var = tk.StringVar(value="Sistema listo...")
        status_bar = ttk.Label(
            parent, textvariable=self.status_var,
            style='Retro.TLabel'
        )
        status_bar.pack(fill=tk.X, pady=(10, 0))
    
    def refresh_article_list(self):
        """Actualiza la lista de artículos"""
        self.article_listbox.delete(0, tk.END)
        for article in self.articles.list_articles():
            status = "✓" if article.get('published') else "○"
            self.article_listbox.insert(
                tk.END, 
                f"{status} [{article['category'][:4]}] {article['title'][:30]}"
            )
    
    def on_article_select(self, event):
        """Maneja la selección de un artículo"""
        selection = self.article_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        articles = self.articles.list_articles()
        if index < len(articles):
            article_id = articles[index]['id']
            self.load_article(article_id)
    
    def load_article(self, article_id):
        """Carga un artículo en el editor"""
        article = self.articles.get_article(article_id)
        if not article:
            return
        
        self.current_article_id = article_id
        self.title_var.set(article['title'])
        self.subtitle_var.set(article.get('subtitle', ''))
        self.category_var.set(article['category'])
        self.tags_var.set(', '.join(article.get('tags', [])))
        
        self.content_text.delete('1.0', tk.END)
        self.content_text.insert('1.0', article['content'])
        
        # Mostrar si está publicado en el servidor
        status = "publicado" if article.get('published', False) else "borrador"
        self.set_status(f"Artículo cargado: {article['title']} [{status}]")
    
    def new_article(self):
        """Prepara el editor para un nuevo artículo"""
        self.clear_editor()
        self.current_article_id = None
        self.set_status("Nuevo artículo - Completa los campos")
    
    def save_article(self):
        """Guarda el artículo actual"""
        title = self.title_var.get().strip()
        if not title:
            RetroMessageBox.showerror(self.root, "Error", "El título es obligatorio")
            return
        
        category = self.category_var.get()
        if not category:
            RetroMessageBox.showerror(self.root, "Error", "Selecciona una categoría")
            return
        
        # Mantener el estado de publicación previo si existe
        existing_article = self.articles.get_article(self.current_article_id) if self.current_article_id else None
        was_published = existing_article.get('published', False) if existing_article else False
        
        data = {
            'title': title,
            'subtitle': self.subtitle_var.get().strip(),
            'category': category,
            'content': self.content_text.get('1.0', tk.END).strip(),
            'tags': [t.strip() for t in self.tags_var.get().split(',') if t.strip()],
            'published': was_published  # Mantener estado de publicación
        }
        
        try:
            if self.current_article_id:
                self.articles.update_article(self.current_article_id, data)
                self.set_status(f"Artículo guardado localmente: {title}")
            else:
                article = self.articles.create_article(data)
                self.current_article_id = article['id']
                self.set_status(f"Artículo creado: {title}")
            
            self.refresh_article_list()
            RetroMessageBox.showsuccess(self.root, "Éxito", "Artículo guardado localmente")
        except Exception as e:
            RetroMessageBox.showerror(self.root, "Error", f"Error al guardar: {str(e)}")
    
    def delete_article(self):
        """Elimina el artículo seleccionado"""
        if not self.current_article_id:
            RetroMessageBox.showwarning(self.root, "Aviso", "Selecciona un artículo para eliminar")
            return
        
        # Verificar si el artículo estaba publicado
        article = self.articles.get_article(self.current_article_id)
        was_published = article and article.get('published', False)
        
        # Preguntar si también eliminar del servidor
        delete_from_server = False
        if was_published:
            delete_from_server = RetroMessageBox.askyesno(
                self.root,
                "Eliminar del servidor",
                "Este artículo está publicado en el servidor.\n"
                "¿Deseas eliminarlo también del servidor web?"
            )
        else:
            if not RetroMessageBox.askyesno(self.root, "Confirmar", "¿Eliminar este artículo?"):
                return
        
        # Eliminar del servidor si se confirmó
        if delete_from_server:
            try:
                self.set_status("Eliminando del servidor...")
                server = self.config.get("server")
                if server.get("host"):
                    uploader = SFTPUploader(self.config)
                    uploader.connect()
                    remote_file = f"{server['remote_path']}/{self.current_article_id}.html"
                    try:
                        if uploader.sftp is not None:
                            uploader.sftp.remove(remote_file)
                        self.set_status("Artículo eliminado del servidor")
                    except IOError:
                        # El archivo no existía en el servidor
                        pass
                    uploader.disconnect()
            except Exception as e:
                RetroMessageBox.showwarning(
                    self.root,
                    "Aviso", 
                    f"No se pudo eliminar del servidor:\n{str(e)}\n\n"
                    "El artículo se eliminará solo localmente."
                )
        
        # Eliminar localmente
        self.articles.delete_article(self.current_article_id)
        self.clear_editor()
        self.refresh_article_list()
        self.set_status("Artículo eliminado")
    
    def clear_editor(self):
        """Limpia el editor"""
        self.current_article_id = None
        self.title_var.set("")
        self.subtitle_var.set("")
        self.category_var.set("")
        self.tags_var.set("")
        self.content_text.delete('1.0', tk.END)
        self.set_status("Editor limpio - Nuevo artículo")
    
    def preview_article(self):
        """Muestra vista previa del artículo"""
        if not self.title_var.get():
            RetroMessageBox.showwarning(self.root, "Aviso", "Escribe algo primero")
            return
        
        # Crear artículo temporal
        temp_article = {
            'title': self.title_var.get(),
            'subtitle': self.subtitle_var.get(),
            'category': self.category_var.get() or 'GENERAL',
            'content': self.content_text.get('1.0', tk.END),
            'tags': [t.strip() for t in self.tags_var.get().split(',') if t.strip()],
            'created': datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        html = self.generator.generate_article_html(temp_article)
        
        # Ajustar rutas CSS para que apunten al directorio padre
        parent_dir = Path(__file__).parent.parent.parent.absolute()
        html = html.replace('href="css/', f'href="file://{parent_dir}/css/')
        html = html.replace("href='css/", f"href='file://{parent_dir}/css/")
        
        # Guardar preview temporal
        preview_path = Path("preview.html")
        with open(preview_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        # Abrir en navegador (fix para Firefox/Snap)
        import webbrowser
        gtk_path = os.environ.pop('GTK_PATH', None)
        try:
            webbrowser.open(f'file://{preview_path.absolute()}')
        finally:
            if gtk_path:
                os.environ['GTK_PATH'] = gtk_path
        self.set_status("Vista previa abierta en navegador")
    
    def show_config(self):
        """Muestra el diálogo de configuración"""
        config_window = tk.Toplevel(self.root)
        config_window.title("Configuración")
        config_window.geometry("450x680")
        config_window.configure(bg=RetroTheme.BG_DARK)
        config_window.transient(self.root)
        config_window.grab_set()
        
        frame = ttk.Frame(config_window, style='Retro.TFrame')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(frame, text="═══ CONFIGURACIÓN DEL SERVIDOR ═══", 
                 style='Title.TLabel').pack(pady=(0, 20))
        
        # Selector de protocolo
        proto_frame = ttk.Frame(frame, style='Retro.TFrame')
        proto_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(proto_frame, text="Protocolo:", style='Retro.TLabel').pack(side=tk.LEFT)
        
        # Obtener protocolo actual de la configuración
        current_protocol = self.config.get("server", "protocol")
        if not isinstance(current_protocol, str) or not current_protocol:
            current_protocol = "ftp"
        protocol_var = tk.StringVar(value=current_protocol)
        
        # Variable para el label de hint (se define después)
        key_hint_label: tk.Label | None = None
        
        def on_protocol_change(*args):
            proto = protocol_var.get()
            if proto == "ftp":
                entries['port'].delete(0, tk.END)
                entries['port'].insert(0, "21")
                if key_hint_label is not None:
                    key_hint_label.config(text="(No aplica para FTP)")
            else:
                entries['port'].delete(0, tk.END)
                entries['port'].insert(0, "22")
                if key_hint_label is not None:
                    key_hint_label.config(text="(Opcional, ruta a clave SSH privada)")
        
        ftp_radio = tk.Radiobutton(proto_frame, text="FTP", variable=protocol_var, value="ftp",
                                   bg=RetroTheme.BG_DARK, fg=RetroTheme.NEON_GREEN,
                                   selectcolor=RetroTheme.BG_PURPLE, activebackground=RetroTheme.BG_DARK,
                                   font=RetroTheme.FONT_MAIN, command=on_protocol_change)
        ftp_radio.pack(side=tk.LEFT, padx=10)
        
        sftp_radio = tk.Radiobutton(proto_frame, text="SFTP (SSH)", variable=protocol_var, value="sftp",
                                    bg=RetroTheme.BG_DARK, fg=RetroTheme.NEON_CYAN,
                                    selectcolor=RetroTheme.BG_PURPLE, activebackground=RetroTheme.BG_DARK,
                                    font=RetroTheme.FONT_MAIN, command=on_protocol_change)
        sftp_radio.pack(side=tk.LEFT, padx=10)
        
        # Campos de configuración
        fields = [
            ("Host:", "host", self.config.get("server", "host"), None),
            ("Puerto:", "port", str(self.config.get("server", "port") or 21), None),
            ("Usuario:", "username", self.config.get("server", "username"), None),
            ("Contraseña:", "password", self.config.get("server", "password"), None),
            ("Clave SSH:", "key_file", self.config.get("server", "key_file"), "key_hint"),
            ("Ruta remota:", "remote_path", self.config.get("server", "remote_path"), None),
        ]
        
        entries: dict[str, tk.Entry] = {}
        for i, (label, key, value, hint) in enumerate(fields):
            ttk.Label(frame, text=label, style='Retro.TLabel').pack(anchor=tk.W)
            entry = tk.Entry(
                frame, width=50,
                bg=RetroTheme.BG_PURPLE, fg=RetroTheme.TEXT_PRIMARY,
                insertbackground=RetroTheme.NEON_GREEN, font=RetroTheme.FONT_MAIN,
                show='*' if key == 'password' else ''
            )
            entry.insert(0, value or '')
            entry.pack(fill=tk.X, pady=(0, 2))
            entries[key] = entry
            if hint == "key_hint":
                hint_text = "(No aplica para FTP)" if protocol_var.get() == "ftp" else "(Opcional, ruta a clave SSH privada)"
                key_hint_label = tk.Label(frame, text=hint_text, 
                                     bg=RetroTheme.BG_DARK, fg=RetroTheme.TEXT_SECONDARY,
                                     font=RetroTheme.FONT_SMALL)
                key_hint_label.pack(anchor=tk.W, pady=(0, 8))
        
        # Separador
        ttk.Separator(frame, orient='horizontal').pack(fill=tk.X, pady=10)
        ttk.Label(frame, text="═══ CONFIGURACIÓN DEL SITIO ═══", 
                 style='Title.TLabel').pack(pady=(0, 10))
        
        # Campo de autor
        ttk.Label(frame, text="Nombre del autor:", style='Retro.TLabel').pack(anchor=tk.W)
        author_entry = tk.Entry(
            frame, width=50,
            bg=RetroTheme.BG_PURPLE, fg=RetroTheme.TEXT_PRIMARY,
            insertbackground=RetroTheme.NEON_GREEN, font=RetroTheme.FONT_MAIN
        )
        current_author = self.config.get("site", "author")
        author_entry.insert(0, current_author if isinstance(current_author, str) else "Admin")
        author_entry.pack(fill=tk.X, pady=(0, 2))
        tk.Label(frame, text="(Se mostrará como autor en los artículos publicados)", 
                bg=RetroTheme.BG_DARK, fg=RetroTheme.TEXT_SECONDARY,
                font=RetroTheme.FONT_SMALL).pack(anchor=tk.W, pady=(0, 8))
        
        def save_config():
            self.config.set(protocol_var.get(), "server", "protocol")
            self.config.set(entries['host'].get(), "server", "host")
            self.config.set(int(entries['port'].get() or 21), "server", "port")
            self.config.set(entries['username'].get(), "server", "username")
            self.config.set(entries['password'].get(), "server", "password")
            self.config.set(entries['key_file'].get(), "server", "key_file")
            self.config.set(entries['remote_path'].get(), "server", "remote_path")
            self.config.set(author_entry.get() or "Admin", "site", "author")
            self.config.save()
            RetroMessageBox.showsuccess(self.root, "Éxito", "Configuración guardada")
            config_window.destroy()
        
        btn_save = ttk.Button(frame, text="Guardar", style='Retro.TButton',
                  command=save_config)
        btn_save.pack(pady=20)
        ToolTip(btn_save, "Guardar cambios y cerrar")
    
    def show_upload_animation(self, on_complete_callback):
        """Muestra una ventana con animación retro de subida"""
        self.anim_window = tk.Toplevel(self.root)
        self.anim_window.title("Transmitiendo...")
        self.anim_window.geometry("520x480")
        self.anim_window.configure(bg=RetroTheme.BG_DARK)
        self.anim_window.transient(self.root)
        self.anim_window.grab_set()
        self.anim_window.resizable(False, False)
        
        # Marco principal con borde neón
        self.anim_main_frame = tk.Frame(
            self.anim_window, bg=RetroTheme.BG_DARK,
            highlightbackground=RetroTheme.NEON_CYAN,
            highlightthickness=2
        )
        self.anim_main_frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        # Barra de título personalizada
        title_bar = tk.Frame(self.anim_main_frame, bg=RetroTheme.BG_PURPLE, height=35)
        title_bar.pack(fill=tk.X)
        title_bar.pack_propagate(False)
        
        tk.Label(
            title_bar, text="═══ TRANSMISIÓN EN CURSO ═══",
            bg=RetroTheme.BG_PURPLE, fg=RetroTheme.NEON_CYAN,
            font=("Courier New", 12, "bold")
        ).pack(expand=True)
        
        # Frame de contenido
        frame = tk.Frame(self.anim_main_frame, bg=RetroTheme.BG_DARK)
        frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Terminal de salida con borde
        terminal_frame = tk.Frame(
            frame, bg=RetroTheme.NEON_GREEN,
            highlightbackground=RetroTheme.NEON_GREEN,
            highlightthickness=1
        )
        terminal_frame.pack(pady=10, fill=tk.X)
        
        self.anim_terminal = tk.Text(
            terminal_frame, width=55, height=12,
            bg=RetroTheme.BG_DARK, fg=RetroTheme.NEON_GREEN,
            font=("Courier New", 10),
            insertbackground=RetroTheme.NEON_GREEN,
            relief=tk.FLAT, borderwidth=5
        )
        self.anim_terminal.pack()
        self.anim_terminal.config(state=tk.DISABLED)
        
        # Barra de progreso ASCII
        self.progress_label = tk.Label(
            frame, text="[░░░░░░░░░░░░░░░░░░░░] 0%",
            bg=RetroTheme.BG_DARK, fg=RetroTheme.NEON_YELLOW,
            font=("Courier New", 12)
        )
        self.progress_label.pack(pady=10)
        
        # Estado
        self.anim_status = tk.Label(
            frame, text="Iniciando conexión...",
            bg=RetroTheme.BG_DARK, fg=RetroTheme.NEON_PINK,
            font=("Courier New", 10)
        )
        self.anim_status.pack(pady=5)
        
        # Frame para botones (inicialmente vacío)
        self.anim_btn_frame = tk.Frame(frame, bg=RetroTheme.BG_DARK)
        self.anim_btn_frame.pack(pady=10)
        
        # Efecto de parpadeo del borde
        self.anim_blink_active = True
        def blink_border():
            if self.anim_blink_active and hasattr(self, 'anim_main_frame') and self.anim_main_frame.winfo_exists():
                current = self.anim_main_frame.cget("highlightbackground")
                new_color = RetroTheme.BG_DARK if current == RetroTheme.NEON_CYAN else RetroTheme.NEON_CYAN
                self.anim_main_frame.configure(highlightbackground=new_color)
                self.anim_window.after(500, blink_border)
        blink_border()
        
        # Centrar ventana
        self.anim_window.update_idletasks()
        width = self.anim_window.winfo_width()
        height = self.anim_window.winfo_height()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (width // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (height // 2)
        self.anim_window.geometry(f"+{x}+{y}")
        
        # Iniciar callback
        self.anim_lines = []
        self.root.after(100, on_complete_callback)
    
    def anim_add_line(self, text, color=None):
        """Añade una línea al terminal de animación"""
        if hasattr(self, 'anim_terminal'):
            self.anim_terminal.config(state=tk.NORMAL)
            self.anim_terminal.insert(tk.END, f"{text}\n")
            self.anim_terminal.see(tk.END)
            self.anim_terminal.config(state=tk.DISABLED)
            self.root.update_idletasks()
    
    def anim_update_progress(self, current, total):
        """Actualiza la barra de progreso ASCII"""
        if hasattr(self, 'progress_label'):
            percent = int((current / total) * 100) if total > 0 else 0
            filled = int(percent / 5)
            bar = "█" * filled + "░" * (20 - filled)
            self.progress_label.config(text=f"[{bar}] {percent}%")
            self.root.update_idletasks()
    
    def anim_set_status(self, text):
        """Actualiza el estado en la animación"""
        if hasattr(self, 'anim_status'):
            self.anim_status.config(text=text)
            self.root.update_idletasks()
    
    def anim_finish(self, success=True, message="", url=None):
        """Finaliza la animación"""
        if hasattr(self, 'anim_window') and self.anim_window.winfo_exists():
            # Detener el parpadeo del borde
            self.anim_blink_active = False
            
            # Cambiar color del borde según resultado
            result_color = RetroTheme.NEON_GREEN if success else RetroTheme.NEON_RED
            self.anim_main_frame.configure(highlightbackground=result_color)
            
            if success:
                self.anim_add_line("")
                self.anim_add_line("════════════════════════════════════════")
                self.anim_add_line("  ✓ TRANSMISIÓN COMPLETADA CON ÉXITO")
                self.anim_add_line("════════════════════════════════════════")
                self.anim_set_status(message)
                self.progress_label.config(text="[████████████████████] 100%", fg=RetroTheme.NEON_GREEN)
            else:
                self.anim_add_line("")
                self.anim_add_line("════════════════════════════════════════")
                self.anim_add_line("  ✗ ERROR EN LA TRANSMISIÓN")
                self.anim_add_line("════════════════════════════════════════")
                self.anim_set_status(message)
                self.progress_label.config(fg=RetroTheme.NEON_RED)
            
            # Limpiar frame de botones existente
            for widget in self.anim_btn_frame.winfo_children():
                widget.destroy()
            
            # Función para crear botones con estilo retro
            def create_retro_button(parent, text, color, command):
                btn = tk.Button(
                    parent, text=f"[ {text} ]",
                    font=("Courier New", 10),
                    fg=color, bg=RetroTheme.BG_DARK,
                    activeforeground=RetroTheme.BG_DARK,
                    activebackground=color,
                    bd=0, highlightthickness=1,
                    highlightbackground=color,
                    cursor="hand2",
                    command=command
                )
                btn.pack(side=tk.LEFT, padx=8)
                # Efecto hover
                btn.bind("<Enter>", lambda e: btn.configure(fg=RetroTheme.BG_DARK, bg=color))
                btn.bind("<Leave>", lambda e: btn.configure(fg=color, bg=RetroTheme.BG_DARK))
                return btn
            
            # Botón para abrir en navegador (solo si hay URL y fue exitoso)
            if success and url:
                def open_in_browser():
                    import webbrowser
                    gtk_path = os.environ.pop('GTK_PATH', None)
                    try:
                        webbrowser.open(url)
                    finally:
                        if gtk_path:
                            os.environ['GTK_PATH'] = gtk_path
                
                create_retro_button(
                    self.anim_btn_frame, "ABRIR EN NAVEGADOR",
                    RetroTheme.NEON_CYAN, open_in_browser
                )
            
            # Botón para cerrar
            close_color = RetroTheme.NEON_GREEN if success else RetroTheme.NEON_YELLOW
            create_retro_button(
                self.anim_btn_frame, "CERRAR",
                close_color, self.anim_window.destroy
            )
    
    def show_retro_validation_error(self, missing_fields):
        """Muestra un mensaje de error retro cuando faltan campos"""
        error_window = tk.Toplevel(self.root)
        error_window.title("ERROR DE VALIDACIÓN")
        error_window.geometry("400x280")
        error_window.configure(bg='#000000')
        error_window.transient(self.root)
        error_window.grab_set()
        error_window.resizable(False, False)
        
        frame = tk.Frame(error_window, bg='#000000')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título con efecto retro
        tk.Label(frame, text="╔════════════════════════════════╗",
                bg='#000000', fg=RetroTheme.NEON_PINK,
                font=("Courier New", 10)).pack()
        tk.Label(frame, text="║    ⚠ ERROR DE TRANSMISIÓN ⚠   ║",
                bg='#000000', fg=RetroTheme.NEON_PINK,
                font=("Courier New", 10, "bold")).pack()
        tk.Label(frame, text="╚════════════════════════════════╝",
                bg='#000000', fg=RetroTheme.NEON_PINK,
                font=("Courier New", 10)).pack()
        
        tk.Label(frame, text="",bg='#000000').pack(pady=5)
        
        tk.Label(frame, text="Datos incompletos detectados.",
                bg='#000000', fg=RetroTheme.NEON_YELLOW,
                font=("Courier New", 10)).pack()
        tk.Label(frame, text="Complete los siguientes campos:",
                bg='#000000', fg=RetroTheme.TEXT_SECONDARY,
                font=("Courier New", 9)).pack(pady=(5,10))
        
        # Lista de campos faltantes
        for field in missing_fields:
            tk.Label(frame, text=f"  ► {field}",
                    bg='#000000', fg=RetroTheme.NEON_CYAN,
                    font=("Courier New", 10)).pack(anchor=tk.W)
        
        tk.Label(frame, text="",bg='#000000').pack(pady=5)
        
        
        btn_ok = ttk.Button(frame, text="[ ENTENDIDO ]", style='Retro.TButton',
                  command=error_window.destroy)
        btn_ok.pack(pady=10)
        ToolTip(btn_ok, "Cerrar alerta y corregir campos")
    
    def publish_current_article(self):
        """Publica el artículo actual al servidor"""
        # Validar todos los campos
        missing_fields = []
        
        title = self.title_var.get().strip()
        if not title:
            missing_fields.append("TÍTULO")
        
        subtitle = self.subtitle_var.get().strip()
        if not subtitle:
            missing_fields.append("SUBTÍTULO")
        
        category = self.category_var.get()
        if not category:
            missing_fields.append("CATEGORÍA")
        
        content = self.content_text.get('1.0', tk.END).strip()
        if not content:
            missing_fields.append("CONTENIDO")
        
        tags = self.tags_var.get().strip()
        if not tags:
            missing_fields.append("TAGS")
        
        # Si faltan campos, mostrar error retro
        if missing_fields:
            self.show_retro_validation_error(missing_fields)
            return
        
        # Verificar configuración del servidor
        server = self.config.get("server")
        if not server.get("host"):
            RetroMessageBox.showerror(self.root, "Error", "Configura el servidor primero (Archivo → Configuración)")
            return
        
        data = {
            'title': title,
            'subtitle': subtitle,
            'category': category,
            'content': content,
            'tags': [t.strip() for t in tags.split(',') if t.strip()],
            'published': True  # Marcar como publicado
        }
        
        try:
            if self.current_article_id:
                self.articles.update_article(self.current_article_id, data)
            else:
                article = self.articles.create_article(data)
                self.current_article_id = article['id']
        except Exception as e:
            RetroMessageBox.showerror(self.root, "Error", f"Error al guardar: {str(e)}")
            return
        
        # Confirmar publicación
        if not RetroMessageBox.askyesno(self.root, "Publicar", 
                                   f"¿Publicar '{title}' al servidor?"):
            return
        
        article_id = self.current_article_id
        full_article = self.articles.get_article(article_id)
        
        def do_upload():
            try:
                import time
                
                protocol = server.get('protocol', 'ftp').upper()
                
                self.anim_add_line("CTPFA UPLOAD SYSTEM v1.0")
                self.anim_add_line("─" * 40)
                time.sleep(0.3)
                
                self.anim_add_line(f"> Conectando a {server['host']} ({protocol})...")
                self.anim_set_status(f"Estableciendo conexión {protocol}...")
                
                uploader = FileUploader(self.config)
                uploader.connect()
                
                self.anim_add_line("  ✓ Conexión establecida")
                time.sleep(0.2)
                
                remote_path = server['remote_path']
                filename = f"{article_id}.html"
                
                self.anim_add_line("")
                self.anim_add_line("> Generando HTML...")
                
                # Generar HTML del artículo
                html = self.generator.generate_article_html(full_article)
                self.anim_add_line(f"  ✓ HTML generado ({len(html)} bytes)")
                time.sleep(0.2)
                
                self.anim_add_line("")
                self.anim_add_line(f"> Subiendo: {filename}")
                self.anim_set_status(f"Subiendo: {title[:40]}...")
                self.anim_update_progress(0, 1)
                
                # Subir artículo
                remote_file = f"{remote_path}/{filename}"
                uploader.upload_string(html, remote_file)
                
                self.anim_add_line(f"  ✓ Artículo subido")
                time.sleep(0.15)
                
                # Actualizar index.html
                self.anim_add_line("")
                self.anim_add_line("> Actualizando índice del sitio...")
                self.anim_set_status("Regenerando index.html...")
                
                # Generar y subir index.html
                index_html = self.generator.generate_index_html(self.articles.list_articles())
                uploader.upload_string(index_html, f"{remote_path}/index.html")
                self.anim_add_line("  ✓ index.html actualizado")

                
                
                self.anim_update_progress(1, 1)
                self.anim_add_line("")
                self.anim_add_line("> Cerrando conexión...")
                uploader.disconnect()
                
                # Construir URL del artículo publicado
                article_url = build_web_url(server, filename)
                
                self.anim_finish(True, f"'{title}' publicado correctamente", url=article_url)
                self.set_status(f"✓ Publicado: {title}")
                self.refresh_article_list()
                
            except Exception as e:
                self.anim_finish(False, str(e))
                self.set_status(f"Error: {str(e)}")
        
        # Mostrar ventana de animación y ejecutar
        self.show_upload_animation(lambda: threading.Thread(target=do_upload).start())

    def publish_all(self):
        """Sincroniza todos los artículos marcados al servidor"""
        server = self.config.get("server")
        if not server.get("host"):
            RetroMessageBox.showerror(self.root, "Error", "Configura el servidor primero")
            return
        
        # Contar artículos a publicar (solo los que tienen published=True)
        articles_to_publish = []
        for art in self.articles.list_articles():
            article = self.articles.get_article(art['id'])
            if article and article.get('published', False):
                articles_to_publish.append(article)  # Guardar el artículo completo
        
        if not articles_to_publish:
            RetroMessageBox.showwarning(self.root, "Aviso", 
                "No hay artículos para sincronizar.\n\n"
                "Para publicar un artículo, usa el botón 'Publicar'\n"
                "en el editor del artículo.")
            return
        
        # Mostrar lista de artículos que se van a sincronizar
        article_names = "\n".join([f"  • {article['title']}" for article in articles_to_publish[:5]])
        if len(articles_to_publish) > 5:
            article_names += f"\n  ... y {len(articles_to_publish) - 5} más"
        
        # Confirmar
        if not RetroMessageBox.askyesno(self.root, "Sincronizar TODO", 
                f"Se sincronizarán {len(articles_to_publish)} artículo(s) al servidor:\n\n"
                f"{article_names}\n\n"
                f"¿Continuar?"):
            return
        
        def do_upload():
            try:
                import time
                
                protocol = server.get('protocol', 'ftp').upper()
                
                self.anim_add_line("CTPFA UPLOAD SYSTEM v1.0")
                self.anim_add_line("─" * 40)
                time.sleep(0.3)
                
                self.anim_add_line(f"> Conectando a {server['host']} ({protocol})...")
                self.anim_set_status(f"Estableciendo conexión {protocol}...")
                
                uploader = FileUploader(self.config)
                uploader.connect()
                
                self.anim_add_line("  ✓ Conexión establecida")
                time.sleep(0.2)
                
                remote_path = server['remote_path']
                total = len(articles_to_publish)
                published_count = 0
                
                self.anim_add_line("")
                self.anim_add_line("> Iniciando transferencia de archivos...")
                self.anim_add_line("")
                
                for i, full_article in enumerate(articles_to_publish):
                    filename = f"{full_article['id']}.html"
                    self.anim_add_line(f"  [{i+1}/{total}] {filename[:35]}")
                    self.anim_set_status(f"Subiendo: {full_article['title'][:40]}...")
                    self.anim_update_progress(i, total)
                    
                    # Generar HTML
                    html = self.generator.generate_article_html(full_article)
                    
                    # Subir
                    remote_file = f"{remote_path}/{filename}"
                    uploader.upload_string(html, remote_file)
                    
                    self.anim_add_line(f"        → Transferido ({len(html)} bytes)")
                    published_count += 1
                    time.sleep(0.15)
                
                self.anim_update_progress(total, total)
                self.anim_add_line("")
                
                # Actualizar index.html
                self.anim_add_line("> Actualizando índice del sitio...")
                self.anim_set_status("Regenerando index.html...")
                index_html = self.generator.generate_index_html(self.articles.list_articles())
                uploader.upload_string(index_html, f"{remote_path}/index.html")
                self.anim_add_line("  ✓ index.html actualizado")
                
                
                self.anim_add_line("")
                self.anim_add_line("> Cerrando conexión...")
                uploader.disconnect()
                
                # URL del sitio
                site_url = build_web_url(server)
                
                self.anim_finish(True, f"Se publicaron {published_count} artículo(s)", url=site_url)
                self.set_status(f"✓ Publicados {published_count} artículos")
                
            except Exception as e:
                self.anim_finish(False, str(e))
                self.set_status(f"Error: {str(e)}")
        
        # Mostrar ventana de animación y ejecutar
        self.show_upload_animation(lambda: threading.Thread(target=do_upload).start())


    def import_from_server(self):
        """Importa artículos desde el servidor"""
        server = self.config.get("server")
        if not server.get("host"):
            RetroMessageBox.showerror(self.root, "Error", "Configura el servidor primero")
            return
            
        if not RetroMessageBox.askyesno(self.root, "Importar del servidor", 
                "Se buscarán artículos en el servidor y se importarán a local.\n"
                "Los artículos existentes se actualizarán.\n\n"
                "¿Continuar?"):
            return

        def do_import():
            try:
                import time
                
                protocol = server.get('protocol', 'ftp').upper()
                
                self.anim_add_line("CTPFA IMPORT SYSTEM v1.0")
                self.anim_add_line("─" * 40)
                time.sleep(0.3)
                
                self.anim_add_line(f"> Conectando a {server['host']} ({protocol})...")
                self.anim_set_status(f"Estableciendo conexión {protocol}...")
                
                uploader = FileUploader(self.config)
                uploader.connect()
                
                self.anim_add_line("  ✓ Conexión establecida")
                time.sleep(0.2)
                
                self.anim_add_line("")
                self.anim_add_line("> Listando archivos remotos...")
                remote_path = server['remote_path']
                
                # Listar archivos
                files = uploader.list_files(remote_path)
                
                # Filtrar solo .html ignorando index.html y articulo.html (plantilla)
                article_files = [
                    f for f in files 
                    if f.endswith('.html') and f not in ['index.html', 'articulo.html']
                ]
                
                self.anim_add_line(f"  ✓ Encontrados {len(article_files)} artículos")
                
                if not article_files:
                    self.anim_add_line("  ! No hay artículos para importar")
                    time.sleep(1)
                    uploader.disconnect()
                    self.anim_finish(True, "No se encontraron artículos nuevos")
                    return

                total = len(article_files)
                imported_count = 0
                
                self.anim_add_line("")
                self.anim_add_line("> Iniciando descarga e importación...")
                self.anim_add_line("")
                
                for i, filename in enumerate(article_files):
                    self.anim_add_line(f"  [{i+1}/{total}] {filename}")
                    self.anim_set_status(f"Importando: {filename}...")
                    self.anim_update_progress(i, total)
                    
                    # Descargar contenido
                    remote_file = f"{remote_path}/{filename}"
                    content = uploader.download_string(remote_file)
                    
                    if content:
                        # Importar (overwrite=False para respetar locales)
                        article = self.articles.import_article_from_html(content, filename, overwrite=False)
                        if article:
                            self.anim_add_line(f"        → Importado: {article['title'][:30]}")
                            imported_count += 1
                        else:
                            # Puede devolver None si falló O si ya existía (y overwrite=False)
                            # Verificamos si existe para dar mensaje adecuado
                            article_id = filename.replace('.html', '')
                            if self.articles.get_article(article_id):
                                self.anim_add_line(f"        → Omitido (Ya existe localmente)")
                            else:
                                self.anim_add_line("        ✗ Fallo al importar")
                    else:
                        self.anim_add_line("        ✗ Fallo al descargar")
                        
                    time.sleep(0.1)
                
                self.anim_update_progress(total, total)
                self.anim_add_line("")
                self.anim_add_line("> Cerrando conexión...")
                uploader.disconnect()
                
                self.anim_finish(True, f"Se importaron {imported_count} artículo(s)")
                self.set_status(f"✓ Importados {imported_count} artículos")
                
                # Actualizar lista en el hilo principal
                self.root.after(0, self.refresh_article_list)
                
            except Exception as e:
                self.anim_finish(False, str(e))
                self.set_status(f"Error: {str(e)}")

        # Mostrar ventana de animación y ejecutar
        self.show_upload_animation(lambda: threading.Thread(target=do_import).start())

    def download_as_markdown(self):
        """Descarga artículos del servidor como archivos Markdown"""
        server = self.config.get("server")
        if not server.get("host"):
            RetroMessageBox.showerror(self.root, "Error", "Configura el servidor primero")
            return

        # Pedir directorio de destino
        dest_dir = filedialog.askdirectory(title="Seleccionar carpeta de destino")
        if not dest_dir:
            return

        def do_download():
            try:
                import time
                import os
                protocol = server.get('protocol', 'ftp').upper()
                self.anim_add_line(f"> Conectando a {server['host']}...")
                self.anim_set_status(f"Conectando {protocol}...")
                uploader = FileUploader(self.config)
                uploader.connect()
                self.anim_add_line("  ✓ Conexión establecida")
                remote_path = server['remote_path']
                files = uploader.list_files(remote_path)
                article_files = [f for f in files if f.endswith('.html') and f not in ['index.html', 'articulo.html']]
                if not article_files:
                    self.anim_add_line("  ! No hay artículos")
                    uploader.disconnect()
                    self.anim_finish(True, "Sin artículos")
                    return
                total = len(article_files)
                count = 0
                self.anim_add_line(f"> Descargando {total} artículos...")
                for i, filename in enumerate(article_files):
                    self.anim_add_line(f"  [{i+1}/{total}] {filename}")
                    self.anim_update_progress(i, total)
                    remote_file = f"{remote_path}/{filename}"
                    content = uploader.download_string(remote_file)
                    if content:
                        data = self.articles.extract_article_data(content, filename)
                        if data:
                            md_body = data.get('content', '').strip()
                            if not md_body:
                                md_body = '*[El contenido del artículo está vacío o no se pudo extraer.]*'
                            md_content = f"""---\ntitle: {data.get('title','')}\ncategory: {data.get('category','')}\ntags: {', '.join(data.get('tags', []))}\ndate: {data.get('created', '')}\n---\n\n{md_body}\n"""
                            slug = data.get('id', filename.replace('.html', ''))
                            local_path = os.path.join(dest_dir, f"{slug}.md")
                            with open(local_path, 'w', encoding='utf-8') as f:
                                f.write(md_content)
                            self.anim_add_line(f"        → Guardado: {slug}.md")
                            count += 1
                        else:
                            self.anim_add_line("        ✗ Error extrayendo datos")
                    else:
                        self.anim_add_line("        ✗ Fallo al descargar")
                    time.sleep(0.1)
                self.anim_update_progress(total, total)
                uploader.disconnect()
                self.anim_finish(True, f"Descargados {count} archivos .md")
                self.set_status(f"✓ Descarga completada en {dest_dir}")
            except Exception as e:
                self.anim_finish(False, str(e))
                self.set_status(f"Error: {str(e)}")
                self.set_status(f"Error: {str(e)}")

        self.show_upload_animation(lambda: threading.Thread(target=do_download).start())

    
    
    def cleanup(self):
        """Limpia archivos temporales al cerrar"""
        preview_file = Path("preview.html")
        if preview_file.exists():
            try:
                preview_file.unlink()
            except:
                pass
    
    def run(self):
        """Ejecuta la aplicación"""
        # Registrar limpieza al cerrar
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.mainloop()
    
    def _on_closing(self):
        """Manejador para cuando se cierra la ventana"""
        self.cleanup()
        self.root.destroy()
