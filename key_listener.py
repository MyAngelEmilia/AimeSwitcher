import time
from typing import Callable

import keyboard

from config import NUMKEY_MAP


class KeyListener:
    """全局键盘监听器，检测数字键长按并触发回调。"""

    def __init__(self, threshold_ms: int = 500,
                 on_long_press: Callable[[str], None] | None = None,
                 on_log: Callable[[str], None] | None = None):
        self.threshold_ms = threshold_ms
        self.on_long_press = on_long_press
        self._log = on_log or (lambda m: None)
        self._press_times: dict[str, float] = {}
        self._triggered_keys: set[str] = set()
        self._active = False
        self._suppressed = False

    @property
    def suppressed(self) -> bool:
        return self._suppressed

    @suppressed.setter
    def suppressed(self, value: bool):
        self._suppressed = value

    def start(self):
        self._press_times.clear()
        self._triggered_keys.clear()
        self._active = True
        keyboard.hook(self._on_event, suppress=False)
        self._log("监听已启动，等待长按数字键...")

    def stop(self):
        self._active = False
        self._press_times.clear()
        self._triggered_keys.clear()
        keyboard.unhook_all()
        self._log("监听已停止")

    def _normalize(self, event) -> str | None:
        return NUMKEY_MAP.get(event.name)

    def _on_event(self, event):
        if not self._active or self._suppressed:
            return

        digit = self._normalize(event)
        if digit is None:
            return

        if event.event_type == "down":
            if digit not in self._press_times:
                self._press_times[digit] = time.time()
                self._log(f"[按下] digit={digit} scan={event.scan_code}")
            else:
                elapsed_ms = (time.time() - self._press_times[digit]) * 1000
                if elapsed_ms >= self.threshold_ms and digit not in self._triggered_keys:
                    self._log(f"[长按] digit={digit} 持续{elapsed_ms:.0f}ms >= {self.threshold_ms}ms -> 触发!")
                    self._triggered_keys.add(digit)
                    if self.on_long_press:
                        self.on_long_press(digit)

        elif event.event_type == "up":
            self._press_times.pop(digit, None)
            self._triggered_keys.discard(digit)
            self._log(f"[释放] digit={digit}")
