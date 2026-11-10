# -*- coding: utf-8 -*-
"""ByteAutoTheme | Windows 10/11 | PySide6 + psutil + astral + tzdata.

All application preferences: HKCU\\Software\\ByteAutoTheme.
There is no settings JSON, backup subsystem, extra launcher, or console window
when launched with pythonw.exe / a PyInstaller --windowed executable.
"""
from __future__ import annotations

import ctypes
import datetime as datetime
import json
import math
import os
import re
import subprocess
import sys
import time
import unicodedata
import uuid
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo

# Support #
# Update Python # py -m pip install --upgrade pip
# Install Components # py -m pip install --upgrade PySide6 psutil astral tzdata pyinstaller
# Compile # py -m PyInstaller --noconfirm --clean --onefile --windowed --name "ByteAutoTheme" --icon "ByteAutoTheme.ICO" --collect-all tzdata --collect-all astral "Byte Auto Theme.py"

import psutil
from astral import LocationInfo
from astral.sun import sun
from PySide6.QtCore import Qt, QLocale, QThread, QTime, QTimer, QUrl, Signal
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtNetwork import QLocalServer, QLocalSocket, QNetworkAccessManager, QNetworkRequest
from PySide6.QtWidgets import (
    QApplication, QButtonGroup, QCheckBox, QComboBox, QColorDialog, QDialog, QFileDialog, QScrollArea,
    QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QMenu, QProgressBar, QPushButton, QSlider, QSpinBox, QStackedWidget,
    QSystemTrayIcon, QTimeEdit, QVBoxLayout, QWidget,
)

WINDOWS = sys.platform == "win32"
if WINDOWS:
    import winreg

APP = "ByteAutoTheme"
SETTINGS_KEY = r"Software\ByteAutoTheme"
PERSONALIZE = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
DWM = r"Software\Microsoft\Windows\DWM"
TOUCH = r"Software\Microsoft\TabletTip\1.7"
COLOR_FILTER = r"Software\Microsoft\ColorFiltering"
STARTUP_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"

DEFAULTS = {
    "schedule_kind": "manual", "light_time": "07:00", "dark_time": "19:00",
    "city": "", "city_confirmed": False, "latitude": 41.0082,
    "longitude": 28.9784, "timezone": "Europe/Istanbul",
    "windows_mode": True, "app_mode": True, "title_accent": False,
    "taskbar_accent": False, "touch_theme": False, "color_filter": False,
    "wallpaper_enabled": False, "wallpaper_light": "", "wallpaper_dark": "",
    "theme_enabled": False, "theme_light": "", "theme_dark": "",
    "game_guard": False, "gpu_threshold": 30, "gpu_interval": 6,
    "apps_guard": False, "blocked_apps": "", "idle_guard": False,
    "idle_minutes": 5, "startup": False, "notify": True,
    "hide_tray": False, "language": "system", "ui_theme": "auto",
    "screen_enabled": False, "screen_auto": True,
    "screen_day_kelvin": 6500, "screen_night_kelvin": 3800,
    "screen_manual_kelvin": 4500, "screen_night_dim": 12,
    "screen_transition": 90, "screen_follow_theme": True,
    "monitor_profiles": "{}",
}

# Explicit local matches work without networking, including dotted/dotless I.
TR_CITIES = {
    "istanbul": ("İstanbul", 41.0082, 28.9784),
    "ankara": ("Ankara", 39.9334, 32.8597),
    "izmir": ("İzmir", 38.4237, 27.1428),
    "bursa": ("Bursa", 40.1885, 29.0610),
    "antalya": ("Antalya", 36.8969, 30.7133),
    "adana": ("Adana", 37.0000, 35.3213),
    "konya": ("Konya", 37.8746, 32.4932),
    "gaziantep": ("Gaziantep", 37.0662, 37.3833),
    "mersin": ("Mersin", 36.8121, 34.6415),
    "kayseri": ("Kayseri", 38.7225, 35.4875),
    "eskisehir": ("Eskişehir", 39.7667, 30.5256),
    "diyarbakir": ("Diyarbakır", 37.9144, 40.2306),
    "samsun": ("Samsun", 41.2867, 36.3300),
    "trabzon": ("Trabzon", 41.0027, 39.7168),
    "erzurum": ("Erzurum", 39.9043, 41.2679),
    "malatya": ("Malatya", 38.3552, 38.3095),
    "sakarya": ("Sakarya", 40.7569, 30.3781),
    "kocaeli": ("Kocaeli", 40.7654, 29.9408),
    "tekirdag": ("Tekirdağ", 40.9781, 27.5117),
    "edirne": ("Edirne", 41.6772, 26.5559),
    "hatay": ("Hatay", 36.2021, 36.1602),
    "denizli": ("Denizli", 37.7765, 29.0864),
    "mugla": ("Muğla", 37.2153, 28.3636),
    "balikesir": ("Balıkesir", 39.6484, 27.8826),
    "manisa": ("Manisa", 38.6191, 27.4289),
    "ordu": ("Ordu", 40.9862, 37.8797),
    "rize": ("Rize", 41.0201, 40.5234),
    "van": ("Van", 38.4891, 43.4089),
    "sanliurfa": ("Şanlıurfa", 37.1674, 38.7955),
    "kahramanmaras": ("Kahramanmaraş", 37.5753, 36.9228),
    "afyonkarahisar": ("Afyonkarahisar", 38.7569, 30.5387),
    "canakkale": ("Çanakkale", 40.1467, 26.4086),
    "kutahya": ("Kütahya", 39.4242, 29.9833),
    "usak": ("Uşak", 38.6823, 29.4082),
    "bolu": ("Bolu", 40.7395, 31.6116),
    "zonguldak": ("Zonguldak", 41.4564, 31.7987),
    "amasya": ("Amasya", 40.6539, 35.8330),
    "tokat": ("Tokat", 40.3167, 36.5500),
    "corum": ("Çorum", 40.5489, 34.9533),
    "sivas": ("Sivas", 39.7500, 37.0167),
    "elazig": ("Elazığ", 38.6743, 39.2232),
    "kars": ("Kars", 40.6013, 43.0975),
    "igdir": ("Iğdır", 39.9208, 44.0440),
    "yalova": ("Yalova", 40.6550, 29.2769),
}

# Translation keys are unique to the UI; no numbered/duplicated headings.
TEXT = {
    "quick": ("Hızlı Ayarlar", "Quick Settings"),
    "automation": ("Otomasyon", "Automation"),
    "personalization": ("Kişiselleştirme", "Personalization"),
    "system": ("Sistem Alanları", "System Areas"),
    "conditions": ("Geçiş Koşulları", "Conditions"),
    "general": ("Genel", "General"),
    "screen": ("Ekran", "Screen"),
    "system_heading": ("Sistem Alanları", "System Areas"),
    "short_windows_mode": ("Windows modu", "Windows mode"),
    "short_app_mode": ("Uygulama modu", "App mode"),
    "short_title_accent": ("Başlık / kenarlık rengi", "Title / border accent"),
    "short_taskbar_accent": ("Görev çubuğu rengi", "Taskbar accent"),
    "short_touch_theme": ("Dokunmatik klavye", "Touch keyboard"),
    "short_color_filter": ("Renk filtresi", "Color filter"),
    "screen_enabled": ("Ekran rengini ayarla", "Adjust screen colors"),
    "screen_auto": ("Gün boyunca otomatik değiştir", "Change automatically through the day"),
    "screen_follow_theme": ("Açık/koyu tema ile ekran renklerini eşitle", "Synchronize screen colors with light/dark theme"),
    "monitor_options": ("Monitöre Özel Renk Ayarları…", "Per-Monitor Color Settings…"),
    "monitor_choose": ("Bağlı ekran", "Connected display"),
    "monitor_enabled": ("Bu monitöre renk düzeltmesi uygula", "Apply color correction to this monitor"),
    "monitor_offset": ("Sıcaklık farkı", "Temperature adjustment"),
    "monitor_dim": ("Ek karartma", "Additional dimming"),
    "monitor_red": ("Kırmızı seviyesi", "Red level"),
    "monitor_green": ("Yeşil seviyesi", "Green level"),
    "monitor_blue": ("Mavi seviyesi", "Blue level"),
    "monitor_pick": ("Monitöre renk tonu seç…", "Choose display tint…"),
    "monitor_reset": ("Monitör ayarlarını sıfırla", "Reset display settings"),
    "monitor_close": ("Kapat", "Close"),
    "monitor_empty": ("Bağlı monitör bulunamadı", "No connected display found"),
    "monitor_note": ("Ayarlar seçili ekrana özeldir ve kayıtlı kalır. RGB seviyeleri en fazla %100'dür. HDR, klonlama veya bazı sürücüler bağımsız renk düzeltmesini desteklemeyebilir.",
                     "Settings apply only to the selected display and are saved. RGB levels are at most 100%. HDR, mirrored displays, and some drivers may not support independent correction."),

    "screen_day_kelvin": ("Gündüz sıcaklığı", "Daytime temperature"),
    "screen_night_kelvin": ("Gece sıcaklığı", "Nighttime temperature"),
    "screen_manual_kelvin": ("Sabit sıcaklık", "Fixed temperature"),
    "screen_night_dim": ("Ekran karartma", "Screen dimming"),
    "screen_transition": ("Yumuşak geçiş", "Smooth transition"),
    "screen_now": ("Şimdi: {temp} K · %{dim} karartma", "Now: {temp} K · {dim}% dimming"),
    "screen_off": ("Ekran ayarı kapalı", "Screen adjustment off"),
    "screen_unavailable": ("Ekranların renk ayarı uygulanamadı (HDR veya sürücü kısıtı olabilir)",
                           "Could not adjust displays (HDR or driver restriction may apply)"),
    "screen_monitors": ("Monitörler: {ok}/{total}", "Monitors: {ok}/{total}"),
    "screen_partial": ("Uygulanamayan: {names}", "Not applied: {names}"),
    "screen_note": ("Şehir seçiliyse güneş saatleri, değilse gündüz/gece saatleri kullanılır. HDR veya Gece Işığı etkileyebilir.",
                    "Uses sunrise/sunset when a city is set; otherwise day/night times. HDR or Night light may interfere."),
    "system_ui": ("Sistem temasını izle", "Follow system theme"),
    "light_ui": ("Açık arayüz", "Light interface"),
    "dark_ui": ("Koyu arayüz", "Dark interface"),
    "dark": ("☾  Koyu Mod", "☾  Dark Mode"),
    "light": ("☀  Açık Mod", "☀  Light Mode"),
    "open_windows": ("Windows Kişiselleştirme", "Windows Personalization"),
    "current": ("Windows uygulama teması: {mode}", "Windows app theme: {mode}"),
    "light_word": ("Açık", "Light"),
    "dark_word": ("Koyu", "Dark"),
    "schedule": ("Zamanlama", "Schedule"),
    "manual": ("Manuel", "Manual"),
    "time": ("Saat aralığı", "Time range"),
    "sun": ("Gün doğumu / gün batımı", "Sunrise / sunset"),
    "light_start": ("Gündüz başlangıcı", "Day starts"),
    "dark_start": ("Gece başlangıcı", "Night starts"),
    "city_search": ("Şehir ara", "Search city"),
    "search": ("Ara", "Search"),
    "solar_empty": ("Güneş saatleri için şehir seç.", "Select a city for sunrise and sunset."),
    "solar_result": ("Doğuş {rise}  ·  Batış {set}", "Sunrise {rise}  ·  Sunset {set}"),
    "solar_failed": ("Güneş saatleri hesaplanamadı.", "Sunrise/sunset could not be calculated."),
    "wallpaper_enabled": ("Masaüstü arka planını değiştir", "Change desktop wallpaper"),
    "wall_light": ("Açık arka plan", "Light wallpaper"),
    "wall_dark": ("Koyu arka plan", "Dark wallpaper"),
    "theme_enabled": ("Windows tema dosyası kullan (.theme)", "Use Windows theme files (.theme)"),
    "theme_light": ("Açık tema", "Light theme"),
    "theme_dark": ("Koyu tema", "Dark theme"),
    "windows_mode": ("Windows modu (Başlat, görev çubuğu)", "Windows mode (Start, taskbar)"),
    "app_mode": ("Uygulama modu", "App mode"),
    "title_accent": ("Başlık ve pencere kenarlığı vurgu rengi", "Accent on title bars and borders"),
    "taskbar_accent": ("Görev çubuğu vurgu rengi", "Taskbar accent color"),
    "touch_theme": ("Dokunmatik klavye ve giriş teması", "Touch keyboard and input theme"),
    "color_filter": ("Koyu modda renk filtresi", "Color filter in dark mode"),
    "system_tip": ("Renk filtresi Windows'ta seçili filtreyi kullanır.", "Color filter uses the selected Windows filter."),
    "game_guard": ("Yüksek GPU kullanımında geçiş yapma", "Pause switches during high GPU use"),
    "gpu_threshold": ("GPU eşiği", "GPU threshold"),
    "gpu_interval": ("Örnekleme", "Sampling"),
    "gpu_idle": ("GPU izleme kapalı", "GPU monitoring off"),
    "gpu_wait": ("GPU ölçümü bekleniyor", "Waiting for GPU reading"),
    "gpu_unavailable": ("GPU sayacı kullanılamıyor", "GPU counter unavailable"),
    "apps_guard": ("Seçili uygulamalar açıkken geçiş yapma", "Pause while selected apps are running"),
    "apps_hint": ("game.exe, obs64.exe", "game.exe, obs64.exe"),
    "add_app": ("Uygulama Ekle", "Add App"),
    "idle_guard": ("Kullanıcı aktifken geçiş yapma", "Pause while user is active"),
    "idle_minutes": ("Boşta kalma süresi", "Idle time"),
    "startup": ("Windows ile başlat", "Start with Windows"),
    "notify": ("Tema geçişinde bildirim göster", "Notify on theme change"),
    "hide_tray": ("Sistem tepsisi simgesini gizle", "Hide system tray icon"),
    "tray_tip": ("Kapatınca arka planda çalışır. Gizliyken yeniden açmak için programı çalıştır.",
                 "Closing keeps it running. Launch the app again to show its window."),
    "quit": ("Tamamen Çık", "Exit Completely"),
    "ready": ("Hazır", "Ready"),
    "saved": ("Ayarlar kaydedildi", "Settings saved"),
    "applied": ("{mode} mod uygulandı", "{mode} mode applied"),
    "paused": ("Geçiş bekletildi: {reason}", "Switch postponed: {reason}"),
    "blocked_gpu": ("GPU %{value} (eşik %{threshold})", "GPU {value}% (threshold {threshold}%)"),
    "blocked_app": ("Açık: {apps}", "Running: {apps}"),
    "blocked_idle": ("Kullanıcı aktif", "User active"),
    "city_found": ("Şehir seçildi: {city}", "City selected: {city}"),
    "city_not_found": ("Şehir bulunamadı", "City not found"),
    "city_failed": ("Şehir aranamadı", "Could not search city"),
    "invalid_file": ("Seçilen dosya bulunamadı", "Selected file not found"),
    "apply_failed": ("Tema uygulanamadı", "Could not apply theme"),
    "windows_only": ("Windows 10/11 gerekli", "Requires Windows 10/11"),
    "tray_show": ("Pencereyi Aç", "Show Window"),
    "tray_dark": ("Koyu Mod", "Dark Mode"),
    "tray_light": ("Açık Mod", "Light Mode"),
    "choose_image": ("Görsel Seç", "Choose Image"),
    "choose_theme": ("Windows Teması Seç", "Choose Windows Theme"),
    "choose_exe": ("Uygulama Seç", "Choose Application"),
    "no_file": ("Dosya seçilmedi", "No file selected"),
}


