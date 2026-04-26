# ──────────────────────────────────────────────────────────#  main.py  –  точка входа в приложение

import sys
from PySide6.QtWidgets import QApplication

from constants import APP_STYLESHEET
from ui.login_window import LoginWindow


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLESHEET)

    window = LoginWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()