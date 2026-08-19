import sqlite3
import os
import secrets
from typing import Optional, Dict, Any

def get_app_data_dir() -> str:
    appdata = os.environ.get("APPDATA")
    if not appdata:
        appdata = os.path.expanduser("~")
    data_dir = os.path.join(appdata, "SnapClip")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

DB_PATH = os.path.join(get_app_data_dir(), "snapclip.db")

class DatabaseManager:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Settings
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS config (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            # Active Pairing Session (current PIN)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS active_pin (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    pin TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Paired Devices & Tokens
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS paired_devices (
                    token TEXT PRIMARY KEY,
                    device_name TEXT NOT NULL,
                    paired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            
            # Ensure PIN exists
            self.get_or_create_pin()

    def get_or_create_pin(self) -> str:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT pin FROM active_pin WHERE id = 1")
            row = cursor.fetchone()
            if row:
                return row["pin"]
            else:
                # Generate new 6-digit numeric PIN
                pin = f"{secrets.randbelow(900000) + 100000:06d}"
                cursor.execute("INSERT INTO active_pin (id, pin) VALUES (1, ?)", (pin,))
                conn.commit()
                return pin

    def rotate_pin(self) -> str:
        pin = f"{secrets.randbelow(900000) + 100000:06d}"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO active_pin (id, pin) VALUES (1, ?)", (pin,))
            conn.commit()
        return pin

    def register_paired_device(self, token: str, device_name: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO paired_devices (token, device_name, last_seen)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (token, device_name))
            conn.commit()

    def is_token_valid(self, token: str) -> bool:
        if not token:
            return False
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT token FROM paired_devices WHERE token = ?", (token,))
            row = cursor.fetchone()
            if row:
                # Update last seen
                cursor.execute("UPDATE paired_devices SET last_seen = CURRENT_TIMESTAMP WHERE token = ?", (token,))
                conn.commit()
                return True
            return False

    def get_paired_devices(self) -> list[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT token, device_name, paired_at, last_seen FROM paired_devices")
            return [dict(row) for row in cursor.fetchall()]

    def remove_paired_device(self, token: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM paired_devices WHERE token = ?", (token,))
            conn.commit()

    def clear_all_paired_devices(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM paired_devices")
            conn.commit()

    def get_config(self, key: str, default: str = "") -> str:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM config WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row["value"] if row else default

    def set_config(self, key: str, value: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", (key, value))
            conn.commit()
