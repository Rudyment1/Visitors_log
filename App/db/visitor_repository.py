# ──────────────────────────────────────────────────────────
#  db/visitor_repository.py  –  работа с таблицей посетителей
# ──────────────────────────────────────────────────────────
import sqlite3
from datetime import datetime, timedelta

from constants import DB_VISITORS, ARCHIVE_DAYS


class VisitorRepository:
    """CRUD + архивация для таблицы visitors."""

    def __init__(self):
        self.conn = sqlite3.connect(DB_VISITORS)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    # ── Инициализация ─────────────────────────────────────

    def _init_schema(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS visitors (
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

    # ── Чтение ────────────────────────────────────────────

    def get_by_period(self, date_from: str, date_to: str) -> list:
        return self.conn.execute(
            """SELECT * FROM visitors
               WHERE date >= ? AND date <= ?
               ORDER BY date, entry_time""",
            (date_from, date_to)
        ).fetchall()

    def get_recent(self) -> list:
        return self.conn.execute(
            "SELECT * FROM visitors ORDER BY date DESC, entry_time DESC"
        ).fetchall()

    def get_organizations(self) -> list[str]:
        rows = self.conn.execute(
            "SELECT DISTINCT org FROM visitors WHERE org != '' ORDER BY org"
        ).fetchall()
        return [r[0] for r in rows if r[0]]

    def get_fio_list(self) -> list[str]:
        rows = self.conn.execute(
            "SELECT DISTINCT fio FROM visitors WHERE fio != '' ORDER BY fio"
        ).fetchall()
        return [r[0] for r in rows if r[0]]

    def get_accompany_fio_list(self) -> list[str]:
        rows = self.conn.execute(
            "SELECT DISTINCT accompany_fio FROM visitors WHERE accompany_fio != '' ORDER BY accompany_fio"
        ).fetchall()
        return [r[0] for r in rows if r[0]]

    def get_stats(self) -> tuple[int, int]:
        today = str(datetime.now().date())

        today_count = self.conn.execute(
            "SELECT COUNT(*) FROM visitors WHERE date=?",
            (today,)
        ).fetchone()[0]

        inside_count = self.conn.execute(
            """SELECT COUNT(*) FROM visitors
               WHERE entry_time != ''
                 AND (exit_time = '' OR exit_time IS NULL)"""
        ).fetchone()[0]

        return today_count, inside_count

    # ── Запись ────────────────────────────────────────────

    def create(self, data: tuple) -> int:
        """
        Добавляет запись.
        data = (date, fio, org, reason, accompany,
                accompany_fio, entry_time, exit_time, passed_by)
        """
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO visitors
                (date, fio, org, reason, accompany,
                 accompany_fio, entry_time, exit_time, passed_by)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, data)
        self.conn.commit()
        return cur.lastrowid

    def update(self, visitor_id: int, data: tuple):
        self.conn.execute("""
            UPDATE visitors SET
                date=?, fio=?, org=?, reason=?, accompany=?,
                accompany_fio=?, entry_time=?, exit_time=?, passed_by=?
            WHERE id=?
        """, (*data, visitor_id))
        self.conn.commit()

    def delete(self, visitor_id: int):
        self.conn.execute("DELETE FROM visitors WHERE id=?", (visitor_id,))
        self.conn.commit()

    # ── Перенос старых записей ────────────────────────────

    def get_old_records(self) -> tuple[list, int]:
        cutoff = (datetime.now() - timedelta(days=ARCHIVE_DAYS)).date()
        rows = self.conn.execute(
            "SELECT * FROM visitors WHERE date < ? ORDER BY date",
            (str(cutoff),)
        ).fetchall()
        return rows, len(rows)

    def delete_old_records(self):
        cutoff = (datetime.now() - timedelta(days=ARCHIVE_DAYS)).date()
        self.conn.execute(
            "DELETE FROM visitors WHERE date < ?",
            (str(cutoff),)
        )
        self.conn.commit()