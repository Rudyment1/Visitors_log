# ──────────────────────────────────────────────────────────
#  constants.py  –  глобальные константы приложения
# ──────────────────────────────────────────────────────────

APP_NAME    = "Журнал посетителей"
DB_USERS    = "users.db"
DB_VISITORS = "visitors_recent.db"
EXCEL_PATH  = "visitors_history.xlsx"
DB_VISITORS_ALL = "visitors_all.db"
DB_AUDIT_LOG = "audit_log.db"


ARCHIVE_DAYS = 3   # записи старше N дней уходят в архив
RECENT_DAYS  = 30  # сколько дней показывать в таблице

# ── Индексы столбцов таблицы посетителей ─────────────────
COL_ID            = 0   # скрытый, хранит DB id
COL_NUM           = 1   # порядковый номер (генерируется при загрузке)
COL_DATE          = 2
COL_FIO           = 3
COL_ORG           = 4
COL_REASON        = 5
COL_ACCOMPANY_FIO = 6
COL_ENTRY         = 7
COL_EXIT          = 8

TABLE_HEADERS = [
    "ID", "№", "Дата", "ФИО", "Организация", "Основание",
    "ФИО сопров.", "Вход", "Выход",
]


ROLES = ["guard", "admin"]
ACCOMPANY_OPTIONS = ["Нет", "Да"]

# ── QSS / тёмная тема (Catppuccin Mocha) ─────────────────
APP_STYLESHEET = """
QMainWindow, QDialog, QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
}

/* ── Поля ввода ── */
QLineEdit, QComboBox, QDateEdit, QTimeEdit {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px 10px;
    color: #cdd6f4;
    selection-background-color: #89b4fa;
}
QLineEdit:focus, QComboBox:focus,
QDateEdit:focus, QTimeEdit:focus {
    border-color: #89b4fa;
}

/* ── Кнопки (базовые) ── */
QPushButton {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 7px 16px;
    color: #cdd6f4;
    font-weight: 500;
}
QPushButton:hover   { background-color: #45475a; border-color: #89b4fa; }
QPushButton:pressed { background-color: #181825; }

/* ── Кнопки-акценты ── */
QPushButton#btn_add   { background-color: #a6e3a1; color: #1e1e2e; border: none; font-weight: 600; }
QPushButton#btn_add:hover   { background-color: #94d89e; }

QPushButton#btn_save  { background-color: #89b4fa; color: #1e1e2e; border: none; font-weight: 600; }
QPushButton#btn_save:hover  { background-color: #74a8f8; }

QPushButton#btn_del   { background-color: #f38ba8; color: #1e1e2e; border: none; font-weight: 600; }
QPushButton#btn_del:hover   { background-color: #eb7fa0; }

QPushButton#btn_login {
    background-color: #89b4fa; color: #1e1e2e;
    border: none; font-weight: 700;
    padding: 10px 24px; font-size: 14px;
}
QPushButton#btn_login:hover { background-color: #74a8f8; }

/* ── Таблица ── */
QTableWidget {
    background-color: #181825;
    alternate-background-color: #1e1e2e;
    border: 1px solid #313244;
    border-radius: 8px;
    gridline-color: #313244;
    color: #cdd6f4;
    selection-background-color: #45475a;
}
QTableWidget::item { padding: 4px 8px; }

QHeaderView::section {
    background-color: #313244;
    color: #89b4fa;
    font-weight: 600;
    padding: 8px;
    border: none;
    border-right: 1px solid #45475a;
    border-bottom: 1px solid #45475a;
}

/* ── Скроллбары ── */
QScrollBar:vertical {
    background: #1e1e2e; width: 8px; border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #45475a; border-radius: 4px; min-height: 20px;
}
QScrollBar::handle:vertical:hover { background: #89b4fa; }

QScrollBar:horizontal {
    background: #1e1e2e; height: 8px; border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background: #45475a; border-radius: 4px; min-width: 20px;
}
QScrollBar::handle:horizontal:hover { background: #89b4fa; }

/* ── Прочее ── */
QStatusBar {
    background: #181825;
    color: #6c7086;
    border-top: 1px solid #313244;
}

QComboBox::drop-down { border: none; padding-right: 8px; }
QComboBox QAbstractItemView {
    background-color: #313244;
    border: 1px solid #45475a;
    selection-background-color: #45475a;
    color: #cdd6f4;
}
"""
