"""
NeuroFace - Status Badge Widget
Badge de estado con estilo pill (bordes infinitamente redondeados)
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel


class StatusBadge(QLabel):
    """Badge de estado con diferentes tonos visuales."""
    
    TONES = ("good", "info", "warn", "risk", "muted")
    
    def __init__(self, text: str = "", tone: str = "muted", parent=None) -> None:
        super().__init__(text, parent)
        self.setObjectName("StatusBadge")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.set_tone(tone)

    def set_tone(self, tone: str) -> None:
        """Establece el tono visual del badge."""
        if tone not in self.TONES:
            tone = "muted"
        self.setProperty("tone", tone)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
    
    def set_text_and_tone(self, text: str, tone: str) -> None:
        """Actualiza texto y tono en una sola llamada."""
        self.setText(text)
        self.set_tone(tone)
