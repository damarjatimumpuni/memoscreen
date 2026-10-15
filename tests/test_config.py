"""Headless tests for the config module."""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import config


class ConfigTests(unittest.TestCase):
    def setUp(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.appdata = Path(temp_dir.name)
        env = mock.patch.dict(os.environ, {"APPDATA": str(self.appdata)})
        env.start()
        self.addCleanup(env.stop)

    def config_path(self) -> Path:
        return config.get_config_dir() / config.CONFIG_FILE_NAME

    def test_missing_file_returns_defaults(self):
        self.assertEqual(config.load_config(), config.AppConfig())

    def test_save_creates_directory_and_round_trip(self):
        cfg = config.AppConfig(
            status="SEDANG RAPAT",
            custom_message="Pesan kustom",
            background_color="#07583D",
            text_color="#FFD84D",
            show_clock=False,
        )
        config.save_config(cfg)
        self.assertTrue(self.config_path().exists())
        self.assertEqual(config.load_config(), cfg)

    def test_malformed_json_returns_defaults(self):
        self.config_path().parent.mkdir(parents=True, exist_ok=True)
        self.config_path().write_text("{bukan json", encoding="utf-8")
        self.assertEqual(config.load_config(), config.AppConfig())

    def test_non_object_json_returns_defaults(self):
        self.config_path().parent.mkdir(parents=True, exist_ok=True)
        self.config_path().write_text(json.dumps(["tidak", "valid"]), encoding="utf-8")
        self.assertEqual(config.load_config(), config.AppConfig())

    def test_invalid_values_fall_back_to_defaults(self):
        data = {
            "status": "   ",
            "custom_message": 123,
            "background_color": "bukan-warna",
            "text_color": "#12345",
            "show_clock": "ya",
        }
        self.config_path().parent.mkdir(parents=True, exist_ok=True)
        self.config_path().write_text(json.dumps(data), encoding="utf-8")
        self.assertEqual(config.load_config(), config.AppConfig())

    def test_save_failure_does_not_raise(self):
        blocker = self.appdata / "blocker"
        blocker.write_text("bukan direktori", encoding="utf-8")
        with mock.patch.dict(os.environ, {"APPDATA": str(blocker)}):
            config.save_config(config.AppConfig())


if __name__ == "__main__":
    unittest.main()