def registry_get(key: str, name: str, default=None):
    if not WINDOWS:
        return default
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key) as handle:
            return winreg.QueryValueEx(handle, name)[0]
    except OSError:
        return default


def registry_set(key: str, values: dict):
    if not WINDOWS or not values:
        return
    with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_SET_VALUE) as handle:
        for name, value in values.items():
            typ = winreg.REG_DWORD if isinstance(value, (bool, int)) else winreg.REG_SZ
            winreg.SetValueEx(handle, name, 0, typ, int(value) if typ == winreg.REG_DWORD else str(value))


def load_settings():
    data = DEFAULTS.copy()
    for key, original in DEFAULTS.items():
        value = registry_get(SETTINGS_KEY, key, original)
        try:
            if isinstance(original, bool):
                data[key] = bool(int(value))
            elif isinstance(original, int):
                data[key] = int(value)
            elif isinstance(original, float):
                data[key] = float(value)
            else:
                data[key] = str(value)
        except (ValueError, TypeError):
            pass
    # Map settings written by previous versions; keep a single stable state.
    data["schedule_kind"] = {
        "Manuel": "manual", "Saat aralığı": "time",
        "Gün doğumu / gün batımı": "sun",
    }.get(data["schedule_kind"], data["schedule_kind"])
    if data["schedule_kind"] not in ("manual", "time", "sun"):
        data["schedule_kind"] = "manual"
    for key, low, high in (("screen_day_kelvin", 4500, 7500),
                           ("screen_night_kelvin", 2700, 5500),
                           ("screen_manual_kelvin", 2700, 7500),
                           ("screen_night_dim", 0, 30),
                           ("screen_transition", 15, 180)):
        data[key] = max(low, min(high, data[key]))
    if data["ui_theme"] not in ("auto", "light", "dark"):
        data["ui_theme"] = "auto"
    if data["language"] not in ("system", "tr", "en"):
        data["language"] = "system"
    if data["city"].strip() == "İstanbul (örnek)":
        data["city"], data["city_confirmed"] = "", False
    return data


def norm_city(city):
    city = city.split(",", 1)[0].strip().casefold().replace("ı", "i")
    return "".join(c for c in unicodedata.normalize("NFKD", city)
                   if not unicodedata.combining(c))


def windows_dark():
    try:
        return int(registry_get(PERSONALIZE, "AppsUseLightTheme", 1)) == 0
    except (ValueError, TypeError):
        return False


def notify_windows():
    if not WINDOWS:
        return
    result = ctypes.c_size_t()
    for setting in ("ImmersiveColorSet", "WindowsThemeElement", "ColorFiltering"):
        ctypes.windll.user32.SendMessageTimeoutW(
            0xFFFF, 0x001A, 0, ctypes.c_wchar_p(setting), 0x0002, 350,
            ctypes.byref(result))


def set_wallpaper_all_monitors(path):
    """Windows 10/11: assign one wallpaper to *every* connected monitor.

    SPI_SETDESKWALLPAPER is legacy and can leave secondary wallpapers unchanged
    if Windows is using per-monitor wallpapers. IDesktopWallpaper explicitly
    targets every monitor when its monitorID parameter is NULL.
    """
    if not WINDOWS:
        return False

    class GUID(ctypes.Structure):
        _fields_ = [("Data1", ctypes.c_uint32), ("Data2", ctypes.c_uint16),
                    ("Data3", ctypes.c_uint16), ("Data4", ctypes.c_ubyte * 8)]

    def make_guid(value):
        return GUID.from_buffer_copy(uuid.UUID(value).bytes_le)

    ole32 = ctypes.WinDLL("ole32")
    ole32.CoInitializeEx.argtypes = [ctypes.c_void_p, ctypes.c_uint]
    ole32.CoInitializeEx.restype = ctypes.c_long
    ole32.CoCreateInstance.argtypes = [ctypes.POINTER(GUID), ctypes.c_void_p,
                                      ctypes.c_uint, ctypes.POINTER(GUID),
                                      ctypes.POINTER(ctypes.c_void_p)]
    ole32.CoCreateInstance.restype = ctypes.c_long
    ole32.CoUninitialize.argtypes = []
    ole32.CoUninitialize.restype = None

    initialized = ole32.CoInitializeEx(None, 2)  # COINIT_APARTMENTTHREADED
    # RPC_E_CHANGED_MODE means another library already initialized COM as MTA.
    if initialized not in (0, 1, -2147417850):
        return False
    instance = ctypes.c_void_p()
    try:
        clsid = make_guid("C2CF3110-460E-4FC1-B9D0-8A1C0C9CC4BD")
        iid = make_guid("B92B56A9-8B55-4E14-9A89-0199BBB6F93B")
        hr = ole32.CoCreateInstance(ctypes.byref(clsid), None,
                                    4,  # CLSCTX_LOCAL_SERVER
                                    ctypes.byref(iid), ctypes.byref(instance))
        if hr != 0 or not instance.value:
            return False
        vtable = ctypes.cast(instance, ctypes.POINTER(
            ctypes.POINTER(ctypes.c_void_p))).contents
        set_wallpaper = ctypes.WINFUNCTYPE(
            ctypes.c_long, ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_wchar_p)(vtable[3])
        return set_wallpaper(instance, None, str(Path(path).resolve())) == 0
    finally:
        if instance.value:
            vtable = ctypes.cast(instance, ctypes.POINTER(
                ctypes.POINTER(ctypes.c_void_p))).contents
            release = ctypes.WINFUNCTYPE(ctypes.c_ulong, ctypes.c_void_p)(vtable[2])
            release(instance)
        if initialized in (0, 1):
            ole32.CoUninitialize()


def set_color_filter(enabled):
    # Windows does not reliably activate color filters with a registry write alone.
    old = registry_get(COLOR_FILTER, "Active", 0)
    if not WINDOWS or bool(old) == enabled:
        return
    previous_hotkey = registry_get(COLOR_FILTER, "HotkeyEnabled", 0)
    try:
        registry_set(COLOR_FILTER, {"HotkeyEnabled": 1})
        user32 = ctypes.windll.user32
        for code in (0x5B, 0x11, 0x43):  # Windows + Ctrl + C
            user32.keybd_event(code, 0, 0, 0)
        for code in (0x43, 0x11, 0x5B):
            user32.keybd_event(code, 0, 2, 0)
        time.sleep(0.12)
        if bool(registry_get(COLOR_FILTER, "Active", 0)) != enabled:
            registry_set(COLOR_FILTER, {"Active": int(enabled)})
    finally:
        registry_set(COLOR_FILTER, {"HotkeyEnabled": int(previous_hotkey)})


def idle_seconds():
    if not WINDOWS:
        return 0

    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

    info = LASTINPUTINFO(ctypes.sizeof(LASTINPUTINFO), 0)
    if not ctypes.windll.user32.GetLastInputInfo(ctypes.byref(info)):
        return 0
    return ((ctypes.windll.kernel32.GetTickCount() - info.dwTime) & 0xFFFFFFFF) / 1000


