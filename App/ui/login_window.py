from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel
)
from PySide6.QtCore import Qt

from db.user_repository import UserRepository
from constants import APP_NAME


class LoginWindow(QWidget):
    """Окно входа в систему."""

    def __init__(self):
        super().__init__()
        self.user_repo = UserRepository()
        self._build_ui()

    def _build_ui(self):
        self.setWindowTitle(f"Вход — {APP_NAME}")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(12)

        title = QLabel(APP_NAME)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-size: 17px; font-weight: 700;"
            "color: #89b4fa; margin-bottom: 8px;"
        )

        self.input_login = QLineEdit()
        self.input_login.setPlaceholderText("Логин")

        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Пароль")
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password.returnPressed.connect(self._authenticate)

        password_row = QHBoxLayout()
        password_row.setSpacing(4)
        password_row.addWidget(self.input_password)

        self.btn_show_password = QPushButton("•••")
        self.btn_show_password.setFixedSize(36, 32)
        self.btn_show_password.setCheckable(True)
        self.btn_show_password.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_show_password.setStyleSheet(
            "QPushButton { font-size: 11px; padding: 0; }"
            "QPushButton:checked { color: #89b4fa; }"
        )
        self.btn_show_password.toggled.connect(self._toggle_password_visibility)
        password_row.addWidget(self.btn_show_password)

        self.label_error = QLabel("")
        self.label_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_error.setStyleSheet("color: #f38ba8; font-size: 12px;")

        btn_login = QPushButton("Войти")
        btn_login.setObjectName("btn_login")
        btn_login.clicked.connect(self._authenticate)

        layout.addWidget(title)
        layout.addWidget(self.input_login)
        layout.addLayout(password_row)
        layout.addWidget(btn_login)
        layout.addWidget(self.label_error)

    def _toggle_password_visibility(self, checked: bool):
        if checked:
            self.input_password.setEchoMode(QLineEdit.EchoMode.Normal)
            self.btn_show_password.setText("abc")
        else:
            self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
            self.btn_show_password.setText("•••")

    def _authenticate(self):
        username = self.input_login.text().strip()
        password = self.input_password.text()
        user = self.user_repo.authenticate(username, password)

        if user:
            self.label_error.setText("")
            self._open_main_window(user)
        else:
            self.label_error.setText("Неверный логин или пароль")

    def _open_main_window(self, user):
        from ui.main_window import MainWindow
        from db.log_repository import LogRepository

        LogRepository().log(user["full_name"], "ВХОД В СИСТЕМУ")
        self.main_window = MainWindow(user)
        self.main_window.show()
        self.close()