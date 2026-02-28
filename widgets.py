import tkinter as tk

from theme import C_ACCENT, C_ACCENT_HOVER, FONT


class ModernButton(tk.Label):
    def __init__(self, parent, text="", command=None,
                 bg_color=C_ACCENT, hover_color=C_ACCENT_HOVER, text_color="#ffffff",
                 font_cfg=(FONT, 10, "bold"), padx=14, pady=5, **kw):
        super().__init__(parent, text=text, font=font_cfg, fg=text_color, bg=bg_color,
                         cursor="hand2", padx=padx, pady=pady, **kw)
        self._command = command
        self._bg = bg_color
        self._hover = hover_color
        self.bind("<Enter>", lambda e: self.configure(bg=hover_color))
        self.bind("<Leave>", lambda e: self.configure(bg=bg_color))
        self.bind("<ButtonRelease-1>", lambda e: self._on_click())

    def _on_click(self):
        if self._command:
            self._command()

    def set_text(self, text):
        self.configure(text=text)