def running_blocked_apps(raw):
    names = {Path(x.strip().strip('"')).name.casefold()
             for x in re.split(r"[,;\n]+", raw) if x.strip()}
    if not names:
        return []
    matches = set()
    for process in psutil.process_iter(["name"]):
        try:
            name = (process.info.get("name") or "").casefold()
            if name in names:
                matches.add(name)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return sorted(matches)


def gpu_usage():
    if not WINDOWS:
        return None
    cmd = (
        "$ErrorActionPreference='Stop';"
        "Get-CimInstance Win32_PerfFormattedData_GPUPerformanceCounters_GPUEngine "
        "| Select-Object Name,UtilizationPercentage | ConvertTo-Json -Compress"
    )
    try:
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", cmd],
            text=True, encoding="utf-8", errors="replace", capture_output=True,
            timeout=8, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if result.returncode or not result.stdout.strip():
            return None
        values = json.loads(result.stdout)
        if isinstance(values, dict):
            values = [values]
        engines = {}
        for item in values:
            name = str(item.get("Name", ""))
            match = re.search(r"(luid_[^_]+_[^_]+_phys_\d+_eng_\d+)_engtype_", name, re.I)
            if not match:
                continue
            try:
                utilization = max(0.0, float(item["UtilizationPercentage"]))
            except (KeyError, ValueError, TypeError):
                continue
            key = match.group(1)
            engines[key] = engines.get(key, 0.0) + utilization
        return round(min(100.0, max(engines.values())), 1) if engines else None
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None


class GPUWorker(QThread):
    measurement = Signal(object)

    def __init__(self):
        super().__init__()
        self.enabled = False
        self.interval = 6

    def run(self):
        while not self.isInterruptionRequested():
            if self.enabled:
                self.measurement.emit(gpu_usage())
            duration = self.interval if self.enabled else 1
            for _ in range(duration * 10):
                if self.isInterruptionRequested():
                    return
                self.msleep(100)


def app_icon():
    """Draw a complete, inset moon mark at every Windows icon size."""
    icon = QIcon()
    for size in (16, 20, 24, 32, 40, 48, 64, 128, 256):
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.scale(size / 64, size / 64)
        painter.setPen(Qt.NoPen)
        # All shapes stay inside the 64×64 virtual canvas, including their edges.
        painter.setBrush(QColor("#17202c"))
        painter.drawEllipse(7, 7, 50, 50)
        painter.setBrush(QColor("#edaa54"))
        painter.drawEllipse(9, 9, 46, 46)
        painter.setBrush(QColor("#17202c"))
        painter.drawEllipse(21, 9, 34, 36)
        painter.setBrush(QColor("#f6d599"))
        painter.drawEllipse(14, 17, 4, 4)
        painter.end()
        icon.addPixmap(pixmap)
    return icon


def stylesheet(dark):
    palette = ({
        "bg": "#0d1119", "card": "#161e2a", "text": "#e8f0fb", "muted": "#a2b4c8",
        "edge": "#324052", "input": "#212d3c", "hover": "#2b3a4c",
        "primary": "#39b8bc", "primary_text": "#07171c", "tab": "#1b2634",
        "selected": "#324b5c", "positive": "#e6a257",
    } if dark else {
        "bg": "#f4f7fb", "card": "#ffffff", "text": "#233548", "muted": "#64788d",
        "edge": "#c8d5e3", "input": "#f9fbff", "hover": "#e2edf7",
        "primary": "#138d9c", "primary_text": "#ffffff", "tab": "#e8eff6",
        "selected": "#c8e8ed", "positive": "#b46a22",
    })
    c = palette
    return f"""
        QWidget {{ background: {c['bg']}; color: {c['text']}; font: 9pt 'Segoe UI'; }}
        QMainWindow {{ background: {c['bg']}; }}
        QFrame#panel {{ background: {c['card']}; border: 1px solid {c['edge']}; border-radius: 9px; }}
        QLabel, QCheckBox {{ background: transparent; }}
        QLabel#title {{ font-size: 15pt; font-weight: 750; }}
        QLabel#hint {{ color: {c['muted']}; font-size: 8.5pt; }}
        QLabel#status {{ color: {c['muted']}; font-size: 8.5pt; }}
        QCheckBox {{ spacing: 8px; padding: 4px 1px; }}
        QCheckBox::indicator {{ width: 16px; height: 16px; border-radius: 4px;
                             background: {c['input']}; border: 1px solid {c['edge']}; }}
        QCheckBox::indicator:checked {{ background: {c['primary']}; border: 1px solid {c['primary']}; }}
        QLineEdit, QTimeEdit, QSpinBox, QComboBox {{
            background: {c['input']}; border: 1px solid {c['edge']}; border-radius: 6px;
            padding: 6px 8px; min-height: 19px;
        }}
        QComboBox::drop-down {{ border: none; width: 22px; }}
        QComboBox QAbstractItemView {{ background: {c['card']};
                                      selection-background-color: {c['selected']}; }}
        QPushButton {{ background: {c['tab']}; border: 1px solid {c['edge']};
                       border-radius: 6px; padding: 7px 10px; font-weight: 600; }}
        QPushButton:hover {{ background: {c['hover']}; }}
        QPushButton:checked {{ background: {c['selected']}; border-color: {c['primary']}; }}
        QPushButton#nav {{ border-radius: 6px; padding: 8px 3px; }}
        QPushButton#nav:checked {{ background: {c['selected']}; border-color: {c['primary']}; }}
        QPushButton#primary {{ background: {c['primary']}; color: {c['primary_text']}; border-color: {c['primary']}; }}
        QPushButton#primary:hover {{ background: {c['hover']}; color: {c['text']}; }}
        QPushButton#danger {{ color: {c['positive']}; }}
        QPushButton#mini {{ padding: 5px 7px; min-width: 21px; }}
        QProgressBar {{ background: {c['input']}; border: 1px solid {c['edge']};
                        border-radius: 4px; min-height: 9px; max-height: 9px; text-align: center; }}
        QProgressBar::chunk {{ background: {c['primary']}; border-radius: 4px; }}
        QSlider::groove:horizontal {{ background: {c['edge']}; height: 6px; border-radius: 3px; }}
        QSlider::sub-page:horizontal {{ background: {c['primary']}; border-radius: 3px; }}
        QSlider::handle:horizontal {{ background: {c['primary']}; width: 13px;
                                      margin: -5px 0; border-radius: 6px; }}
        QToolTip {{ background: {c['card']}; color: {c['text']}; border: 1px solid {c['edge']}; }}
    """


def kelvin_rgb(kelvin):
    """Approximate RGB proportions for a black-body white point."""
    t = max(1900.0, min(7500.0, float(kelvin))) / 100.0
    r = 255.0 if t <= 66 else 329.698727446 * ((t - 60) ** -0.1332047592)
    g = (99.4708025861 * math.log(t) - 161.1195681661) if t <= 66 else (288.1221695283 * (t - 60) ** -0.0755148492)
    b = (0.0 if t <= 19 else 138.5177312231 * math.log(t - 10) - 305.0447927307) if t <= 66 else 255.0
    return tuple(max(0.0, min(1.0, c / 255.0)) for c in (r, g, b))


def daylight_weight(hour, sunrise, sunset, transition_minutes):
    """0 at night, 1 at noon; smooths both boundaries over N minutes."""
    width = max(15, transition_minutes) / 60.0

    def smoothstep(value):
        v = max(0.0, min(1.0, value))
        return v * v * (3 - 2 * v)

    morning = smoothstep((hour - sunrise) / width + 0.5)
    evening = 1.0 - smoothstep((hour - sunset) / width + 0.5)
    return max(0.0, min(1.0, morning * evening))


