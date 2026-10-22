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
    """The fullscreen overlay that shows the status message."""

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

        self.window = tk.Toplevel(parent)
        self.window.configure(bg=background_color)
        self.window.attributes("-fullscreen", True)
        self.window.attributes("-topmost", True)
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.window.bind("<Escape>", lambda _event: self.close())

        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        font, text = fit_message(message, screen_width, screen_height)
        self._label = tk.Label(
            self.window,
            text=text,
            font=font,
            bg=background_color,
            fg=text_color,
        )
        # Placed with absolute coordinates only, so the bouncing loop can
        # move the label without fighting relative placement options.
        self._label.place(x=0, y=0, anchor="nw")
        self.window.update_idletasks()
        self._position = [
            max(0, (screen_width - self._label.winfo_reqwidth()) // 2),
            max(0, (screen_height - self._label.winfo_reqheight()) // 2),
        ]
        self._label.place(x=self._position[0], y=self._position[1])

        if show_clock:
            clock_size = max(16, screen_height // 30)
            self.clock_label = tk.Label(
                self.window,
                text="",
                font=(FONT_FAMILY, clock_size, "bold"),
                bg=background_color,
                fg=text_color,
            )
            self.clock_label.place(relx=0.5, rely=CLOCK_Y_FRACTION, anchor="center")
            self._update_clock()

        self.window.focus_force()

        if bounce:
            self._motion_id = self.window.after(50, self._start_motion)

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
        width = self._label.winfo_reqwidth()
        height = self._label.winfo_reqheight()

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
        self._label.place(x=self._position[0], y=self._position[1])
        self._motion_id = self.window.after(FRAME_MS, self._animate)

    # ------------------------------------------------------------------
    # Clock and cleanup
    # ------------------------------------------------------------------

    def _update_clock(self) -> None:
        if self._closed:
            return
        self.clock_label.config(text=datetime.now().strftime("%H:%M"))
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
