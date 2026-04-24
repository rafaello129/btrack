"""
NeuroFace Desktop Theme - Premium Medical Interface
Diseño clínico avanzado, sofisticado y de alta gama
Inspirado en software médico de nueva generación
"""
from __future__ import annotations


# =============================================================================
# PALETA DE COLORES NEUROFACE - PREMIUM MEDICAL
# =============================================================================

class NeuroFaceColors:
    """
    Paleta premium para interfaz médica clínica.
    Negro carbón/grafito con acentos ámbar-cobre sofisticados.
    """
    
    # -------------------------------------------------------------------------
    # FONDOS - Negro carbón profundo, no negro puro absoluto
    # -------------------------------------------------------------------------
    BACKGROUND_DEEPEST = "#0C0C0E"      # Carbón más profundo
    BACKGROUND_BASE = "#101012"          # Base principal grafito
    BACKGROUND_MAIN = "#141416"          # Fondo de aplicación
    
    # -------------------------------------------------------------------------
    # SUPERFICIES - Variaciones de antracita y grafito oscuro
    # -------------------------------------------------------------------------
    SURFACE_LOWEST = "#18181B"           # Superficie base
    SURFACE = "#1C1C20"                  # Superficie estándar
    SURFACE_ELEVATED = "#222226"         # Superficie elevada
    SURFACE_HIGHEST = "#28282D"          # Superficie más alta
    SURFACE_HOVER = "#2E2E34"            # Hover state
    SURFACE_ACTIVE = "#34343B"           # Active state
    
    # -------------------------------------------------------------------------
    # ACENTO PRINCIPAL - Ámbar clínico / Cobre elegante / Dorado suave
    # -------------------------------------------------------------------------
    AMBER = "#C9A66B"                    # Ámbar principal - cálido y sofisticado
    AMBER_LIGHT = "#D4B87D"              # Ámbar claro
    AMBER_LIGHTER = "#E0CA94"            # Ámbar más claro
    AMBER_DARK = "#A68B52"               # Ámbar oscuro
    AMBER_DARKER = "#8A7343"             # Ámbar más oscuro
    AMBER_GLOW = "rgba(201, 166, 107, 0.15)"  # Resplandor sutil
    AMBER_CONTAINER = "#2A251C"          # Contenedor ámbar
    
    # -------------------------------------------------------------------------
    # ACENTOS FUNCIONALES - Sutiles y desaturados
    # -------------------------------------------------------------------------
    # Azul clínico tenue
    CLINICAL_BLUE = "#6B9DC9"            # Azul clínico
    CLINICAL_BLUE_MUTED = "#5A8AB5"      # Azul apagado
    CLINICAL_BLUE_CONTAINER = "#1A222A"  # Contenedor azul
    
    # Verde desaturado - resultados favorables
    CLINICAL_GREEN = "#6BC98A"           # Verde clínico
    CLINICAL_GREEN_MUTED = "#5AB578"     # Verde apagado
    CLINICAL_GREEN_CONTAINER = "#1A2A20" # Contenedor verde
    
    # Ámbar de advertencia
    CLINICAL_WARN = "#C9A66B"            # Advertencia (mismo ámbar)
    CLINICAL_WARN_CONTAINER = "#2A251C"  # Contenedor advertencia
    
    # Rojo elegante - alertas clínicas
    CLINICAL_RED = "#C96B6B"             # Rojo clínico elegante
    CLINICAL_RED_MUTED = "#B55A5A"       # Rojo apagado
    CLINICAL_RED_CONTAINER = "#2A1A1A"   # Contenedor rojo
    
    # -------------------------------------------------------------------------
    # TEXTO - Blanco suave, no puro
    # -------------------------------------------------------------------------
    TEXT_PRIMARY = "#F0F0F2"             # Blanco suave principal
    TEXT_SECONDARY = "#A8A8B0"           # Gris cálido/acero claro
    TEXT_TERTIARY = "#707078"            # Gris tenue
    TEXT_MUTED = "#505058"               # Gris muy tenue
    TEXT_ON_AMBER = "#121214"            # Texto sobre ámbar
    
    # -------------------------------------------------------------------------
    # BORDES Y LÍNEAS - Gris humo translúcido
    # -------------------------------------------------------------------------
    BORDER_INVISIBLE = "#1E1E22"         # Casi invisible
    BORDER_SUBTLE = "#252528"            # Muy sutil
    BORDER_DEFAULT = "#2C2C30"           # Normal
    BORDER_VISIBLE = "#38383E"           # Visible
    BORDER_HOVER = "#444448"             # Hover
    BORDER_FOCUS = "#C9A66B"             # Focus (ámbar)
    
    # -------------------------------------------------------------------------
    # ESTADOS DE SEVERIDAD CLÍNICA
    # -------------------------------------------------------------------------
    SEVERITY_STABLE = "#6BC98A"          # Estable/Normal
    SEVERITY_INFO = "#6B9DC9"            # Informativo
    SEVERITY_ATTENTION = "#C9A66B"       # Atención
    SEVERITY_REVIEW = "#C98A6B"          # Revisar
    SEVERITY_ALERT = "#C96B6B"           # Alerta


