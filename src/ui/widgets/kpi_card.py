"""
NeuroFace - KPI Card Widget
Tarjeta de indicador clave de rendimiento con estilo Material Design 3
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QSizePolicy, QVBoxLayout


class KpiCard(QFrame):
    """Tarjeta de KPI con título, valor y texto de ayuda."""
    
    def __init__(self, title: str, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("KpiCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("KpiTitle")

        self.value_label = QLabel("--")
        self.value_label.setObjectName("KpiValue")
        self.value_label.setWordWrap(True)
        self.value_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.helper_label = QLabel("Sin datos")
        self.helper_label.setObjectName("KpiHelper")
        self.helper_label.setWordWrap(True)

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.helper_label)

    def update_data(self, value: str, helper: str = "", tone: str = "info") -> None:
        """Actualiza el valor y tono del KPI."""
        self.value_label.setText(value)
        self.helper_label.setText(helper)
        self.value_label.setProperty("tone", tone)
        self.value_label.style().unpolish(self.value_label)
        self.value_label.style().polish(self.value_label)
        self.value_label.update()
