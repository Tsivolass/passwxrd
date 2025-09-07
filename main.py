import sys
import os
import ctypes
from pathlib import Path
from PySide6 import QtCore, QtGui, QtWidgets
import sys, traceback
import os
import shutil
import sqlite3
import base64
import json
import datetime
from pathlib import Path
import hashlib
import hmac
import winreg
import base64
from io import BytesIO
from PIL import Image
import pystray
import win32crypt
from Crypto.Cipher import AES
import asyncio
from winsdk.windows.security.credentials.ui import UserConsentVerifier


from pathlib import Path
if getattr(sys, "frozen", False):
    base_path = Path(sys._MEIPASS)
else:
    base_path = Path(__file__).parent


def excepthook(exc_type, exc_value, exc_tb):
    with open("error.log", "w", encoding="utf-8") as f:
        traceback.print_exception(exc_type, exc_value, exc_tb, file=f)
def get_hwnd(widget: QtWidgets.QWidget) -> int:
    hwnd = widget.winId()
    return int(hwnd) 
sys.excepthook = excepthook

try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u"com.passwxrd.app")
except Exception:
    pass


ICON_B64 = """
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
"""

icon_bytes = base64.b64decode(ICON_B64)
async def _require_windows_hello():
    try:
        availability = await UserConsentVerifier.check_availability_async()
        if availability != 0:
            return True
        result = await UserConsentVerifier.request_verification_async("Get access to Passwxrd")
        return result == 0
    except Exception as e:
        print(f"Windows Hello error: {e}")
        return False

def require_windows_hello():
    try:
        if hasattr(QtCore.QThread, 'currentThread'):
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(_require_windows_hello())
                return result
            finally:
                loop.close()
        else:
            return asyncio.run(_require_windows_hello())
    except Exception as e:
        print(f"Windows Hello authentication failed: {e}")
        return False
  

LOCALAPPDATA = os.getenv("LOCALAPPDATA") 
APP_DIR = Path(LOCALAPPDATA) / "passwxrd"
BACKUP_DIR = APP_DIR / "backups"
EXPORT_DIR = APP_DIR / "exports"
APP_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

SETTINGS_PATH = APP_DIR / "settings.json"
MASTER_PATH = APP_DIR / "master.json"

CHROMIUM = {
    "chrome": Path(LOCALAPPDATA) / "Google/Chrome/User Data",
    "edge": Path(LOCALAPPDATA) / "Microsoft/Edge/User Data",
    "brave": Path(LOCALAPPDATA) / "BraveSoftware/Brave-Browser/User Data",
    "chromium": Path(LOCALAPPDATA) / "Chromium/User Data",
    "opera": Path(LOCALAPPDATA) / "Opera Software/Opera Stable",
}

def load_settings():
    if SETTINGS_PATH.exists():
        try:
            return json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"auto_lock_enabled": True, "autostart_enabled": True}

def save_settings(s):
    try:
        SETTINGS_PATH.write_text(json.dumps(s, indent=2), encoding="utf-8")
    except Exception:
        pass

def set_setting(key, value):
    s = load_settings()
    s[key] = value
    save_settings(s)

def get_setting(key, default=None):
    s = load_settings()
    return s.get(key, default)

def set_autostart(enabled: bool, exe_path: str):
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_ALL_ACCESS) as k:
            if enabled:
                winreg.SetValueEx(k, "passwxrd", 0, winreg.REG_SZ, f"\"{exe_path}\"")
            else:
                try:
                    winreg.DeleteValue(k, "passwxrd")
                except FileNotFoundError:
                    pass
        set_setting("autostart_enabled", enabled)
        return True
    except Exception:
        return False

def is_autostart_enabled():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run") as k:
            val, _ = winreg.QueryValueEx(k, "passwxrd")
            return bool(val)
    except FileNotFoundError:
        return False
    except Exception:
        return False

def master_exists():
    return MASTER_PATH.exists()

def _pbkdf2(password: str, salt: bytes, iterations: int = 200000, dklen: int = 32):
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations, dklen)

def set_master_password(password: str):
    salt = os.urandom(16)
    hashv = _pbkdf2(password, salt)
    data = {"salt": base64.b64encode(salt).decode(), "hash": base64.b64encode(hashv).decode(), "iter": 200000}
    MASTER_PATH.write_text(json.dumps(data), encoding="utf-8")
    return True