class DisplayGamma:
    """Apply/restore a gamma LUT independently for every active Windows display.

    Windows can reset gamma ramps when a theme, driver, HDR mode or monitor
    topology changes. The active display list and current ramps are checked on
    each update instead of relying on one cached, potentially stale DC.

    Windows/GDI drivers can refuse or silently ignore gamma changes, notably
    with HDR. Read-back is best-effort verification, not a hardware guarantee.
    """

    # Tolerance for display-driver quantization of 16-bit LUT entries.
    READBACK_TOLERANCE = 1024

    def __init__(self):
        self.displays = {}       # logical display name -> {dc, original}
        self.targets = {}        # logical display name -> {rect, id, label}
        self.profile_for_monitor = {}
        self.applied_names = []
        self.failed_names = []
        self._topology = None
        self._reopen = False
        self._held_failures = set()  # drivers that reject independent gamma LUTs
        if not WINDOWS:
            return

        from ctypes import wintypes

        class MonitorInfoEx(ctypes.Structure):
            _fields_ = [
                ("cbSize", wintypes.DWORD),
                ("rcMonitor", wintypes.RECT),
                ("rcWork", wintypes.RECT),
                ("dwFlags", wintypes.DWORD),
                ("szDevice", wintypes.WCHAR * 32),
            ]

        class DisplayDevice(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD), ("DeviceName", wintypes.WCHAR * 32),
                ("DeviceString", wintypes.WCHAR * 128),
                ("StateFlags", wintypes.DWORD),
                ("DeviceID", wintypes.WCHAR * 128),
                ("DeviceKey", wintypes.WCHAR * 128),
            ]

        self.device_type = DisplayDevice
        self.monitor_info_type = MonitorInfoEx
        self.monitor_callback_type = ctypes.WINFUNCTYPE(
            ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p,
            ctypes.POINTER(wintypes.RECT), ctypes.c_ssize_t)
        self.gdi = ctypes.WinDLL("gdi32", use_last_error=True)
        self.user32 = ctypes.WinDLL("user32", use_last_error=True)
        self.user32.EnumDisplayMonitors.argtypes = [
            ctypes.c_void_p, ctypes.c_void_p, self.monitor_callback_type,
            ctypes.c_ssize_t,
        ]
        self.user32.EnumDisplayMonitors.restype = ctypes.c_int
        self.user32.GetMonitorInfoW.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self.user32.GetMonitorInfoW.restype = ctypes.c_int
        self.user32.EnumDisplayDevicesW.argtypes = [
            ctypes.c_wchar_p, ctypes.c_uint, ctypes.POINTER(DisplayDevice), ctypes.c_uint]
        self.user32.EnumDisplayDevicesW.restype = ctypes.c_int
        self.gdi.CreateDCW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p,
                                        ctypes.c_wchar_p, ctypes.c_void_p]
        self.gdi.CreateDCW.restype = ctypes.c_void_p
        self.gdi.GetDeviceGammaRamp.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self.gdi.GetDeviceGammaRamp.restype = ctypes.c_int
        self.gdi.SetDeviceGammaRamp.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self.gdi.SetDeviceGammaRamp.restype = ctypes.c_int
        self.gdi.DeleteDC.argtypes = [ctypes.c_void_p]
        self.gdi.DeleteDC.restype = ctypes.c_int

    def mark_display_change(self):
        """Invalidate monitor DCs after Windows has changed the display layout."""
        self._reopen = True

    def _enumerate_monitors(self):
        """Identify each active desktop target by Windows PnP monitor identity."""
        monitors = {}

        def receive(monitor, _hdc, _rect, _context):
            info = self.monitor_info_type()
            info.cbSize = ctypes.sizeof(info)
            if self.user32.GetMonitorInfoW(monitor, ctypes.byref(info)):
                name = info.szDevice
                rect = info.rcMonitor
                device = self.device_type()
                device.cb = ctypes.sizeof(device)
                # EnumDisplayDevices(display-name, 0) resolves monitor name/ID.
                valid = bool(self.user32.EnumDisplayDevicesW(name, 0,
                                                              ctypes.byref(device), 0))
                # DeviceID is normally the monitor's PnP instance identifier.
                identity = (device.DeviceID.strip() if valid else "") or name
                description = (device.DeviceString.strip() if valid else "")
                label = name.rsplit(chr(92), 1)[-1]
                if description and not description.lower().startswith('generic pnp'):
                    label += " · " + description
                label += f" ({rect.right - rect.left}×{rect.bottom - rect.top})"
                if info.dwFlags & 1:
                    label += " ★"
                monitors[name] = {
                    "rect": (rect.left, rect.top, rect.right, rect.bottom),
                    "id": identity.casefold(), "label": label,
                }
            return 1

        callback = self.monitor_callback_type(receive)
        self.user32.EnumDisplayMonitors(None, None, callback, 0)
        # Two identical monitors can share a reported model ID. Avoid mixing
        # their profiles by including the logical output in that case.
        identities = [info["id"] for info in monitors.values()]
        for name, info in monitors.items():
            if identities.count(info["id"]) > 1:
                info["id"] += "|" + name.casefold()
        return monitors

    def list_monitors(self):
        self._refresh_displays()
        return [(name, info["id"], info["label"])
                for name, info in sorted(self.targets.items())]

    def _read_ramp(self, dc):
        ramp = (ctypes.c_ushort * 768)()
        if self.gdi.GetDeviceGammaRamp(dc, ctypes.byref(ramp)):
            return ramp
        return None

    def _open_display(self, name, old_state=None):
        # The GDI device name (e.g. r"\.\DISPLAY2") targets a particular
        # monitor; a plain desktop DC would usually target the primary screen.
        dc = self.gdi.CreateDCW("DISPLAY", name, None, None)
        if not dc:
            return None
        original = self._read_ramp(dc)
        if original is None:
            self.gdi.DeleteDC(dc)
            return None
        # Preserve the pre-adjustment calibration across mode/layout changes.
        # Never use an already color-adjusted ramp as a new baseline.
        if old_state is not None:
            original = old_state["original"]
        return {"dc": dc, "original": original}

    def _refresh_displays(self):
        if not WINDOWS:
            self.targets = {}
            return
        targets = self._enumerate_monitors()
        topology = tuple(sorted((name, v["rect"], v["id"])
                                for name, v in targets.items()))
        if topology == self._topology and not self._reopen and len(self.displays) == len(targets):
            self.targets = targets
            return

        previous = self.displays
        current = {}
        for name in targets:
            old = previous.get(name)
            if old and topology == self._topology and not self._reopen:
                current[name] = old
                continue
            # A different monitor on the same DISPLAY output must not inherit
            # the old monitor's calibration table.
            old_identity = getattr(self, "_previous_ids", {}).get(name)
            replacement = self._open_display(
                name, old if old_identity == targets[name]["id"] else None)
            if replacement is not None:
                current[name] = replacement

        # When the monitor configuration changes, the old contexts can be
        # invalid; don't attempt restoration through those stale handles.
        for state in previous.values():
            if state not in current.values():
                self.gdi.DeleteDC(state["dc"])

        self.displays = current
        self.targets = targets
        self._previous_ids = {name: v["id"] for name, v in targets.items()}
        if topology != self._topology:
            self._held_failures.clear()
        self._topology = topology
        self._reopen = False

    @staticmethod
    def _ramp_for(original, scales):
        ramp = (ctypes.c_ushort * 768)()
        for channel in range(3):
            offset = 256 * channel
            scale = scales[channel]
            for i in range(256):
                ramp[offset + i] = min(65535, round(original[offset + i] * scale))
        return ramp

    @classmethod
    def _approximately_equal(cls, current, wanted):
        if current is None:
            return False
        # Sampling is sufficient to detect the usual Windows gamma resets.
        return all(abs(int(current[channel * 256 + index]) -
                       int(wanted[channel * 256 + index])) <= cls.READBACK_TOLERANCE
                   for channel in range(3)
                   for index in (0, 32, 64, 128, 192, 255))

    @staticmethod
    def safe_profile(raw):
        if not isinstance(raw, dict):
            raw = {}
        def bound(key, default, lo, hi):
            try:
                return max(lo, min(hi, int(raw.get(key, default))))
            except (ValueError, TypeError):
                return default
        return {
            "enabled": bool(raw.get("enabled", True)),
            "offset": bound("offset", 0, -2000, 2000),
            "dim": bound("dim", 0, 0, 20),
            "red": bound("red", 100, 65, 100),
            "green": bound("green", 100, 65, 100),
            "blue": bound("blue", 100, 65, 100),
        }

    def apply(self, kelvin, dim_percent, force=False, profiles=None):
        self.applied_names = []
        self.failed_names = []
        self._refresh_displays()
        if not self.targets:
            return False
        profiles = profiles or {}
        reference = kelvin_rgb(6500)
        wanted_for = {}
        # Each logical desktop monitor gets an independent gamma LUT.
        for name, info in self.targets.items():
            state = self.displays.get(name)
            if state is None:
                self.failed_names.append(name)
                continue
            correction = self.safe_profile(profiles.get(info["id"]))
            if not correction["enabled"]:
                wanted = state["original"]
            else:
                temp = max(2700, min(7500, kelvin + correction["offset"]))
                brightness = 1.0 - max(0, min(40, dim_percent + correction["dim"])) / 100.0
                rgb = kelvin_rgb(temp)
                scales = [max(.54, min(1.0, rgb[i] /
                          max(.001, reference[i]) * brightness *
                          (correction[("red", "green", "blue")[i]] / 100.0)))
                          for i in range(3)]
                wanted = self._ramp_for(state["original"], scales)
            wanted_for[name] = wanted
            present = self._read_ramp(state["dc"])
            if (force or name not in self._held_failures) and (
                    force or not self._approximately_equal(present, wanted)):
                if self.gdi.SetDeviceGammaRamp(state["dc"], ctypes.byref(wanted)):
                    state["was_modified"] = bool(correction["enabled"])
        # Verify AFTER all writes. Some GPU drivers use one gamma LUT for
        # multiple outputs, so a later write may overwrite the first.
        for name, wanted in wanted_for.items():
            current = self._read_ramp(self.displays[name]["dc"])
            if self._approximately_equal(current, wanted):
                self.applied_names.append(name)
            else:
                self.failed_names.append(name)
        # Avoid repeatedly flickering a shared hardware gamma LUT every 10s.
        # A forced update (user edit/theme change) retries the affected output.
        self._held_failures = set(self.failed_names)
        return bool(self.applied_names) and not self.failed_names

    def restore(self):
        if not WINDOWS:
            return
        self._refresh_displays()
        for state in self.displays.values():
            self.gdi.SetDeviceGammaRamp(state["dc"],
                                         ctypes.byref(state["original"]))
            self.gdi.DeleteDC(state["dc"])
        self.displays.clear()
        self.targets.clear()
        self.applied_names.clear()
        self.failed_names.clear()
        self._topology = None
        self._reopen = False
        self._held_failures.clear()


class MonitorSettingsDialog(QDialog):
    """Edits persisted per-monitor gamma corrections without touching other monitors."""

    def __init__(self, owner):
        super().__init__(owner)
        self.owner = owner
        self.setWindowTitle(owner.t("monitor_options"))
        self.setMinimumSize(470, 490)
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        body = QVBoxLayout(self)
        body.setSpacing(10)
        body.addWidget(QLabel(owner.t("monitor_choose")))
        self.monitor_select = QComboBox()
        self.monitor_select.currentIndexChanged.connect(self.select_monitor)
        body.addWidget(self.monitor_select)
        self.enabled = QCheckBox(owner.t("monitor_enabled"))
        self.enabled.toggled.connect(self.save)
        body.addWidget(self.enabled)
        self.sliders = {}
        self.value_labels = {}
        for key, text_key, lo, hi, step, suffix in (
            ("offset", "monitor_offset", -2000, 2000, 50, " K"),
            ("dim", "monitor_dim", 0, 20, 1, "%"),
            ("red", "monitor_red", 65, 100, 1, "%"),
            ("green", "monitor_green", 65, 100, 1, "%"),
            ("blue", "monitor_blue", 65, 100, 1, "%"),
        ):
            line = QHBoxLayout()
            title = QLabel(owner.t(text_key))
            title.setMinimumWidth(140)
            line.addWidget(title)
            slider = QSlider(Qt.Horizontal)
            slider.setRange(lo, hi)
            slider.setSingleStep(step)
            slider.setPageStep(step)
            line.addWidget(slider, 1)
            amount = QLabel()
            amount.setMinimumWidth(66)
            amount.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            line.addWidget(amount)
            body.addLayout(line)
            self.sliders[key] = slider
            self.value_labels[key] = amount
            slider.valueChanged.connect(lambda _value, k=key, a=amount, su=suffix:
                                        self.slider_changed(k, a, su))
        self.status = QLabel()
        self.status.setObjectName("hint")
        self.status.setWordWrap(True)
        body.addWidget(self.status)
        note = QLabel(owner.t("monitor_note"))
        note.setObjectName("hint")
        note.setWordWrap(True)
        body.addWidget(note)
        buttons = QHBoxLayout()
        choose_tint = QPushButton(owner.t("monitor_pick"))
        choose_tint.clicked.connect(self.choose_tint)
        buttons.addWidget(choose_tint)
        reset = QPushButton(owner.t("monitor_reset"))
        reset.clicked.connect(self.reset_selected)
        buttons.addWidget(reset)
        close = QPushButton(owner.t("monitor_close"))
        close.clicked.connect(self.close)
        buttons.addWidget(close)
        body.addLayout(buttons)
        self.loading = False
        self.refresh_monitors()

    def refresh_monitors(self):
        old = self.monitor_select.currentData()
        entries = self.owner.gamma.list_monitors()
        self.monitor_select.blockSignals(True)
        self.monitor_select.clear()
        for _device_name, identity, label in entries:
            self.monitor_select.addItem(label, identity)
        if old:
            idx = self.monitor_select.findData(old)
            if idx >= 0:
                self.monitor_select.setCurrentIndex(idx)
        self.monitor_select.blockSignals(False)
        self.select_monitor()

    def select_monitor(self, *_args):
        self.loading = True
        identity = self.monitor_select.currentData()
        if identity is None:
            self.enabled.setChecked(False)
            self.status.setText(self.owner.t("monitor_empty"))
            profile = DisplayGamma.safe_profile({"enabled": False})
        else:
            profile = DisplayGamma.safe_profile(
                self.owner.monitor_profiles.get(identity))
            self.status.setText(self.monitor_select.currentText())
        self.enabled.setChecked(profile["enabled"])
        self.enabled.setEnabled(identity is not None)
        for key, slider in self.sliders.items():
            slider.setValue(profile[key])
            slider.setEnabled(bool(identity is not None and profile["enabled"]))
        for key, slider in self.sliders.items():
            self.slider_changed(key, self.value_labels[key],
                                " K" if key == "offset" else "%", save=False)
        self.loading = False

    def slider_changed(self, key, label, suffix, save=True):
        if label is not None:
            value = self.sliders[key].value()
            label.setText((f"{value:+d}" if key == "offset" else str(value)) + suffix)
        if save:
            self.save()

    def save(self, *_args):
        if self.loading:
            return
        identity = self.monitor_select.currentData()
        if identity is None:
            return
        for slider in self.sliders.values():
            slider.setEnabled(self.enabled.isChecked())
        self.owner.monitor_profiles[identity] = {
            "enabled": self.enabled.isChecked(),
            **{key: widget.value() for key, widget in self.sliders.items()},
        }
        self.owner.store_monitor_profiles()
        self.owner.update_screen(force=True)

    def choose_tint(self):
        if self.monitor_select.currentData() is None:
            return
        current = QColor(*[round(self.sliders[channel].value() * 255 / 100)
                            for channel in ("red", "green", "blue")])
        selected = QColorDialog.getColor(current, self, self.owner.t("monitor_pick"))
        if not selected.isValid():
            return
        # Convert a chosen hue to conservative, legible hardware RGB gains.
        # A color tint is not a fullscreen solid-color overlay.
        rgb = [selected.red(), selected.green(), selected.blue()]
        peak = max(1, *rgb)
        self.loading = True
        for channel, intensity in zip(("red", "green", "blue"), rgb):
            self.sliders[channel].setValue(max(65, round(intensity / peak * 100)))
        self.loading = False
        self.save()

    def reset_selected(self):
        identity = self.monitor_select.currentData()
        if identity is None:
            return
        self.owner.monitor_profiles.pop(identity, None)
        self.owner.store_monitor_profiles()
        self.select_monitor()
        self.owner.update_screen(force=True)


