# 🌗 ByteAutoTheme

**Automatic light and dark mode switching**

ByteAutoTheme makes it easy to keep your Windows desktop comfortable throughout the day. Switch between light and dark mode whenever you want, set your own schedule, or let the app follow sunrise and sunset in your city.

You can also change wallpapers, adjust screen colors, and prevent theme changes from interrupting games or other activities — all from a simple desktop app.

## ✨ Features

- **Automatic theme switching** — Choose specific times or use local sunrise and sunset. Manual switching is always available.
- **Customize what changes** — Control Windows and app themes separately, with optional accent colors, touch keyboard settings, and color filters.
- **Light and dark wallpapers** — Pick a different wallpaper for each mode and apply it across connected monitors.
- **Windows theme files** — Use your own `.theme` files for a more personalized setup.
- **Comfortable screen colors** — Adjust color temperature and dimming for daytime or nighttime, with smooth transitions and a daily preview graph.
- **Per-monitor adjustments** — Detect connected displays and set individual color temperature adjustments, dimming, and RGB tint levels for each supported monitor.
- **Smart pause options** — Delay automatic switches while certain apps are running, GPU usage is high, or you're actively using your PC.
- **Runs in the background** — Access quick actions from the system tray, launch with Windows, and enable optional notifications.
- **English and Turkish interface** — Choose your preferred language and app appearance.

## 💻 Requirements

- **Windows 10 or Windows 11**
- **Python 3.10 or newer** if running the source code
- An internet connection is only needed when searching for cities not included in the app's built-in list.

## 🚀 Getting Started

### Download Windows executable from releases (optional)

### Run from source

1. Download this repository using **Code → Download ZIP**, then extract it to a folder.
2. Install [Python](https://www.python.org/downloads/) if you don't already have it.
3. Open **PowerShell** or **Command Prompt** in the extracted folder.
4. Install the required packages and then run the py script.
   py -m pip install PySide6 psutil astral tzdata

The project includes the Python application and its icon. No separate configuration file is needed.

### Build a Windows executable (optional)

If you prefer a standalone `.exe`, you can build one from the source:

```
py -m pip install pyinstaller
py -m PyInstaller --noconfirm --clean --onefile --windowed --name "ByteAutoTheme" --icon "ByteAutoTheme.ico" --collect-all tzdata --collect-all astral "Byte Auto Theme.py"
```

Your executable will be created at **`dist\ByteAutoTheme.exe`**.

## 🛠️ How to Use

Once ByteAutoTheme is open, you'll find six main sections:

| Section | What it does |
| --- | --- |
| **Quick Settings** | Switch between light and dark mode instantly. |
| **Automation** | Choose manual, scheduled, or sunrise/sunset switching. |
| **Conditions** | Pause automatic changes while gaming, using selected apps, or actively working. |
| **Personalization** | Choose wallpapers, Windows themes, and system appearance options. |
| **Screen** | Set screen warmth, dimming, and individual monitor color adjustments. |
| **General** | Manage startup, notifications, language, and system tray behavior. |

**A simple setup:** Open **Automation**, choose **Sunrise / Sunset**, and select your city. Then visit **Personalization** to choose what should change when the mode switches. You can enable screen adjustments separately in **Screen**.

Your preferences are saved automatically.

## 📌 Good to Know

- **Closing the window doesn't exit the app.** ByteAutoTheme continues running in the background. Use **Exit Completely** from the app or system tray when you want to stop it.
- **Multi-monitor color controls depend on your hardware.** HDR, mirrored displays, some graphics drivers, or Windows Night Light may limit independent color adjustments.
- **Sunrise and sunset times** are calculated for your selected city. Common Turkish cities are available offline; searching for other cities may require internet access.
- **Settings are stored locally** in your Windows user settings. No account or cloud service is required for normal use.

## 🤝 Feedback and Contributions

Found a bug or have an idea for an improvement? Feel free to [open an issue](https://github.com/EgeGurkan/ByteAutoTheme/issues). Suggestions and contributions are welcome.