def verify_master_password(password: str):
    if not master_exists():
        return False
    try:
        data = json.loads(MASTER_PATH.read_text(encoding="utf-8"))
        salt = base64.b64decode(data["salt"])
        stored = base64.b64decode(data["hash"])
        calc = _pbkdf2(password, salt, data.get("iter", 200000))
        return hmac.compare_digest(stored, calc)
    except Exception:
        return False

def reset_master_password(new_password: str):
    return set_master_password(new_password)

def get_encryption_key(browser: str, user_data_root: Path):
    state_path = user_data_root / "Local State"
    if not state_path.exists():
        return None
    with open(state_path, "r", encoding="utf-8") as f:
        local_state = json.load(f)
    key_b64 = local_state.get("os_crypt", {}).get("encrypted_key")
    if not key_b64:
        return None
    key = base64.b64decode(key_b64)[5:]
    return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]

def decrypt_password(buff: bytes, key: bytes) -> str:
    try:
        if buff and buff[:3] == b"v10":
            iv = buff[3:15]
            payload = buff[15:]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            decrypted = cipher.decrypt(payload)[:-16]
            return decrypted.decode("utf-8", errors="ignore")
        return win32crypt.CryptUnprotectData(buff, None, None, None, 0)[1].decode("utf-8", errors="ignore")
    except Exception:
        return ""

def iter_chromium_profiles():
    items = []
    for browser, root in CHROMIUM.items():
        if not root.exists():
            continue
        if browser == "opera":
            db_path = root / "Login Data"
            if db_path.exists():
                items.append((browser, "Default", db_path, root))
            continue
        for child in root.iterdir():
            if not child.is_dir():
                continue
            db_path = child / "Login Data"
            if db_path.exists():
                items.append((browser, child.name, db_path, root))
    return items

def list_profiles():
    out = []
    for b, profile, db_path, _root in iter_chromium_profiles():
        out.append((b, profile))
    return out

def list_all_passwords():
    results = []
    seen = set()
    for browser, profile, db_path, root in iter_chromium_profiles():
        key = get_encryption_key(browser, root)
        if key is None:
            continue
        try:
            tmp = BACKUP_DIR / f"{browser}_{profile}_LoginData_copy.db"
            shutil.copy2(db_path, tmp)
        except Exception:
            tmp = db_path
        try:
            conn = sqlite3.connect(str(tmp))
            cur = conn.cursor()
            cur.execute("SELECT origin_url, action_url, username_value, password_value, signon_realm, id FROM logins")
            rows = cur.fetchall()
            conn.close()
        except Exception:
            rows = []
        for row in rows:
            url = row[0] or row[1] or ""
            username = row[2] or ""
            enc = row[3]
            pw = decrypt_password(enc, key) if enc else ""
            entry_id = int(row[5])
            sig = (browser, profile, entry_id)
            if sig in seen:
                continue
            seen.add(sig)
            results.append({
                "browser": browser,
                "profile": profile,
                "url": url,
                "username": username,
                "password": pw,
                "entry_id": entry_id,
                "db_path": str(db_path),
                "root": str(root),
            })
    return results

def backup_db(db_path: str):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = BACKUP_DIR / f"{Path(db_path).stem}_{ts}.db"
    try:
        shutil.copy2(db_path, dest)
    except Exception:
        pass
    return dest

def encrypt_password(password: str, key: bytes) -> bytes:
    iv = os.urandom(12)
    cipher = AES.new(key, AES.MODE_GCM, iv)
    encrypted, tag = cipher.encrypt_and_digest(password.encode("utf-8"))
    return b"v10" + iv + encrypted + tag

def update_entry(entry, new_url, new_username, new_password):
    db_path = entry["db_path"]
    backup_db(db_path)
    root = Path(entry["root"])
    key = get_encryption_key(entry["browser"], root)
    if key is None:
        return False
    enc = encrypt_password(new_password, key)
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("UPDATE logins SET origin_url=?, username_value=?, password_value=? WHERE id=?",
                    (new_url, new_username, enc, entry["entry_id"]))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

def delete_entry(entry):
    db_path = entry["db_path"]
    backup_db(db_path)
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("DELETE FROM logins WHERE id=?", (entry["entry_id"],))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

def add_entry(browser: str, profile: str, url: str, username: str, password: str):
    target = None
    root = None
    for b, p, dbp, r in iter_chromium_profiles():
        if b == browser and p == profile:
            target = dbp
            root = r
            break
    if target is None:
        return False
    backup_db(str(target))
    key = get_encryption_key(browser, root)
    if key is None:
        return False
    enc = encrypt_password(password, key)
    try:
        conn = sqlite3.connect(str(target))
        cur = conn.cursor()
        cur.execute("INSERT INTO logins (origin_url, username_value, password_value) VALUES (?, ?, ?)",
                    (url, username, enc))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

