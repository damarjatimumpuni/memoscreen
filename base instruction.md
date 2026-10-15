# AGENTS.md — Status Screen Saver

## 1. Project Overview

Build a lightweight Windows desktop application using Python that displays large, highly readable status messages in fullscreen mode.

The application is intended for an office PC. Users can select a predefined status or enter a custom message, then display it prominently on the monitor so colleagues can see the user's current activity.

Example messages:
- SEDANG SHOLAT
- SEDANG MAKAN
- SEDANG RAPAT
- SEDANG ISTIRAHAT
- SEDANG DINAS
- JANGAN DIGANGGU

The application should be simple, reliable, lightweight, and easy to run on Windows 10 and Windows 11.

**Important:** This is a fullscreen status display application, not a Windows `.scr` screensaver implementation.

## 2. Technology Stack

Use:
- Python 3.11 or newer.
- Tkinter and ttk for the graphical interface.
- JSON for saving user preferences.
- `time` or `datetime` for the optional digital clock.
- PyInstaller for optional Windows executable packaging.

Avoid unnecessary dependencies. Do not use web technologies, Electron, databases, or large GUI frameworks.

The application should run without an internet connection.

## 3. User Interface

### 3.1 Main Control Window

Create a compact, modern-looking control window.

Requirements:
- Dark theme with a clean, minimalist layout.
- Window title: `Status Screen Saver`.
- Status selection using a dropdown.
- A custom message input field.
- Background color selection using preset color swatches.
- Text color selection, if practical.
- A checkbox to show or hide the digital clock.
- A primary `Mulai` button.
- A secondary `Stop` button, disabled when no fullscreen window is active.
- A small status indicator such as `Aplikasi siap`.
- Remember the last selected status, background color, and clock preference.

The interface must use Indonesian labels.

Suggested layout:

    Status Screen Saver
    -------------------------------
    Status
    [ Sedang Sholat                 v ]

    Pesan Kustom (opsional)
    [ Tulis pesan lain...            ]

    Warna Latar
    [ Hitam ] [ Hijau ] [ Biru ] [ Ungu ]

    [x] Tampilkan jam digital

    [ Mulai ]                  [ Stop ]

    ● Aplikasi siap

Use `ttk` widgets where appropriate. If standard Tkinter styling cannot provide a particular visual effect, prefer a simple, consistent alternative instead of adding a dependency.

### 3.2 Fullscreen Status Window

When the user clicks `Mulai`, display the selected message in a fullscreen window.

Requirements:
- Cover the entire primary monitor.
- Hide the normal window decorations and taskbar while fullscreen.
- Center the message horizontally and vertically.
- Use a bold, sans-serif font.
- Use a large font size that automatically adjusts to the available screen dimensions and message length.
- Keep the text readable at common desktop resolutions.
- Support long custom messages by reducing the font size as needed.
- Use the selected background and text colors.
- Optionally show a digital clock near the bottom center.
- Do not show unnecessary buttons, menus, or other controls in fullscreen mode.
- Prevent text from being clipped at the screen edges.

Suggested visual style:

    +----------------------------------------------+
    |                                              |
    |                                              |
    |              SEDANG SHOLAT                   |
    |                                              |
    |                    10:24                     |
    +----------------------------------------------+

The design should be minimal and professional, with no mandatory animations, images, or decorative elements.

### 3.3 Colors

Provide a small set of predefined background colors:

- Dark charcoal: `#101418`
- Dark green: `#07583D`
- Navy blue: `#173B78`
- Purple: `#43216B`
- Dark red: `#55231F`
- Slate: `#263548`

Default text color: `#FFFFFF`.

Ensure adequate contrast between the text and background.

## 4. Status Presets

Include these default statuses:

1. SEDANG SHOLAT
2. SEDANG MAKAN
3. SEDANG RAPAT
4. SEDANG ISTIRAHAT
5. SEDANG BEKERJA
6. SEDANG DINAS
7. SEDANG KE TOILET
8. SEDANG CEK LAPANGAN
9. SEDANG AMBIL DATA
10. JANGAN DIGANGGU

Store the preset definitions separately from the GUI code so they can be modified easily.

The user must be able to enter any custom message.

When a custom message is non-empty, display that message instead of the selected preset.

Trim leading and trailing whitespace. Do not allow an empty message to open the fullscreen window.

## 5. Fullscreen Controls

Implement predictable exit behavior:

- Pressing `ESC` closes the fullscreen window.
- Clicking `Stop` in the control window closes the fullscreen window.
- Closing the fullscreen window must not terminate the main application.
- Starting the display again should work without restarting the application.
- Prevent multiple fullscreen windows from being opened simultaneously.
- Restore focus to the control window when fullscreen mode closes, where practical.

Use Tkinter event bindings and clean up callbacks correctly.

