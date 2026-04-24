"""
NeuroFace - Collapsible Section Widget
Sección colapsable con animación suave
"""
from __future__ import annotations

from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import QFrame, QToolButton, QVBoxLayout, QWidget


class CollapsibleSection(QFrame):
    """Sección que puede expandirse/colapsarse con animación."""
    
    def __init__(self, title: str, content: QWidget, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("CollapsibleSection")

        self.toggle_button = QToolButton()
        self.toggle_button.setText(f"  {title}")
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(Qt.ArrowType.RightArrow)
        self.toggle_button.toggled.connect(self._on_toggled)
        self.toggle_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.content = content
        self.content.setVisible(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.content)

    def _on_toggled(self, checked: bool) -> None:
        """Maneja el evento de toggle con animación."""
        self.toggle_button.setArrowType(
            Qt.ArrowType.DownArrow if checked else Qt.ArrowType.RightArrow
        )
        self.content.setVisible(checked)
