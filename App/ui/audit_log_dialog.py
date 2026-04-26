# ──────────────────────────────────────────────────────────
#  ui/audit_log_dialog.py  –  просмотр журнала действий
# ──────────────────────────────────────────────────────────
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QLabel, QLineEdit, QAbstractItemView,
)
from PySide6.QtCore import Qt

from db.log_repository import LogRepository


class AuditLogDialog(QDialog):
    """Диалог просмотра журнала действий сотрудников."""

    HEADERS = ["ID", "Дата и время", "Сотрудник", "Действие", "Подробности"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.log_repo = LogRepository()
        self.setWindowTitle("Журнал действий")
        self.resize(860, 500)
        self._build_ui()
        self._load()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Поиск
        top = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍  Поиск по сотруднику или действию...")
        self.search.textChanged.connect(self._filter)
        top.addWidget(self.search)
        layout.addLayout(top)

        # Таблица
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(self.HEADERS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(28)
        self.table.setColumnHidden(0, True)
        layout.addWidget(self.table)

        # Кнопка закрыть
        btn_row = QHBoxLayout()
        self.count_label = QLabel()
        self.count_label.setStyleSheet("color: #6c7086; font-size: 12px;")
        btn_close = QPushButton("Закрыть")
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(self.count_label)
        btn_row.addStretch()
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

    def _load(self):
        self.table.setRowCount(0)
        for record in self.log_repo.get_all():
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, val in enumerate(record):
                item = QTableWidgetItem(str(val) if val else "")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter if col != 4 else Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row, col, item)
        self._update_count()

    def _filter(self):
        text = self.search.text().lower().strip()
        visible = 0
        for row in range(self.table.rowCount()):
            user = (self.table.item(row, 2) or QTableWidgetItem("")).text().lower()
            action = (self.table.item(row, 3) or QTableWidgetItem("")).text().lower()
            details = (self.table.item(row, 4) or QTableWidgetItem("")).text().lower()
            match = not text or any(text in s for s in (user, action, details))
            self.table.setRowHidden(row, not match)
            if match:
                visible += 1
        self._update_count(visible)

    def _update_count(self, visible: int | None = None):
        total = self.table.rowCount()
        if visible is None:
            visible = total
        self.count_label.setText(f"Записей: {visible} из {total}")