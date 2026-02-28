import os
import time
import threading
from typing import Callable

import keyboard

from config import mask_card


class CardSwitcher:
    """负责写入卡号文件和模拟 Enter 长按。"""

    def __init__(self, on_success: Callable[[str, str], None] | None = None,
                 on_log: Callable[[str], None] | None = None):
        self.on_success = on_success
        self._log = on_log or (lambda m: None)
        self._busy = False

    @property
    def busy(self) -> bool:
        return self._busy

    def switch(self, card_id: str, note: str, aime_path: str, enter_duration: float):
        if self._busy:
            return
        self._log(f"  -> 开始切换: card={mask_card(card_id)} note={note!r} path={aime_path}")
        self._busy = True
        threading.Thread(target=self._do_switch,
                         args=(card_id, note, aime_path, enter_duration),
                         daemon=True).start()

    def _do_switch(self, card_id: str, note: str, aime_path: str, enter_duration: float):
        try:
            os.makedirs(os.path.dirname(aime_path), exist_ok=True)
            with open(aime_path, "w", encoding="utf-8") as f:
                f.write(card_id + "\n")
            self._log(f"  -> 卡号已写入 {aime_path}")

            self._log(f"  -> 模拟长按 Enter {enter_duration}秒...")
            keyboard.press("enter")
            time.sleep(enter_duration)
            keyboard.release("enter")
            self._log(f"  -> Enter 已释放，显示浮窗")

            if self.on_success:
                self.on_success(card_id, note)
        except Exception as e:
            self._log(f"  -> 切换失败: {e}")
        finally:
            self._busy = False
