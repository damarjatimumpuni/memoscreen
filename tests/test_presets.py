"""Headless tests for the presets module."""

import re
import unittest

import presets

HEX_COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")


class PresetsTests(unittest.TestCase):
    def test_status_presets_not_empty_and_unique(self):
        self.assertTrue(presets.STATUS_PRESETS)
        self.assertEqual(len(presets.STATUS_PRESETS), len(set(presets.STATUS_PRESETS)))

    def test_background_colors_valid(self):
        self.assertTrue(presets.BACKGROUND_COLORS)
        for name, hex_color in presets.BACKGROUND_COLORS:
            self.assertTrue(name)
            self.assertRegex(hex_color, HEX_COLOR)

    def test_text_colors_valid(self):
        self.assertTrue(presets.TEXT_COLORS)
        for name, hex_color in presets.TEXT_COLORS:
            self.assertTrue(name)
            self.assertRegex(hex_color, HEX_COLOR)

    def test_defaults_are_members_of_presets(self):
        self.assertIn(presets.DEFAULT_STATUS, presets.STATUS_PRESETS)
        self.assertIn(
            presets.DEFAULT_BACKGROUND, [color for _name, color in presets.BACKGROUND_COLORS]
        )
        self.assertIn(
            presets.DEFAULT_TEXT_COLOR, [color for _name, color in presets.TEXT_COLORS]
        )


if __name__ == "__main__":
    unittest.main()
