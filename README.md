# ByteAutoTheme

**Automatic light and dark mode switching for Windows 10 and Windows 11.**

ByteAutoTheme is a lightweight desktop utility built with Python and PySide6. It lets you switch Windows themes manually, at specific times, or according to local sunrise and sunset. It can also change wallpapers, apply `.theme` files, adjust display color temperature, and postpone automatic switches while you're busy.

> **Platform:** Windows 10 / Windows 11  
> **Interface languages:** English and Turkish  
> **Default behavior:** Manual switching; automation is optional.

## Features

### 🌗 Theme automation

- **Manual switching:** Change between light and dark mode instantly.
- **Time-based scheduling:** Set separate times for daytime and nighttime modes.
- **Sunrise/sunset scheduling:** Calculate local transition times for a selected city.
- **City lookup:** Common Turkish cities are available offline; other locations can be searched using the Open-Meteo geocoding API.
- **Independent targets:** Choose whether to switch the Windows interface, application theme, or both.

### 🎨 Personalization

- Assign different **wallpapers** for light and dark mode.
- Apply separate Windows **`.theme` files** when switching.
- Configure accent colors for **title bars/window borders** and the **taskbar**.
- Optionally adjust the **touch keyboard theme** and toggle Windows' selected **color filter** in dark mode.

### 🌡️ Display adjustments

- Set a fixed display color temperature or vary it automatically during the day.
- Configure day/night color temperatures, nighttime dimming, and smooth transition duration.
- Preview the 24-hour temperature profile in a built-in graph.
- Apply adjustments through Windows display gamma ramps, with restoration when the feature is disabled or the app exits normally.

> Display adjustments require a compatible graphics driver. HDR, Windows Night Light, and third-party color-management software may affect the result.

### 🎮 Intelligent switch protection

Automatic switching can be postponed when:

- **GPU usage** exceeds your configured threshold.
- **Selected applications** are running (for example, a game or recording software).
- **You are actively using the PC**, until the configured idle period has passed.

GPU monitoring uses Windows performance counters through PowerShell and may not be available on every system.

### ⚙️ Everyday convenience

- Runs in the background with an optional **system tray icon** and quick theme actions.
- Optional **start with Windows** and theme-switch notifications.
- **Single-instance behavior:** Running the app again brings its existing window forward.
- Compact six-tab interface with **English/Turkish language switching** and independent light/dark UI styling.
- Saves preferences in the Windows Registry; **no separate settings JSON file** is required.

## Requirements

- Windows 10 or Windows 11
- Python **3.10+ recommended** for running from source
- Python packages: `PySide6`, `psutil`, `astral`, `tzdata`
- `PyInstaller` (only if building the executable)

## Run from source

1. Download the source file and icon into the same folder.
2. Rename the Python file to **`Byte Auto Theme.py`** if it has a download suffix such as `(2)`.
3. Open PowerShell or Command Prompt in that folder and install the dependencies:

   ```powershell
   py -m pip install --upgrade PySide6 psutil astral tzdata
   ```

4. Launch the application:

   ```powershell
   py "Byte Auto Theme.py"
   ```

On Windows, the script attempts to relaunch itself through `pythonw.exe` so that a console window does not remain open.

## Build a standalone `.exe`

Install PyInstaller:

```powershell
py -m pip install --upgrade pyinstaller
```

From the project folder, run:

```powershell
py -m PyInstaller --noconfirm --clean --onefile --windowed --name "ByteAutoTheme" --icon "ByteAutoTheme.ico" --collect-all tzdata --collect-all astral "Byte Auto Theme.py"
```

The generated executable will be located at:

```text
dist\ByteAutoTheme.exe
```

The `--windowed` option hides the console window. The `--onefile` option packages the application into a single executable. To use a different source filename, update the last argument of the build command accordingly.

## Getting started

1. Open **Quick Settings** to apply light or dark mode immediately.
2. Open **Automation** and choose **Manual**, **Time Range**, or **Sunrise / Sunset**.
3. For sunrise/sunset mode, search for and select your city.
4. Use **Personalization** to choose which Windows components to change and optionally assign wallpapers or `.theme` files.
5. Use **Screen** to enable display color temperature and dimming adjustments.
6. Use **Conditions** to avoid interruptions during gaming, selected apps, or active use.
7. In **General**, configure startup, notifications, and tray visibility.

Changes are saved automatically.

## Settings and behavior

Application preferences are stored at:

```text
HKEY_CURRENT_USER\Software\ByteAutoTheme
```

Windows-specific changes are applied through the current user's theme/personalization settings and the relevant Windows APIs. Enabling **Start with Windows** adds an entry under:

```text
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
```

Closing the window normally keeps ByteAutoTheme running in the background. Use **Exit Completely** in the application or tray menu to quit.

## Notes and limitations

- **Windows only:** Windows theme switching and display gamma controls use Windows APIs.
- **Optional internet access:** City lookup outside the bundled Turkish city list contacts the Open-Meteo geocoding service. Sunrise/sunset calculations themselves run locally using `astral` once location information is available.
- **GPU monitoring:** The GPU-usage condition depends on Windows GPU performance counters; if they are unavailable, that protection can prevent automatic switching until disabled.
- **Display compatibility:** Gamma-ramp adjustments may be unsupported or overridden by HDR, Night Light, or graphics utilities.
- **Theme file behavior:** Applying a `.theme` file delegates to Windows and may alter other personalization settings.
- **System tray:** If the tray icon is hidden, launch the application again to reopen the existing window.

## Technology stack

| Component | Purpose |
| --- | --- |
| Python | Application logic and Windows integration |
| PySide6 (Qt) | Desktop interface, tray, threading, and networking |
| psutil | Running-process detection |
| astral + tzdata | Sunrise/sunset calculations and time zones |
| Windows Registry / Win32 APIs | Theme, startup, and display integration |
| PyInstaller | Optional Windows executable packaging |

## Project files

```text
ByteAutoTheme/
├── Byte Auto Theme.py
├── ByteAutoTheme.ico
└── README.md
```

---

**ByteAutoTheme** — a customizable way to keep your Windows desktop in sync with your day.
