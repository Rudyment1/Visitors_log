# ──────────────────────────────────────────────────────────
#  db/all_visitors_repository.py  –  архив посетителей
#  Здесь хранятся записи, удалённые из рабочего журнала.
# ──────────────────────────────────────────────────────────
import sqlite3
from constants import DB_VISITORS_ALL


class AllVisitorsRepository:
    """Архив посетителей."""

    def __init__(self):
        self.conn = sqlite3.connect(DB_VISITORS_ALL)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS visitors_all (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                date          TEXT,
                fio           TEXT,
                org           TEXT,
                reason        TEXT,
                accompany     TEXT,
                accompany_fio TEXT,
                entry_time    TEXT,
                exit_time     TEXT,
                passed_by     TEXT
            )
        """)
        self.conn.commit()

    # ── Запись ────────────────────────────────────────────

    def add(self, data: tuple):
        """
        Добавляет запись в архив.
        data = (date, fio, org, reason, accompany,
                accompany_fio, entry_time, exit_time, passed_by)
        """
        self.conn.execute("""
            INSERT INTO visitors_all
                (date, fio, org, reason, accompany,
                 accompany_fio, entry_time, exit_time, passed_by)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, data)
        self.conn.commit()

    # ── Чтение ────────────────────────────────────────────

    def get_all(self) -> list:
        return self.conn.execute(
            "SELECT * FROM visitors_all ORDER BY date DESC, entry_time DESC"
        ).fetchall()

    def get_by_period(self, date_from: str, date_to: str) -> list:
        """Возвращает записи за период [date_from, date_to] включительно."""
        return self.conn.execute(
            """SELECT * FROM visitors_all
               WHERE date >= ? AND date <= ?
               ORDER BY date, entry_time""",
            (date_from, date_to)
        ).fetchall()

    def get_count(self) -> int:
        return self.conn.execute(
            "SELECT COUNT(*) FROM visitors_all"
        ).fetchone()[0]