# ──────────────────────────────────────────────────────────
#  ui/visitor_dialog.py
# ──────────────────────────────────────────────────────────
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QDateEdit, QTimeEdit,
    QPushButton, QMessageBox, QCompleter, QListView
)
from PySide6.QtCore import QDate, QTime, Qt, QEvent, QStringListModel


def _make_completer(suggestions: list[str]) -> QCompleter:
    model = QStringListModel(suggestions)
    c = QCompleter(model)
    c.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
    c.setFilterMode(Qt.MatchFlag.MatchStartsWith)
    c.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
    c.setMaxVisibleItems(6)
    popup = QListView()
    popup.setStyleSheet("""
        QListView {
            background: #313244;
            border: 1px solid #89b4fa;
            border-radius: 6px;
            color: #cdd6f4;
            font-size: 13px;
            outline: none;
        }
        QListView::item {
            padding: 6px 12px;
        }
        QListView::item:hover,
        QListView::item:selected {
            background: #45475a;
            color: #cdd6f4;
        }
    """)

    c.setPopup(popup)
    return c


class VisitorDialog(QDialog):
    """Форма для ввода / редактирования данных посетителя."""

    def __init__(
        self,
        parent=None,
        initial_data: dict | None = None,
        org_suggestions: list[str] | None = None,
        fio_suggestions: list[str] | None = None,
        accompany_fio_suggestions: list[str] | None = None,
    ):
        super().__init__(parent)
        is_edit = initial_data is not None
        self.setWindowTitle(
            "Редактировать посетителя" if is_edit else "Новый посетитель"
        )
        self.setMinimumWidth(440)

        self.result_data: dict | None = None
        self._org_suggestions           = list(org_suggestions or [])
        self._fio_suggestions           = list(fio_suggestions or [])
        self._accompany_fio_suggestions = list(accompany_fio_suggestions or [])
        self._build_ui()

        if is_edit:
            self._populate(initial_data)

    # ── Построение интерфейса ─────────────────────────────

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(10)

        # Дата
        self.field_date = QDateEdit()
        self.field_date.setCalendarPopup(True)
        self.field_date.setDate(QDate.currentDate())
        self.field_date.setDisplayFormat("dd.MM.yyyy")

        # ФИО
        self.field_fio = QLineEdit()
        self.field_fio.setPlaceholderText("Иванов Иван Иванович")
        self._fio_model = QStringListModel(self._fio_suggestions)
        self._fio_comp  = _make_completer(self._fio_suggestions)
        self._fio_comp.setModel(self._fio_model)
        self.field_fio.setCompleter(self._fio_comp)

        # Организация
        self.field_org = QLineEdit()
        self.field_org.setPlaceholderText("ООО «Компания»")
        self._org_model = QStringListModel(self._org_suggestions)
        self._org_comp  = _make_completer(self._org_suggestions)
        self._org_comp.setModel(self._org_model)
        self.field_org.setCompleter(self._org_comp)

        # Основание
        self.field_reason = QLineEdit()
        self.field_reason.setPlaceholderText("Временный пропуск")

        # ФИО сопровождающего
        self.field_accompany_fio = QLineEdit()
        self.field_accompany_fio.setPlaceholderText("Оставьте пустым если нет сопровождения")
        self._acc_model = QStringListModel(self._accompany_fio_suggestions)
        self._acc_comp  = _make_completer(self._accompany_fio_suggestions)
        self._acc_comp.setModel(self._acc_model)
        self.field_accompany_fio.setCompleter(self._acc_comp)

        # Время входа
        self.field_entry_time = QTimeEdit()
        self.field_entry_time.setTime(QTime.currentTime())
        self.field_entry_time.setDisplayFormat("HH:mm")

        # Время выхода
        self.field_exit_time = QTimeEdit()
        self.field_exit_time.setTime(QTime(0, 0))
        self.field_exit_time.setDisplayFormat("HH:mm")
        self.field_exit_time.setSpecialValueText("—")

        form.addRow("Дата:",             self.field_date)
        form.addRow("ФИО посетителя:",   self.field_fio)
        form.addRow("Организация:",      self.field_org)
        form.addRow("Основание визита:", self.field_reason)
        form.addRow("ФИО сопров.:",      self.field_accompany_fio)
        form.addRow("Время входа:",      self.field_entry_time)
        form.addRow("Время выхода:",     self.field_exit_time)

        layout.addLayout(form)
        layout.addLayout(self._build_buttons())

        for field in (self.field_fio, self.field_org,
                      self.field_reason, self.field_accompany_fio):
            field.installEventFilter(self)

    def _build_buttons(self) -> QHBoxLayout:
        row = QHBoxLayout()
        btn_cancel = QPushButton("Отмена")
        btn_cancel.clicked.connect(self.reject)
        btn_cancel.setAutoDefault(False)
        btn_cancel.setDefault(False)

        btn_ok = QPushButton("Сохранить")
        btn_ok.setObjectName("btn_save")
        btn_ok.clicked.connect(self._on_accept)
        btn_ok.setAutoDefault(False)
        btn_ok.setDefault(False)

        row.addWidget(btn_cancel)
        row.addStretch()
        row.addWidget(btn_ok)
        return row

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self.focusNextChild()
                return True
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            return
        super().keyPressEvent(event)

    # ── Логика ────────────────────────────────────────────

    def _populate(self, data: dict):
        if data.get("date"):
            self.field_date.setDate(
                QDate.fromString(data["date"], "yyyy-MM-dd"))
        self.field_fio.setText(data.get("fio", ""))
        self.field_org.setText(data.get("org", ""))
        self.field_reason.setText(data.get("reason", ""))
        self.field_accompany_fio.setText(data.get("accompany_fio", ""))

        if data.get("entry_time"):
            self.field_entry_time.setTime(
                QTime.fromString(data["entry_time"], "HH:mm"))
        if data.get("exit_time"):
            self.field_exit_time.setTime(
                QTime.fromString(data["exit_time"], "HH:mm"))

    def _add_to_model(self, model: QStringListModel, text: str):
        if not text:
            return
        items = model.stringList()
        if text not in items:
            items.append(text)
            items.sort()
            model.setStringList(items)

    def _on_accept(self):
        if not self.field_fio.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите ФИО посетителя")
            return

        exit_time = self.field_exit_time.time()
        exit_str  = (
            "" if exit_time == QTime(0, 0)
            else exit_time.toString("HH:mm")
        )

        fio           = self.field_fio.text().strip()
        org           = self.field_org.text().strip()
        accompany_fio = self.field_accompany_fio.text().strip()

        self._add_to_model(self._fio_model, fio)
        self._add_to_model(self._org_model, org)
        if accompany_fio:
            self._add_to_model(self._acc_model, accompany_fio)

        self.result_data = {
            "date":          self.field_date.date().toString("yyyy-MM-dd"),
            "fio":           fio,
            "org":           org,
            "reason":        self.field_reason.text().strip(),
            "accompany":     "Да" if accompany_fio else "Нет",
            "accompany_fio": accompany_fio,
            "entry_time":    self.field_entry_time.time().toString("HH:mm"),
            "exit_time":     exit_str,
        }
        self.accept()