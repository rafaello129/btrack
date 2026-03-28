from __future__ import annotations

import os
import unittest

from PySide6.QtWidgets import QApplication

from src.ui.main_window import MainWindow


class UISmokeTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        cls.app = QApplication.instance() or QApplication([])

    def test_window_open_close(self) -> None:
        window = MainWindow()
        window.show()
        self.app.processEvents()
        self.assertTrue(window.isVisible())
        window.close()
        self.app.processEvents()


if __name__ == "__main__":
    unittest.main()
