"""Fullscreen display: adaptive text sizing, bouncing motion, digital clock, and exit behavior."""

import math
import random
import tkinter as tk
import tkinter.font as tkfont
from datetime import datetime
from typing import Callable

from styles import FONT_FAMILY

MIN_FONT_SIZE = 16
MAX_FONT_SIZE = 220
# Fractions of the screen the text may occupy; the rest is a safety margin
# so the text is never clipped at the screen edges.
MAX_WIDTH_FRACTION = 0.92
MAX_HEIGHT_FRACTION = 0.55
CLOCK_Y_FRACTION = 0.85

# Bouncing motion: frame interval in milliseconds and speed in pixels per frame.
FRAME_MS = 20
MIN_SPEED = 2.0
MAX_SPEED = 6.0


def _wrap_text(text: str, font: tkfont.Font, max_width: int) -> str:
    """Greedily wrap text on word boundaries so each line fits max_width pixels."""
    words = text.split()
    if not words:
        return text
    lines = [words[0]]
    for word in words[1:]:
        if font.measure(f"{lines[-1]} {word}") <= max_width:
            lines[-1] = f"{lines[-1]} {word}"
        else:
            lines.append(word)
    return "\n".join(lines)


def fit_message(text: str, screen_width: int, screen_height: int) -> tuple[tkfont.Font, str]:
    """Pick the largest bold font that fits the message on the screen.

    Short messages stay on one line at a large size; long messages are
    wrapped and the font shrinks until the wrapped block fits.
    """
    max_width = int(screen_width * MAX_WIDTH_FRACTION)
    max_height = int(screen_height * MAX_HEIGHT_FRACTION)
    size = min(MAX_FONT_SIZE, max(MIN_FONT_SIZE, screen_height // 8))

    while size > MIN_FONT_SIZE:
        font = tkfont.Font(family=FONT_FAMILY, size=size, weight="bold")
        if font.measure(text) <= max_width:
            return font, text
        wrapped = _wrap_text(text, font, max_width)
        lines = wrapped.split("\n")
        width_ok = all(font.measure(line) <= max_width for line in lines)
        height_ok = len(lines) * font.metrics("linespace") <= max_height
        if width_ok and height_ok:
            return font, wrapped
        size -= 2

    font = tkfont.Font(family=FONT_FAMILY, size=MIN_FONT_SIZE, weight="bold")
    return font, _wrap_text(text, font, max_width)


class FullscreenStatusWindow:
    """The fullscreen overlay that shows the status message.

    Every element is drawn on a single canvas, so no widget paints a
    background box over the moving message and the clock has no backdrop.
    """

    def __init__(
        self,
        parent: tk.Tk,
        message: str,
        background_color: str,
        text_color: str,
        show_clock: bool,
        on_close: Callable[[], None],
        bounce: bool = False,
    ) -> None:
        self._on_close = on_close
        self._after_id: str | None = None
        self._motion_id: str | None = None
        self._closed = False
        self._position = [0, 0]
        self._velocity = [0.0, 0.0]
        self._size = [0, 0]

        self.window = tk.Toplevel(parent)
        self.window.configure(bg=background_color)
        self.window.attributes("-fullscreen", True)
        self.window.attributes("-topmost", True)
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.window.bind("<Escape>", lambda _event: self.close())

        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        self.canvas = tk.Canvas(
            self.window,
            bg=background_color,
            highlightthickness=0,
            borderwidth=0,
            width=screen_width,
            height=screen_height,
        )
        self.canvas.pack(fill="both", expand=True)

        font, text = fit_message(message, screen_width, screen_height)
        self._text_id = self.canvas.create_text(
            0, 0, text=text, font=font, fill=text_color, anchor="nw"
        )
        self.window.update_idletasks()
        self._measure_text()
        self._position = [
            max(0, (screen_width - self._size[0]) // 2),
            max(0, (screen_height - self._size[1]) // 2),
        ]
        self._move_text()

        if show_clock:
            clock_size = max(16, screen_height // 30)
            self._clock_id = self.canvas.create_text(
                screen_width / 2,
                screen_height * CLOCK_Y_FRACTION,
                text="",
                font=(FONT_FAMILY, clock_size, "bold"),
                fill=text_color,
                anchor="center",
            )
            self._update_clock()

        self.window.focus_force()

        if bounce:
            self._motion_id = self.window.after(50, self._start_motion)

    # ------------------------------------------------------------------
    # Canvas helpers
    # ------------------------------------------------------------------

    def _measure_text(self) -> None:
        """Read the on-screen size of the message text."""
        x1, y1, x2, y2 = self.canvas.bbox(self._text_id)
        self._size = [int(x2 - x1), int(y2 - y1)]

    def _move_text(self) -> None:
        self.canvas.coords(self._text_id, self._position[0], self._position[1])

    # ------------------------------------------------------------------
    # Bouncing motion
    # ------------------------------------------------------------------

    def _start_motion(self) -> None:
        """Give the message a random direction and start the bounce loop."""
        if self._closed:
            return
        screen_width = self.window.winfo_screenwidth()
        speed = max(MIN_SPEED, min(MAX_SPEED, screen_width / 600))
        angle = random.uniform(0, 2 * math.pi)
        self._velocity = [speed * math.cos(angle), speed * math.sin(angle)]
        self._animate()

    def _animate(self) -> None:
        """Move the message one step, bouncing off the screen edges."""
        if self._closed:
            return
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        width, height = self._size

        x = self._position[0] + self._velocity[0]
        y = self._position[1] + self._velocity[1]

        if x <= 0:
            x = 0
            self._velocity[0] = abs(self._velocity[0])
        elif x + width >= screen_width:
            x = screen_width - width
            self._velocity[0] = -abs(self._velocity[0])

        if y <= 0:
            y = 0
            self._velocity[1] = abs(self._velocity[1])
        elif y + height >= screen_height:
            y = screen_height - height
            self._velocity[1] = -abs(self._velocity[1])

        self._position = [int(x), int(y)]
        self._move_text()
        self._motion_id = self.window.after(FRAME_MS, self._animate)

    # ------------------------------------------------------------------
    # Clock and cleanup
    # ------------------------------------------------------------------

    def _update_clock(self) -> None:
        if self._closed:
            return
        self.canvas.itemconfig(self._clock_id, text=datetime.now().strftime("%H:%M"))
        self._after_id = self.window.after(1000, self._update_clock)

    def close(self) -> None:
        """Close the fullscreen window and cancel all scheduled updates."""
        if self._closed:
            return
        self._closed = True
        for after_id in (self._after_id, self._motion_id):
            if after_id is not None:
                self.window.after_cancel(after_id)
        self._after_id = None
        self._motion_id = None
        self.window.destroy()
        self._on_close()