def get_app_stylesheet() -> str:
    """
    Retorna el stylesheet premium de NeuroFace.
    Interfaz médica clínica de alta gama.
    """
    c = NeuroFaceColors
    
    return f"""
/* ==========================================================================
   NEUROFACE DESKTOP - PREMIUM MEDICAL INTERFACE
   Diseño clínico avanzado para software médico de nueva generación
   ========================================================================== */

/* --------------------------------------------------------------------------
   BASE - Fundamentos del sistema visual
   -------------------------------------------------------------------------- */
QWidget {{
    background-color: {c.BACKGROUND_MAIN};
    color: {c.TEXT_PRIMARY};
    font-family: "Segoe UI Variable", "SF Pro Display", "Inter", "Segoe UI", sans-serif;
    font-size: 13px;
    font-weight: 400;
    selection-background-color: {c.AMBER};
    selection-color: {c.TEXT_ON_AMBER};
}}

QMainWindow {{
    background-color: {c.BACKGROUND_DEEPEST};
}}

QFrame#AppShell {{
    background: transparent;
    border: none;
}}

/* --------------------------------------------------------------------------
   TOP BAR - Header premium con fondo negro
   -------------------------------------------------------------------------- */
QFrame#TopBar {{
    background-color: #000000;
    border: none;
    border-radius: 14px;
}}

QFrame#LogoContainer {{
    background-color: #000000;
    border: 1px solid {c.BORDER_SUBTLE};
    border-radius: 10px;
}}

QLabel#BrandTitle {{
    font-size: 30px;
    font-weight: 700;
    color: {c.TEXT_PRIMARY};
    letter-spacing: 4px;
}}

QLabel#BrandSubtitle {{
    font-size: 11px;
    font-weight: 400;
    color: {c.TEXT_TERTIARY};
    letter-spacing: 0.8px;
}}

/* --------------------------------------------------------------------------
   INDICADOR DE ANÁLISIS EN PROGRESO
   -------------------------------------------------------------------------- */
QLabel#ThinkingIndicator {{
    background-color: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 {c.AMBER_CONTAINER},
        stop:1 {c.SURFACE_ELEVATED}
    );
    color: {c.AMBER_LIGHT};
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 1px;
    padding: 6px 14px;
    border: 1px solid {c.AMBER_DARK};
    border-radius: 16px;
}}

/* --------------------------------------------------------------------------
   PANELS & CARDS - Capas oscuras satinadas con profundidad
   -------------------------------------------------------------------------- */
QFrame#MainPanel {{
    background-color: {c.SURFACE_LOWEST};
    border: 1px solid {c.BORDER_SUBTLE};
    border-radius: 16px;
}}

QFrame#Card,
QFrame#ImageCard,
QFrame#CollapsibleSection {{
    background-color: {c.SURFACE};
    border: 1px solid {c.BORDER_SUBTLE};
    border-radius: 12px;
}}

QFrame#ResultHeroCard {{
    background-color: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 {c.SURFACE_ELEVATED},
        stop:0.5 {c.SURFACE_HIGHEST},
        stop:1 {c.SURFACE_ELEVATED}
    );
    border: 1px solid {c.BORDER_DEFAULT};
    border-left: 3px solid {c.AMBER};
    border-radius: 14px;
}}

QFrame#KpiCard {{
    background-color: {c.SURFACE};
    border: 1px solid {c.BORDER_SUBTLE};
    border-radius: 10px;
}}

QFrame#KpiCard:hover {{
    background-color: {c.SURFACE_ELEVATED};
    border-color: {c.BORDER_DEFAULT};
}}

QFrame#DisclaimerCard {{
    background-color: {c.SURFACE_LOWEST};
    border: 1px solid {c.BORDER_SUBTLE};
    border-left: 2px solid {c.CLINICAL_BLUE_MUTED};
    border-radius: 8px;
}}

/* --------------------------------------------------------------------------
   IMAGE VIEW - Panel hero de captura facial
   -------------------------------------------------------------------------- */
QLabel#ImageHint {{
    color: {c.TEXT_TERTIARY};
    font-size: 11px;
    font-weight: 400;
    letter-spacing: 0.3px;
}}

QLabel#ImageView {{
    background-color: {c.BACKGROUND_DEEPEST};
    border: 1px solid {c.BORDER_DEFAULT};
    border-radius: 12px;
    color: {c.TEXT_MUTED};
}}

/* --------------------------------------------------------------------------
   GROUP BOX - Módulos de configuración clínica
   -------------------------------------------------------------------------- */
QGroupBox {{
    background-color: {c.SURFACE};
    border: 1px solid {c.BORDER_SUBTLE};
    border-radius: 12px;
    margin-top: 20px;
    padding: 18px 16px 14px 16px;
    font-weight: 500;
    color: {c.TEXT_PRIMARY};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 18px;
    padding: 2px 10px;
    background-color: {c.SURFACE};
    border-radius: 4px;
    color: {c.AMBER};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
}}

/* --------------------------------------------------------------------------
   BUTTONS - Sistema de botones premium
   -------------------------------------------------------------------------- */
QPushButton {{
    background-color: {c.SURFACE_ELEVATED};
    border: 1px solid {c.BORDER_DEFAULT};
    border-radius: 8px;
    color: {c.TEXT_PRIMARY};
    padding: 11px 20px;
    min-height: 20px;
    font-weight: 500;
    font-size: 13px;
    letter-spacing: 0.3px;
}}

QPushButton:hover {{
    background-color: {c.SURFACE_HOVER};
    border-color: {c.BORDER_HOVER};
}}

QPushButton:pressed {{
    background-color: {c.SURFACE_ACTIVE};
}}

QPushButton:focus {{
    border-color: {c.AMBER_DARK};
}}

/* Botón primario - Ámbar protagonista */
QPushButton[role="primary"] {{
    background-color: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 {c.AMBER_LIGHT},
        stop:1 {c.AMBER}
    );
    border: none;
    color: {c.TEXT_ON_AMBER};
    font-weight: 600;
    letter-spacing: 0.5px;
}}

QPushButton[role="primary"]:hover {{
    background-color: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 {c.AMBER_LIGHTER},
        stop:1 {c.AMBER_LIGHT}
    );
}}

QPushButton[role="primary"]:pressed {{
    background-color: {c.AMBER_DARK};
}}

/* Botón de peligro/detener */
QPushButton[role="danger"] {{
    background-color: {c.CLINICAL_RED_CONTAINER};
    border: 1px solid {c.CLINICAL_RED_MUTED};
    color: {c.CLINICAL_RED};
}}

QPushButton[role="danger"]:hover {{
    background-color: #301A1A;
    border-color: {c.CLINICAL_RED};
}}

QPushButton:disabled {{
    background-color: {c.SURFACE};
    border-color: {c.BORDER_INVISIBLE};
    color: {c.TEXT_MUTED};
}}

/* --------------------------------------------------------------------------
   FORM CONTROLS - Controles refinados
   -------------------------------------------------------------------------- */
QComboBox {{
    background-color: {c.SURFACE};
    border: 1px solid {c.BORDER_DEFAULT};
    border-radius: 8px;
    padding: 9px 14px;
    color: {c.TEXT_PRIMARY};
    min-height: 20px;
    font-weight: 400;
}}

QComboBox:hover {{
    border-color: {c.BORDER_HOVER};
    background-color: {c.SURFACE_ELEVATED};
}}

QComboBox:focus {{
    border-color: {c.AMBER_DARK};
}}

QComboBox::drop-down {{
    border: none;
    width: 28px;
}}

QComboBox QAbstractItemView {{
    background-color: {c.SURFACE_ELEVATED};
    border: 1px solid {c.BORDER_DEFAULT};
    border-radius: 8px;
    selection-background-color: {c.AMBER_CONTAINER};
    selection-color: {c.AMBER_LIGHT};
    padding: 6px;
    outline: none;
}}

QTextEdit {{
    background-color: {c.SURFACE_LOWEST};
    border: 1px solid {c.BORDER_SUBTLE};
    border-radius: 8px;
    padding: 12px;
    color: {c.TEXT_SECONDARY};
    font-family: "JetBrains Mono", "Cascadia Code", "Consolas", monospace;
    font-size: 11px;
    line-height: 1.5;
}}

QTextEdit:focus {{
    border-color: {c.BORDER_DEFAULT};
}}

QToolButton {{
    background-color: transparent;
    border: 1px solid {c.BORDER_SUBTLE};
    border-radius: 8px;
    padding: 10px 16px;
    color: {c.TEXT_SECONDARY};
    font-weight: 500;
    text-align: left;
}}

QToolButton:hover {{
    background-color: {c.SURFACE_ELEVATED};
    border-color: {c.BORDER_DEFAULT};
    color: {c.TEXT_PRIMARY};
}}

QToolButton:checked {{
    background-color: {c.AMBER_CONTAINER};
    border-color: {c.AMBER_DARK};
    color: {c.AMBER_LIGHT};
}}

/* --------------------------------------------------------------------------
   CHECKBOX - Switches premium
   -------------------------------------------------------------------------- */
QCheckBox {{
    spacing: 12px;
    color: {c.TEXT_SECONDARY};
    font-weight: 400;
}}

QCheckBox:hover {{
    color: {c.TEXT_PRIMARY};
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 1.5px solid {c.BORDER_DEFAULT};
    background-color: {c.SURFACE};
}}

QCheckBox::indicator:hover {{
    border-color: {c.BORDER_HOVER};
    background-color: {c.SURFACE_ELEVATED};
}}

QCheckBox::indicator:checked {{
    background-color: {c.AMBER};
    border-color: {c.AMBER};
}}

QCheckBox::indicator:checked:hover {{
    background-color: {c.AMBER_LIGHT};
    border-color: {c.AMBER_LIGHT};
}}

/* --------------------------------------------------------------------------
   SCROLLBARS - Minimalistas y elegantes
   -------------------------------------------------------------------------- */
QScrollArea {{
    border: none;
    background: transparent;
}}

QScrollBar:vertical {{
    background-color: transparent;
    width: 10px;
    margin: 6px 2px;
}}

QScrollBar::handle:vertical {{
    background-color: {c.BORDER_DEFAULT};
    min-height: 50px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {c.BORDER_HOVER};
}}

QScrollBar::handle:vertical:pressed {{
    background-color: {c.AMBER_DARK};
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background-color: transparent;
    height: 10px;
    margin: 2px 6px;
}}

QScrollBar::handle:horizontal {{
    background-color: {c.BORDER_DEFAULT};
    min-width: 50px;
    border-radius: 4px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {c.BORDER_HOVER};
}}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* --------------------------------------------------------------------------
   SPLITTER - Divisores arrastrables visibles
   -------------------------------------------------------------------------- */
QSplitter::handle {{
    background-color: {c.BORDER_DEFAULT};
    width: 6px;
    margin: 16px 0;
    border-radius: 3px;
}}

QSplitter::handle:hover {{
    background-color: {c.AMBER};
}}

QSplitter::handle:pressed {{
    background-color: {c.AMBER_LIGHT};
}}

/* --------------------------------------------------------------------------
   TYPOGRAPHY - Sistema tipográfico jerarquizado
   -------------------------------------------------------------------------- */
QLabel#SectionTitle {{
    font-size: 13px;
    font-weight: 600;
    color: {c.TEXT_PRIMARY};
    letter-spacing: 0.5px;
}}

QLabel#HeroTitle {{
    font-size: 24px;
    font-weight: 600;
    color: {c.TEXT_PRIMARY};
    letter-spacing: 0.3px;
}}

QLabel#HeroSubtitle {{
    font-size: 13px;
    font-weight: 400;
    color: {c.TEXT_SECONDARY};
    line-height: 1.5;
}}

QLabel#HeroNextStep {{
    font-size: 12px;
    font-weight: 400;
    color: {c.TEXT_SECONDARY};
    background-color: {c.SURFACE_LOWEST};
    border: none;
    border-left: 2px solid {c.AMBER};
    border-radius: 0px;
    padding: 12px 16px;
    line-height: 1.4;
}}

/* --------------------------------------------------------------------------
   STATUS BADGES - Pills premium translúcidas
   -------------------------------------------------------------------------- */
QLabel#StatusBadge {{
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
    border: none;
    background-color: {c.SURFACE_ELEVATED};
    color: {c.TEXT_SECONDARY};
}}

QLabel#StatusBadge[tone="good"] {{
    color: {c.SEVERITY_STABLE};
    background-color: {c.CLINICAL_GREEN_CONTAINER};
}}

QLabel#StatusBadge[tone="info"] {{
    color: {c.SEVERITY_INFO};
    background-color: {c.CLINICAL_BLUE_CONTAINER};
}}

QLabel#StatusBadge[tone="warn"] {{
    color: {c.SEVERITY_ATTENTION};
    background-color: {c.AMBER_CONTAINER};
}}

QLabel#StatusBadge[tone="risk"] {{
    color: {c.SEVERITY_ALERT};
    background-color: {c.CLINICAL_RED_CONTAINER};
}}

QLabel#StatusBadge[tone="muted"] {{
    color: {c.TEXT_TERTIARY};
    background-color: {c.SURFACE};
}}

/* --------------------------------------------------------------------------
   KPI CARDS - Microtarjetas técnicas premium
   -------------------------------------------------------------------------- */
QLabel#KpiTitle {{
    color: {c.TEXT_TERTIARY};
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.2px;
}}

QLabel#KpiValue {{
    font-size: 24px;
    font-weight: 600;
    color: {c.TEXT_PRIMARY};
    letter-spacing: -0.5px;
}}

QLabel#KpiValue[tone="good"] {{ color: {c.SEVERITY_STABLE}; }}
QLabel#KpiValue[tone="info"] {{ color: {c.SEVERITY_INFO}; }}
QLabel#KpiValue[tone="warn"] {{ color: {c.SEVERITY_ATTENTION}; }}
QLabel#KpiValue[tone="risk"] {{ color: {c.SEVERITY_ALERT}; }}
QLabel#KpiValue[tone="muted"] {{ color: {c.TEXT_MUTED}; }}

QLabel#KpiHelper {{
    color: {c.TEXT_MUTED};
    font-size: 10px;
    font-weight: 400;
}}

/* --------------------------------------------------------------------------
   PROGRESS BAR - Instrumentación médica fina
   -------------------------------------------------------------------------- */
QProgressBar {{
    border: none;
    border-radius: 3px;
    background-color: {c.SURFACE_LOWEST};
    text-align: center;
    color: {c.TEXT_SECONDARY};
    height: 6px;
    font-size: 9px;
}}

QProgressBar::chunk {{
    border-radius: 3px;
    background-color: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 {c.AMBER_DARK},
        stop:1 {c.AMBER}
    );
}}

/* --------------------------------------------------------------------------
   DISCLAIMER - Aviso médico profesional
   -------------------------------------------------------------------------- */
QLabel#DisclaimerTitle {{
    font-size: 11px;
    font-weight: 600;
    color: {c.CLINICAL_BLUE};
    letter-spacing: 0.5px;
}}

QLabel#DisclaimerText {{
    color: {c.TEXT_TERTIARY};
    font-size: 11px;
    font-weight: 400;
    line-height: 1.5;
}}

/* --------------------------------------------------------------------------
   LOGO WIDGET
   -------------------------------------------------------------------------- */
QLabel#LogoLabel {{
    background: transparent;
    border: none;
}}

/* --------------------------------------------------------------------------
   SPECIAL STATES - Estados visuales refinados
   -------------------------------------------------------------------------- */

/* Labels secundarios */
QLabel {{
    background: transparent;
}}

/* Campos de texto con estado */
QLineEdit {{
    background-color: {c.SURFACE};
    border: 1px solid {c.BORDER_DEFAULT};
    border-radius: 8px;
    padding: 9px 14px;
    color: {c.TEXT_PRIMARY};
    selection-background-color: {c.AMBER};
    selection-color: {c.TEXT_ON_AMBER};
}}

QLineEdit:hover {{
    border-color: {c.BORDER_HOVER};
}}

QLineEdit:focus {{
    border-color: {c.AMBER_DARK};
    background-color: {c.SURFACE_ELEVATED};
}}

/* Tooltips elegantes */
QToolTip {{
    background-color: {c.SURFACE_HIGHEST};
    border: 1px solid {c.BORDER_DEFAULT};
    border-radius: 6px;
    padding: 8px 12px;
    color: {c.TEXT_PRIMARY};
    font-size: 12px;
}}

/* Menús contextuales */
QMenu {{
    background-color: {c.SURFACE_ELEVATED};
    border: 1px solid {c.BORDER_DEFAULT};
    border-radius: 10px;
    padding: 6px;
}}

QMenu::item {{
    padding: 10px 20px;
    border-radius: 6px;
    color: {c.TEXT_PRIMARY};
}}

QMenu::item:selected {{
    background-color: {c.AMBER_CONTAINER};
    color: {c.AMBER_LIGHT};
}}

QMenu::separator {{
    height: 1px;
    background-color: {c.BORDER_SUBTLE};
    margin: 6px 12px;
}}

/* --------------------------------------------------------------------------
   MÉTRICAS AVANZADAS - Panel de análisis detallado
   -------------------------------------------------------------------------- */
QFrame#MetricsCard {{
    background-color: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 {c.SURFACE_ELEVATED},
        stop:1 {c.SURFACE}
    );
    border: 1px solid {c.BORDER_DEFAULT};
    border-radius: 14px;
}}

QLabel#MetricsTitle {{
    font-size: 14px;
    font-weight: 700;
    color: {c.AMBER_LIGHT};
    letter-spacing: 2px;
    text-transform: uppercase;
}}

QLabel#MetricsSubtitle {{
    font-size: 10px;
    font-weight: 400;
    color: {c.TEXT_TERTIARY};
    letter-spacing: 0.5px;
}}

QFrame#MetricsSeparator {{
    background-color: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 transparent,
        stop:0.2 {c.BORDER_DEFAULT},
        stop:0.8 {c.BORDER_DEFAULT},
        stop:1 transparent
    );
}}

QFrame#MetricRow {{
    background-color: {c.SURFACE_LOWEST};
    border: 1px solid {c.BORDER_INVISIBLE};
    border-radius: 8px;
}}

QFrame#MetricRow:hover {{
    background-color: {c.SURFACE};
    border-color: {c.BORDER_SUBTLE};
}}

QLabel#MetricName {{
    font-size: 12px;
    font-weight: 500;
    color: {c.TEXT_SECONDARY};
}}

QLabel#MetricValue {{
    font-size: 13px;
    font-weight: 600;
    color: {c.AMBER};
    font-family: "JetBrains Mono", "Cascadia Code", "Consolas", monospace;
}}

QProgressBar#MetricBar {{
    border: none;
    border-radius: 4px;
    background-color: {c.SURFACE_LOWEST};
    height: 8px;
}}

QProgressBar#MetricBar::chunk {{
    border-radius: 4px;
    background-color: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 {c.AMBER_DARK},
        stop:0.5 {c.AMBER},
        stop:1 {c.AMBER_LIGHT}
    );
}}
"""
