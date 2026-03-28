from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from src.shared.logging_config import configure_logging
from src.ui import MainWindow, get_app_stylesheet


def main() -> int:
    configure_logging()
    app = QApplication(sys.argv)
    app.setStyleSheet(get_app_stylesheet())
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