def move_entry(entry, target_browser: str, target_profile: str):
    ok = add_entry(target_browser, target_profile, entry["url"], entry["username"], entry["password"])
    if ok:
        delete_entry(entry)
    return ok

def make_universal(entry):
    ok_any = False
    for b, p, _dbp, _r in iter_chromium_profiles():
        ok = add_entry(b, p, entry["url"], entry["username"], entry["password"])
        if ok:
            ok_any = True
    return ok_any

def export_passwords(entries, filename: str = None):
    if filename is None:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = EXPORT_DIR / f"export_{ts}.csv"
    with open(filename, "w", encoding="utf-8", newline="") as f:
        f.write("browser,profile,url,username,password\n")
        for e in entries:
            b = e.get("browser", "")
            p = e.get("profile", "")
            u = (e.get("url", "") or "").replace(",", " ")
            n = (e.get("username", "") or "").replace(",", " ")
            pw = (e.get("password", "") or "").replace(",", " ")
            f.write(f"{b},{p},{u},{n},{pw}\n")
    return filename

def all_profiles_struct():
    out = {}
    for b, p, _dbp, _r in iter_chromium_profiles():
        out.setdefault(b, []).append(p)
    return out

class TitleBar(QtWidgets.QWidget):
    toggle_sidebar = QtCore.Signal()
    def __init__(self, parent=None, title="passwxrd"):
        super().__init__(parent)
        self._start_pos = None
        self._pressed = False
        self.setFixedHeight(40)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(8)
        self.btn_menu = QtWidgets.QToolButton()
        self.btn_menu.setText("☰")
        self.btn_menu.clicked.connect(self.toggle_sidebar.emit)
        layout.addWidget(self.btn_menu)
        self.icon_label = QtWidgets.QLabel()
        self.icon_label.setFixedSize(24, 24)
        layout.addWidget(self.icon_label)
        self.title_label = QtWidgets.QLabel(title)
        font = self.title_label.font()
        font.setPointSize(10)
        self.title_label.setFont(font)
        layout.addWidget(self.title_label, 1)
        self.clock_label = QtWidgets.QLabel("")
        self.clock_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.clock_label.setMinimumWidth(200)
        layout.addWidget(self.clock_label)
        self.btn_min = QtWidgets.QToolButton()
        self.btn_min.setText("—")
        self.btn_max = QtWidgets.QToolButton()
        self.btn_max.setText("□")
        self.btn_close = QtWidgets.QToolButton()
        self.btn_close.setText("✕")
        for b in (self.btn_min, self.btn_max, self.btn_close):
            b.setAutoRaise(True)
        self.btn_min.clicked.connect(lambda: self.window().showMinimized())
        self.btn_max.clicked.connect(self.on_max_restore)
        self.btn_close.clicked.connect(self.on_close_to_tray)
        layout.addWidget(self.btn_min)
        layout.addWidget(self.btn_max)
        layout.addWidget(self.btn_close)
        self.setStyleSheet("QLabel{color:#ddd} QToolButton{color:#ddd}")
    def set_icon(self, icon: QtGui.QIcon):
        pix = icon.pixmap(24, 24)
        self.icon_label.setPixmap(pix)
    def set_clock_text(self, text: str):
        self.clock_label.setText(text)
    def on_max_restore(self):
        w = self.window()
        if w.isMaximized():
            w.showNormal()
            self.btn_max.setText("□")
        else:
            w.showMaximized()
            self.btn_max.setText("❐")
    def on_close_to_tray(self):
        w = self.window()
        if hasattr(w, "main_content") and hasattr(w.main_content, "send_to_tray"):
            w.main_content.send_to_tray()
        else:
            w.hide()
    def mousePressEvent(self, e):
        if e.button() == QtCore.Qt.LeftButton:
            self._pressed = True
            self._start_pos = e.globalPosition().toPoint()
            self._window_start = self.window().frameGeometry().topLeft()
            e.accept()
    def mouseMoveEvent(self, e):
        if self._pressed:
            delta = e.globalPosition().toPoint() - self._start_pos
            self.window().move(self._window_start + delta)
            e.accept()
    def mouseReleaseEvent(self, e):
        self._pressed = False
    def mouseDoubleClickEvent(self, e):
        self.on_max_restore()

