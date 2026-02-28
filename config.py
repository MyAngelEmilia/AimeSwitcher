import json
import os
import sys

APP_DIR = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, "frozen", False) else __file__))
CONFIG_FILE = os.path.join(APP_DIR, "aime_switcher_config.json")

DEFAULT_CONFIG = {
    "aime_path": os.path.join(APP_DIR, "DEVICE", "aime.txt"),
    "enter_duration": 3.0,
    "long_press_threshold": 500,
    "debug": False,
    "cards": {str(i): {"card_id": "", "note": ""} for i in range(10)},
}

NUMKEY_MAP = {str(i): str(i) for i in range(10)}


def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            for k, v in DEFAULT_CONFIG.items():
                cfg.setdefault(k, v)
            for i in range(10):
                cfg["cards"].setdefault(str(i), {"card_id": "", "note": ""})
            return cfg
        except Exception:
            pass
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    save_config(cfg)
    return cfg


def save_config(cfg: dict):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def mask_card(card_id: str) -> str:
    if len(card_id) <= 8:
        return "*" * len(card_id)
    return card_id[:4] + "*" * (len(card_id) - 8) + card_id[-4:]
