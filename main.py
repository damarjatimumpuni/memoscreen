"""Memo Screen — application entry point and main control window."""

import logging
import sys
import time
import tkinter as tk
from tkinter import messagebox, ttk

import config
import presets
import styles
from fullscreen import FullscreenStatusWindow
from winapi import is_workstation_locked

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def _enable_dpi_awareness() -> None:
    """Ask Windows for sharp DPI scaling. Must run before the Tk root exists."""
    if sys.platform != "win32":
        return
    try:
        import ctypes

        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError):
        pass


class MemoScreenApp:
    """The main control window."""

    # How often the session state is checked after the screen was locked.
    UNLOCK_POLL_MS = 250
    # Give up watching if the lock never shows up on screen.
    UNLOCK_GIVE_UP_SECONDS = 10

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Memo Screen")
        self.root.configure(bg=styles.BG_WINDOW)
        self.root.resizable(False, False)

        self.app_config = config.load_config()
        self.fullscreen_window: FullscreenStatusWindow | None = None
        self._loading = False
        self._unlock_watch_id: str | None = None
        self._saw_lock = False
        self._lock_time = 0.0

        self._build_ui()
        self._load_ui_from_config()
        self._update_buttons()

        self.root.update_idletasks()
        self.root.eval("tk::PlaceWindow . center")
        self.root.protocol("WM_DELETE_WINDOW", self._on_root_close)

    # ------------------------------------------------------------------
    # Interface construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        style = ttk.Style(self.root)
        styles.configure_ttk_style(style)

        outer = ttk.Frame(self.root, padding=20)
        outer.grid(row=0, column=0, sticky="nsew")
        outer.columnconfigure(0, weight=1)
        outer.columnconfigure(1, weight=1)

        ttk.Label(outer, text="Memo Screen", style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 16)
        )

        ttk.Label(outer, text="Template Messages").grid(row=1, column=0, columnspan=2, sticky="w")
        self.status_var = tk.StringVar()
        self.status_combo = ttk.Combobox(
            outer,
            textvariable=self.status_var,
            values=presets.STATUS_PRESETS,
            state="readonly",
            width=34,
        )
        self.status_combo.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(4, 12))
        self.status_combo.bind("<<ComboboxSelected>>", lambda _event: self._on_preference_changed())

        ttk.Label(outer, text="Custom Text (Override Template)").grid(
            row=3, column=0, columnspan=2, sticky="w"
        )
        self.custom_var = tk.StringVar()
        self.custom_entry = ttk.Entry(outer, textvariable=self.custom_var, width=34)
        self.custom_entry.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(4, 12))
        self.custom_var.trace_add("write", lambda *_args: self._on_preference_changed())

        ttk.Label(outer, text="Background Color").grid(
            row=5, column=0, columnspan=2, sticky="w", pady=(0, 4)
        )
        self.bg_color_var = tk.StringVar()
        self.bg_name_var = tk.StringVar()
        self.bg_swatches = self._build_swatch_row(
            outer, 6, presets.BACKGROUND_COLORS, self.bg_name_var, self._select_background_color
        )

        ttk.Label(outer, text="Text Color").grid(
            row=7, column=0, columnspan=2, sticky="w", pady=(12, 4)
        )
        self.text_color_var = tk.StringVar()
        self.text_name_var = tk.StringVar()
        self.text_swatches = self._build_swatch_row(
            outer, 8, presets.TEXT_COLORS, self.text_name_var, self._select_text_color
        )

        self.clock_var = tk.BooleanVar()
        ttk.Checkbutton(
            outer,
            text="Show Digital Clock",
            variable=self.clock_var,
            command=self._on_preference_changed,
        ).grid(row=9, column=0, columnspan=2, sticky="w", pady=(12, 8))

        self.bounce_var = tk.BooleanVar()
        ttk.Checkbutton(
            outer,
            text="Bounce Animation",
            variable=self.bounce_var,
            command=self._on_preference_changed,
        ).grid(row=10, column=0, columnspan=2, sticky="w", pady=(0, 16))

        button_row = ttk.Frame(outer)
        button_row.grid(row=11, column=0, columnspan=2, sticky="")
        self.start_button = ttk.Button(
            button_row, text="Start", style="Accent.TButton", command=self._start, width=16
        )
        self.start_button.pack()

    def _build_swatch_row(
        self,
        parent: ttk.Frame,
        row: int,
        colors: list[tuple[str, str]],
        name_var: tk.StringVar,
        on_select,
    ) -> list[tuple[tk.Canvas, str, str]]:
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, columnspan=2, sticky="w")

        swatches: list[tuple[tk.Canvas, str, str]] = []
        for name, hex_color in colors:
            canvas = tk.Canvas(
                frame,
                width=styles.SWATCH_SIZE,
                height=styles.SWATCH_SIZE,
                bg=hex_color,
                highlightthickness=2,
                highlightbackground=styles.BORDER,
                cursor="hand2",
            )
            canvas.pack(side="left", padx=(0, 8))
            canvas.bind("<Button-1>", lambda _event, color=hex_color: on_select(color))
            swatches.append((canvas, name, hex_color))

        ttk.Label(frame, textvariable=name_var, style="Muted.TLabel").pack(
            side="left", padx=(4, 0)
        )
        return swatches

    # ------------------------------------------------------------------
    # Preferences
    # ------------------------------------------------------------------

    def _load_ui_from_config(self) -> None:
        cfg = self.app_config
        self._loading = True
        try:
            self.status_var.set(
                cfg.status if cfg.status in presets.STATUS_PRESETS else presets.DEFAULT_STATUS
            )
            self.custom_var.set(cfg.custom_message)
            self.bg_color_var.set(cfg.background_color)
            self.text_color_var.set(cfg.text_color)
            self.clock_var.set(cfg.show_clock)
            self.bounce_var.set(cfg.bounce)
        finally:
            self._loading = False
        self._refresh_swatches(self.bg_swatches, self.bg_name_var, self.bg_color_var.get())
        self._refresh_swatches(self.text_swatches, self.text_name_var, self.text_color_var.get())

    def _on_preference_changed(self) -> None:
        if self._loading:
            return
        self.app_config.status = self.status_var.get()
        self.app_config.custom_message = self.custom_var.get()
        self.app_config.background_color = self.bg_color_var.get()
        self.app_config.text_color = self.text_color_var.get()
        self.app_config.show_clock = self.clock_var.get()
        self.app_config.bounce = self.bounce_var.get()
        config.save_config(self.app_config)

    def _select_background_color(self, hex_color: str) -> None:
        self.bg_color_var.set(hex_color)
        self._refresh_swatches(self.bg_swatches, self.bg_name_var, hex_color)
        self._on_preference_changed()

    def _select_text_color(self, hex_color: str) -> None:
        self.text_color_var.set(hex_color)
        self._refresh_swatches(self.text_swatches, self.text_name_var, hex_color)
        self._on_preference_changed()

    def _refresh_swatches(
        self,
        swatches: list[tuple[tk.Canvas, str, str]],
        name_var: tk.StringVar,
        selected: str,
    ) -> None:
        for canvas, name, hex_color in swatches:
            is_selected = hex_color.lower() == selected.lower()
            canvas.config(
                highlightbackground=styles.SELECTED_BORDER if is_selected else styles.BORDER
            )
            if is_selected:
                name_var.set(f"{name} {hex_color}")

    # ------------------------------------------------------------------
    # Fullscreen mode
    # ------------------------------------------------------------------

    def _start(self) -> None:
        if self.fullscreen_window is not None:
            return

        message = self.custom_var.get().strip() or self.status_var.get().strip()
        if not message:
            messagebox.showwarning("Memo Screen", "Please enter a message before starting.")
            return

        self._on_preference_changed()
        logger.info("Membuka mode layar penuh: %s", message)
        self.fullscreen_window = FullscreenStatusWindow(
            parent=self.root,
            message=message,
            background_color=self.bg_color_var.get(),
            text_color=self.text_color_var.get(),
            show_clock=self.clock_var.get(),
            on_close=self._on_fullscreen_closed,
            bounce=self.bounce_var.get(),
            on_locked=self._on_workstation_locked,
        )
        self._update_buttons()

    def _on_fullscreen_closed(self) -> None:
        self.fullscreen_window = None
        self._update_buttons()
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def _update_buttons(self) -> None:
        active = self.fullscreen_window is not None
        self.start_button.state(["disabled"] if active else ["!disabled"])

    # ------------------------------------------------------------------
    # Locked session handling
    # ------------------------------------------------------------------

    def _on_workstation_locked(self) -> None:
        """Watch the session and quit the app once the user logs back in."""
        logger.info("Sesi dikunci, menunggu login kembali")
        self._saw_lock = False
        self._lock_time = time.monotonic()
        self._unlock_watch_id = self.root.after(self.UNLOCK_POLL_MS, self._watch_unlock)

    def _watch_unlock(self) -> None:
        if is_workstation_locked():
            self._saw_lock = True
        elif self._saw_lock:
            logger.info("Login kembali terdeteksi, menutup aplikasi")
            self._shutdown()
            return
        elif time.monotonic() - self._lock_time > self.UNLOCK_GIVE_UP_SECONDS:
            # The lock never showed up, so there is nothing to wait for.
            self._unlock_watch_id = None
            return
        self._unlock_watch_id = self.root.after(self.UNLOCK_POLL_MS, self._watch_unlock)

    def _shutdown(self) -> None:
        """Close the fullscreen window and quit the application."""
        self._cancel_unlock_watch()
        if self.fullscreen_window is not None:
            self.fullscreen_window.close()
        self.root.destroy()

    def _cancel_unlock_watch(self) -> None:
        if self._unlock_watch_id is not None:
            self.root.after_cancel(self._unlock_watch_id)
            self._unlock_watch_id = None

    def _on_root_close(self) -> None:
        self._cancel_unlock_watch()
        if self.fullscreen_window is not None:
            self.fullscreen_window.close()
        self.root.destroy()


def main() -> None:
    _enable_dpi_awareness()
    root = tk.Tk()
    MemoScreenApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