class FramelessWindow(QtWidgets.QWidget):
    def __init__(self, content_widget: QtWidgets.QWidget, title="passwxrd"):
        super().__init__(None, QtCore.Qt.Window)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlag(QtCore.Qt.WindowSystemMenuHint, True)
        v = QtWidgets.QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        self.titlebar = TitleBar(self, title)
        self.titlebar.toggle_sidebar.connect(content_widget.toggle_sidebar)
        v.addWidget(self.titlebar)
        v.addWidget(content_widget)
        self.setStyleSheet("""
            QWidget#Sidebar { background-color: #1f1f1f; color: #eaeaea; }
            QWidget { background-color: #141414; color: #eaeaea; }
            QPushButton { padding: 8px; border-radius: 8px; background:#232323; border:1px solid #3a3a3a; }
            QPushButton:hover { background:#2e2e2e; }
            QLineEdit, QComboBox, QCheckBox { background:#1b1b1b; border:1px solid #3a3a3a; border-radius:6px; padding:6px; color:#eaeaea; }
            QTableWidget { gridline-color:#3a3a3a; background:#161616; alternate-background-color:#151515; }
            QHeaderView::section { background:#1d1d1d; color:#cfcfcf; border:1px solid #3a3a3a; padding:6px; }
            QMenu { background:#1b1b1b; color:#eaeaea; border:1px solid #3a3a3a; }
        """)
    def setWindowIcon(self, icon: QtGui.QIcon):
        super().setWindowIcon(icon)
        self.titlebar.set_icon(icon)