class TemperatureGraph(QWidget):
    """Small 24h graph in the Screen tab; no separate dialog or scroll area."""

    def __init__(self, owner):
        super().__init__(owner)
        self.owner = owner
        self.setFixedHeight(106)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        dark = self.owner.ui_is_dark
        subtle = QColor("#34465a" if dark else "#d8e2ec")
        text_color = QColor("#a2b4c8" if dark else "#64788d")
        top, bottom = 9, self.height() - 25
        left, right = 10, self.width() - 10
        p.setPen(QPen(subtle, 1))
        p.drawLine(left, bottom, right, bottom)
        p.drawLine(left, top, right, top)
        p.setPen(text_color)
        for hour in (0, 6, 12, 18, 24):
            x = left + (right - left) * hour / 24
            p.drawText(int(x - 12), self.height() - 4, f"{hour:02d}")
        bounds = self.owner.screen_day_bounds()
        temps = [self.owner.screen_profile(hour / 5, bounds)[0] for hour in range(121)]
        low = min(temps) - 250
        high = max(temps) + 250
        span = max(500, high - low)
        path = QPainterPath()
        for i, kelvin in enumerate(temps):
            x = left + (right - left) * i / 120
            y = bottom - (bottom - top) * (kelvin - low) / span
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        p.setPen(QPen(QColor("#26aab3" if dark else "#138d9c"), 2.4))
        p.drawPath(path)
        now = datetime.datetime.now().hour + datetime.datetime.now().minute / 60
        temp, _ = self.owner.screen_profile(now, bounds)
        x = left + (right - left) * now / 24
        y = bottom - (bottom - top) * (temp - low) / span
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#eea14d"))
        p.drawEllipse(int(x - 4), int(y - 4), 8, 8)
        p.end()


