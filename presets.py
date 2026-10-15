"""Predefined status messages and color presets.

Edit the lists below to change the available statuses and colors
without touching the GUI code.
"""

STATUS_PRESETS: list[str] = [
    "AT MASJID",
    "HAVING LUNCH",
    "OUT FOR MEETING",
    "TOILET FOR A SEC",
    "DON'T TURN OFF, SHUT DOWN AUTOMATICALLY",
]

# (Display name, hex color)
BACKGROUND_COLORS: list[tuple[str, str]] = [
    ("Black", "#101418"),
    ("Green", "#07583D"),
    ("Blue", "#173B78"),
    ("Magenta", "#43216B"),
    ("Red", "#55231F"),
    ("Slate", "#263548"),
]

TEXT_COLORS: list[tuple[str, str]] = [
    ("White", "#FFFFFF"),
    ("Yellow", "#FFD84D"),
    ("Light Green", "#7BE0A3"),
    ("Black", "#101418"),
]

DEFAULT_STATUS = STATUS_PRESETS[0]
DEFAULT_BACKGROUND = BACKGROUND_COLORS[0][1]
DEFAULT_TEXT_COLOR = TEXT_COLORS[0][1]