class HomePage(QtWidgets.QWidget):
    def __init__(self, switch_callback):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        label = QtWidgets.QLabel("passwxrd")
        f = label.font()
        f.setPointSize(18)
        f.setBold(True)
        label.setFont(f)
        layout.addWidget(label)
        grid = QtWidgets.QGridLayout()
        tiles = [
            ("Password Lab", lambda: switch_callback("lab")),
            ("Discord", lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl("https://discord.com"))),
            ("Support", lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl("https://support.microsoft.com"))),
            ("Settings", lambda: switch_callback("settings")),
        ]
        for i, (text, action) in enumerate(tiles):
            btn = QtWidgets.QPushButton(text)
            btn.setFixedSize(160, 160)
            btn.setStyleSheet("""
                QPushButton{background:#202020;border:1px solid #3f3f3f;border-radius:12px;}
                QPushButton:hover{background:#2a2a2a;border-color:#6aa0ff;}
            """)
            btn.clicked.connect(action)
            grid.addWidget(btn, i // 2, i % 2)
        layout.addLayout(grid)
        layout.addStretch()

class EditDialog(QtWidgets.QDialog):
    def __init__(self, entry, parent=None):
        super().__init__(parent)
        self.entry = entry
        self.setWindowTitle("Edit Password")
        form = QtWidgets.QFormLayout(self)
        self.url_edit = QtWidgets.QLineEdit(entry.get("url", ""))
        self.user_edit = QtWidgets.QLineEdit(entry.get("username", ""))
        self.pass_edit = QtWidgets.QLineEdit(entry.get("password", ""))
        self.pass_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.show_cb = QtWidgets.QCheckBox("Show password")
        self.show_cb.stateChanged.connect(self.toggle_show)
        form.addRow("URL", self.url_edit)
        form.addRow("Username", self.user_edit)
        form.addRow("Password", self.pass_edit)
        form.addRow("", self.show_cb)
        self.transfer_btn = QtWidgets.QPushButton("Transfer to profile")
        self.transfer_menu = QtWidgets.QMenu(self)
        profs = all_profiles_struct()
        for b, plist in profs.items():
            for p in plist:
                act = self.transfer_menu.addAction(f"{b}/{p}")
                act.triggered.connect(lambda _, br=b, pr=p: self.transfer_to(br, pr))
        self.transfer_btn.setMenu(self.transfer_menu)
        self.universal_btn = QtWidgets.QPushButton("Make universal")
        self.universal_btn.clicked.connect(self.make_universal)
        self.save_btn = QtWidgets.QPushButton("Save")
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        row = QtWidgets.QHBoxLayout()
        row.addWidget(self.transfer_btn)
        row.addWidget(self.universal_btn)
        row.addStretch()
        row.addWidget(self.save_btn)
        row.addWidget(self.cancel_btn)
        form.addRow(row)
    def toggle_show(self, state):
        self.pass_edit.setEchoMode(QtWidgets.QLineEdit.Normal if state else QtWidgets.QLineEdit.Password)
    def transfer_to(self, browser, profile):
        ok = move_entry(self.entry, browser, profile)
        QtWidgets.QMessageBox.information(self, "Transfer", "Moved" if ok else "Failed")
    def make_universal(self):
        ok = make_universal(self.entry)
        QtWidgets.QMessageBox.information(self, "Universal", "Done" if ok else "Failed")

class PasswordLab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        v = QtWidgets.QVBoxLayout(self)
        top = QtWidgets.QHBoxLayout()
        self.search = QtWidgets.QLineEdit()
        self.search.setPlaceholderText("Search URL or username")
        self.search.textChanged.connect(self.filter_table)
        self.add_btn = QtWidgets.QPushButton("Add")
        self.add_btn.clicked.connect(self.add_entry)
        self.edit_btn = QtWidgets.QPushButton("Edit")
        self.edit_btn.clicked.connect(self.edit_entry)
        self.del_btn = QtWidgets.QPushButton("Delete")
        self.del_btn.clicked.connect(self.delete_entry)
        self.copy_btn = QtWidgets.QPushButton("Copy Password")
        self.copy_btn.clicked.connect(self.copy_password)
        self.export_btn = QtWidgets.QPushButton("Export Selected")
        self.export_btn.clicked.connect(self.export_selected)
        for w in (self.search, self.add_btn, self.edit_btn, self.del_btn, self.copy_btn, self.export_btn):
            top.addWidget(w)
        v.addLayout(top)
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Browser", "Profile", "URL", "Username", "Password"])
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        v.addWidget(self.table)
        self.refresh()
    def refresh(self):
        data = list_all_passwords()
        self.all_entries = data
        self.table.setRowCount(len(data))
        for i, e in enumerate(data):
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(e["browser"]))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(e["profile"]))
            self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(e["url"]))
            self.table.setItem(i, 3, QtWidgets.QTableWidgetItem(e["username"]))
            self.table.setItem(i, 4, QtWidgets.QTableWidgetItem(e["password"]))
        self.table.resizeColumnsToContents()
    def filter_table(self, text):
        t = text.lower()
        for row in range(self.table.rowCount()):
            url = self.table.item(row, 2).text().lower() if self.table.item(row, 2) else ""
            user = self.table.item(row, 3).text().lower() if self.table.item(row, 3) else ""
            show = (t in url) or (t in user)
            self.table.setRowHidden(row, not show)
    def get_selected_entry(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self.all_entries):
            return None
        return self.all_entries[row]
    def add_entry(self):
        profs = all_profiles_struct()
        default_browser = None
        default_profile = None
        for b, plist in profs.items():
            if plist:
                default_browser = b
                default_profile = plist[0]
                break
        dlg = EditDialog({"url": "", "username": "", "password": "", "browser": default_browser or "chrome", "profile": default_profile or "Default"}, self)
        if dlg.exec():
            add_entry(default_browser or "chrome", default_profile or "Default", dlg.url_edit.text(), dlg.user_edit.text(), dlg.pass_edit.text())
            self.refresh()
    def edit_entry(self):
        entry = self.get_selected_entry()
        if not entry:
            return
        dlg = EditDialog(entry, self)
        if dlg.exec():
            update_entry(entry, dlg.url_edit.text(), dlg.user_edit.text(), dlg.pass_edit.text())
            self.refresh()
    def delete_entry(self):
        entry = self.get_selected_entry()
        if entry and QtWidgets.QMessageBox.question(self, "Delete", "Delete this password?") == QtWidgets.QMessageBox.Yes:
            delete_entry(entry)
            self.refresh()
    def copy_password(self):
        entry = self.get_selected_entry()
        if entry:
            QtWidgets.QApplication.clipboard().setText(entry["password"])
    def export_selected(self):
        entry = self.get_selected_entry()
        if entry:
            path = export_passwords([entry])
            QtWidgets.QMessageBox.information(self, "Export", f"Exported to {path}")

class ExportLab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        v = QtWidgets.QVBoxLayout(self)
        btn = QtWidgets.QPushButton("Export All to CSV")
        btn.clicked.connect(self.export_all)
        v.addWidget(btn)
        v.addStretch()
    def export_all(self):
        data = list_all_passwords()
        path = export_passwords(data)
        QtWidgets.QMessageBox.information(self, "Export", f"Passwords exported to {path}")

class SafePage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel("Windows verification required. Complete Windows Hello to continue.")) 
        layout.addStretch()

