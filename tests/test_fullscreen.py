"""Headless tests for the text wrapping logic in fullscreen.py."""

import unittest

from fullscreen import _wrap_text


class FakeFont:
    """Stand-in for tkfont.Font with a fixed per-character width."""

    def __init__(self, char_width: int) -> None:
        self.char_width = char_width

    def measure(self, text: str) -> int:
        return len(text) * self.char_width


class WrapTextTests(unittest.TestCase):
    def test_short_text_is_not_wrapped(self):
        self.assertEqual(_wrap_text("SEDANG SHOLAT", FakeFont(10), 500), "SEDANG SHOLAT")

    def test_long_text_wraps_on_word_boundaries(self):
        text = "SEDANG SHOLAT DAN ISTIRAHAT"
        wrapped = _wrap_text(text, FakeFont(10), 150)
        lines = wrapped.split("\n")
        self.assertGreater(len(lines), 1)
        for line in lines:
            self.assertLessEqual(len(line) * 10, 150)
        # Wrapping only breaks at spaces, so newlines can be
        # turned back into spaces to recover the original text.
        self.assertEqual(wrapped.replace("\n", " "), text)

    def test_single_long_word_stays_on_one_line(self):
        self.assertEqual(_wrap_text("PESANSANGATPANJANG", FakeFont(10), 50), "PESANSANGATPANJANG")

    def test_empty_text(self):
        self.assertEqual(_wrap_text("", FakeFont(10), 100), "")


if __name__ == "__main__":
    unittest.main()
