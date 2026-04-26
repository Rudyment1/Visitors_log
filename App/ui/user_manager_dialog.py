# ──────────────────────────────────────────────────────────
#  ui/user_manager_dialog.py  –  управление пользователями
# ──────────────────────────────────────────────────────────

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QLineEdit, QComboBox, QMessageBox,
    QAbstractItemView,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent

from db.user_repository import UserRepository
from constants import ROLES


class UserManagerDialog(QDialog):
    """Диалог просмотра и управления учётными записями."""

    PROTECTED_LOGIN = "admin"

    def __init__(self, parent=None):
        super().__init__(parent)

        self.user_repo = UserRepository()

        self.setWindowTitle("Пользователи системы")
        self.resize(560, 340)

        self._build_ui()
        self._load_users()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "Логин", "Роль", "ФИО"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setColumnHidden(0, True)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(32)

        btn_row = QHBoxLayout()

        btn_add = QPushButton("＋ Добавить пользователя")
        btn_add.setObjectName("btn_add")
        btn_add.clicked.connect(self._open_add_dialog)

        btn_del = QPushButton("✕ Удалить")
        btn_del.setObjectName("btn_del")
        btn_del.clicked.connect(self._delete_selected)

        btn_row.addWidget(btn_add)
        btn_row.addStretch()
        btn_row.addWidget(btn_del)

        layout.addWidget(self.table)
        layout.addLayout(btn_row)

    def _load_users(self):
        self.table.setRowCount(0)

        for row_data in self.user_repo.get_all():
            row = self.table.rowCount()
            self.table.insertRow(row)

            for col, val in enumerate(row_data):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, col, item)

    def _open_add_dialog(self):
        dlg = _AddUserDialog(self)

        if dlg.exec() == QDialog.DialogCode.Accepted:
            if dlg.result_data is None:
                return

            try:
                self.user_repo.create(**dlg.result_data)
                self._load_users()
            except Exception as exc:
                QMessageBox.warning(self, "Ошибка", f"Не удалось создать: {exc}")

    def _delete_selected(self):
        row = self.table.currentRow()

        if row == -1:
            return

        login_item = self.table.item(row, 1)
        id_item = self.table.item(row, 0)

        if login_item is None or id_item is None:
            return

        login = login_item.text()

        if login == self.PROTECTED_LOGIN:
            QMessageBox.warning(
                self,
                "Запрещено",
                "Нельзя удалить учётную запись главного администратора."
            )
            return

        answer = QMessageBox.question(
            self,
            "Удаление",
            f"Удалить пользователя «{login}»?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if answer == QMessageBox.StandardButton.Yes:
            user_id = int(id_item.text())
            self.user_repo.delete(user_id)
            self.table.removeRow(row)


class _AddUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.result_data: dict[str, str] | None = None

        self.setWindowTitle("Новый пользователь")
        self.setMinimumWidth(360)

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        form = QFormLayout()
        form.setSpacing(10)

        self.input_login = QLineEdit()
        self.input_fullname = QLineEdit()

        self.input_role = QComboBox()
        self.input_role.addItems(ROLES)

        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)

        pw_row = QHBoxLayout()
        pw_row.setSpacing(4)
        pw_row.addWidget(self.input_password)

        self._btn_show1 = QPushButton("•••")
        self._btn_show1.setFixedSize(36, 28)
        self._btn_show1.setCheckable(True)
        self._btn_show1.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._btn_show1.setStyleSheet(
            "QPushButton { font-size: 11px; padding: 0; }"
            "QPushButton:checked { color: #89b4fa; }"
        )
        self._btn_show1.toggled.connect(self._toggle_password1)

        pw_row.addWidget(self._btn_show1)

        self.input_password2 = QLineEdit()
        self.input_password2.setEchoMode(QLineEdit.EchoMode.Password)

        pw2_row = QHBoxLayout()
        pw2_row.setSpacing(4)
        pw2_row.addWidget(self.input_password2)

        self._btn_show2 = QPushButton("•••")
        self._btn_show2.setFixedSize(36, 28)
        self._btn_show2.setCheckable(True)
        self._btn_show2.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._btn_show2.setStyleSheet(
            "QPushButton { font-size: 11px; padding: 0; }"
            "QPushButton:checked { color: #89b4fa; }"
        )
        self._btn_show2.toggled.connect(self._toggle_password2)

        pw2_row.addWidget(self._btn_show2)

        form.addRow("Логин:", self.input_login)
        form.addRow("Пароль:", pw_row)
        form.addRow("Подтверждение:", pw2_row)
        form.addRow("Роль:", self.input_role)
        form.addRow("ФИО:", self.input_fullname)

        layout.addLayout(form)

        btn_create = QPushButton("Создать")
        btn_create.setObjectName("btn_save")
        btn_create.setAutoDefault(False)
        btn_create.setDefault(False)
        btn_create.clicked.connect(self._on_accept)

        layout.addWidget(btn_create)

    def _toggle_password1(self, checked: bool):
        if checked:
            self.input_password.setEchoMode(QLineEdit.EchoMode.Normal)
            self._btn_show1.setText("abc")
        else:
            self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
            self._btn_show1.setText("•••")

    def _toggle_password2(self, checked: bool):
        if checked:
            self.input_password2.setEchoMode(QLineEdit.EchoMode.Normal)
            self._btn_show2.setText("abc")
        else:
            self.input_password2.setEchoMode(QLineEdit.EchoMode.Password)
            self._btn_show2.setText("•••")

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            return

        super().keyPressEvent(event)

    def _on_accept(self):
        login = self.input_login.text().strip()
        password = self.input_password.text()
        confirm = self.input_password2.text()

        if not login:
            QMessageBox.warning(self, "Ошибка", "Введите логин")
            return

        if not password:
            QMessageBox.warning(self, "Ошибка", "Введите пароль")
            return

        if password != confirm:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают")
            self.input_password2.clear()
            self.input_password2.setFocus()
            return

        self.result_data = {
            "username": login,
            "password": password,
            "role": self.input_role.currentText(),
            "full_name": self.input_fullname.text().strip(),
        }

        self.accept()