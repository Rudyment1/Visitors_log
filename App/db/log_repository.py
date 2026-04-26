# ──────────────────────────────────────────────────────────
#  db/log_repository.py  –  журнал действий пользователей
# ──────────────────────────────────────────────────────────
import sqlite3
from datetime import datetime
from constants import DB_AUDIT_LOG


class LogRepository:
    """Записывает и читает лог действий сотрудников."""

    def __init__(self):
        self.conn = sqlite3.connect(DB_AUDIT_LOG)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp  TEXT NOT NULL,
                user       TEXT NOT NULL,
                action     TEXT NOT NULL,
                details    TEXT
            )
        """)
        self.conn.commit()

    # ── Запись ────────────────────────────────────────────

    def log(self, user: str, action: str, details: str = ""):
        self.conn.execute(
            "INSERT INTO audit_log (timestamp, user, action, details) VALUES (?,?,?,?)",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user, action, details)
        )
        self.conn.commit()

    # ── Чтение ────────────────────────────────────────────

    def get_all(self) -> list:
        return self.conn.execute(
            "SELECT * FROM audit_log ORDER BY id DESC"
        ).fetchall()