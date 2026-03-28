from __future__ import annotations


def get_app_stylesheet() -> str:
    return """
QWidget {
    background-color: #0d141b;
    color: #e7edf3;
    font-family: "Segoe UI", "Noto Sans", sans-serif;
    font-size: 13px;
}

QMainWindow {
    background-color: #0b1117;
}

QFrame#AppShell {
    background: transparent;
    border: none;
}

QFrame#TopBar {
    background-color: #111a23;
    border: 1px solid #1c2a37;
    border-radius: 14px;
}

QLabel#BrandTitle {
    font-size: 22px;
    font-weight: 700;
    color: #eaf4ff;
}

QLabel#BrandSubtitle {
    font-size: 13px;
    color: #9cb1c4;
}

QFrame#MainPanel,
QFrame#ResultHeroCard,
QFrame#Card,
QFrame#KpiCard,
QFrame#ImageCard,
QFrame#DisclaimerCard,
QFrame#CollapsibleSection {
    background-color: #121d27;
    border: 1px solid #223242;
    border-radius: 12px;
}

QLabel#ImageHint {
    color: #89a0b7;
    font-size: 12px;
}

QLabel#ImageView {
    border: 1px solid #294154;
    border-radius: 10px;
    background-color: #0a131b;
    color: #8fa4b7;
}

QGroupBox {
    border: 1px solid #243544;
    border-radius: 10px;
    margin-top: 14px;
    padding: 12px 12px 10px 12px;
    background-color: #0f1821;
    font-weight: 600;
    color: #cfe0ef;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 6px;
    color: #8ec3df;
}

QPushButton {
    border: 1px solid #2d4356;
    border-radius: 9px;
    background-color: #162331;
    color: #d8e6f2;
    padding: 8px 12px;
    min-height: 18px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #1c2b3b;
    border-color: #3a5870;
}

QPushButton:pressed {
    background-color: #15212d;
}

QPushButton[role="primary"] {
    background-color: #1aa1b8;
    color: #062129;
    border-color: #38bcd2;
}

QPushButton[role="primary"]:hover {
    background-color: #35b6cb;
}

QPushButton[role="danger"] {
    background-color: #5a2430;
    border-color: #8e3d50;
    color: #ffdfe5;
}

QPushButton[role="danger"]:hover {
    background-color: #71303e;
}

QPushButton:disabled {
    color: #778fa3;
    border-color: #293847;
    background-color: #121b24;
}

QComboBox,
QTextEdit,
QToolButton {
    border: 1px solid #30495f;
    border-radius: 8px;
    background-color: #0f1821;
    padding: 6px 8px;
    color: #dce8f3;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    border: 1px solid #3a5167;
    background-color: #0f1821;
    selection-background-color: #1f3346;
}

QCheckBox {
    spacing: 8px;
    color: #d2dfeb;
}

QCheckBox::indicator {
    width: 17px;
    height: 17px;
    border-radius: 4px;
    border: 1px solid #3a5064;
    background-color: #0c141c;
}

QCheckBox::indicator:checked {
    background-color: #1aa1b8;
    border-color: #36bfd4;
}

QScrollArea {
    border: none;
    background: transparent;
}

QSplitter::handle {
    background-color: #111a23;
    width: 8px;
    margin: 10px 0;
    border-radius: 4px;
}

QSplitter::handle:hover {
    background-color: #1f3446;
}

QLabel#SectionTitle {
    font-size: 14px;
    font-weight: 700;
    color: #d9e7f3;
}

QLabel#HeroTitle {
    font-size: 24px;
    font-weight: 700;
    color: #edf6ff;
}

QLabel#HeroSubtitle {
    font-size: 13px;
    color: #b8cad9;
}

QLabel#HeroNextStep {
    font-size: 13px;
    color: #c9deef;
    background-color: #0e1821;
    border: 1px solid #273949;
    border-radius: 8px;
    padding: 8px;
}

QLabel#StatusBadge {
    border-radius: 10px;
    padding: 4px 10px;
    font-size: 12px;
    font-weight: 700;
    border: 1px solid #2f4455;
    background-color: #15202a;
    color: #c2d5e7;
}

QLabel#StatusBadge[tone="good"] {
    color: #9ef0c2;
    border-color: #2a6f4e;
    background-color: #133427;
}

QLabel#StatusBadge[tone="info"] {
    color: #8fddff;
    border-color: #2d6882;
    background-color: #123046;
}

QLabel#StatusBadge[tone="warn"] {
    color: #ffd89e;
    border-color: #8c6a2a;
    background-color: #3f2f10;
}

QLabel#StatusBadge[tone="risk"] {
    color: #ffb3b3;
    border-color: #91414d;
    background-color: #4b1c24;
}

QLabel#StatusBadge[tone="muted"] {
    color: #adc0d0;
    border-color: #334757;
    background-color: #17232e;
}

QLabel#KpiTitle {
    color: #96adc2;
    font-size: 12px;
}

QLabel#KpiValue {
    font-size: 22px;
    font-weight: 700;
    color: #e9f5ff;
}

QLabel#KpiValue[tone="good"] { color: #9bf3c4; }
QLabel#KpiValue[tone="info"] { color: #9adfff; }
QLabel#KpiValue[tone="warn"] { color: #ffd69a; }
QLabel#KpiValue[tone="risk"] { color: #ffacb5; }
QLabel#KpiValue[tone="muted"] { color: #b7cad9; }

QLabel#KpiHelper {
    color: #93a9bc;
    font-size: 12px;
}

QProgressBar {
    border: 1px solid #2c4050;
    border-radius: 6px;
    background-color: #0d151d;
    text-align: center;
    color: #d5e7f4;
    height: 14px;
}

QProgressBar::chunk {
    border-radius: 5px;
    background-color: #1aa1b8;
}

QTextEdit {
    background-color: #0d151d;
    border: 1px solid #2a3f4f;
}

QLabel#DisclaimerTitle {
    font-size: 13px;
    font-weight: 700;
    color: #a6d3ea;
}

QLabel#DisclaimerText {
    color: #b7c9d8;
    font-size: 12px;
}

QToolButton {
    text-align: left;
    font-weight: 700;
    color: #b6cadb;
}
"""
