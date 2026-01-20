"""
Ventanas emergentes y diálogos con tema retro para CTPFA CMS
"""

import tkinter as tk
from .theme import RetroTheme


class RetroMessageBox:
    """Ventanas emergentes con tema retro"""
    
    @staticmethod
    def _create_dialog(parent, title, message, dialog_type="info", buttons=None):
        """Crea un diálogo personalizado con tema retro"""
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.configure(bg=RetroTheme.BG_DARK)
        dialog.resizable(False, False)
        dialog.transient(parent)
        dialog.grab_set()
        
        # Centrar en la ventana padre
        dialog.update_idletasks()
        
        # Configurar colores según tipo
        colors = {
            "info": (RetroTheme.NEON_CYAN, "ℹ"),
            "success": (RetroTheme.NEON_GREEN, "✓"),
            "warning": (RetroTheme.NEON_ORANGE, "⚠"),
            "error": (RetroTheme.NEON_RED, "✗"),
            "question": (RetroTheme.NEON_YELLOW, "?")
        }
        accent_color, icon = colors.get(dialog_type, colors["info"])
        
        # Marco principal con borde neón
        main_frame = tk.Frame(dialog, bg=RetroTheme.BG_DARK, 
                             highlightbackground=accent_color,
                             highlightthickness=2)
        main_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Barra de título personalizada
        title_bar = tk.Frame(main_frame, bg=RetroTheme.BG_PURPLE, height=30)
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)
        
        title_label = tk.Label(title_bar, text=f"═══ {title.upper()} ═══",
                              font=RetroTheme.FONT_MAIN,
                              fg=accent_color, bg=RetroTheme.BG_PURPLE)
        title_label.pack(expand=True)
        
        # Contenido
        content_frame = tk.Frame(main_frame, bg=RetroTheme.BG_DARK)
        content_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Icono y mensaje
        icon_label = tk.Label(content_frame, text=icon, font=("Courier New", 32),
                             fg=accent_color, bg=RetroTheme.BG_DARK)
        icon_label.pack(pady=(0, 10))
        
        msg_label = tk.Label(content_frame, text=message, font=RetroTheme.FONT_MAIN,
                            fg=RetroTheme.TEXT_PRIMARY, bg=RetroTheme.BG_DARK,
                            wraplength=350, justify="center")
        msg_label.pack(pady=(0, 15))
        
        # Botones
        btn_frame = tk.Frame(main_frame, bg=RetroTheme.BG_DARK)
        btn_frame.pack(pady=(0, 15))
        
        result = {"value": None}
        
        def create_button(text, value, color):
            btn = tk.Button(btn_frame, text=f"[ {text} ]", font=RetroTheme.FONT_MAIN,
                           fg=color, bg=RetroTheme.BG_DARK,
                           activeforeground=RetroTheme.BG_DARK,
                           activebackground=color,
                           bd=0, highlightthickness=1,
                           highlightbackground=color,
                           cursor="hand2",
                           command=lambda: (result.update({"value": value}), dialog.destroy()))
            btn.pack(side="left", padx=5)
            # Efecto hover
            btn.bind("<Enter>", lambda e: btn.configure(fg=RetroTheme.BG_DARK, bg=color))
            btn.bind("<Leave>", lambda e: btn.configure(fg=color, bg=RetroTheme.BG_DARK))
            return btn
        
        if buttons is None:
            buttons = [("ACEPTAR", True, accent_color)]
        
        for text, value, color in buttons:
            create_button(text, value, color)
        
        # Centrar diálogo
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (width // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (height // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Efecto de parpadeo del borde
        def blink_border():
            current = main_frame.cget("highlightbackground")
            new_color = RetroTheme.BG_DARK if current == accent_color else accent_color
            main_frame.configure(highlightbackground=new_color)
            if dialog.winfo_exists():
                dialog.after(500, blink_border)
        
        blink_border()
        
        dialog.wait_window()
        return result["value"]
    
    @classmethod
    def showinfo(cls, parent, title, message):
        """Muestra mensaje informativo"""
        return cls._create_dialog(parent, title, message, "info")
    
    @classmethod
    def showsuccess(cls, parent, title, message):
        """Muestra mensaje de éxito"""
        return cls._create_dialog(parent, title, message, "success")
    
    @classmethod
    def showwarning(cls, parent, title, message):
        """Muestra mensaje de advertencia"""
        return cls._create_dialog(parent, title, message, "warning")
    
    @classmethod
    def showerror(cls, parent, title, message):
        """Muestra mensaje de error"""
        return cls._create_dialog(parent, title, message, "error")
    
    @classmethod
    def askyesno(cls, parent, title, message):
        """Pregunta sí/no"""
        buttons = [
            ("SÍ", True, RetroTheme.NEON_GREEN),
            ("NO", False, RetroTheme.NEON_RED)
        ]
        return cls._create_dialog(parent, title, message, "question", buttons)
