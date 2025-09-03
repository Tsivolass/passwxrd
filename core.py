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

import win32crypt
from Crypto.Cipher import AES

LOCALAPPDATA = os.getenv("LOCALAPPDATA") or ""
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
    return {"auto_lock_enabled": True, "autostart_enabled": False}

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
