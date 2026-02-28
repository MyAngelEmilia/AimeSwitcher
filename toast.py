import ctypes
import tkinter as tk

from config import mask_card
from theme import C_ACCENT, C_TEXT2, FONT, FONT_MONO

GWL_EXSTYLE = -20
WS_EX_NOACTIVATE = 0x08000000
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_TOPMOST = 0x00000008
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_NOACTIVATE = 0x0010
HWND_TOPMOST = -1

_user32 = ctypes.windll.user32


class ToastOverlay:
    """屏幕右上角的浮窗提示，不抢走其他程序焦点。"""

    def __init__(self, root: tk.Tk):
        self._root = root
        self._win: tk.Toplevel | None = None
        self._cancel_id = None

    def show(self, card_id: str, note: str, duration_ms: int = 2500):
        self._root.after(0, self._do_show, card_id, note, duration_ms)

    def _do_show(self, card_id: str, note: str, duration_ms: int):
        if self._win is not None:
            try:
                if self._cancel_id is not None:
                    self._win.after_cancel(self._cancel_id)
                self._win.destroy()
            except Exception:
                pass
            self._win = None

        win = tk.Toplevel(self._root)
        self._win = win
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.attributes("-alpha", 0.96)
        toast_bg = "#ffffff"
        win.configure(bg=toast_bg)

        frame = tk.Frame(win, bg=toast_bg, padx=28, pady=16,
                         highlightthickness=1, highlightbackground="#d0d8e0")
        frame.pack()

        tk.Frame(frame, bg=C_ACCENT, height=3).pack(fill="x", pady=(0, 12))

        tk.Label(frame, text="卡号已切换", font=(FONT, 14, "bold"),
                 fg=C_ACCENT, bg=toast_bg).pack(pady=(0, 6))

        tk.Label(frame, text=mask_card(card_id), font=(FONT_MONO, 20, "bold"),
                 fg="#1a2a3a", bg=toast_bg).pack(pady=(0, 4))

        if note:
            tk.Label(frame, text=note, font=(FONT, 11),
                     fg=C_TEXT2, bg=toast_bg).pack(pady=(0, 2))

        win.update_idletasks()
        w = win.winfo_width()
        sx = win.winfo_screenwidth()
        win.geometry(f"+{sx - w - 20}+20")

        win.update_idletasks()
        try:
            frame_id = win.wm_frame()
            hwnd = int(frame_id, 16) if frame_id else _user32.FindWindowW(None, None)
        except Exception:
            hwnd = _user32.FindWindowW(None, None)

        style = _user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        _user32.SetWindowLongW(hwnd, GWL_EXSTYLE,
                               style | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW | WS_EX_TOPMOST)
        _user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                             SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE)

        self._cancel_id = win.after(duration_ms, self._fade_out)

    def _fade_out(self):
        if self._win is None:
            return
        try:
            alpha = self._win.attributes("-alpha")
            if alpha > 0.1:
                self._win.attributes("-alpha", alpha - 0.08)
                self._cancel_id = self._win.after(40, self._fade_out)
            else:
                self._win.destroy()
                self._win = None
        except Exception:
            self._win = None
