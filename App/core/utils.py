# ──────────────────────────────────────────────────────────
#  core/utils.py  –  вспомогательные функции
# ──────────────────────────────────────────────────────────
import hashlib
from datetime import datetime, date


def hash_password(password: str) -> str:
    """SHA-256 хэш пароля."""
    return hashlib.sha256(password.encode()).hexdigest()


def today_str() -> str:
    """Сегодняшняя дата в формате ISO (YYYY-MM-DD)."""
    return str(date.today())


def now_time_str() -> str:
    """Текущее время в формате HH:MM."""
    return datetime.now().strftime("%H:%M")


def format_date_display(iso_date: str) -> str:
    """Преобразует ISO-дату в отображаемый формат DD.MM.YYYY."""
    try:
        return datetime.strptime(iso_date, "%Y-%m-%d").strftime("%d.%m.%Y")
    except ValueError:
        return iso_date


def parse_date_to_iso(display_date: str) -> str:
    """Преобразует отображаемую дату DD.MM.YYYY обратно в ISO YYYY-MM-DD."""
    try:
        return datetime.strptime(display_date, "%d.%m.%Y").strftime("%Y-%m-%d")
    except ValueError:
        return display_date  # уже ISO или неизвестный формат — вернуть как есть