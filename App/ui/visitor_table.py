# ──────────────────────────────────────────────────────────
#  ui/visitor_table.py  –  таблица посетителей с подсветкой
# ──────────────────────────────────────────────────────────

from typing import Any

from PySide6.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush

from constants import (
    TABLE_HEADERS,
    COL_ID,
    COL_NUM,
    COL_DATE,
    COL_ENTRY,
    COL_EXIT,
)
from core.utils import format_date_display, parse_date_to_iso


COLOR_INSIDE_BG = QColor("#2d1e2e")
COLOR_INSIDE_FG = QColor("#f5c2e7")
COLOR_DEFAULT_FG = QColor("#cdd6f4")


_DB_ID = 0
_DB_DATE = 1
_DB_FIO = 2
_DB_ORG = 3
_DB_REASON = 4
_DB_ACCOMPANY = 5
_DB_ACCOMPANY_FIO = 6
_DB_ENTRY = 7
_DB_EXIT = 8


class VisitorTable(QTableWidget):
    """Таблица журнала посетителей."""

    def __init__(self, parent=None):
        super().__init__(0, len(TABLE_HEADERS), parent)
        self._setup()

    def _setup(self):
        self.setHorizontalHeaderLabels(TABLE_HEADERS)

        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        for col in (COL_NUM, COL_ENTRY, COL_EXIT):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)

        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setColumnHidden(COL_ID, True)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(32)

    def populate(self, records: list[Any]):
        """Очищает таблицу и заполняет записями из БД."""
        self.setRowCount(0)

        for num, record in enumerate(records, start=1):
            row = self.rowCount()
            self.insertRow(row)
            self._fill_row(row, record, num)

        self.refresh_colors()

    def _fill_row(self, row: int, record: Any, num: int):
        db = list(record)

        self._set_item(row, COL_ID, str(db[_DB_ID]))
        self._set_item(row, COL_NUM, str(num))
        self._set_item(row, COL_DATE, format_date_display(db[_DB_DATE] or ""))

        self._set_item(row, 3, str(db[_DB_FIO] or ""))
        self._set_item(row, 4, str(db[_DB_ORG] or ""))
        self._set_item(row, 5, str(db[_DB_REASON] or ""))

        accompany_fio = ""
        if db[_DB_ACCOMPANY] == "Да":
            accompany_fio = str(db[_DB_ACCOMPANY_FIO] or "")

        self._set_item(row, 6, accompany_fio)
        self._set_item(row, COL_ENTRY, str(db[_DB_ENTRY] or ""))
        self._set_item(row, COL_EXIT, str(db[_DB_EXIT] or ""))

    def _set_item(self, row: int, col: int, text: str):
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setItem(row, col, item)

    def refresh_colors(self):
        """Подсвечивает строки посетителей, которые ещё внутри."""
        for row in range(self.rowCount()):
            if self.isRowHidden(row):
                continue

            entry = self._cell_text(row, COL_ENTRY)
            exit_ = self._cell_text(row, COL_EXIT)

            self._color_row(row, highlight=bool(entry) and not bool(exit_))

    def _color_row(self, row: int, highlight: bool):
        for col in range(1, self.columnCount()):
            item = self.item(row, col)

            if item is None:
                continue

            if highlight:
                item.setBackground(QBrush(COLOR_INSIDE_BG))
                item.setForeground(QBrush(COLOR_INSIDE_FG))
            else:
                item.setBackground(QBrush())
                item.setForeground(QBrush(COLOR_DEFAULT_FG))

    def _cell_text(self, row: int, col: int) -> str:
        item = self.item(row, col)

        if item is None:
            return ""

        return item.text().strip()

    def row_as_dict(self, row: int) -> dict[str, str]:
        """Возвращает данные строки. Дата — всегда ISO YYYY-MM-DD."""
        return {
            "id": self._cell_text(row, COL_ID),
            "date": parse_date_to_iso(self._cell_text(row, COL_DATE)),
            "fio": self._cell_text(row, 3),
            "org": self._cell_text(row, 4),
            "reason": self._cell_text(row, 5),
            "accompany_fio": self._cell_text(row, 6),
            "entry_time": self._cell_text(row, COL_ENTRY),
            "exit_time": self._cell_text(row, COL_EXIT),
        }