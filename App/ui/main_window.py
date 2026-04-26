# ──────────────────────────────────────────────────────────
#  ui/main_window.py  –  главное окно приложения
# ──────────────────────────────────────────────────────────
from datetime import datetime

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QStatusBar, QMessageBox,
)
from PySide6.QtCore import QTimer

from db.visitor_repository import VisitorRepository
from db.log_repository import LogRepository
from db.all_visitors_repository import AllVisitorsRepository
from db.backup_manager import BackupManager
from ui.visitor_table import VisitorTable
from ui.visitor_dialog import VisitorDialog
from ui.user_manager_dialog import UserManagerDialog
from ui.audit_log_dialog import AuditLogDialog
from ui.report_dialog import ReportDialog
from core.utils import now_time_str
from constants import APP_NAME


class MainWindow(QMainWindow):
    """Главное окно журнала посетителей."""

    def __init__(self, user):
        super().__init__()
        self.visitor_repo     = VisitorRepository()
        self.log_repo         = LogRepository()
        self.all_visitors_repo = AllVisitorsRepository()

        self.current_user_role = user["role"]
        self.current_user_name = user["full_name"]

        self.setWindowTitle(APP_NAME)
        self.resize(1400, 650)

        self._build_ui()
        self._load_visitors()
        self._archive_old_records()
        self._run_backup()
        self._start_refresh_timer()

    # ── Построение интерфейса ─────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setSpacing(10)
        root.setContentsMargins(12, 10, 12, 10)

        root.addLayout(self._build_toolbar())
        root.addWidget(self._build_stats_label())
        root.addWidget(self._build_table())

        self.setStatusBar(self._build_status_bar())

    def _build_toolbar(self) -> QHBoxLayout:
        bar = QHBoxLayout()
        bar.setSpacing(8)

        # Блок пользователя: имя + кнопка выхода под ним
        user_block = QVBoxLayout()
        user_block.setSpacing(2)

        user_label = QLabel(f"👤  {self.current_user_name}  [{self.current_user_role}]")
        user_label.setStyleSheet("color: #a6e3a1; font-weight: 600;")

        btn_logout = QPushButton("Выйти")
        btn_logout.setFixedHeight(20)
        btn_logout.setStyleSheet(
            "font-size: 11px; padding: 0px 8px;"
            "background-color: #f38ba8; color: #1e1e2e; border: none;"
        )
        btn_logout.clicked.connect(self._logout)

        user_block.addWidget(user_label)
        user_block.addWidget(btn_logout)

        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("🔍  Поиск по ФИО, организации, основанию...")
        self.search_field.setMinimumWidth(280)
        self.search_field.textChanged.connect(self._filter_table)

        btn_add  = self._make_button("＋ Добавить",       "btn_add", self._add_visitor)
        btn_edit = self._make_button("✏ Редактировать",   None,      self._edit_visitor)
        btn_exit = self._make_button("🚪 Отметить выход", None,      self._mark_exit)
        btn_del  = self._make_button("✕ Удалить",         "btn_del", self._delete_visitor)

        bar.addLayout(user_block)
        bar.addSpacing(8)
        bar.addWidget(self.search_field)
        bar.addStretch()
        bar.addWidget(btn_add)
        bar.addWidget(btn_edit)
        bar.addWidget(btn_exit)
        bar.addWidget(btn_del)

        if self.current_user_role == "admin":
            btn_report = self._make_button("📊 Отчёт",            None, self._open_report)
            btn_users  = self._make_button("⚙ Пользователи",      None, lambda: UserManagerDialog(self).exec())
            btn_log    = self._make_button("📋 Журнал действий",   None, lambda: AuditLogDialog(self).exec())
            bar.addWidget(btn_report)
            bar.addWidget(btn_users)
            bar.addWidget(btn_log)

        return bar

    def _build_stats_label(self) -> QLabel:
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet(
            "color: #6c7086; font-size: 12px; padding: 2px 4px;"
        )
        return self.stats_label

    def _build_table(self) -> VisitorTable:
        self.visitor_table = VisitorTable()
        self.visitor_table.doubleClicked.connect(self._edit_visitor)
        return self.visitor_table

    def _build_status_bar(self) -> QStatusBar:
        bar = QStatusBar()
        self.status_label = QLabel()
        bar.addWidget(self.status_label)
        return bar

    @staticmethod
    def _make_button(text: str, object_name: str | None,
                     slot) -> QPushButton:
        btn = QPushButton(text)
        if object_name:
            btn.setObjectName(object_name)
        btn.clicked.connect(slot)
        return btn

    # ── Загрузка данных ───────────────────────────────────

    def _load_visitors(self):
        records = self.visitor_repo.get_recent()
        self.visitor_table.populate(records)
        self._update_stats()
        self._update_status(f"Записей загружено: {self.visitor_table.rowCount()}")

    def _update_stats(self):
        today_count, inside_count = self.visitor_repo.get_stats()
        self.stats_label.setText(
            f"Сегодня посетителей: {today_count}   |   "
            f"Сейчас в здании: {inside_count}   |   "
            f"Всего в журнале: {self.visitor_table.rowCount()}"
        )

    def _update_status(self, message: str = ""):
        ts = datetime.now().strftime("%d.%m.%Y  %H:%M")
        self.status_label.setText(f"{message}   {ts}")

    # ── Действия с посетителями ───────────────────────────

    def _add_visitor(self):
        dlg = VisitorDialog(
            self,
            org_suggestions=self.visitor_repo.get_organizations(),
            fio_suggestions=self.visitor_repo.get_fio_list(),
            accompany_fio_suggestions=self.visitor_repo.get_accompany_fio_list(),
        )
        if dlg.exec() != VisitorDialog.DialogCode.Accepted or not dlg.result_data:
            return

        d = dlg.result_data
        row_data = (
            d["date"], d["fio"], d["org"], d["reason"],
            d["accompany"], d["accompany_fio"],
            d["entry_time"], d["exit_time"],
            self.current_user_name,
        )
        self.visitor_repo.create(row_data)
        self.log_repo.log(self.current_user_name, "ДОБАВЛЕНИЕ",
                          f"{d['fio']} / {d['org']}")
        self._load_visitors()
        self._update_status(f"Добавлен: {d['fio']}")

    def _edit_visitor(self):
        row = self.visitor_table.currentRow()
        if row == -1:
            QMessageBox.information(
                self, "Редактирование",
                "Выберите строку для редактирования."
            )
            return

        data = self.visitor_table.row_as_dict(row)
        dlg = VisitorDialog(
            self,
            initial_data=data,
            org_suggestions=self.visitor_repo.get_organizations(),
            fio_suggestions=self.visitor_repo.get_fio_list(),
            accompany_fio_suggestions=self.visitor_repo.get_accompany_fio_list(),
        )
        if dlg.exec() != VisitorDialog.DialogCode.Accepted or not dlg.result_data:
            return

        visitor_id = int(data["id"]) if data["id"] else None
        if not visitor_id:
            return

        d = dlg.result_data
        self.visitor_repo.update(visitor_id, (
            d["date"], d["fio"], d["org"], d["reason"],
            d["accompany"], d["accompany_fio"],
            d["entry_time"], d["exit_time"],
            self.current_user_name,
        ))

        # Формируем детальный лог изменений
        changes = []
        field_names = {
            "fio":           "ФИО",
            "org":           "Организация",
            "reason":        "Основание",
            "accompany_fio": "Сопровождающий",
            "entry_time":    "Вход",
            "exit_time":     "Выход",
            "date":          "Дата",
        }
        for field, label in field_names.items():
            old = (data.get(field) or "").strip()
            new = (d.get(field) or "").strip()
            if old != new:
                changes.append(f"{label}: «{old}» → «{new}»")

        details = f"{d['fio']} | " + ("; ".join(changes) if changes else "без изменений")
        self.log_repo.log(self.current_user_name, "РЕДАКТИРОВАНИЕ", details)
        self._load_visitors()
        self._update_status(f"Обновлено: {d['fio']}")

    def _mark_exit(self):
        row = self.visitor_table.currentRow()
        if row == -1:
            QMessageBox.information(self, "Выход", "Выберите запись.")
            return

        data = self.visitor_table.row_as_dict(row)
        if not data["id"]:
            return

        if data["exit_time"]:
            QMessageBox.information(
                self, "Выход",
                "Время выхода уже зафиксировано."
            )
            return

        exit_time = now_time_str()
        accompany_fio = data["accompany_fio"]

        self.visitor_repo.update(int(data["id"]), (
            data["date"], data["fio"], data["org"], data["reason"],
            "Да" if accompany_fio else "Нет", accompany_fio,
            data["entry_time"], exit_time,
            self.current_user_name,
        ))

        self.log_repo.log(
            self.current_user_name,
            "ВЫХОД",
            f"{data['fio']} в {exit_time}"
        )

        self._load_visitors()
        self._update_status(f"Выход: {data['fio']} в {exit_time}")

    def _delete_visitor(self):
        row = self.visitor_table.currentRow()
        if row == -1:
            QMessageBox.information(self, "Удаление", "Выберите запись.")
            return

        data = self.visitor_table.row_as_dict(row)
        fio = data.get("fio") or "запись"

        answer = QMessageBox.question(
            self, "Удаление",
            f"Удалить запись «{fio}»?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        if data["id"]:
            self.visitor_repo.delete(int(data["id"]))

        self.log_repo.log(self.current_user_name, "УДАЛЕНИЕ", fio)
        self.visitor_table.removeRow(row)
        self._update_stats()
        self._update_status(f"Удалено: {fio}")

    # ── Выход из учётной записи ───────────────────────────

    def _logout(self):
        self.log_repo.log(self.current_user_name, "ВЫХОД ИЗ СИСТЕМЫ")
        self._timer.stop()
        from ui.login_window import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

    def _filter_table(self):
        text = self.search_field.text().lower().strip()
        for row in range(self.visitor_table.rowCount()):
            data = self.visitor_table.row_as_dict(row)
            match = (
                not text
                or text in data.get("fio", "").lower()
                or text in data.get("org", "").lower()
                or text in data.get("reason", "").lower()
                or text in data.get("accompany_fio", "").lower()
            )
            self.visitor_table.setRowHidden(row, not match)

    # ── Отчёт ─────────────────────────────────────────────

    def _open_report(self):
        ReportDialog(self.visitor_repo, self.all_visitors_repo, self).exec()

    # ── Архив ─────────────────────────────────────────────

    def _archive_old_records(self):
        """При запуске переносит старые записи из рабочего журнала в архив."""
        rows, count = self.visitor_repo.get_old_records()
        if not rows:
            return

        for r in rows:
            self.all_visitors_repo.add((
                r["date"], r["fio"], r["org"], r["reason"],
                r["accompany"], r["accompany_fio"],
                r["entry_time"], r["exit_time"], r["passed_by"]
            ))

        self.visitor_repo.delete_old_records()
        self._update_status(f"Перенесено в архив: {count} записей")

    # ── Бэкап ─────────────────────────────────────────────

    def _run_backup(self):
        created = BackupManager().run_if_needed()
        if created:
            self._update_status("Резервная копия БД создана")

    def _start_refresh_timer(self):
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_timer_tick)
        self._timer.start(60_000)  # каждую минуту

    def _on_timer_tick(self):
        self.visitor_table.refresh_colors()
        self._update_status()