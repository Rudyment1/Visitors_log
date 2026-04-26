# ──────────────────────────────────────────────────────────
#  ui/report_dialog.py  –  отчёт за период из двух БД
#
#  Логика выборки:
#    период целиком ≤ 3 дней назад  → только visitors_recent
#    период целиком > 3 дней назад  → только visitors_all
#    смежный период (захватывает обе) → recent + all, дедупликация по fio+date+entry_time
# ──────────────────────────────────────────────────────────
import os
from datetime import date, timedelta

import pandas as pd
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QDateEdit, QPushButton, QLabel, QMessageBox, QFileDialog,
)
from PySide6.QtCore import QDate, Qt

from constants import ARCHIVE_DAYS

REPORT_COLUMNS = [
    "ID", "Дата", "ФИО", "Организация", "Основание",
    "Сопровождение", "ФИО сопров.", "Вход", "Выход", "Пропустил",
]


class ReportDialog(QDialog):
    """Диалог выбора периода и экспорта в Excel.
    Принимает два репозитория: recent и all.
    """

    def __init__(self, recent_repo, all_repo, parent=None):
        super().__init__(parent)
        self._recent = recent_repo
        self._all = all_repo
        self.setWindowTitle("Создать отчёт")
        self.setMinimumWidth(380)
        self._build_ui()

    # ── Интерфейс ─────────────────────────────────────────

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        title = QLabel("Выберите период для отчёта")
        title.setStyleSheet("font-size: 14px; font-weight: 600; color: #cdd6f4;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDisplayFormat("dd.MM.yyyy")
        self.date_from.setDate(QDate.currentDate().addDays(-7))

        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDisplayFormat("dd.MM.yyyy")
        self.date_to.setDate(QDate.currentDate())

        form.addRow("С:", self.date_from)
        form.addRow("По:", self.date_to)
        layout.addLayout(form)

        # Быстрые кнопки
        quick = QHBoxLayout()
        quick.setSpacing(6)
        for label, days in [("Сегодня", 0), ("Неделя", 7), ("Месяц", 30), ("Год", 365)]:
            btn = QPushButton(label)
            btn.setFixedHeight(28)
            btn.setStyleSheet("font-size: 11px;")
            btn.setAutoDefault(False)
            btn.clicked.connect(lambda _, d=days: self._set_period(d))
            quick.addWidget(btn)
        layout.addLayout(quick)

        # Источник данных и счётчик
        self.source_label = QLabel("")
        self.source_label.setAlignment(Qt.AlignCenter)
        self.source_label.setStyleSheet("color: #89b4fa; font-size: 11px;")
        layout.addWidget(self.source_label)

        self.count_label = QLabel("")
        self.count_label.setAlignment(Qt.AlignCenter)
        self.count_label.setStyleSheet("color: #6c7086; font-size: 12px;")
        layout.addWidget(self.count_label)

        self.date_from.dateChanged.connect(self._update_count)
        self.date_to.dateChanged.connect(self._update_count)
        self._update_count()

        # Кнопки
        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Отмена")
        btn_cancel.setAutoDefault(False)
        btn_cancel.setDefault(False)
        btn_cancel.clicked.connect(self.reject)

        btn_export = QPushButton("📥 Сохранить Excel")
        btn_export.setObjectName("btn_save")
        btn_export.setAutoDefault(False)
        btn_export.setDefault(False)
        btn_export.clicked.connect(self._export)

        btn_row.addWidget(btn_cancel)
        btn_row.addStretch()
        btn_row.addWidget(btn_export)
        layout.addLayout(btn_row)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            return
        super().keyPressEvent(event)

    # ── Логика выборки ────────────────────────────────────

    def _cutoff_date(self) -> date:
        """Граница между recent и all БД."""
        return date.today() - timedelta(days=ARCHIVE_DAYS)

    def _get_rows(self) -> tuple[list, str]:
        """Возвращает (строки, описание_источника)."""
        d_from = self.date_from.date().toPython()
        d_to = self.date_to.date().toPython()
        cutoff = self._cutoff_date()

        d_from_str = d_from.isoformat()
        d_to_str = d_to.isoformat()

        if d_to >= cutoff and d_from >= cutoff:
            rows = self._recent.get_by_period(d_from_str, d_to_str)
            source = "📋 Источник: рабочий журнал"

        elif d_to < cutoff:
            rows = self._all.get_by_period(d_from_str, d_to_str)
            source = "🗄 Источник: полный архив"

        else:
            rows_recent = self._recent.get_by_period(d_from_str, d_to_str)
            rows_all = self._all.get_by_period(d_from_str, d_to_str)

            seen = set()
            rows = []

            for r in list(rows_all) + list(rows_recent):
                key = (str(r[2]), str(r[1]), str(r[7]))  # fio, date, entry_time
                if key not in seen:
                    seen.add(key)
                    rows.append(r)

            rows.sort(key=lambda r: (str(r[1]), str(r[7])))
            source = "🔀 Источник: рабочий журнал + полный архив"

        return rows, source

    def _set_period(self, days: int):
        self.date_to.setDate(QDate.currentDate())
        self.date_from.setDate(QDate.currentDate().addDays(-days))

    def _update_count(self):
        rows, source = self._get_rows()
        self.source_label.setText(source)
        self.count_label.setText(f"Записей за период: {len(rows)}")

    # ── Экспорт ───────────────────────────────────────────

    def _export(self):
        rows, source = self._get_rows()
        if not rows:
            QMessageBox.information(self, "Отчёт", "За выбранный период нет записей.")
            return

        default_filename = (
            f"отчёт_{self.date_from.date().toString('yyyy-MM-dd')}"
            f"_{self.date_to.date().toString('yyyy-MM-dd')}.xlsx"
        )

        default_path = os.path.join(os.path.expanduser("~"), default_filename)

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить отчёт",
            default_path,
            "Excel files (*.xlsx)"
        )

        if not file_path:
            return

        if not file_path.lower().endswith(".xlsx"):
            file_path += ".xlsx"

        try:
            df = pd.DataFrame([tuple(r) for r in rows], columns=REPORT_COLUMNS)
            df["Дата"] = df["Дата"].apply(
                lambda x: f"{str(x)[8:10]}.{str(x)[5:7]}.{str(x)[:4]}"
                if len(str(x)) == 10 else x
            )

            df.to_excel(file_path, index=False)

            QMessageBox.information(
                self,
                "Отчёт создан",
                f"Сохранено записей: {len(rows)}\n"
                f"Файл: {file_path}"
            )
            self.accept()

        except Exception as exc:
            QMessageBox.critical(
                self,
                "Ошибка сохранения",
                f"Не удалось сохранить Excel-файл:\n{exc}"
            )