class SettingsPage(QtWidgets.QWidget):
    autostart_toggled = QtCore.Signal(bool)
    autolock_toggled = QtCore.Signal(bool)
    reset_master_requested = QtCore.Signal()
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        self.theme_toggle = QtWidgets.QCheckBox("Dark Theme")
        self.theme_toggle.setChecked(True)
        layout.addWidget(self.theme_toggle)
        self.export_path = QtWidgets.QLineEdit(str(EXPORT_DIR))
        layout.addWidget(QtWidgets.QLabel("Export Directory"))
        layout.addWidget(self.export_path)
        self.auto_start = QtWidgets.QCheckBox("Start with Windows")
        self.auto_start.setChecked(is_autostart_enabled())
        layout.addWidget(self.auto_start)
        self.auto_lock = QtWidgets.QCheckBox("Enable Auto-lock")
        self.auto_lock.setChecked(get_setting("auto_lock_enabled", True))
        layout.addWidget(self.auto_lock)
        self.reset_master = QtWidgets.QPushButton("Reset Master Password (Windows Hello)")
        layout.addWidget(self.reset_master)
        layout.addStretch()
        self.auto_start.stateChanged.connect(lambda s: self.autostart_toggled.emit(bool(s)))
        self.auto_lock.stateChanged.connect(lambda s: self.autolock_toggled.emit(bool(s)))
        self.reset_master.clicked.connect(self.reset_master_requested.emit)

class MasterSetupDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Create Master Password")
        form = QtWidgets.QFormLayout(self)
        self.p1 = QtWidgets.QLineEdit()
        self.p1.setEchoMode(QtWidgets.QLineEdit.Password)
        self.p2 = QtWidgets.QLineEdit()
        self.p2.setEchoMode(QtWidgets.QLineEdit.Password)
        self.show_cb = QtWidgets.QCheckBox("Show passwords")
        self.show_cb.stateChanged.connect(self.toggle_show)
        form.addRow("Password", self.p1)
        form.addRow("Confirm", self.p2)
        form.addRow("", self.show_cb)
        btn = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        btn.accepted.connect(self.accept)
        btn.rejected.connect(self.reject)
        form.addRow(btn)
    def toggle_show(self, state):
        mode = QtWidgets.QLineEdit.Normal if state else QtWidgets.QLineEdit.Password
        self.p1.setEchoMode(mode)
        self.p2.setEchoMode(mode)
    def get_password(self):
        return self.p1.text() if self.p1.text() and self.p1.text() == self.p2.text() else None

class MasterLoginDialog(QtWidgets.QDialog):
    reset_requested = QtCore.Signal()
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enter Master Password")
        form = QtWidgets.QFormLayout(self)
        self.p = QtWidgets.QLineEdit()
        self.p.setEchoMode(QtWidgets.QLineEdit.Password)
        form.addRow("Master Password", self.p)
        btns = QtWidgets.QHBoxLayout()
        self.ok_btn = QtWidgets.QPushButton("OK")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.reset_btn = QtWidgets.QPushButton("Reset Password")
        btns.addWidget(self.ok_btn)
        btns.addWidget(self.cancel_btn)
        btns.addWidget(self.reset_btn)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        self.reset_btn.clicked.connect(self.on_reset)
        form.addRow(btns)
    def get_password(self):
        return self.p.text()
    def on_reset(self):
        self.reset_requested.emit()
        self.reject()

