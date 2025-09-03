import sys
import os
import ctypes
from pathlib import Path
from PySide6 import QtCore, QtGui, QtWidgets
import core
from auth import require_windows_hello

try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u"com.passwxrd.app")
except Exception:
    pass

APP_ICON = "icon.ico"

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
        # ❌ minimize to tray via MainWindow helper
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
        # Call MainWindow.send_to_tray() through the frameless wrapper
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
        profs = core.all_profiles_struct()
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
        ok = core.move_entry(self.entry, browser, profile)
        QtWidgets.QMessageBox.information(self, "Transfer", "Moved" if ok else "Failed")
    def make_universal(self):
        ok = core.make_universal(self.entry)
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
        data = core.list_all_passwords()
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
        profs = core.all_profiles_struct()
        default_browser = None
        default_profile = None
        for b, plist in profs.items():
            if plist:
                default_browser = b
                default_profile = plist[0]
                break
        dlg = EditDialog({"url": "", "username": "", "password": "", "browser": default_browser or "chrome", "profile": default_profile or "Default"}, self)
        if dlg.exec():
            core.add_entry(default_browser or "chrome", default_profile or "Default", dlg.url_edit.text(), dlg.user_edit.text(), dlg.pass_edit.text())
            self.refresh()
    def edit_entry(self):
        entry = self.get_selected_entry()
        if not entry:
            return
        dlg = EditDialog(entry, self)
        if dlg.exec():
            core.update_entry(entry, dlg.url_edit.text(), dlg.user_edit.text(), dlg.pass_edit.text())
            self.refresh()
    def delete_entry(self):
        entry = self.get_selected_entry()
        if entry and QtWidgets.QMessageBox.question(self, "Delete", "Delete this password?") == QtWidgets.QMessageBox.Yes:
            core.delete_entry(entry)
            self.refresh()
    def copy_password(self):
        entry = self.get_selected_entry()
        if entry:
            QtWidgets.QApplication.clipboard().setText(entry["password"])
    def export_selected(self):
        entry = self.get_selected_entry()
        if entry:
            path = core.export_passwords([entry])
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
        data = core.list_all_passwords()
        path = core.export_passwords(data)
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
        self.export_path = QtWidgets.QLineEdit(str(core.EXPORT_DIR))
        layout.addWidget(QtWidgets.QLabel("Export Directory"))
        layout.addWidget(self.export_path)
        self.auto_start = QtWidgets.QCheckBox("Start with Windows")
        self.auto_start.setChecked(core.is_autostart_enabled())
        layout.addWidget(self.auto_start)
        self.auto_lock = QtWidgets.QCheckBox("Enable Auto-lock")
        self.auto_lock.setChecked(core.get_setting("auto_lock_enabled", True))
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
        icon = QtGui.QIcon(APP_ICON) if Path(APP_ICON).exists() else self.app_ref.windowIcon()
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

    # NEW: Single place that handles minimizing to tray
    def send_to_tray(self):
    # Hide the outer FramelessWindow, not just MainWindow
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
        if core.get_setting("auto_lock_enabled", True):
            if not self.clock_timer.isActive():
                self.clock_timer.start(1000)
            if self.titlebar_ref:
                self.titlebar_ref.set_clock_text("Auto-lock: " + self.format_time())
        else:
            self.clock_timer.stop()
            if self.titlebar_ref:
                self.titlebar_ref.set_clock_text("Auto-lock: Off")

    def update_clock(self):
        if not core.get_setting("auto_lock_enabled", True):
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
        ok = core.set_autostart(bool(enabled), exe)
        if not ok:
            QtWidgets.QMessageBox.warning(self, "Autostart", "Failed to update Start with Windows.")

    def on_autolock_toggled(self, enabled):
        core.set_setting("auto_lock_enabled", bool(enabled))
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
            core.reset_master_password(pw)
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

        if core.get_setting("auto_lock_enabled", True):
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
    if not core.master_exists():
        dlg = MasterSetupDialog()
        if dlg.exec():
            pw = dlg.get_password()
            if not pw:
                QtWidgets.QMessageBox.warning(None, "Master Password", "Passwords do not match.")
                return False
            core.set_master_password(pw)
            QtWidgets.QMessageBox.information(None, "Master Password", "Master password set.")
            return True
        return False
    return True

def require_master_login():
    if not core.master_exists():
        return True
    attempts = 3
    while attempts > 0:
        dlg = MasterLoginDialog()
        # Connect reset action
        reset_triggered = []
        def do_reset():
            if require_windows_hello():
                if core.MASTER_PATH.exists():
                    core.MASTER_PATH.unlink()
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
            if core.verify_master_password(pw):
                return True
            attempts -= 1
            QtWidgets.QMessageBox.warning(None, "Master Password", f"Incorrect password. {attempts} attempt(s) left.")
        else:
            if reset_triggered:
                return True  # reset succeeded, skip login
            return False
    return False

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    if Path(APP_ICON).exists():
        app.setWindowIcon(QtGui.QIcon(APP_ICON))
    if not require_windows_hello():
        pass
    if not first_run_master_setup():
        sys.exit(0)
    if not require_master_login():
        sys.exit(0)
    main_content = MainWindow(app)
    win = FramelessWindow(main_content, title="passwxrd")
    # Keep a back-reference so TitleBar can reach MainWindow for tray actions
    win.main_content = main_content
    main_content.set_titlebar(win.titlebar)
    if Path(APP_ICON).exists():
        win.setWindowIcon(QtGui.QIcon(APP_ICON))
    win.resize(1100, 680)
    win.show()
    sys.exit(app.exec())
