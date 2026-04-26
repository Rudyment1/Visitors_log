# ──────────────────────────────────────────────────────────
#  db/backup_manager.py  –  еженедельное резервное копирование БД
# ──────────────────────────────────────────────────────────
import os
import shutil
from datetime import datetime, timedelta

from constants import DB_USERS, DB_VISITORS, DB_VISITORS_ALL, DB_AUDIT_LOG

BACKUP_DIR = "backups"
BACKUP_INTERVAL = 7   # дней между бэкапами


class BackupManager:
    """Создаёт еженедельные копии всех БД в папку backups/."""

    def __init__(self):
        os.makedirs(BACKUP_DIR, exist_ok=True)
        self._stamp_file = os.path.join(BACKUP_DIR, ".last_backup")

    def run_if_needed(self) -> bool:
        """Создаёт бэкап, если прошло BACKUP_INTERVAL дней."""
        if not self._is_due():
            return False
        self._create_backup()
        self._write_stamp()
        return True

    def _is_due(self) -> bool:
        if not os.path.exists(self._stamp_file):
            return True

        try:
            with open(self._stamp_file, "r", encoding="utf-8") as f:
                last = f.read().strip()
            last_dt = datetime.fromisoformat(last)
            return datetime.now() - last_dt >= timedelta(days=BACKUP_INTERVAL)
        except Exception:
            return True

    def _create_backup(self):
        ts = datetime.now().strftime("%Y-%m-%d")
        folder = os.path.join(BACKUP_DIR, ts)
        os.makedirs(folder, exist_ok=True)

        for db_path in (DB_USERS, DB_VISITORS, DB_VISITORS_ALL, DB_AUDIT_LOG):
            if os.path.exists(db_path):
                dst = os.path.join(folder, os.path.basename(db_path))
                shutil.copy2(db_path, dst)

    def _write_stamp(self):
        with open(self._stamp_file, "w", encoding="utf-8") as f:
            f.write(datetime.now().isoformat())