class MainWindow(QtWidgets.QWidget):
    clock_tick = QtCore.Signal(str)
    def __init__(self, app_ref: QtWidgets.QApplication):
        super().__init__()
        self.app_ref = app_ref
        h = QtWidgets.QHBoxLayout(self)
        self.sidebar = QtWidgets.QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(160)
        self.sidebar.hide()
        side_layout = QtWidgets.QVBoxLayout(self.sidebar)
        btn_home = QtWidgets.QPushButton("Home")
        btn_home.clicked.connect(lambda: self.switch_page("home"))
        btn_lab = QtWidgets.QPushButton("Password Lab")
        btn_lab.clicked.connect(lambda: self.switch_page("lab"))
        btn_export = QtWidgets.QPushButton("Export Lab")
        btn_export.clicked.connect(lambda: self.switch_page("export"))
        btn_settings = QtWidgets.QPushButton("Settings")
        btn_settings.clicked.connect(lambda: self.switch_page("settings"))
        btn_lock = QtWidgets.QPushButton("Lock Now")
        btn_lock.clicked.connect(self.lock_now)
        for b in (btn_home, btn_lab, btn_export, btn_settings, btn_lock):
            side_layout.addWidget(b)
        side_layout.addStretch()
        self.pages = QtWidgets.QStackedWidget()
        self.home = HomePage(self.switch_page)
        self.lab = PasswordLab()
        self.export = ExportLab()
        self.settings = SettingsPage()
        self.safepage = SafePage()
        self.pages.addWidget(self.home)
        self.pages.addWidget(self.lab)
        self.pages.addWidget(self.export)
        self.pages.addWidget(self.settings)
        self.pages.addWidget(self.safepage)
        h.addWidget(self.sidebar)
        h.addWidget(self.pages, 1)
        self.switch_page("home")
        self.titlebar_ref = None
        self.time_left = 5 * 60
        self.clock_timer = QtCore.QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(icon_bytes)
        APP_ICON = QtGui.QIcon(pixmap)
        icon = QtGui.QIcon(APP_ICON) if APP_ICON else self.app_ref.windowIcon()
        self.tray_icon.setIcon(icon)
        m = QtWidgets.QMenu()
        a_open = m.addAction("Open Passwxrd")
        a_open.triggered.connect(self.restore_from_tray)
        a_lock = m.addAction("Lock Vault")
        a_lock.triggered.connect(self.lock_now)
        m.addSeparator()
        a_exit = m.addAction("Exit")
        a_exit.triggered.connect(self.exit_app)
        self.tray_icon.setContextMenu(m)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()
        self.settings.autostart_toggled.connect(self.on_autostart_toggled)
        self.settings.autolock_toggled.connect(self.on_autolock_toggled)
        self.settings.reset_master_requested.connect(self.on_reset_master)
        self.clock_tick.connect(self.on_clock_tick)
        self.apply_autolock_ui()

    def send_to_tray(self):
        if hasattr(self, "parentWidget") and self.parentWidget():
            self.parentWidget().hide()
        else:
            self.hide()

        self.clock_timer.stop()
        if self.titlebar_ref:
            self.titlebar_ref.set_clock_text("Auto-lock: Off (tray)")
        self.tray_icon.showMessage(
            "passwxrd",
            "Still running in the background (auto-lock paused).",
            QtWidgets.QSystemTrayIcon.Information,
            2500    
        )


    def set_titlebar(self, titlebar):
        self.titlebar_ref = titlebar
        self.on_clock_tick(self.format_time())

    def toggle_sidebar(self):
        self.sidebar.setVisible(not self.sidebar.isVisible())

    def switch_page(self, name):
        if name == "home":
            self.pages.setCurrentWidget(self.home)
        elif name == "lab":
            self.lab.refresh()
            self.pages.setCurrentWidget(self.lab)
        elif name == "export":
            self.pages.setCurrentWidget(self.export)
        elif name == "settings":
            self.pages.setCurrentWidget(self.settings)
        elif name == "safe":
            self.pages.setCurrentWidget(self.safepage)

    def format_time(self):
        m, s = divmod(self.time_left, 60)
        return f"{m:02d}:{s:02d}"

    def apply_autolock_ui(self):
        if get_setting("auto_lock_enabled", True):
            if not self.clock_timer.isActive():
                self.clock_timer.start(1000)
            if self.titlebar_ref:
                self.titlebar_ref.set_clock_text("Auto-lock: " + self.format_time())
        else:
            self.clock_timer.stop()
            if self.titlebar_ref:
                self.titlebar_ref.set_clock_text("Auto-lock: Off")

    def update_clock(self):
        if not get_setting("auto_lock_enabled", True):
            return
        self.time_left -= 1
        if self.time_left < 0:
            self.time_left = 0
        self.clock_tick.emit("Auto-lock: " + self.format_time())
        if self.time_left == 0:
            if require_windows_hello():
                self.time_left = 5 * 60
                self.clock_tick.emit("Auto-lock: " + self.format_time())
            else:
                QtWidgets.QMessageBox.warning(self, "Locked", "Session locked.")
                QtWidgets.QApplication.quit()

    def on_clock_tick(self, text):
        if self.titlebar_ref:
            self.titlebar_ref.set_clock_text(text)

    def lock_now(self):
        self.switch_page("safe")
        QtWidgets.QMessageBox.information(self, "Locked", "Session locked. Complete Windows Hello to continue.")
        if require_windows_hello():
            self.time_left = 5 * 60
            self.clock_tick.emit("Auto-lock: " + self.format_time())
            self.switch_page("home")
        else:
            QtWidgets.QMessageBox.warning(self, "Authentication failed", "Closing application.")
            QtWidgets.QApplication.quit()

    def on_autostart_toggled(self, enabled):
        exe = sys.executable
        if exe.lower().endswith("python.exe") or exe.lower().endswith("pythonw.exe"):
            exe = os.path.abspath(sys.argv[0])
        ok = set_autostart(bool(enabled), exe)
        if not ok:
            QtWidgets.QMessageBox.warning(self, "Autostart", "Failed to update Start with Windows.")

    def on_autolock_toggled(self, enabled):
        set_setting("auto_lock_enabled", bool(enabled))
        self.apply_autolock_ui()

    def on_reset_master(self):
        if not require_windows_hello():
            QtWidgets.QMessageBox.warning(self, "Windows Hello", "Verification failed.")
            return
        dlg = MasterSetupDialog()
        if dlg.exec():
            pw = dlg.get_password()
            if not pw:
                QtWidgets.QMessageBox.warning(self, "Master Password", "Passwords do not match.")
                return
            reset_master_password(pw)
            QtWidgets.QMessageBox.information(self, "Master Password", "Master password reset.")

    def restore_from_tray(self):
        if hasattr(self, "parentWidget") and self.parentWidget():
            self.parentWidget().showNormal()
            self.parentWidget().raise_()
            self.parentWidget().activateWindow()
        else:
            self.showNormal()
            self.raise_()
            self.activateWindow()

        if get_setting("auto_lock_enabled", True):
            self.time_left = 5 * 60
            self.clock_timer.start(1000)
            self.clock_tick.emit("Auto-lock: " + self.format_time())


    def on_tray_activated(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.Trigger:
            if self.isHidden():
                self.restore_from_tray()
            else:
                self.send_to_tray()

    def closeEvent(self, event):
        event.ignore()
        self.send_to_tray()

    def exit_app(self):
        self.tray_icon.hide()
        QtWidgets.QApplication.instance().quit()


def first_run_master_setup():
    if not master_exists():
        dlg = MasterSetupDialog()
        if dlg.exec():
            pw = dlg.get_password()
            if not pw:
                QtWidgets.QMessageBox.warning(None, "Master Password", "Passwords do not match.")
                return False
            set_master_password(pw)
            QtWidgets.QMessageBox.information(None, "Master Password", "Master password set.")
            return True
        return False
    return True

def require_master_login():
    if not master_exists():
        return True
    attempts = 3
    while attempts > 0:
        dlg = MasterLoginDialog()
        reset_triggered = []
        def do_reset():
            if require_windows_hello():
                if MASTER_PATH.exists():
                    MASTER_PATH.unlink()
                if not first_run_master_setup():
                    QtWidgets.QMessageBox.warning(None, "Master Password", "Password reset cancelled.")
                else:
                    QtWidgets.QMessageBox.information(None, "Master Password", "Password reset successful.")
                    reset_triggered.append(True)
            else:
                QtWidgets.QMessageBox.warning(None, "Windows Hello", "Verification failed.")
        dlg.reset_requested.connect(do_reset)
        if dlg.exec():
            pw = dlg.get_password()
            if verify_master_password(pw):
                return True
            attempts -= 1
            QtWidgets.QMessageBox.warning(None, "Master Password", f"Incorrect password. {attempts} attempt(s) left.")
        else:
            if reset_triggered:
                return True 
            return False
    return False
if __name__ == "__main__":
    if getattr(sys, "frozen", False):
        import ctypes
        from ctypes import wintypes
        try:
            kernel32 = ctypes.windll.kernel32
            user32 = ctypes.windll.user32
            kernel32.AllocConsole()
            console_window = kernel32.GetConsoleWindow()
            if console_window:
                user32.ShowWindow(console_window, 0) 
            import os
            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, 1) 
            os.dup2(devnull, 2) 
            os.close(devnull)  
        except Exception:
              pass 
    app = QtWidgets.QApplication(sys.argv)
    if not require_windows_hello():
        sys.exit(0)
    if not first_run_master_setup():
        sys.exit(0)
    if not require_master_login():
        sys.exit(0)
    main_content = MainWindow(app)
    win = FramelessWindow(main_content, title="passwxrd")
    win.main_content = main_content
    main_content.set_titlebar(win.titlebar)
    pixmap = QtGui.QPixmap()
    pixmap.loadFromData(icon_bytes)
    APP_ICON = QtGui.QIcon(pixmap)
    app.setWindowIcon(APP_ICON)
    win.setWindowIcon(APP_ICON)
    win.resize(1100, 680)
    win.show()
    sys.exit(app.exec())