class ByteAutoTheme(QMainWindow):
    TABS = ("quick", "automation", "conditions", "personalization", "screen", "general")

    def __init__(self):
        super().__init__()
        self.data = load_settings()
        self.language = self.system_language() if self.data["language"] == "system" else self.data["language"]
        self.localized = []
        self.controls = {}
        self.last_mode = None
        self.manual_hold = None
        self.last_block = ""
        self.is_applying = False
        self.quit_requested = False
        self.ui_is_dark = None
        self.gpu_value = None
        self.gpu_sampled = False
        self.gamma = DisplayGamma()
        try:
            loaded_profiles = json.loads(self.data.get("monitor_profiles", "{}"))
            self.monitor_profiles = loaded_profiles if isinstance(loaded_profiles, dict) else {}
        except (TypeError, ValueError):
            self.monitor_profiles = {}
        self.monitor_dialog = None
        self.last_screen_profile = None
        self.network = QNetworkAccessManager(self)
        self.setWindowTitle(APP)
        self.setWindowIcon(app_icon())
        self.build_ui()
        # One compact, fixed window size for every tab. The user cannot resize it.
        self.setFixedSize(535, 680)
        self.set_ui_theme(force=True)
        self.build_tray()
        self.connect_controls()
        # Qt notifies us immediately when an external monitor is attached,
        # unplugged or becomes the primary display.
        app = QApplication.instance()
        app.screenAdded.connect(self.display_configuration_changed)
        app.screenRemoved.connect(self.display_configuration_changed)
        app.primaryScreenChanged.connect(self.display_configuration_changed)

        # Persist all defaults once, then only write modified preferences.
        registry_set(SETTINGS_KEY, self.data)
        self.gpu_worker = GPUWorker()
        self.gpu_worker.enabled = self.data["game_guard"]
        self.gpu_worker.interval = self.data["gpu_interval"]
        self.gpu_worker.measurement.connect(self.receive_gpu)
        self.gpu_worker.start()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(10000)
        QTimer.singleShot(700, self.tick)
        self.update_solar_label()
        self.update_appearance_label()
        self.update_tray()
        self.update_screen()
        if self.data["startup"]:
            self.update_startup()

    @staticmethod
    def system_language():
        if WINDOWS:
            try:
                return "tr" if ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0x3FF == 0x1F else "en"
            except (OSError, AttributeError):
                pass
        return "tr" if QLocale.system().language() == QLocale.Turkish else "en"

    def t(self, key, **values):
        original = TEXT.get(key, (key, key))
        translated = original[0 if self.language == "tr" else 1]
        return translated.format(**values) if values else translated

    def localized_control(self, widget, key, setter="setText"):
        self.localized.append((widget, setter, key))
        getattr(widget, setter)(self.t(key))
        return widget

    def label(self, key, muted=False):
        widget = self.localized_control(QLabel(), key)
        if muted:
            widget.setObjectName("hint")
            widget.setWordWrap(True)
        return widget

    def button(self, key, primary=False):
        widget = self.localized_control(QPushButton(), key)
        if primary:
            widget.setObjectName("primary")
        return widget

    def checkbox(self, key, text_key=None):
        widget = self.localized_control(QCheckBox(), text_key or key)
        widget.setChecked(self.data[key])
        self.controls[key] = widget
        return widget

    def panel(self):
        frame = QFrame()
        frame.setObjectName("panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 15, 16, 15)
        layout.setSpacing(11)
        return frame, layout

    @staticmethod
    def horizontal(*widgets):
        line = QHBoxLayout()
        line.setContentsMargins(0, 0, 0, 0)
        line.setSpacing(8)
        both_buttons = all(isinstance(widget, QPushButton) for widget in widgets)
        for widget in widgets:
            line.addWidget(widget, 1 if both_buttons or isinstance(widget, QLineEdit) else 0)
        return line

    def path_field(self, key, caption, file_type):
        line = QHBoxLayout()
        line.setContentsMargins(0, 0, 0, 0)
        line.setSpacing(6)
        name = self.label(caption, True)
        name.setMinimumWidth(104)
        line.addWidget(name)
        edit = QLineEdit(self.data[key])
        self.localized_control(edit, "no_file", "setPlaceholderText")
        self.controls[key] = edit
        line.addWidget(edit, 1)
        browse = QPushButton("…")
        browse.setObjectName("mini")
        browse.setFixedWidth(30)
        browse.clicked.connect(lambda: self.browse_file(edit, file_type))
        line.addWidget(browse)
        return line

    def build_ui(self):
        center = QWidget()
        self.setCentralWidget(center)
        layout = QVBoxLayout(center)
        layout.setContentsMargins(12, 9, 12, 10)
        layout.setSpacing(10)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(6)
        icon = QLabel()
        icon.setFixedSize(32, 32)
        icon.setAlignment(Qt.AlignCenter)
        icon.setPixmap(app_icon().pixmap(28, 28))
        header.addWidget(icon, 0, Qt.AlignVCenter)
        title = QLabel(APP)
        title.setObjectName("title")
        header.addWidget(title, 0, Qt.AlignVCenter)
        header.addStretch()
        self.theme_buttons = {}
        self.theme_group = QButtonGroup(self)
        self.theme_group.setExclusive(True)
        for mode, symbol, tooltip in (("auto", "◐", "system_ui"),
                                      ("light", "☀", "light_ui"),
                                      ("dark", "☾", "dark_ui")):
            button = QPushButton(symbol)
            button.setObjectName("mini")
            button.setFixedWidth(32)
            button.setCheckable(True)
            button.setChecked(self.data["ui_theme"] == mode)
            self.localized_control(button, tooltip, "setToolTip")
            self.theme_group.addButton(button)
            self.theme_buttons[mode] = button
            header.addWidget(button)
            button.clicked.connect(lambda checked=False, m=mode: self.select_ui_theme(m))
        self.language_button = QPushButton(self.language.upper())
        self.language_button.setObjectName("mini")
        self.language_button.setFixedWidth(39)
        self.language_button.clicked.connect(self.toggle_language)
        header.addWidget(self.language_button)
        layout.addLayout(header)

        # Altı sekme, iki satırlı kompakt gezinme.
        self.pages = QStackedWidget()
        self.tab_buttons = {}
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        navigation = QGridLayout()
        navigation.setContentsMargins(0, 0, 0, 0)
        navigation.setSpacing(5)
        for index, name in enumerate(self.TABS):
            button = self.localized_control(QPushButton(), name)
            button.setObjectName("nav")
            button.setCheckable(True)
            button.setChecked(index == 0)
            self.nav_group.addButton(button)
            self.tab_buttons[name] = button
            navigation.addWidget(button, index // 3, index % 3)
            button.clicked.connect(lambda checked=False, n=index: self.pages.setCurrentIndex(n))
        layout.addLayout(navigation)

        # Tek sekme sırası: butonlar ve içerikler aynı TABS dizisini kullanır.
        page_builders = {
            "quick": self.make_quick,
            "automation": self.make_automation,
            "conditions": self.make_conditions,
            "personalization": self.make_personalization,
            "screen": self.make_screen,
            "general": self.make_general,
        }
        for name in self.TABS:
            page = QWidget()
            contents = QVBoxLayout(page)
            contents.setContentsMargins(0, 1, 0, 0)
            contents.setSpacing(0)
            frame, body = self.panel()
            page_builders[name](body)
            if name == "screen":
                # Extra monitor controls remain accessible within the fixed window.
                scroll = QScrollArea(page)
                scroll.setWidgetResizable(True)
                scroll.setFrameShape(QFrame.NoFrame)
                scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                wrapper = QWidget()
                inner = QVBoxLayout(wrapper)
                inner.setContentsMargins(0, 0, 3, 0)
                inner.addWidget(frame)
                inner.addStretch(1)
                scroll.setWidget(wrapper)
                contents.addWidget(scroll, 1)
            else:
                contents.addWidget(frame, 0)
                contents.addStretch(1)
            self.pages.addWidget(page)
        # İlk açılışta Hızlı Ayarlar gösterilir; görünür sekme ile düğme eşleşir.
        self.pages.currentChanged.connect(self.tab_changed)
        self.pages.setCurrentIndex(0)
        self.tab_buttons["quick"].setChecked(True)
        layout.addWidget(self.pages, 1)

        self.status = QLabel(self.t("ready"))
        self.status.setObjectName("status")
        self.status.setWordWrap(True)
        self.status.setMinimumHeight(25)
        layout.addWidget(self.status)

    def tab_changed(self, index):
        if 0 <= index < len(self.TABS):
            self.tab_buttons[self.TABS[index]].setChecked(True)

    def make_quick(self, body):
        self.current_label = QLabel()
        self.current_label.setObjectName("hint")
        body.addWidget(self.current_label)
        dark = self.button("dark", True)
        light = self.button("light", True)
        dark.clicked.connect(lambda: self.apply_theme("dark", manual=True))
        light.clicked.connect(lambda: self.apply_theme("light", manual=True))
        body.addLayout(self.horizontal(dark, light))
        open_settings = self.button("open_windows")
        open_settings.clicked.connect(self.open_personalization)
        body.addWidget(open_settings)

    def make_automation(self, body):
        body.addWidget(self.label("schedule", True))
        self.schedule = QComboBox()
        for kind in ("manual", "time", "sun"):
            self.schedule.addItem(self.t(kind), kind)
        self.schedule.setCurrentIndex(max(0, self.schedule.findData(self.data["schedule_kind"])))
        self.controls["schedule_kind"] = self.schedule
        body.addWidget(self.schedule)

        self.time_panel = QWidget()
        times = QGridLayout(self.time_panel)
        times.setContentsMargins(0, 0, 0, 0)
        times.setSpacing(8)
        times.addWidget(self.label("light_start", True), 0, 0)
        times.addWidget(self.label("dark_start", True), 0, 1)
        for column, key in enumerate(("light_time", "dark_time")):
            control = QTimeEdit(QTime.fromString(self.data[key], "HH:mm"))
            control.setDisplayFormat("HH:mm")
            times.addWidget(control, 1, column)
            self.controls[key] = control
        body.addWidget(self.time_panel)

        self.sun_panel = QWidget()
        sun_layout = QVBoxLayout(self.sun_panel)
        sun_layout.setContentsMargins(0, 0, 0, 0)
        sun_layout.setSpacing(8)
        self.city_edit = QLineEdit(self.data["city"])
        self.city_edit.setClearButtonEnabled(True)
        self.localized_control(self.city_edit, "city_search", "setPlaceholderText")
        self.controls["city"] = self.city_edit
        search = self.button("search")
        search.clicked.connect(self.search_city)
        self.city_edit.returnPressed.connect(self.search_city)
        sun_layout.addLayout(self.horizontal(self.city_edit, search))
        self.solar_label = QLabel()
        self.solar_label.setObjectName("hint")
        sun_layout.addWidget(self.solar_label)
        body.addWidget(self.sun_panel)
        self.update_schedule_panel()

    def make_personalization(self, body):
        body.setSpacing(7)
        body.addWidget(self.checkbox("wallpaper_enabled"))
        body.addLayout(self.path_field("wallpaper_light", "wall_light", "image"))
        body.addLayout(self.path_field("wallpaper_dark", "wall_dark", "image"))
        body.addSpacing(5)
        body.addWidget(self.checkbox("theme_enabled"))
        body.addLayout(self.path_field("theme_light", "theme_light", "theme"))
        body.addLayout(self.path_field("theme_dark", "theme_dark", "theme"))
        body.addSpacing(5)
        section = self.label("system_heading")
        section.setStyleSheet("font-weight: 700")
        body.addWidget(section)
        systems = QGridLayout()
        systems.setContentsMargins(0, 0, 0, 0)
        systems.setHorizontalSpacing(8)
        systems.setVerticalSpacing(2)
        for index, key in enumerate(("windows_mode", "app_mode", "title_accent",
                                     "taskbar_accent", "touch_theme", "color_filter")):
            control = self.checkbox(key, "short_" + key)
            self.localized_control(control, key, "setToolTip")
            systems.addWidget(control, index // 2, index % 2)
        body.addLayout(systems)
        body.addWidget(self.label("system_tip", True))

    def screen_slider(self, body, key, low, high, step, suffix):
        row = QHBoxLayout()
        row.setSpacing(9)
        caption = self.label(key, True)
        caption.setMinimumWidth(125)
        row.addWidget(caption)
        slider = QSlider(Qt.Horizontal)
        slider.setRange(low, high)
        slider.setSingleStep(step)
        slider.setPageStep(step)
        slider.setTracking(False)
        slider.setValue(self.data[key])
        self.controls[key] = slider
        row.addWidget(slider, 1)
        value = QLabel()
        value.setMinimumWidth(63)
        value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        row.addWidget(value)
        def update_value():
            unit = (" dk" if self.language == "tr" else " min") if key == "screen_transition" else suffix
            value.setText(f"{slider.value()}{unit}")
        slider.valueChanged.connect(update_value)
        update_value()
        body.addLayout(row)
        return caption, slider, value

    def make_screen(self, body):
        body.addWidget(self.checkbox("screen_enabled"))
        body.addWidget(self.checkbox("screen_auto"))
        body.addWidget(self.checkbox("screen_follow_theme"))
        options = self.button("monitor_options")
        options.clicked.connect(self.open_monitor_settings)
        body.addWidget(options)
        self.screen_graph = TemperatureGraph(self)
        body.addWidget(self.screen_graph)
        self.screen_day_row = self.screen_slider(body, "screen_day_kelvin", 4500, 7500, 100, " K")
        self.screen_night_row = self.screen_slider(body, "screen_night_kelvin", 2700, 5500, 100, " K")
        self.screen_manual_row = self.screen_slider(body, "screen_manual_kelvin", 2700, 7500, 100, " K")
        self.screen_dim_row = self.screen_slider(body, "screen_night_dim", 0, 30, 1, " %")
        self.screen_transition_row = self.screen_slider(body, "screen_transition", 15, 180, 15, " dk")
        self.screen_status = QLabel()
        self.screen_status.setObjectName("hint")
        self.screen_status.setWordWrap(True)
        body.addWidget(self.screen_status)
        body.addWidget(self.label("screen_note", True))
        self.update_screen_panels()

    def update_screen_panels(self):
        automatic = self.controls["screen_auto"].isChecked()
        for group in (self.screen_day_row, self.screen_night_row, self.screen_transition_row):
            for widget in group:
                widget.setVisible(automatic)
        for widget in self.screen_manual_row:
            widget.setVisible(not automatic)
        for key in ("screen_day_kelvin", "screen_night_kelvin", "screen_manual_kelvin",
                    "screen_night_dim", "screen_transition", "screen_auto"):
            self.controls[key].setEnabled(self.controls["screen_enabled"].isChecked())
        self.controls["screen_follow_theme"].setEnabled(
            self.controls["screen_enabled"].isChecked() and automatic)
        self.screen_transition_row[2].setText(
            f"{self.controls['screen_transition'].value()} {'dk' if self.language == 'tr' else 'min'}")
        self.screen_graph.update()

    def make_conditions(self, body):
        body.addWidget(self.checkbox("game_guard"))
        gpu_row = QHBoxLayout()
        gpu_row.addWidget(self.label("gpu_threshold", True), 1)
        self.gpu_threshold = QSpinBox()
        self.gpu_threshold.setRange(1, 100)
        self.gpu_threshold.setSuffix(" %")
        self.gpu_threshold.setValue(self.data["gpu_threshold"])
        self.controls["gpu_threshold"] = self.gpu_threshold
        gpu_row.addWidget(self.gpu_threshold)
        gpu_row.addWidget(self.label("gpu_interval", True))
        self.gpu_interval = QComboBox()
        for seconds in (6, 12, 24):
            self.gpu_interval.addItem(f"{seconds} {'sn' if self.language == 'tr' else 's'}", seconds)
        self.gpu_interval.setCurrentIndex(max(0, self.gpu_interval.findData(self.data["gpu_interval"])))
        self.controls["gpu_interval"] = self.gpu_interval
        gpu_row.addWidget(self.gpu_interval)
        body.addLayout(gpu_row)
        self.gpu_bar = QProgressBar()
        self.gpu_bar.setRange(0, 100)
        self.gpu_bar.setTextVisible(False)
        body.addWidget(self.gpu_bar)
        self.gpu_label = self.label("gpu_wait", True)
        body.addWidget(self.gpu_label)
        body.addSpacing(9)

        body.addWidget(self.checkbox("apps_guard"))
        self.apps_edit = QLineEdit(self.data["blocked_apps"])
        self.localized_control(self.apps_edit, "apps_hint", "setPlaceholderText")
        self.controls["blocked_apps"] = self.apps_edit
        add = self.button("add_app")
        add.clicked.connect(self.add_process)
        body.addLayout(self.horizontal(self.apps_edit, add))
        body.addSpacing(9)

        body.addWidget(self.checkbox("idle_guard"))
        idle_row = QHBoxLayout()
        idle_row.addWidget(self.label("idle_minutes", True), 1)
        self.idle_minutes = QSpinBox()
        self.idle_minutes.setRange(1, 120)
        self.idle_minutes.setValue(self.data["idle_minutes"])
        self.controls["idle_minutes"] = self.idle_minutes
        idle_row.addWidget(self.idle_minutes)
        body.addLayout(idle_row)
        self.update_gpu_label()

    def make_general(self, body):
        body.addWidget(self.checkbox("startup"))
        body.addWidget(self.checkbox("notify"))
        body.addWidget(self.checkbox("hide_tray"))
        body.addWidget(self.label("tray_tip", True))
        body.addSpacing(10)
        exit_button = self.button("quit")
        exit_button.setObjectName("danger")
        exit_button.clicked.connect(self.quit_app)
        body.addWidget(exit_button)

    def connect_controls(self):
        for key, widget in self.controls.items():
            if isinstance(widget, QCheckBox):
                widget.toggled.connect(self.changed)
            elif isinstance(widget, QComboBox):
                widget.currentIndexChanged.connect(self.changed)
            elif isinstance(widget, (QSpinBox, QSlider)):
                widget.valueChanged.connect(self.changed)
            elif isinstance(widget, QTimeEdit):
                widget.timeChanged.connect(self.changed)
            else:
                widget.editingFinished.connect(self.changed)
        self.city_edit.textEdited.connect(self.city_edited)

    def control_value(self, widget):
        if isinstance(widget, QCheckBox):
            return widget.isChecked()
        if isinstance(widget, QComboBox):
            return widget.currentData()
        if isinstance(widget, (QSpinBox, QSlider)):
            return widget.value()
        if isinstance(widget, QTimeEdit):
            return widget.time().toString("HH:mm")
        return widget.text().strip()

    def changed(self):
        updates = {key: value for key, widget in self.controls.items()
                   if (value := self.control_value(widget)) != self.data[key]}
        if not updates:
            return
        self.data.update(updates)
        registry_set(SETTINGS_KEY, updates)
        if "schedule_kind" in updates:
            self.last_mode = None
            self.manual_hold = None
            self.update_schedule_panel()
        if "startup" in updates:
            self.update_startup()
        if "hide_tray" in updates:
            self.update_tray()
        if "game_guard" in updates:
            self.gpu_worker.enabled = updates["game_guard"]
            self.gpu_value = None
            self.gpu_sampled = False
            self.update_gpu_label()
        if "gpu_interval" in updates:
            self.gpu_worker.interval = updates["gpu_interval"]
        if "city" in updates and self.data["city_confirmed"]:
            self.data["city_confirmed"] = False
            registry_set(SETTINGS_KEY, {"city_confirmed": False})
            self.update_solar_label()
        if any(key.startswith("screen_") for key in updates):
            self.update_screen_panels()
            self.update_screen(force=True)
        elif any(key in updates for key in ("latitude", "longitude", "light_time", "dark_time", "city")):
            self.update_screen(force=True)
        if "schedule_kind" in updates:
            self.tick()

    def city_edited(self):
        if self.data["city_confirmed"]:
            self.data["city_confirmed"] = False
            registry_set(SETTINGS_KEY, {"city_confirmed": False})
            self.update_solar_label()

    def select_ui_theme(self, mode):
        self.data["ui_theme"] = mode
        registry_set(SETTINGS_KEY, {"ui_theme": mode})
        self.set_ui_theme(force=True)

    def set_ui_theme(self, force=False):
        dark = windows_dark() if self.data["ui_theme"] == "auto" else self.data["ui_theme"] == "dark"
        if not force and dark == self.ui_is_dark:
            return
        self.ui_is_dark = dark
        self.setStyleSheet(stylesheet(dark))
        if WINDOWS:
            try:
                dark_value = ctypes.c_int(int(dark))
                dwm = ctypes.WinDLL("dwmapi")
                for attribute in (20, 19):
                    if dwm.DwmSetWindowAttribute(
                        ctypes.c_void_p(int(self.winId())), attribute,
                        ctypes.byref(dark_value), ctypes.sizeof(dark_value)) == 0:
                        break
            except (OSError, AttributeError):
                pass

    def toggle_language(self):
        self.language = "en" if self.language == "tr" else "tr"
        self.data["language"] = self.language
        registry_set(SETTINGS_KEY, {"language": self.language})
        for widget, setter, key in self.localized:
            getattr(widget, setter)(self.t(key))
        if self.monitor_dialog is not None:
            self.monitor_dialog.close()
            self.monitor_dialog = None  # rebuild localized monitor labels on next opening
        for index in range(self.schedule.count()):
            self.schedule.setItemText(index, self.t(self.schedule.itemData(index)))
        for index in range(self.gpu_interval.count()):
            seconds = self.gpu_interval.itemData(index)
            self.gpu_interval.setItemText(index, f"{seconds} {'sn' if self.language == 'tr' else 's'}")
        self.language_button.setText(self.language.upper())
        self.update_solar_label()
        self.update_gpu_label()
        self.update_appearance_label()
        self.update_screen_panels()
        self.update_screen(force=True)
        self.tray_show.setText(self.t("tray_show"))
        self.tray_dark.setText(self.t("tray_dark"))
        self.tray_light.setText(self.t("tray_light"))
        self.tray_exit.setText(self.t("quit"))
        self.set_status("ready")

    def set_status(self, key, **values):
        self.status.setText(self.t(key, **values))

    def update_appearance_label(self):
        mode = self.t("dark_word" if windows_dark() else "light_word")
        self.current_label.setText(self.t("current", mode=mode))

    def update_schedule_panel(self):
        schedule = self.schedule.currentData()
        self.time_panel.setVisible(schedule == "time")
        self.sun_panel.setVisible(schedule == "sun")

    def sun_times(self):
        if not self.data["city_confirmed"] or not self.data["city"]:
            return None
        try:
            tz = ZoneInfo(self.data["timezone"])
            now = datetime.datetime.now(tz)
            location = LocationInfo(self.data["city"], "", self.data["timezone"],
                                    float(self.data["latitude"]), float(self.data["longitude"]))
            values = sun(location.observer, date=now.date(), tzinfo=tz)
            return now, values["sunrise"], values["sunset"]
        except (ValueError, KeyError, OSError, OverflowError):
            return None

    def update_solar_label(self):
        if not self.data["city_confirmed"]:
            self.solar_label.setText(self.t("solar_empty"))
            return
        values = self.sun_times()
        if not values:
            self.solar_label.setText(self.t("solar_failed"))
            return
        _, sunrise, sunset = values
        self.solar_label.setText(self.t("solar_result", rise=sunrise.strftime("%H:%M"),
                                        set=sunset.strftime("%H:%M")))

    def search_city(self):
        name = self.city_edit.text().strip()
        if not name:
            return
        local = TR_CITIES.get(norm_city(name))
        if local:
            self.accept_city(local[0], local[1], local[2], "Europe/Istanbul")
            return
        # Uses the existing app network manager; no second geocoding path.
        url = QUrl("https://geocoding-api.open-meteo.com/v1/search?name="
                   + quote(name) + "&count=5&language=en&format=json")
        reply = self.network.get(QNetworkRequest(url))
        reply.setProperty("city_request", name)
        reply.finished.connect(lambda: self.city_reply(reply))

    def city_reply(self, reply):
        try:
            request = str(reply.property("city_request"))
            if norm_city(request) != norm_city(self.city_edit.text()):
                return
            if reply.error():
                self.set_status("city_failed")
                return
            results = json.loads(bytes(reply.readAll()).decode("utf-8")).get("results", [])
            if not results:
                self.set_status("city_not_found")
                return
            same = [item for item in results if norm_city(item.get("name", "")) == norm_city(request)]
            chosen = (same or results)[0]
            self.accept_city(chosen["name"], float(chosen["latitude"]),
                             float(chosen["longitude"]), chosen.get("timezone", ""))
        except (KeyError, ValueError, TypeError):
            self.set_status("city_failed")
        finally:
            reply.deleteLater()

    def accept_city(self, city, latitude, longitude, timezone):
        try:
            ZoneInfo(timezone)
        except (ValueError, KeyError, OSError):
            self.set_status("city_failed")
            return
        self.city_edit.setText(city)
        changes = {"city": city, "city_confirmed": True, "latitude": latitude,
                   "longitude": longitude, "timezone": timezone}
        self.data.update(changes)
        registry_set(SETTINGS_KEY, changes)
        self.update_solar_label()
        self.last_mode = None
        self.update_screen(force=True)
        self.set_status("city_found", city=city)
        if self.data["schedule_kind"] == "sun":
            self.tick()

    def expected_mode(self):
        kind = self.data["schedule_kind"]
        if kind == "manual":
            return None
        if kind == "sun":
            values = self.sun_times()
            if not values:
                return None
            now, sunrise, sunset = values
            return "light" if sunrise <= now < sunset else "dark"
        try:
            now = datetime.datetime.now().time()
            start = datetime.time.fromisoformat(self.data["light_time"])
            end = datetime.time.fromisoformat(self.data["dark_time"])
        except ValueError:
            return None
        if start == end:
            return "dark"
        if start < end:
            return "light" if start <= now < end else "dark"
        return "light" if now >= start or now < end else "dark"

    def guard_reason(self):
        if self.data["game_guard"]:
            if self.gpu_value is None:
                return self.t("gpu_unavailable")
            if self.gpu_value >= self.data["gpu_threshold"]:
                return self.t("blocked_gpu", value=self.gpu_value,
                              threshold=self.data["gpu_threshold"])
        if self.data["apps_guard"]:
            matches = running_blocked_apps(self.data["blocked_apps"])
            if matches:
                return self.t("blocked_app", apps=", ".join(matches))
        if self.data["idle_guard"] and idle_seconds() < self.data["idle_minutes"] * 60:
            return self.t("blocked_idle")
        return ""

    def open_monitor_settings(self):
        if self.monitor_dialog is None:
            self.monitor_dialog = MonitorSettingsDialog(self)
        else:
            self.monitor_dialog.refresh_monitors()
        self.monitor_dialog.show()
        self.monitor_dialog.raise_()
        self.monitor_dialog.activateWindow()

    def store_monitor_profiles(self):
        value = json.dumps(self.monitor_profiles, ensure_ascii=False,
                           separators=(",", ":"))
        self.data["monitor_profiles"] = value
        registry_set(SETTINGS_KEY, {"monitor_profiles": value})

    def screen_day_bounds(self):
        solar = self.sun_times()
        if solar:
            _, sunrise, sunset = solar
            local_rise = sunrise.astimezone()
            local_set = sunset.astimezone()
            return (local_rise.hour + local_rise.minute / 60,
                    local_set.hour + local_set.minute / 60)
        try:
            start = datetime.time.fromisoformat(self.data["light_time"])
            end = datetime.time.fromisoformat(self.data["dark_time"])
            rise = start.hour + start.minute / 60
            set_ = end.hour + end.minute / 60
            return (rise, set_) if rise < set_ else (7.0, 19.0)
        except ValueError:
            return (7.0, 19.0)

    def screen_profile(self, hour, bounds=None):
        if not self.data["screen_auto"]:
            return (self.data["screen_manual_kelvin"], self.data["screen_night_dim"])
        if self.data.get("screen_follow_theme", True):
            mode = self.last_mode or ("dark" if windows_dark() else "light")
            level = 0.0 if mode == "dark" else 1.0
        else:
            rise, set_ = bounds or self.screen_day_bounds()
            level = daylight_weight(hour, rise, set_, self.data["screen_transition"])
        temp = round((self.data["screen_night_kelvin"] +
                      (self.data["screen_day_kelvin"] - self.data["screen_night_kelvin"]) * level) / 25) * 25
        dim = round(self.data["screen_night_dim"] * (1 - level))
        return (int(temp), int(dim))

    def update_screen(self, force=False):
        if not hasattr(self, "screen_status"):
            return
        if not self.data["screen_enabled"]:
            # Restore the saved original LUT on every connected display.
            if self.gamma.displays:
                self.gamma.restore()
            self.last_screen_profile = None
            self.screen_status.setText(self.t("screen_off"))
            self.screen_graph.update()
            return

        now = datetime.datetime.now()
        current = now.hour + now.minute / 60 + now.second / 3600
        profile = self.screen_profile(current)
        # Always examine EVERY monitor, even when the Kelvin value has not
        # changed. Windows may reset just one display after a theme switch,
        # sleep/resume or a monitor connection change.
        success = self.gamma.apply(*profile, force=force,
                                   profiles=self.monitor_profiles)
        total = len(self.gamma.targets)
        applied = len(self.gamma.applied_names)
        self.last_screen_profile = profile if success else None
        if not success:
            self.screen_status.setText(self.t("screen_unavailable") + " · " +
                                       self.t("screen_monitors", ok=applied, total=total))
        else:
            caption = (self.t("screen_now", temp=profile[0], dim=profile[1]) + " · " +
                       self.t("screen_monitors", ok=applied, total=total))
            if self.gamma.failed_names:
                caption += "\n" + self.t("screen_partial",
                                         names=", ".join(self.gamma.failed_names))
            self.screen_status.setText(caption)
        self.screen_graph.update()

    def display_configuration_changed(self, *_args):
        # Qt screen notifications are emitted for plugged/unplugged displays;
        # the native Windows event also catches resolution/driver changes.
        self.gamma.mark_display_change()
        if self.monitor_dialog is not None and self.monitor_dialog.isVisible():
            QTimer.singleShot(800, self.monitor_dialog.refresh_monitors)
        if self.data["screen_enabled"]:
            QTimer.singleShot(500, lambda: self.update_screen(force=True))
            QTimer.singleShot(2300, lambda: self.update_screen(force=True))
        if self.data["wallpaper_enabled"] and self.last_mode in ("light", "dark"):
            wallpaper = self.data["wallpaper_" + self.last_mode]
            if wallpaper and Path(wallpaper).is_file():
                QTimer.singleShot(1200,
                    lambda p=wallpaper: set_wallpaper_all_monitors(p))

    def nativeEvent(self, event_type, message):
        if WINDOWS:
            try:
                from ctypes import wintypes
                msg = wintypes.MSG.from_address(int(message))
                # WM_DISPLAYCHANGE, WM_DEVICECHANGE, WM_POWERBROADCAST
                if msg.message in (0x007E, 0x0219, 0x0218):
                    self.display_configuration_changed()
            except (ValueError, TypeError, OSError):
                pass
        return super().nativeEvent(event_type, message)

    def tick(self):
        self.set_ui_theme()
        self.update_appearance_label()
        self.update_screen()
        if self.is_applying:
            return
        desired = self.expected_mode()
        if desired is None:
            return
        if self.manual_hold is not None:
            if desired == self.manual_hold:
                return
            self.manual_hold = None
        if desired == self.last_mode:
            return
        reason = self.guard_reason()
        if reason:
            if self.last_block != reason:
                self.status.setText(self.t("paused", reason=reason))
                self.last_block = reason
            return
        self.last_block = ""
        self.apply_theme(desired)

    def apply_theme(self, mode, manual=False):
        if not WINDOWS:
            self.set_status("windows_only")
            return
        if self.is_applying:
            return
        if manual and self.data["schedule_kind"] != "manual":
            self.manual_hold = self.expected_mode()
        self.is_applying = True
        path = self.data["theme_dark" if mode == "dark" else "theme_light"]
        if self.data["theme_enabled"] and path:
            if not Path(path).is_file() or Path(path).suffix.casefold() != ".theme":
                self.is_applying = False
                self.set_status("invalid_file")
                return
            try:
                os.startfile(path)
            except OSError:
                self.is_applying = False
                self.set_status("apply_failed")
                return
            # Windows theme files can overwrite color registry values.
            QTimer.singleShot(2000, lambda: self.finish_theme(mode))
        else:
            self.finish_theme(mode)

    def reapply_wallpaper_if_current(self, wallpaper, mode):
        if (self.last_mode == mode and self.data["wallpaper_enabled"]
                and Path(wallpaper).is_file()):
            set_wallpaper_all_monitors(wallpaper)

    def finish_theme(self, mode):
        dark = mode == "dark"
        try:
            changes = {}
            if self.data["windows_mode"]:
                changes["SystemUsesLightTheme"] = int(not dark)
            if self.data["app_mode"]:
                changes["AppsUseLightTheme"] = int(not dark)
            registry_set(PERSONALIZE, changes)
            if self.data["title_accent"]:
                registry_set(DWM, {"ColorPrevalence": int(dark)})
            if self.data["taskbar_accent"]:
                registry_set(PERSONALIZE, {"ColorPrevalence": int(dark)})
            if self.data["touch_theme"]:
                registry_set(TOUCH, {"SelectedThemeName": "DarkTheme" if dark else "LightTheme",
                                     "SelectedThemeIndex": int(dark), "ThemeDataVersion": 2})
            if self.data["color_filter"]:
                set_color_filter(dark)
            wallpaper_problem = False
            if self.data["wallpaper_enabled"]:
                wallpaper = self.data["wallpaper_dark" if dark else "wallpaper_light"]
                if wallpaper:
                    wallpaper_problem = (not Path(wallpaper).is_file() or
                                         not set_wallpaper_all_monitors(wallpaper))
            notify_windows()
            # Reconcile color ramps across all monitors after Windows applies
            # a theme; delayed passes handle asynchronous per-display resets.
            if self.data["wallpaper_enabled"] and not wallpaper_problem:
                # .theme files and Explorer can asynchronously replace the
                # wallpaper on secondary screens after our first COM call.
                wallpaper = self.data["wallpaper_dark" if dark else "wallpaper_light"]
                if wallpaper and Path(wallpaper).is_file():
                    for delay in (750, 2500, 5500):
                        QTimer.singleShot(delay,
                            lambda p=wallpaper, m=mode: self.reapply_wallpaper_if_current(p, m))
            if self.data["screen_enabled"]:
                QTimer.singleShot(350, lambda: self.update_screen(force=True))
                QTimer.singleShot(1800, lambda: self.update_screen(force=True))
                QTimer.singleShot(4200, lambda: self.update_screen(force=True))
            self.last_mode = mode
            self.set_ui_theme()
            self.update_appearance_label()
            if wallpaper_problem:
                self.set_status("invalid_file")
            else:
                self.set_status("applied", mode=self.t("dark_word" if dark else "light_word"))
            if self.data["notify"] and self.tray.isVisible():
                self.tray.showMessage(APP, self.status.text(), QSystemTrayIcon.Information, 2500)
        except (OSError, ValueError, AttributeError):
            self.set_status("apply_failed")
        finally:
            self.is_applying = False

    def receive_gpu(self, value):
        if not self.data["game_guard"]:
            return
        self.gpu_value = value
        self.gpu_sampled = True
        self.update_gpu_label()
        if self.data["schedule_kind"] != "manual":
            self.tick()

    def update_gpu_label(self):
        if not self.data["game_guard"]:
            self.gpu_label.setText(self.t("gpu_idle"))
            self.gpu_bar.setValue(0)
        elif self.gpu_value is None:
            self.gpu_label.setText(self.t("gpu_unavailable" if self.gpu_sampled else "gpu_wait"))
            self.gpu_bar.setValue(0)
        else:
            self.gpu_label.setText(f"GPU: {self.gpu_value:g}%")
            self.gpu_bar.setValue(round(self.gpu_value))

    def browse_file(self, edit, kind):
        if kind == "image":
            filter_text = "Images (*.png *.jpg *.jpeg *.bmp);;All files (*)"
            title = self.t("choose_image")
        else:
            filter_text = "Windows Theme (*.theme)"
            title = self.t("choose_theme")
        path, _ = QFileDialog.getOpenFileName(self, title, "", filter_text)
        if path:
            edit.setText(path)
            self.changed()

    def add_process(self):
        path, _ = QFileDialog.getOpenFileName(self, self.t("choose_exe"), "", "Applications (*.exe)")
        if not path:
            return
        existing = [s.strip() for s in self.apps_edit.text().split(",") if s.strip()]
        name = Path(path).name
        if name.casefold() not in {s.casefold() for s in existing}:
            existing.append(name)
        self.apps_edit.setText(", ".join(existing))
        self.controls["apps_guard"].setChecked(True)
        self.changed()

    @staticmethod
    def open_personalization():
        if WINDOWS:
            os.startfile("ms-settings:personalization-colors")

    def update_startup(self):
        if not WINDOWS:
            return
        if self.data["startup"]:
            if getattr(sys, "frozen", False):
                executable = f'"{sys.executable}" --minimized'
            else:
                pythonw = Path(sys.executable).with_name("pythonw.exe")
                python_bin = pythonw if pythonw.is_file() else Path(sys.executable)
                executable = f'"{python_bin}" "{Path(__file__).resolve()}" --minimized'
            registry_set(STARTUP_KEY, {APP: executable})
        else:
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_KEY, 0,
                                    winreg.KEY_SET_VALUE) as key:
                    winreg.DeleteValue(key, APP)
            except OSError:
                pass

    def build_tray(self):
        self.tray = QSystemTrayIcon(app_icon(), self)
        menu = QMenu(self)
        self.tray_show = menu.addAction(self.t("tray_show"), self.show_window)
        self.tray_dark = menu.addAction(self.t("tray_dark"), lambda: self.apply_theme("dark", manual=True))
        self.tray_light = menu.addAction(self.t("tray_light"), lambda: self.apply_theme("light", manual=True))
        menu.addSeparator()
        self.tray_exit = menu.addAction(self.t("quit"), self.quit_app)
        self.tray.setContextMenu(menu)
        self.tray.setToolTip(APP)
        self.tray.activated.connect(lambda reason: self.show_window()
                                    if reason == QSystemTrayIcon.DoubleClick else None)

    def update_tray(self):
        self.tray.setVisible(not self.data["hide_tray"] and QSystemTrayIcon.isSystemTrayAvailable())

    def show_window(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def closeEvent(self, event):
        if self.quit_requested:
            event.accept()
        else:
            event.ignore()
            self.hide()

    def quit_app(self):
        self.quit_requested = True
        if self.monitor_dialog is not None:
            self.monitor_dialog.close()
        self.gamma.restore()
        self.gpu_worker.requestInterruption()
        self.gpu_worker.wait(10000)
        self.tray.hide()
        QApplication.instance().quit()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP)
    app.setQuitOnLastWindowClosed(False)
    app.setFont(QFont("Segoe UI", 9))
    app.setWindowIcon(app_icon())

    # Mutex prevents a second Windows process; local socket reopens the first.
    user = re.sub(r"[^\w-]", "_", os.environ.get("USERNAME", "user"))
    socket_name = f"ByteAutoTheme_{user}"
    mutex = None
    kernel = None
    if WINDOWS:
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        create = kernel.CreateMutexW
        create.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_wchar_p]
        create.restype = ctypes.c_void_p
        mutex = create(None, 0, f"Local\\ByteAutoTheme.{user}")
        if not mutex:
            return 1
        if ctypes.get_last_error() == 183:
            connection = QLocalSocket()
            connection.connectToServer(socket_name)
            if connection.waitForConnected(1500):
                connection.write(b"SHOW")
                connection.flush()
                connection.waitForBytesWritten(1000)
                connection.disconnectFromServer()
            kernel.CloseHandle.argtypes = [ctypes.c_void_p]
            kernel.CloseHandle(mutex)
            return 0

    server = QLocalServer()
    if not server.listen(socket_name):
        if not WINDOWS:
            QLocalServer.removeServer(socket_name)
        if not server.listen(socket_name):
            if mutex and kernel:
                kernel.CloseHandle(mutex)
            return 1

    window = ByteAutoTheme()

    def reopen():
        while server.hasPendingConnections():
            connection = server.nextPendingConnection()
            window.show_window()
            connection.disconnectFromServer()
            connection.deleteLater()

    server.newConnection.connect(reopen)
    if "--minimized" not in sys.argv:
        window.show()
    try:
        return app.exec()
    finally:
        server.close()
        if mutex and kernel:
            kernel.CloseHandle(mutex)


def relaunch_without_console():
    """Keep a .py entry point; when possible, rerun with pythonw.exe."""
    if not WINDOWS or getattr(sys, "frozen", False) or "--console" in sys.argv:
        return False
    interpreter = Path(sys.executable)
    if interpreter.name.casefold() not in ("python.exe", "python3.exe"):
        return False
    pythonw = interpreter.with_name("pythonw.exe")
    if not pythonw.is_file():
        return False
    try:
        subprocess.Popen([str(pythonw), str(Path(__file__).resolve()), *sys.argv[1:]],
                         cwd=str(Path(__file__).resolve().parent),
                         creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return True
    except OSError:
        return False


if __name__ == "__main__":
    if not relaunch_without_console():
        sys.exit(main())
