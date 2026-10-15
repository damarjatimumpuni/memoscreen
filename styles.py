"""Shared visual styling and color definitions."""

from tkinter import ttk

FONT_FAMILY = "Segoe UI"

# Dark theme palette for the control window.
BG_WINDOW = "#1B1F24"
BG_INPUT = "#2E353D"
FG_TEXT = "#E8EAED"
FG_MUTED = "#9AA3AD"
BORDER = "#3A4149"

ACCENT = "#4C8DFF"
ACCENT_HOVER = "#6AA2FF"
ACCENT_PRESSED = "#3B78E0"

BUTTON_BG = "#33404D"
BUTTON_HOVER = "#41505E"
BUTTON_PRESSED = "#2A333C"
DISABLED_BG = "#262C33"

# Border drawn around the currently selected color swatch.
SELECTED_BORDER = "#FFFFFF"
SWATCH_SIZE = 32


def configure_ttk_style(style: ttk.Style) -> None:
    """Apply the dark theme to all ttk widgets."""
    style.theme_use("clam")

    style.configure(
        ".",
        font=(FONT_FAMILY, 10),
        background=BG_WINDOW,
        foreground=FG_TEXT,
        bordercolor=BORDER,
        borderwidth=0,
    )
    style.configure("TFrame", background=BG_WINDOW)
    style.configure("TLabel", background=BG_WINDOW, foreground=FG_TEXT)
    style.configure("Title.TLabel", font=(FONT_FAMILY, 16, "bold"))
    style.configure("Muted.TLabel", background=BG_WINDOW, foreground=FG_MUTED)

    style.configure(
        "TButton",
        font=(FONT_FAMILY, 10, "bold"),
        padding=(18, 8),
        background=BUTTON_BG,
    )
    style.map(
        "TButton",
        background=[
            ("active", BUTTON_HOVER),
            ("pressed", BUTTON_PRESSED),
            ("disabled", DISABLED_BG),
        ],
        foreground=[("disabled", FG_MUTED)],
    )

    style.configure("Accent.TButton", background=ACCENT, foreground="#FFFFFF")
    style.map(
        "Accent.TButton",
        background=[
            ("active", ACCENT_HOVER),
            ("pressed", ACCENT_PRESSED),
            ("disabled", DISABLED_BG),
        ],
        foreground=[("disabled", FG_MUTED)],
    )

    style.configure("TEntry", fieldbackground=BG_INPUT, bordercolor=BORDER, padding=6)
    style.map(
        "TEntry",
        fieldbackground=[("readonly", BG_INPUT), ("disabled", BG_INPUT)],
    )

    style.configure(
        "TCombobox",
        fieldbackground=BG_INPUT,
        bordercolor=BORDER,
        arrowcolor=FG_TEXT,
        padding=6,
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", BG_INPUT), ("active", BG_INPUT), ("disabled", BG_INPUT)],
        foreground=[("readonly", FG_TEXT), ("disabled", FG_MUTED)],
        arrowcolor=[("disabled", FG_MUTED)],
    )

    style.configure("TCheckbutton", background=BG_WINDOW, foreground=FG_TEXT)
    style.map(
        "TCheckbutton",
        background=[("active", BG_WINDOW), ("disabled", BG_WINDOW)],
        foreground=[("disabled", FG_MUTED)],
    )
