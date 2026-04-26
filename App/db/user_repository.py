# ──────────────────────────────────────────────────────────
#  db/user_repository.py  –  работа с таблицей пользователей
# ──────────────────────────────────────────────────────────
import sqlite3
from constants import DB_USERS
from core.utils import hash_password


class UserRepository:
    """CRUD-операции для таблицы users."""

    def __init__(self):
        self.conn = sqlite3.connect(DB_USERS)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()
        self._seed_default_admin()

    # ── Инициализация ─────────────────────────────────────

    def _init_schema(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                username  TEXT UNIQUE NOT NULL,
                password  TEXT NOT NULL,
                role      TEXT NOT NULL,
                full_name TEXT
            )
        """)
        self.conn.commit()

    def _seed_default_admin(self):
        """Создаёт учётную запись creator, если её нет."""
        self.conn.execute("""
            INSERT OR IGNORE INTO users (username, password, role, full_name)
            VALUES ('creator', ?, 'admin', 'Author')
        """, (hash_password("1"),))
        self.conn.commit()

    # ── Чтение ────────────────────────────────────────────

    def get_all(self) -> list:
        return self.conn.execute(
            "SELECT id, username, role, full_name FROM users WHERE username != 'creator'"
        ).fetchall()

    def authenticate(self, username: str, password: str):
        """Возвращает строку пользователя или None."""
        return self.conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, hash_password(password))
        ).fetchone()

    # ── Запись ────────────────────────────────────────────

    def create(self, username: str, password: str,
               role: str, full_name: str):
        self.conn.execute(
            "INSERT INTO users (username, password, role, full_name) VALUES (?,?,?,?)",
            (username, hash_password(password), role, full_name)
        )
        self.conn.commit()

    def change_password(self, user_id: int, new_password: str):
        self.conn.execute(
            "UPDATE users SET password=? WHERE id=?",
            (hash_password(new_password), user_id)
        )
        self.conn.commit()

    def delete(self, user_id: int):
        self.conn.execute("DELETE FROM users WHERE id=?", (user_id,))
        self.conn.commit()