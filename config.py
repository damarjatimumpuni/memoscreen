"""Load and save user preferences in a JSON configuration file."""

import json
import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

CONFIG_DIR_NAME = "MemoScreen"
CONFIG_FILE_NAME = "config.json"

_HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


def get_config_dir() -> Path:
    """Return the per-user configuration directory."""
    appdata = os.getenv("APPDATA")
    base = Path(appdata) if appdata else Path.home() / ".config"
    return base / CONFIG_DIR_NAME


@dataclass
class AppConfig:
    status: str = "SEDANG SHOLAT"
    custom_message: str = ""
    background_color: str = "#101418"
    text_color: str = "#FFFFFF"
    show_clock: bool = True
    bounce: bool = True


def load_config() -> AppConfig:
    """Load preferences, falling back to safe defaults on any problem."""
    defaults = AppConfig()
    path = get_config_dir() / CONFIG_FILE_NAME
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return defaults
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        logger.warning("Konfigurasi tidak dapat dibaca, gunakan bawaan: %s", exc)
        return defaults

    if not isinstance(raw, dict):
        return defaults

    config = defaults
    status = raw.get("status")
    if isinstance(status, str) and status.strip():
        config.status = status.strip()

    custom_message = raw.get("custom_message")
    if isinstance(custom_message, str):
        config.custom_message = custom_message

    background_color = raw.get("background_color")
    if isinstance(background_color, str) and _HEX_COLOR_RE.match(background_color):
        config.background_color = background_color.upper()

    text_color = raw.get("text_color")
    if isinstance(text_color, str) and _HEX_COLOR_RE.match(text_color):
        config.text_color = text_color.upper()

    show_clock = raw.get("show_clock")
    if isinstance(show_clock, bool):
        config.show_clock = show_clock

    bounce = raw.get("bounce")
    if isinstance(bounce, bool):
        config.bounce = bounce

    return config


def save_config(config: AppConfig) -> None:
    """Persist preferences; never raise if saving fails."""
    try:
        directory = get_config_dir()
        directory.mkdir(parents=True, exist_ok=True)
        data = {
            "status": config.status,
            "custom_message": config.custom_message,
            "background_color": config.background_color,
            "text_color": config.text_color,
            "show_clock": config.show_clock,
            "bounce": config.bounce,
        }
        path = directory / CONFIG_FILE_NAME
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError as exc:
        logger.warning("Konfigurasi tidak dapat disimpan: %s", exc)
