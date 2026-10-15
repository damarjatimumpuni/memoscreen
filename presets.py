"""Predefined status messages and color presets.

Edit the lists below to change the available statuses and colors
without touching the GUI code.
"""

STATUS_PRESETS: list[str] = [
    "SEDANG SHOLAT",
    "SEDANG MAKAN",
    "SEDANG RAPAT",
    "SEDANG ISTIRAHAT",
    "SEDANG BEKERJA",
    "SEDANG DINAS",
    "SEDANG KE TOILET",
    "SEDANG CEK LAPANGAN",
    "SEDANG AMBIL DATA",
    "JANGAN DIGANGGU",
]

# (Display name, hex color)
BACKGROUND_COLORS: list[tuple[str, str]] = [
    ("Hitam", "#101418"),
    ("Hijau", "#07583D"),
    ("Biru", "#173B78"),
    ("Ungu", "#43216B"),
    ("Merah", "#55231F"),
    ("Slate", "#263548"),
]

TEXT_COLORS: list[tuple[str, str]] = [
    ("Putih", "#FFFFFF"),
    ("Kuning", "#FFD84D"),
    ("Hijau Muda", "#7BE0A3"),
    ("Hitam", "#101418"),
]

DEFAULT_STATUS = STATUS_PRESETS[0]
DEFAULT_BACKGROUND = BACKGROUND_COLORS[0][1]
DEFAULT_TEXT_COLOR = TEXT_COLORS[0][1]