Do not intercept or disable normal Windows keyboard shortcuts outside the application.

## 6. Digital Clock

The clock is optional and enabled through a checkbox.

Requirements:
- Display the current local system time in `HH:MM` format.
- Update once per second.
- Use Tkinter's `after()` mechanism instead of a blocking loop.
- Cancel or stop scheduled updates when the fullscreen window closes.
- Never use `time.sleep()` in the GUI event thread.

## 7. Configuration and Persistence

Save user preferences in a JSON configuration file.

Persist:
- Last selected status.
- Last custom message, if appropriate.
- Background color.
- Text color.
- Clock visibility.

Use a sensible per-user configuration directory, such as `%APPDATA%/StatusScreenSaver/`.

Do not save user preferences inside a temporary directory or a read-only installation directory.

Requirements:
- Create the configuration directory if it does not exist.
- Handle missing or malformed JSON gracefully.
- Use safe defaults when the configuration cannot be loaded.
- Do not crash when saving preferences fails.

The app must still work if no configuration file exists.

## 8. Multi-Monitor Behavior

For the first version, target the primary monitor only.

Keep the implementation structured so multi-monitor support can be added later.

Do not add complicated display enumeration dependencies for the MVP.

## 9. Project Structure

Use a clean, modular structure similar to:

    status-screen-saver/
    ├── main.py
    ├── presets.py
    ├── config.py
    ├── fullscreen.py
    ├── styles.py
    ├── requirements.txt
    ├── README.md
    └── .gitignore

Responsibilities:

- `main.py`: application entry point and main control window.
- `presets.py`: predefined status messages and color presets.
- `config.py`: loading and saving user preferences.
- `fullscreen.py`: fullscreen display, adaptive text sizing, clock, and exit behavior.
- `styles.py`: shared visual styling and color definitions.
- `requirements.txt`: only required third-party packages, if any.
- `README.md`: setup, usage, testing, and packaging instructions.
- `.gitignore`: ignore Python caches, virtual environments, build artifacts, and local configuration.

Keep the architecture simple. Do not overengineer the application.

## 10. Error Handling and Code Quality

Requirements:
- Use clear function and variable names.
- Add type hints where they improve clarity.
- Separate GUI, configuration, and fullscreen logic.
- Handle window closing and cleanup correctly.
- Avoid duplicated code.
- Avoid global mutable state when a simple class-based design is more appropriate.
- Use the standard Python logging module only where it adds practical value.
- Do not introduce unnecessary abstractions or design patterns.

Do not leave core functionality as TODO comments or placeholder implementations.

## 11. Windows Packaging

Provide instructions for creating a standalone Windows executable using PyInstaller.

Suggested command:

    pyinstaller --noconfirm --clean --windowed --name StatusScreenSaver main.py

Adjust the packaging configuration if additional files or resources are needed.

The application should not require administrator privileges.

Do not automatically modify the Windows registry, change system settings, or install a startup task.

If auto-start functionality is added in the future, make it optional and require explicit user action.

## 12. Testing and Acceptance Criteria

Before declaring the project complete, verify the following:

1. The main window launches successfully on Windows.
2. All predefined statuses are available.
3. A custom message can be entered and displayed.
4. Empty messages are rejected with a clear explanation.
5. The fullscreen window covers the primary monitor.
6. The text is centered and automatically resized to fit.
7. All predefined background colors work.
8. The optional clock updates correctly.
9. Pressing `ESC` closes fullscreen mode.
10. Clicking `Stop` closes fullscreen mode.
11. The main application remains open after fullscreen mode closes.
12. The user can start fullscreen mode repeatedly without errors.
13. Preferences persist after restarting the application.
14. Missing or malformed configuration files do not crash the app.
15. The application runs without an internet connection.
16. The application can be packaged as a standalone Windows executable.

Run any automated tests that can be implemented without requiring a graphical display, and document any tests that must be performed manually on Windows.

Do not claim Windows compatibility has been verified unless it has actually been tested on Windows.

## 13. Development Workflow

Follow this sequence:

1. Inspect the current project directory before modifying files.
2. Create the project structure and implement the complete MVP.
3. Implement the main control window and fullscreen behavior.
4. Implement configuration persistence and clock cleanup.
5. Run syntax checks and any practical automated tests.
6. Fix issues discovered during testing.
7. Write a clear Indonesian README with setup and usage instructions.
8. Explain how to run the app and package it into an executable.

Do not stop after producing a plan or mockup. Implement the working application.

If a requirement is ambiguous, choose the simplest sensible implementation and document the decision.

At completion, provide:
- A summary of implemented features.
- The final project file structure.
- Exact commands to run the application.
- Exact commands to package the application.
- Known limitations and manual testing instructions.

**Final objective:** Deliver a working, lightweight, maintainable Python desktop application for displaying large fullscreen office status messages on Windows 10/11.
