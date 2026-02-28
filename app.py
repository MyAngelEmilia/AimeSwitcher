import time
import tkinter as tk
from tkinter import filedialog

from config import load_config, save_config
from theme import (C_BG, C_SURFACE, C_SURFACE2, C_BORDER, C_TEXT, C_TEXT2,
                   C_ACCENT, C_ENTRY_BG, C_LOG_BG, C_GREEN, C_RED,
                   FONT, FONT_MONO)
from widgets import ModernButton
from toast import ToastOverlay
from key_listener import KeyListener
from switcher import CardSwitcher


class AimeSwitcherApp:
    def __init__(self):
        self.config = load_config()

        self.root = tk.Tk()
        self.root.title("Aime 卡号快切")
        self.root.configure(bg=C_BG)
        self.root.resizable(True, True)
        self.root.minsize(580, 600)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self.toast = ToastOverlay(self.root)
        self.switcher = CardSwitcher(on_success=self.toast.show, on_log=self._log)
        self.listener = KeyListener(
            threshold_ms=self.config.get("long_press_threshold", 500),
            on_long_press=self._on_digit_long_press,
            on_log=self._log,
        )

        self._build_ui()
        self._load_to_ui()
        self.root.after(100, self._start_listen)

    # ── UI ──────────────────────────────────────────────────
    def _build_ui(self):
        root = self.root
        pad = 18

        top = tk.Frame(root, bg=C_BG)
        top.pack(fill="x", padx=pad, pady=(pad, 0))

        tk.Label(top, text="Aime 卡号快切", font=(FONT, 16, "bold"),
                 fg=C_TEXT, bg=C_BG).pack(side="left")

        self.status_var = tk.StringVar(value="  LISTENING")
        self.status_dot = tk.Label(top, text="\u25cf", font=(FONT, 12), fg=C_GREEN, bg=C_BG)
        self.status_dot.pack(side="right")
        self.status_label = tk.Label(top, textvariable=self.status_var, font=(FONT_MONO, 9, "bold"),
                                     fg=C_GREEN, bg=C_BG)
        self.status_label.pack(side="right")

        # 卡号映射
        card_section = tk.Frame(root, bg=C_BG)
        card_section.pack(fill="x", padx=pad, pady=(12, 0))
        tk.Label(card_section, text="卡号映射", font=(FONT, 11, "bold"),
                 fg=C_TEXT2, bg=C_BG).pack(anchor="w")

        card_box = tk.Frame(root, bg=C_SURFACE, bd=0, highlightthickness=1, highlightbackground=C_BORDER)
        card_box.pack(fill="x", padx=pad, pady=(6, 0))

        header = tk.Frame(card_box, bg=C_SURFACE2)
        header.pack(fill="x")
        for text, w in [("键", 4), ("卡号", 32), ("备注", 18)]:
            tk.Label(header, text=text, font=(FONT, 9), fg=C_TEXT2, bg=C_SURFACE2,
                     width=w, anchor="w").pack(side="left", padx=(8, 0), pady=4)

        self.card_entries: list[tuple[tk.Entry, tk.Entry]] = []
        for i in range(10):
            row_bg = C_SURFACE if i % 2 == 0 else C_SURFACE2
            row = tk.Frame(card_box, bg=row_bg)
            row.pack(fill="x")

            tk.Label(row, text=str(i), font=(FONT_MONO, 11, "bold"), fg=C_ACCENT,
                     bg=row_bg, width=3, anchor="center").pack(side="left", padx=(8, 4), pady=3)

            card_e = tk.Entry(row, width=28, font=(FONT_MONO, 10),
                              bg=C_ENTRY_BG, fg=C_TEXT, insertbackground=C_TEXT,
                              relief="flat", highlightthickness=1, highlightbackground=C_BORDER,
                              highlightcolor=C_ACCENT)
            card_e.pack(side="left", padx=(0, 6), pady=3, ipady=2)

            note_e = tk.Entry(row, width=16, font=(FONT, 10),
                              bg=C_ENTRY_BG, fg=C_TEXT, insertbackground=C_TEXT,
                              relief="flat", highlightthickness=1, highlightbackground=C_BORDER,
                              highlightcolor=C_ACCENT)
            note_e.pack(side="left", padx=(0, 8), pady=3, ipady=2)

            self.card_entries.append((card_e, note_e))

        # 设置区域
        setting_section = tk.Frame(root, bg=C_BG)
        setting_section.pack(fill="x", padx=pad, pady=(14, 0))
        tk.Label(setting_section, text="设置", font=(FONT, 11, "bold"),
                 fg=C_TEXT2, bg=C_BG).pack(anchor="w")

        setting_box = tk.Frame(root, bg=C_SURFACE, bd=0, highlightthickness=1, highlightbackground=C_BORDER)
        setting_box.pack(fill="x", padx=pad, pady=(6, 0))

        inner = tk.Frame(setting_box, bg=C_SURFACE)
        inner.pack(fill="x", padx=12, pady=10)

        r1 = tk.Frame(inner, bg=C_SURFACE)
        r1.pack(fill="x", pady=(0, 6))
        tk.Label(r1, text="aime.txt 路径", font=(FONT, 10), fg=C_TEXT2, bg=C_SURFACE, width=14,
                 anchor="w").pack(side="left")
        self.path_var = tk.StringVar()
        tk.Entry(r1, textvariable=self.path_var, font=(FONT_MONO, 9),
                 bg=C_ENTRY_BG, fg=C_TEXT, insertbackground=C_TEXT, relief="flat",
                 highlightthickness=1, highlightbackground=C_BORDER, highlightcolor=C_ACCENT
                 ).pack(side="left", fill="x", expand=True, padx=(0, 6), ipady=3)
        ModernButton(r1, text="浏览", command=self._browse_path,
                     font_cfg=(FONT, 9, "bold"), padx=10, pady=3).pack(side="left")

        r2 = tk.Frame(inner, bg=C_SURFACE)
        r2.pack(fill="x")
        tk.Label(r2, text="Enter 长按", font=(FONT, 10), fg=C_TEXT2, bg=C_SURFACE, width=14,
                 anchor="w").pack(side="left")
        self.dur_var = tk.StringVar()
        tk.Entry(r2, textvariable=self.dur_var, width=6, font=(FONT_MONO, 10),
                 bg=C_ENTRY_BG, fg=C_TEXT, insertbackground=C_TEXT, relief="flat",
                 highlightthickness=1, highlightbackground=C_BORDER, highlightcolor=C_ACCENT
                 ).pack(side="left", ipady=2)
        tk.Label(r2, text="秒", font=(FONT, 10), fg=C_TEXT2, bg=C_SURFACE).pack(side="left", padx=(4, 20))

        tk.Label(r2, text="长按阈值", font=(FONT, 10), fg=C_TEXT2, bg=C_SURFACE).pack(side="left")
        self.thresh_var = tk.StringVar()
        tk.Entry(r2, textvariable=self.thresh_var, width=6, font=(FONT_MONO, 10),
                 bg=C_ENTRY_BG, fg=C_TEXT, insertbackground=C_TEXT, relief="flat",
                 highlightthickness=1, highlightbackground=C_BORDER, highlightcolor=C_ACCENT
                 ).pack(side="left", padx=(6, 0), ipady=2)
        tk.Label(r2, text="ms", font=(FONT, 10), fg=C_TEXT2, bg=C_SURFACE).pack(side="left", padx=(4, 0))

        # 按钮行
        btn_row = tk.Frame(root, bg=C_BG)
        btn_row.pack(fill="x", padx=pad, pady=(12, 0))

        self.toggle_btn = ModernButton(btn_row, text="停止监听", command=self._toggle_listen,
                                       bg_color=C_SURFACE2, hover_color=C_BORDER, text_color=C_TEXT)
        self.toggle_btn.pack(side="left", padx=(0, 8))

        ModernButton(btn_row, text="保存设置", command=self._save_from_ui).pack(side="left", padx=(0, 8))

        self.save_hint = tk.Label(btn_row, text="", font=(FONT, 9), fg=C_GREEN, bg=C_BG)
        self.save_hint.pack(side="left", padx=(4, 0))

        # 日志（仅 debug 模式）
        self.log_text = None
        if not self.config.get("debug", False):
            tk.Frame(root, bg=C_BG, height=16).pack(fill="x")
        else:
            log_section = tk.Frame(root, bg=C_BG)
            log_section.pack(fill="x", padx=pad, pady=(12, 0))
            tk.Label(log_section, text="日志", font=(FONT, 11, "bold"),
                     fg=C_TEXT2, bg=C_BG).pack(anchor="w")

            log_box = tk.Frame(root, bg=C_LOG_BG, bd=0, highlightthickness=1, highlightbackground=C_BORDER)
            log_box.pack(fill="both", expand=True, padx=pad, pady=(6, pad))

            self.log_text = tk.Text(log_box, font=(FONT_MONO, 9), bg=C_LOG_BG, fg="#4a5568",
                                    insertbackground="#4a5568", wrap="word", relief="flat", bd=6)
            scrollbar = tk.Scrollbar(log_box, command=self.log_text.yview)
            self.log_text.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            self.log_text.pack(side="left", fill="both", expand=True)

    # ── 数据 <-> UI ─────────────────────────────────────────
    def _load_to_ui(self):
        for i in range(10):
            card_e, note_e = self.card_entries[i]
            info = self.config["cards"].get(str(i), {})
            card_e.delete(0, "end")
            card_e.insert(0, info.get("card_id", ""))
            note_e.delete(0, "end")
            note_e.insert(0, info.get("note", ""))
        self.path_var.set(self.config.get("aime_path", ""))
        self.dur_var.set(str(self.config.get("enter_duration", 3.0)))
        self.thresh_var.set(str(self.config.get("long_press_threshold", 500)))

    def _collect_ui(self):
        for i in range(10):
            card_e, note_e = self.card_entries[i]
            self.config["cards"][str(i)] = {
                "card_id": card_e.get().strip(),
                "note": note_e.get().strip(),
            }
        self.config["aime_path"] = self.path_var.get().strip()
        try:
            self.config["enter_duration"] = float(self.dur_var.get().strip())
        except ValueError:
            self.config["enter_duration"] = 3.0
        try:
            self.config["long_press_threshold"] = int(self.thresh_var.get().strip())
        except ValueError:
            self.config["long_press_threshold"] = 500

    def _save_from_ui(self):
        self._collect_ui()
        save_config(self.config)
        self.listener.threshold_ms = self.config["long_press_threshold"]
        self._log("设置已保存")
        self.save_hint.configure(text="已保存", fg=C_GREEN)
        self.root.after(2000, lambda: self.save_hint.configure(text=""))

    def _browse_path(self):
        path = filedialog.askopenfilename(
            title="选择 aime.txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if path:
            self.path_var.set(path)

    # ── 监听控制 ────────────────────────────────────────────
    def _toggle_listen(self):
        if self.listener._active:
            self._stop_listen()
        else:
            self._collect_ui()
            save_config(self.config)
            self._start_listen()

    def _start_listen(self):
        self.listener.threshold_ms = self.config.get("long_press_threshold", 500)
        self.listener.start()
        self.toggle_btn.set_text("停止监听")
        self.status_var.set("  LISTENING")
        self.status_label.configure(fg=C_GREEN)
        self.status_dot.configure(fg=C_GREEN)

    def _stop_listen(self):
        self.listener.stop()
        self.toggle_btn.set_text("启动监听")
        self.status_var.set("  STOPPED")
        self.status_label.configure(fg=C_RED)
        self.status_dot.configure(fg=C_RED)

    # ── 按键回调 ────────────────────────────────────────────
    def _on_digit_long_press(self, digit: str):
        if self.switcher.busy:
            return
        info = self.config["cards"].get(digit, {})
        card_id = info.get("card_id", "").strip()
        note = info.get("note", "").strip()
        if not card_id:
            self._log(f"  -> digit={digit} 没有配置卡号，跳过")
            return
        aime_path = self.config.get("aime_path", "")
        if not aime_path:
            self._log(f"  -> aime.txt 路径为空，跳过")
            return

        self.listener.suppressed = True
        self.switcher.switch(card_id, note, aime_path, self.config.get("enter_duration", 3.0))

        def _wait_done():
            if self.switcher.busy:
                self.root.after(200, _wait_done)
            else:
                self.listener.suppressed = False
        self.root.after(200, _wait_done)

    # ── 日志 ────────────────────────────────────────────────
    def _log(self, msg: str):
        ts = time.strftime("%H:%M:%S")
        line = f"[{ts}] {msg}"
        print(line, flush=True)
        try:
            self.root.after(0, self._append_log, line)
        except Exception:
            pass

    def _append_log(self, line: str):
        if self.log_text is None:
            return
        try:
            self.log_text.insert("end", line + "\n")
            self.log_text.see("end")
        except Exception:
            pass

    # ── 生命周期 ────────────────────────────────────────────
    def _on_close(self):
        if self.listener._active:
            self.listener.stop()
        self._collect_ui()
        save_config(self.config)
        self.root.destroy()

    def run(self):
        self.root.mainloop()
