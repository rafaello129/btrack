from __future__ import annotations

import logging
from statistics import fmean
from time import perf_counter

import cv2
import numpy as np
from pathlib import Path
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Property, QUrl
from PySide6.QtGui import QIcon, QPixmap, QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QProgressBar,
    QScrollArea,
    QSplitter,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QGraphicsOpacityEffect,
)
from PySide6.QtMultimedia import QSoundEffect

from src.application.analyze_face_use_case import AnalyzeFaceUseCase
from src.domain.models.face_metrics import AnalysisResult, AnalysisStatus, SymmetryMetrics
from src.domain.services.symmetry_analyzer import SymmetryAnalyzer
from src.infrastructure.camera.webcam_service import WebcamService
from src.infrastructure.vision.mediapipe_face_detector import MediapipeFaceDetector
from src.shared.image_utils import bgr_to_qpixmap, draw_analysis_overlay, resize_for_display
from src.ui.widgets import CollapsibleSection, KpiCard, StatusBadge


class MainWindow(QMainWindow):
    METRIC_LABELS = {
        "asymmetry_distance": "Dist. global",
        "eye_aperture_diff": "Apertura ocular",
        "eyebrow_height_diff": "Altura de cejas",
        "mouth_corner_height_diff": "Comisuras",
        "mouth_tilt_component": "Inclinacion oral",
        "nasolabial_distance_diff": "Dif. nasolabial",
        "oral_excursion_diff": "Excursion oral",
        "roll_angle_component": "Inclinacion general",
    }

    def __init__(self) -> None:
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)

        self.setObjectName("MainWindow")
        self.setWindowTitle("NeuroFace | Monitoreo y analisis temprano de simetria facial")
        self.resize(1520, 900)
        
        # Configurar icono de la ventana
        icon_path = Path(__file__).parent.parent / "img" / "neuroface-icon-256.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self.webcam_service = WebcamService()
        self.face_detector = MediapipeFaceDetector(profile="quality", static_image_mode=False)
        self.symmetry_analyzer = SymmetryAnalyzer()
        self.analyze_face_use_case = AnalyzeFaceUseCase(
            detector=self.face_detector,
            analyzer=self.symmetry_analyzer,
            smoothing_window=5,
        )

        self.current_frame: np.ndarray | None = None
        self.frozen_frame: np.ndarray | None = None
        self.preview_frame: np.ndarray | None = None
        self.last_result: AnalysisResult | None = None

        self._camera_source_active = False
        self._is_frozen = False

        self._last_fps_timestamp = perf_counter()
        self._frame_counter = 0
        self._fps = 0.0

        self.camera_timer = QTimer(self)
        self.camera_timer.setInterval(33)
        self.camera_timer.timeout.connect(self._update_camera_frame)

        self.metric_rows: dict[str, tuple[QProgressBar, QLabel]] = {}
        self.region_rows: dict[str, tuple[StatusBadge, QLabel]] = {}
        self.body_splitter: QSplitter | None = None
        self.left_splitter: QSplitter | None = None
        self.right_column_widget: QWidget | None = None
        
        # Animaciones y efectos
        self._thinking_timer: QTimer | None = None
        self._thinking_dots = 0
        self._pulse_animation: QPropertyAnimation | None = None
        self._thinking_indicator: QLabel | None = None
        
        # Sonidos
        self._setup_sounds()

        self._build_ui()
        self._populate_camera_indices()
        self._refresh_control_states()
        self._set_system_state(
            "muted",
            "Sistema listo para captura",
            "Carga una imagen frontal o activa la camara para iniciar el tamizaje.",
        )
        
        # Abrir maximizado después de construir la UI
        self.showMaximized()
    
    def _setup_sounds(self) -> None:
        """Configura efectos de sonido."""
        self._sound_analyzing: QSoundEffect | None = None
        self._sound_success: QSoundEffect | None = None
        self._sound_warning: QSoundEffect | None = None
        
        # Los sonidos se cargarán si existen
        sounds_path = Path(__file__).parent.parent / "sounds"
        if not sounds_path.exists():
            sounds_path.mkdir(parents=True, exist_ok=True)

    def _build_ui(self) -> None:
        container = QWidget(self)
        self.setCentralWidget(container)

        root = QVBoxLayout(container)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(0)

        shell = QFrame()
        shell.setObjectName("AppShell")
        shell.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        root.addWidget(shell, 1)

        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(16)

        shell_layout.addWidget(self._build_top_bar())

        left_column = self._build_left_column()
        right_column = self._build_right_column()
        self.right_column_widget = right_column

        self.body_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.body_splitter.setChildrenCollapsible(False)
        self.body_splitter.addWidget(left_column)
        self.body_splitter.addWidget(right_column)
        self.body_splitter.setStretchFactor(0, 3)  # Izquierda 30%
        self.body_splitter.setStretchFactor(1, 7)  # Derecha 70%
        self.body_splitter.setHandleWidth(8)  # Handle más ancho para arrastrar fácilmente
        shell_layout.addWidget(self.body_splitter, 1)

        self._apply_responsive_geometry()

    def _build_top_bar(self) -> QWidget:
        frame = QFrame()
        frame.setObjectName("TopBar")

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(24, 20, 24, 20)

        # Logo y branding con fondo negro
        brand = QHBoxLayout()
        brand.setSpacing(20)
        
        # Logo más grande con fondo negro
        logo_container = QFrame()
        logo_container.setObjectName("LogoContainer")
        logo_container.setFixedSize(90, 70)
        logo_container_layout = QHBoxLayout(logo_container)
        logo_container_layout.setContentsMargins(0, 0, 0, 0)
        
        logo_label = QLabel()
        logo_label.setObjectName("LogoLabel")
        logo_path = Path(__file__).parent.parent / "img" / "neuroface-header.png"
        if logo_path.exists():
            logo_pixmap = QPixmap(str(logo_path))
            scaled_logo = logo_pixmap.scaledToHeight(60, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_logo)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_container_layout.addWidget(logo_label)
        brand.addWidget(logo_container)
        
        # Textos de marca
        brand_text = QVBoxLayout()
        brand_text.setSpacing(4)
        title = QLabel("NEUROFACE")
        title.setObjectName("BrandTitle")
        subtitle = QLabel("Monitoreo y análisis temprano de simetría facial")
        subtitle.setObjectName("BrandSubtitle")
        brand_text.addWidget(title)
        brand_text.addWidget(subtitle)
        brand.addLayout(brand_text)

        status = QVBoxLayout()
        status.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        status.setSpacing(8)
        
        badge_row = QHBoxLayout()
        badge_row.setAlignment(Qt.AlignmentFlag.AlignRight)
        badge_row.setSpacing(10)

        self.system_badge = StatusBadge("Sistema", "muted")
        self.workflow_badge = StatusBadge("Sin análisis", "muted")
        badge_row.addWidget(self.system_badge)
        badge_row.addWidget(self.workflow_badge)

        self.system_headline_label = QLabel("Esperando captura")
        self.system_headline_label.setObjectName("SectionTitle")
        self.system_headline_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.system_detail_label = QLabel("")
        self.system_detail_label.setObjectName("BrandSubtitle")
        self.system_detail_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        status.addLayout(badge_row)
        status.addWidget(self.system_headline_label)
        status.addWidget(self.system_detail_label)

        layout.addLayout(brand, stretch=3)
        layout.addLayout(status, stretch=2)
        return frame

    def _build_left_column(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("MainPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(16)

        image_card = QFrame()
        image_card.setObjectName("ImageCard")
        image_layout = QVBoxLayout(image_card)
        image_layout.setContentsMargins(16, 14, 16, 16)
        image_layout.setSpacing(10)

        image_title = QLabel("Captura Facial")
        image_title.setObjectName("SectionTitle")
        image_hint = QLabel("Alinea el rostro de frente, con iluminación uniforme y sin obstrucciones.")
        image_hint.setObjectName("ImageHint")

        self.image_label = QLabel("Esperando fuente de captura")
        self.image_label.setObjectName("ImageView")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.image_label.setMinimumSize(640, 380)

        image_layout.addWidget(image_title)
        image_layout.addWidget(image_hint)
        image_layout.addWidget(self.image_label)
        layout.addWidget(image_card, stretch=1)

        source_group = QGroupBox("FUENTE DE ENTRADA")
        source_layout = QGridLayout(source_group)
        source_layout.setSpacing(12)
        source_layout.setContentsMargins(14, 16, 14, 14)
        
        self.open_image_button = QPushButton("Abrir imagen")
        self.open_image_button.clicked.connect(self._open_image)
        self.camera_index_combo = QComboBox()
        self.start_camera_button = QPushButton("Iniciar cámara")
        self.start_camera_button.clicked.connect(self._start_camera)
        self.stop_camera_button = QPushButton("Detener cámara")
        self.stop_camera_button.setProperty("role", "danger")
        self.stop_camera_button.clicked.connect(self._stop_camera_action)

        cam_label = QLabel("Cámara")
        cam_label.setObjectName("ImageHint")
        
        source_layout.addWidget(self.open_image_button, 0, 0)
        source_layout.addWidget(cam_label, 0, 1)
        source_layout.addWidget(self.camera_index_combo, 0, 2)
        source_layout.addWidget(self.start_camera_button, 0, 3)
        source_layout.addWidget(self.stop_camera_button, 0, 4)

        actions_group = QGroupBox("ACCIONES PRINCIPALES")
        actions_layout = QHBoxLayout(actions_group)
        actions_layout.setSpacing(14)
        actions_layout.setContentsMargins(14, 16, 14, 14)
        
        self.analyze_button = QPushButton("  Analizar captura  ")
        self.analyze_button.setProperty("role", "primary")
        self.analyze_button.clicked.connect(self._analyze_current_frame)
        self.freeze_button = QPushButton("Congelar captura")
        self.freeze_button.clicked.connect(self._toggle_freeze)
        actions_layout.addWidget(self.analyze_button, stretch=2)
        actions_layout.addWidget(self.freeze_button, stretch=1)

        profile_group = QGroupBox("PERFIL DE ANÁLISIS")
        profile_layout = QGridLayout(profile_group)
        profile_layout.setSpacing(10)
        profile_layout.setContentsMargins(14, 16, 14, 14)
        
        self.profile_combo = QComboBox()
        self.profile_combo.addItems(["Quality", "Balanced", "Fast"])
        self.profile_combo.currentTextChanged.connect(self._on_profile_changed)
        self.live_smoothing_checkbox = QCheckBox("Suavizado temporal en flujo de cámara")
        self.live_smoothing_checkbox.setChecked(True)
        
        profile_label = QLabel("Perfil")
        profile_label.setObjectName("ImageHint")
        profile_layout.addWidget(profile_label, 0, 0)
        profile_layout.addWidget(self.profile_combo, 0, 1)
        profile_layout.addWidget(self.live_smoothing_checkbox, 1, 0, 1, 2)

        overlay_group = QGroupBox("VISUALIZACIÓN DE OVERLAY")
        overlay_layout = QHBoxLayout(overlay_group)
        overlay_layout.setSpacing(20)
        overlay_layout.setContentsMargins(14, 16, 14, 14)
        
        self.show_landmarks_checkbox = QCheckBox("Landmarks")
        self.show_landmarks_checkbox.setChecked(True)
        self.show_axis_checkbox = QCheckBox("Eje medio")
        self.show_axis_checkbox.setChecked(True)
        self.show_pairs_checkbox = QCheckBox("Pares simétricos")
        self.show_pairs_checkbox.setChecked(True)
        self.show_guides_checkbox = QCheckBox("Guías clínicas")
        self.show_guides_checkbox.setChecked(True)

        for checkbox in (
            self.show_landmarks_checkbox,
            self.show_axis_checkbox,
            self.show_pairs_checkbox,
            self.show_guides_checkbox,
        ):
            checkbox.stateChanged.connect(self._refresh_preview)
            overlay_layout.addWidget(checkbox)

        status_group = QGroupBox("ESTADO DEL SISTEMA")
        status_layout = QGridLayout(status_group)
        status_layout.setSpacing(8)
        status_layout.setContentsMargins(14, 16, 14, 14)
        
        self.status_label = QLabel("Listo para iniciar")
        self.origin_value_label = QLabel("Sin origen")
        self.fps_label = QLabel("0.0 FPS")
        self.latency_label = QLabel("Latencia: n/d")

        lbl_resumen = QLabel("Resumen")
        lbl_resumen.setObjectName("ImageHint")
        lbl_origen = QLabel("Origen")
        lbl_origen.setObjectName("ImageHint")
        lbl_desempeno = QLabel("Desempeño")
        lbl_desempeno.setObjectName("ImageHint")
        lbl_analisis = QLabel("Análisis")
        lbl_analisis.setObjectName("ImageHint")

        status_layout.addWidget(lbl_resumen, 0, 0)
        status_layout.addWidget(self.status_label, 0, 1)
        status_layout.addWidget(lbl_origen, 1, 0)
        status_layout.addWidget(self.origin_value_label, 1, 1)
        status_layout.addWidget(lbl_desempeno, 2, 0)
        status_layout.addWidget(self.fps_label, 2, 1)
        status_layout.addWidget(lbl_analisis, 3, 0)
        status_layout.addWidget(self.latency_label, 3, 1)

        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(14)
        controls_layout.addWidget(source_group)
        controls_layout.addWidget(actions_group)
        controls_layout.addWidget(profile_group)
        controls_layout.addWidget(overlay_group)
        controls_layout.addWidget(status_group)
        controls_layout.addStretch(1)

        controls_scroll = QScrollArea()
        controls_scroll.setWidgetResizable(True)
        controls_scroll.setFrameShape(QFrame.Shape.NoFrame)
        controls_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        controls_scroll.setWidget(controls_widget)

        self.left_splitter = QSplitter(Qt.Orientation.Vertical)
        self.left_splitter.setChildrenCollapsible(False)
        self.left_splitter.addWidget(image_card)
        self.left_splitter.addWidget(controls_scroll)
        self.left_splitter.setStretchFactor(0, 4)
        self.left_splitter.setStretchFactor(1, 2)

        layout.addWidget(self.left_splitter, 1)
        return panel

    def _build_right_column(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setMinimumWidth(500)
        # Sin máximo para que use todo el espacio disponible
        scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(8, 0, 0, 0)
        content_layout.setSpacing(14)

        # Panel Hero de Resultado Principal
        hero_card = QFrame()
        hero_card.setObjectName("ResultHeroCard")
        hero_layout = QVBoxLayout(hero_card)
        hero_layout.setContentsMargins(20, 18, 20, 18)
        hero_layout.setSpacing(12)

        hero_header = QHBoxLayout()
        self.result_badge = StatusBadge("Resultado orientativo", "muted")
        hero_header.addWidget(self.result_badge)
        hero_header.addStretch(1)
        
        # Indicador de análisis en progreso (animado)
        self._thinking_indicator = QLabel("⚡ Analizando")
        self._thinking_indicator.setObjectName("ThinkingIndicator")
        self._thinking_indicator.hide()
        hero_header.addWidget(self._thinking_indicator)

        self.hero_title_label = QLabel("Sin análisis de simetría")
        self.hero_title_label.setObjectName("HeroTitle")
        self.hero_title_label.setWordWrap(True)
        self.hero_subtitle_label = QLabel(
            "Captura una imagen frontal o congela la cámara para obtener una lectura orientativa."
        )
        self.hero_subtitle_label.setObjectName("HeroSubtitle")
        self.hero_subtitle_label.setWordWrap(True)

        self.hero_next_step_label = QLabel("Siguiente paso: iniciar una captura válida para análisis.")
        self.hero_next_step_label.setObjectName("HeroNextStep")
        self.hero_next_step_label.setWordWrap(True)

        hero_layout.addLayout(hero_header)
        hero_layout.addWidget(self.hero_title_label)
        hero_layout.addWidget(self.hero_subtitle_label)
        hero_layout.addWidget(self.hero_next_step_label)
        content_layout.addWidget(hero_card)

        # Indicadores de Tamizaje
        kpi_card = QFrame()
        kpi_card.setObjectName("Card")
        kpi_layout = QVBoxLayout(kpi_card)
        kpi_layout.setContentsMargins(18, 16, 18, 16)
        kpi_layout.setSpacing(14)
        kpi_title = QLabel("Indicadores de Tamizaje")
        kpi_title.setObjectName("SectionTitle")

        kpi_grid = QGridLayout()
        kpi_grid.setHorizontalSpacing(12)
        kpi_grid.setVerticalSpacing(12)
        self.kpi_cards = {
            "score": KpiCard("PUNTAJE"),
            "quality": KpiCard("CALIDAD"),
            "reliability": KpiCard("CONFIABILIDAD"),
            "attention": KpiCard("ATENCIÓN"),
            "alerts": KpiCard("ALERTAS"),
        }

        kpi_grid.addWidget(self.kpi_cards["score"], 0, 0)
        kpi_grid.addWidget(self.kpi_cards["quality"], 0, 1)
        kpi_grid.addWidget(self.kpi_cards["reliability"], 1, 0)
        kpi_grid.addWidget(self.kpi_cards["alerts"], 1, 1)
        kpi_grid.addWidget(self.kpi_cards["attention"], 2, 0, 1, 2)
        kpi_grid.setColumnStretch(0, 1)
        kpi_grid.setColumnStretch(1, 1)

        kpi_layout.addWidget(kpi_title)
        kpi_layout.addLayout(kpi_grid)
        content_layout.addWidget(kpi_card)

        # Interpretación Clínica Orientativa
        interpretation_card = QFrame()
        interpretation_card.setObjectName("Card")
        interpretation_layout = QVBoxLayout(interpretation_card)
        interpretation_layout.setContentsMargins(18, 16, 18, 16)
        interpretation_layout.setSpacing(10)
        interpretation_title = QLabel("Interpretación Clínica Orientativa")
        interpretation_title.setObjectName("SectionTitle")

        self.interpretation_label = QLabel(
            "El resultado se mostrará en lenguaje orientativo para apoyo al tamizaje temprano."
        )
        self.interpretation_label.setWordWrap(True)

        interpretation_layout.addWidget(interpretation_title)
        interpretation_layout.addWidget(self.interpretation_label)
        content_layout.addWidget(interpretation_card)

        # Hallazgos por Región Facial
        findings_card = QFrame()
        findings_card.setObjectName("Card")
        findings_layout = QGridLayout(findings_card)
        findings_layout.setContentsMargins(18, 16, 18, 16)
        findings_layout.setHorizontalSpacing(14)
        findings_layout.setVerticalSpacing(12)

        findings_title = QLabel("Hallazgos por Región Facial")
        findings_title.setObjectName("SectionTitle")
        findings_layout.addWidget(findings_title, 0, 0, 1, 3)

        regions = [
            ("ocular", "Región ocular"),
            ("cejas", "Cejas"),
            ("boca", "Boca y comisuras"),
            ("alineacion", "Alineación general"),
        ]

        for row, (key, title) in enumerate(regions, start=1):
            label = QLabel(title)
            label.setMinimumWidth(120)
            badge = StatusBadge("Sin lectura", "muted")
            badge.setMinimumWidth(100)
            badge.setMaximumWidth(130)
            detail = QLabel("Pendiente de análisis")
            detail.setWordWrap(True)
            detail.setObjectName("ImageHint")
            detail.setMinimumWidth(150)
            findings_layout.addWidget(label, row, 0)
            findings_layout.addWidget(badge, row, 1)
            findings_layout.addWidget(detail, row, 2)
            findings_layout.setColumnStretch(2, 1)  # La columna de detalle se expande
            self.region_rows[key] = (badge, detail)

        content_layout.addWidget(findings_card)

        # Métricas Avanzadas - Diseño mejorado
        metrics_card = QFrame()
        metrics_card.setObjectName("MetricsCard")
        metrics_layout = QVBoxLayout(metrics_card)
        metrics_layout.setContentsMargins(20, 18, 20, 18)
        metrics_layout.setSpacing(10)
        
        # Header con título
        metrics_title = QLabel("MÉTRICAS")
        metrics_title.setObjectName("MetricsTitle")
        metrics_layout.addWidget(metrics_title)
        
        # Separador visual
        metrics_separator = QFrame()
        metrics_separator.setObjectName("MetricsSeparator")
        metrics_separator.setFixedHeight(1)
        metrics_layout.addWidget(metrics_separator)

        # Métricas en una sola columna para mejor legibilidad
        for metric_key, metric_title in self.METRIC_LABELS.items():
            row_frame = QFrame()
            row_frame.setObjectName("MetricRow")
            row_layout = QHBoxLayout(row_frame)
            row_layout.setContentsMargins(12, 8, 12, 8)
            row_layout.setSpacing(12)
            
            name_label = QLabel(metric_title)
            name_label.setObjectName("MetricName")
            name_label.setMinimumWidth(140)
            
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setFixedHeight(8)
            bar.setObjectName("MetricBar")
            
            value_label = QLabel("--")
            value_label.setObjectName("MetricValue")
            value_label.setMinimumWidth(55)
            value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            row_layout.addWidget(name_label, stretch=0)
            row_layout.addWidget(bar, stretch=1)
            row_layout.addWidget(value_label, stretch=0)
            
            metrics_layout.addWidget(row_frame)
            self.metric_rows[metric_key] = (bar, value_label)
        
        content_layout.addWidget(metrics_card)

        self.tech_text = QTextEdit()
        self.tech_text.setReadOnly(True)
        self.tech_text.setMinimumHeight(170)
        self.tech_text.setPlainText("Sin detalle tecnico disponible.")
        content_layout.addWidget(CollapsibleSection("Detalle tecnico secundario", self.tech_text))

        disclaimer_card = QFrame()
        disclaimer_card.setObjectName("DisclaimerCard")
        disclaimer_layout = QVBoxLayout(disclaimer_card)
        disclaimer_layout.setContentsMargins(14, 12, 14, 12)
        disclaimer_title = QLabel("Aviso responsable")
        disclaimer_title.setObjectName("DisclaimerTitle")
        disclaimer_text = QLabel(
            "Este resultado es orientativo y no sustituye la valoracion medica. "
            "Ante sintomas recientes o hallazgos relevantes, se recomienda evaluacion clinica oportuna."
        )
        disclaimer_text.setObjectName("DisclaimerText")
        disclaimer_text.setWordWrap(True)
        disclaimer_layout.addWidget(disclaimer_title)
        disclaimer_layout.addWidget(disclaimer_text)
        content_layout.addWidget(disclaimer_card)

        content_layout.addStretch(1)
        scroll.setWidget(content)
        return scroll

    def _populate_camera_indices(self) -> None:
        available = WebcamService.list_available_cameras(max_index=5)
        if not available:
            available = [0]

        self.camera_index_combo.clear()
        for index in available:
            self.camera_index_combo.addItem(str(index), userData=index)

    def _open_image(self) -> None:
        if self.webcam_service.is_running:
            self._stop_camera()

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecciona una imagen",
            "",
            "Imagenes (*.png *.jpg *.jpeg *.bmp)",
        )
        if not path:
            return

        frame = cv2.imread(path)
        if frame is None:
            self._set_status("No se pudo cargar la imagen seleccionada.")
            self._set_system_state("warn", "Error al cargar imagen", "Selecciona un archivo valido.")
            return

        self._camera_source_active = False
        self._is_frozen = True
        self.current_frame = frame
        self.frozen_frame = frame.copy()
        self.last_result = None

        self.origin_value_label.setText("Imagen cargada")
        self._set_status("Imagen lista para analisis orientativo.")
        self._set_workflow_badge("Captura lista", "info")
        self._set_system_state("info", "Imagen cargada", "Puedes ejecutar el analisis de simetria facial.")
        self._reset_result_dashboard()
        self._refresh_preview()
        self._refresh_control_states()

    def _start_camera(self) -> None:
        camera_index = self.camera_index_combo.currentData()
        camera_index = 0 if camera_index is None else int(camera_index)

        self.webcam_service.set_camera_index(camera_index)
        if not self.webcam_service.start():
            self._set_status(f"No se pudo abrir camara {camera_index}.")
            self._set_system_state(
                "risk",
                "Camara no disponible",
                self.webcam_service.last_error or "Verifica permisos y dispositivo.",
            )
            return

        self._camera_source_active = True
        self._is_frozen = False
        self.frozen_frame = None
        self.camera_timer.start()

        self.origin_value_label.setText(f"Camara {camera_index}")
        self._set_status("Camara activa. Congela un frame para mayor consistencia.")
        self._set_workflow_badge("Captura activa", "info")
        self._set_system_state(
            "info",
            "Camara activa",
            "Asegura posicion frontal y luz uniforme antes de analizar.",
        )
        self._refresh_control_states()

    def _stop_camera_action(self) -> None:
        self._stop_camera()
        self._set_status("Camara detenida.")
        self._set_system_state(
            "muted",
            "Camara detenida",
            "Puedes cargar una imagen o reactivar la camara para continuar.",
        )

    def _stop_camera(self) -> None:
        self.camera_timer.stop()
        self.webcam_service.stop()
        self._camera_source_active = False
        self._is_frozen = False
        self.frozen_frame = None
        self._refresh_control_states()

    def _toggle_freeze(self) -> None:
        if not self.webcam_service.is_running:
            return

        if self._is_frozen:
            self._is_frozen = False
            self.frozen_frame = None
            self.freeze_button.setText("Congelar captura")
            self._set_status("Captura reanudada.")
            self._set_workflow_badge("Captura activa", "info")
            self._set_system_state("info", "Captura en vivo", "Congela un frame estable para analizar.")
            return

        if self.current_frame is None:
            self._set_status("Aun no hay frame disponible para congelar.")
            return

        self.frozen_frame = self.current_frame.copy()
        self._is_frozen = True
        self.freeze_button.setText("Reanudar captura")
        self._set_status("Frame congelado. Analiza esta muestra para un resultado consistente.")
        self._set_workflow_badge("Captura congelada", "warn")
        self._set_system_state("warn", "Captura congelada", "La muestra permanece fija hasta reanudar.")
        self._refresh_preview()

    def _update_camera_frame(self) -> None:
        frame = self.webcam_service.get_frame()
        if frame is None:
            return

        self.current_frame = frame
        self._frame_counter += 1

        now = perf_counter()
        elapsed = now - self._last_fps_timestamp
        if elapsed >= 1.0:
            self._fps = self._frame_counter / elapsed
            self.fps_label.setText(f"{self._fps:.1f} FPS")
            self._frame_counter = 0
            self._last_fps_timestamp = now

        if not self._is_frozen:
            self.preview_frame = frame
            self._refresh_preview()

    def _analyze_current_frame(self) -> None:
        frame_to_analyze = self._resolve_frame_for_analysis()
        if frame_to_analyze is None:
            self._set_status("No hay captura disponible para analizar.")
            self._set_system_state(
                "warn",
                "Sin muestra valida",
                "Carga una imagen o activa la camara para obtener una captura analizable.",
            )
            return

        if self._camera_source_active and not self._is_frozen and self.current_frame is not None:
            self.frozen_frame = self.current_frame.copy()
            self._is_frozen = True
            self.freeze_button.setText("Reanudar captura")

        mode = "single"
        if self._camera_source_active and self.live_smoothing_checkbox.isChecked() and not self._is_frozen:
            mode = "live"

        self._set_workflow_badge("Analizando", "info")
        self._start_thinking_animation()
        
        result = self.analyze_face_use_case.execute(frame_to_analyze, mode=mode)
        self.last_result = result
        
        self._stop_thinking_animation()

        total_latency = result.timings_ms.get("total")
        if total_latency is not None:
            self.latency_label.setText(f"Latencia: {total_latency:.1f} ms")

        self._render_results(result)
        self._pulse_result_card()  # Efecto visual al mostrar resultado
        self._set_status(result.user_message)
        self._refresh_preview()

    def _resolve_frame_for_analysis(self) -> np.ndarray | None:
        if self._camera_source_active:
            if self.frozen_frame is not None:
                return self.frozen_frame
            if self.current_frame is not None:
                return self.current_frame.copy()
            return None

        return self.frozen_frame if self.frozen_frame is not None else self.current_frame

    def _render_results(self, result: AnalysisResult) -> None:
        if result.status == AnalysisStatus.NO_FACE:
            self._update_hero(
                "warn",
                "Captura no interpretable",
                "No se detecto un rostro util",
                "La muestra no permite identificar landmarks faciales confiables.",
                "Siguiente paso: repite la captura con el rostro de frente y visible.",
            )
            self._update_kpis_no_face()
            self._update_region_findings_default("Sin lectura por falta de rostro detectable.")
            self._reset_metric_rows()
            self._set_interpretation_text(
                "La captura no ofrece condiciones suficientes para analisis orientativo. "
                "Se recomienda repetir en posicion frontal y con buena iluminacion."
            )
            self._set_workflow_badge("Captura invalida", "warn")
            self._set_system_state("warn", "Analisis incompleto", "No se detecto rostro valido.")
            self._set_technical_details(result)
            return

        if result.status == AnalysisStatus.ERROR:
            self._update_hero(
                "risk",
                "Error de analisis",
                "No fue posible completar el analisis",
                "Ocurrio un error tecnico durante el procesamiento.",
                "Siguiente paso: vuelve a capturar la muestra y reintenta.",
            )
            self._update_kpis_error()
            self._update_region_findings_default("Lectura no disponible por error interno.")
            self._reset_metric_rows()
            self._set_interpretation_text(
                "El resultado orientativo no pudo generarse por un error tecnico. "
                "Reintenta y verifica estado de camara y dependencias."
            )
            self._set_workflow_badge("Error", "risk")
            self._set_system_state("risk", "Fallo en el analisis", "Se produjo una excepcion interna.")
            self._set_technical_details(result)
            return

        if result.status == AnalysisStatus.LOW_QUALITY and result.detection is not None:
            quality_label, quality_tone, quality_text = self._quality_summary(result.detection.quality_score)
            self._update_hero(
                "warn",
                "Muestra limitada",
                "Captura insuficiente para interpretacion confiable",
                "Se detecto rostro, pero la calidad reduce la confiabilidad del tamizaje.",
                "Siguiente paso: repetir captura frontal con mejor iluminacion.",
            )
            self.kpi_cards["score"].update_data("--", "Sin lectura valida", "muted")
            self.kpi_cards["quality"].update_data(quality_label, quality_text, quality_tone)
            self.kpi_cards["reliability"].update_data("Limitada", "Resultado con baja confiabilidad", "warn")
            self.kpi_cards["attention"].update_data("Repetir muestra", "Se recomienda nueva captura", "warn")
            self.kpi_cards["alerts"].update_data(
                str(max(1, len(result.detection.warnings))),
                ", ".join(result.detection.warnings) or "Condiciones suboptimas",
                "warn",
            )
            self._update_region_findings_default("Sin hallazgos regionales por baja calidad de muestra.")
            self._reset_metric_rows()
            self._set_interpretation_text(
                "La captura presenta limitaciones que pueden distorsionar la lectura. "
                "Antes de extraer conclusiones, realiza una nueva toma estable y frontal."
            )
            self._set_workflow_badge("Muestra limitada", "warn")
            self._set_system_state("warn", "Calidad limitada", "La muestra no es optima para interpretar.")
            self._set_technical_details(result)
            return

        if result.metrics is None or result.detection is None:
            self._update_hero(
                "muted",
                "Resultado incompleto",
                "No se pudo consolidar la lectura",
                "El flujo de analisis devolvio una respuesta incompleta.",
                "Siguiente paso: repetir captura y analisis.",
            )
            self._update_kpis_error()
            self._update_region_findings_default("Sin datos")
            self._reset_metric_rows()
            self._set_interpretation_text("No hay informacion suficiente para un resumen orientativo.")
            self._set_workflow_badge("Incompleto", "warn")
            self._set_technical_details(result)
            return

        self._render_analyzed_result(result)
        self._set_technical_details(result)

    def _render_analyzed_result(self, result: AnalysisResult) -> None:
        metrics = result.metrics
        detection = result.detection
        assert metrics is not None
        assert detection is not None

        severity_label, severity_tone, severity_subtitle, next_step = self._severity_summary(
            metrics.composite_score
        )
        quality_label, quality_tone, quality_text = self._quality_summary(detection.quality_score)
        reliability_value, reliability_label, reliability_tone = self._reliability_summary(
            detection.quality_score,
            detection.warnings,
            metrics.quality_flags,
        )
        region_summary = self._region_summary(metrics)
        interpretation_text = self._build_interpretation_text(
            severity_label, quality_label, region_summary, detection
        )

        alerts = sorted(set(detection.warnings + metrics.quality_flags))
        attention_value, attention_helper, attention_tone = self._attention_summary(
            metrics.composite_score,
            detection.quality_score,
            alerts,
        )

        self._update_hero(
            severity_tone,
            "Resultado orientativo",
            severity_label,
            severity_subtitle,
            f"Siguiente paso: {next_step}",
        )

        self.kpi_cards["score"].update_data(
            f"{metrics.composite_score:.1f}",
            "Escala orientativa de simetria (0-100)",
            severity_tone,
        )
        self.kpi_cards["quality"].update_data(quality_label, quality_text, quality_tone)
        self.kpi_cards["reliability"].update_data(
            f"{reliability_value:.0f}%",
            reliability_label,
            reliability_tone,
        )
        self.kpi_cards["attention"].update_data(attention_value, attention_helper, attention_tone)
        self.kpi_cards["alerts"].update_data(
            "Sin alertas" if not alerts else str(len(alerts)),
            "Sin alertas relevantes" if not alerts else ", ".join(alerts),
            "good" if not alerts else "warn",
        )

        self._set_interpretation_text(interpretation_text)
        self._update_region_findings(region_summary)
        self._update_metric_rows(metrics)

        self._set_workflow_badge("Analisis completado", severity_tone)
        self._set_system_state(
            severity_tone,
            "Lectura de simetria finalizada",
            "Resultado orientativo disponible para apoyo a deteccion temprana.",
        )

    def _severity_summary(self, score: float) -> tuple[str, str, str, str]:
        if score >= 93.0:
            return (
                "Simetria facial conservada",
                "good",
                "No se observan variaciones relevantes en los puntos faciales evaluados.",
                "Mantener monitoreo orientativo y repetir si aparecen sintomas recientes.",
            )
        if score >= 80.0:
            return (
                "Asimetria facial leve detectada",
                "info",
                "Se identifican diferencias discretas compatibles con variacion leve.",
                "Repetir captura y vigilar evolucion en las proximas horas.",
            )
        if score >= 66.0:
            return (
                "Hallazgos sugestivos de alteracion moderada de simetria",
                "warn",
                "Se observan variaciones notables en regiones clave del rostro.",
                "Considerar evaluacion clinica temprana, especialmente ante sintomas recientes.",
            )
        return (
            "Hallazgos compatibles con asimetria facial relevante",
            "risk",
            "La muestra presenta diferencias marcadas entre ambos lados del rostro.",
            "Se sugiere evaluacion clinica oportuna para descartar alteracion neurologica.",
        )

    def _quality_summary(self, quality_score: float) -> tuple[str, str, str]:
        if quality_score >= 0.85:
            return ("Excelente", "good", "Muestra estable, frontal y adecuada para analisis.")
        if quality_score >= 0.70:
            return ("Adecuada", "info", "La captura permite una interpretacion confiable.")
        if quality_score >= 0.55:
            return ("Limitada", "warn", "Algunos factores pueden afectar la precision.")
        return ("Baja", "risk", "Se recomienda repetir la captura para mejorar confiabilidad.")

    def _reliability_summary(
        self,
        quality_score: float,
        detection_warnings: list[str],
        metric_flags: list[str],
    ) -> tuple[float, str, str]:
        warnings_count = len(set(detection_warnings + metric_flags))
        reliability = max(0.0, min(100.0, quality_score * 100.0 - warnings_count * 8.0))

        if reliability >= 85:
            return reliability, "Alta confiabilidad de muestra", "good"
        if reliability >= 70:
            return reliability, "Confiabilidad favorable para tamizaje", "info"
        if reliability >= 55:
            return reliability, "Confiabilidad intermedia, interpretar con cautela", "warn"
        return reliability, "Confiabilidad limitada, repetir muestra", "risk"

    def _attention_summary(
        self,
        score: float,
        quality_score: float,
        alerts: list[str],
    ) -> tuple[str, str, str]:
        if quality_score < 0.55:
            return ("Repetir captura", "La calidad actual no permite una lectura solida.", "warn")
        if score < 66.0:
            return (
                "Revision clinica sugerida",
                "Hallazgos orientativos relevantes en simetria facial.",
                "risk",
            )
        if score < 80.0:
            return (
                "Seguimiento cercano",
                "Repetir analisis y considerar valoracion clinica temprana.",
                "warn",
            )
        if alerts:
            return ("Monitoreo con cautela", "Existen alertas de calidad o postura.", "info")
        return ("Monitoreo rutinario", "Sin alertas relevantes para esta captura.", "good")

    def _region_summary(self, metrics: SymmetryMetrics) -> dict[str, tuple[str, str, str]]:
        norm = metrics.normalized_metrics

        ocular_value = norm.get("eye_aperture_diff", 0.0)
        cejas_value = norm.get("eyebrow_height_diff", 0.0)
        boca_value = fmean(
            [
                norm.get("mouth_corner_height_diff", 0.0),
                norm.get("mouth_tilt_component", 0.0),
                norm.get("nasolabial_distance_diff", 0.0),
                norm.get("oral_excursion_diff", 0.0),
            ]
        )
        alineacion_value = fmean([norm.get("asymmetry_distance", 0.0), norm.get("roll_angle_component", 0.0)])

        return {
            "ocular": self._describe_region_value(
                ocular_value,
                "Apertura ocular balanceada.",
                "Leve diferencia de apertura entre ambos lados.",
                "Variacion ocular moderada en la muestra.",
                "Variacion ocular relevante en esta captura.",
            ),
            "cejas": self._describe_region_value(
                cejas_value,
                "Altura de cejas estable.",
                "Leve diferencia de altura en cejas.",
                "Variacion moderada de altura de cejas.",
                "Diferencia marcada de altura de cejas.",
            ),
            "boca": self._describe_region_value(
                boca_value,
                "Comisuras y linea oral estables.",
                "Leve variacion en comisuras o inclinacion oral.",
                "Variacion moderada en region oral.",
                "Variacion relevante en region oral/comisuras.",
            ),
            "alineacion": self._describe_region_value(
                alineacion_value,
                "Alineacion facial general conservada.",
                "Leve desviacion de alineacion general.",
                "Desviacion moderada en alineacion global.",
                "Desalineacion global relevante.",
            ),
        }

    def _describe_region_value(
        self,
        value: float,
        good_text: str,
        info_text: str,
        warn_text: str,
        risk_text: str,
    ) -> tuple[str, str, str]:
        if value <= 0.05:
            return "Conservada", "good", good_text
        if value <= 0.12:
            return "Leve", "info", info_text
        if value <= 0.22:
            return "Moderada", "warn", warn_text
        return "Relevante", "risk", risk_text

    def _build_interpretation_text(
        self,
        severity_label: str,
        quality_label: str,
        region_summary: dict[str, tuple[str, str, str]],
        detection,
    ) -> str:
        region_notes = [
            region_summary["ocular"][2],
            region_summary["cejas"][2],
            region_summary["boca"][2],
            region_summary["alineacion"][2],
        ]

        warning_text = ""
        if detection.warnings:
            warning_text = (
                " Se detectaron condiciones de captura que pueden influir en la lectura: "
                + ", ".join(detection.warnings)
                + "."
            )

        return (
            f"{severity_label}. Calidad de muestra: {quality_label}. "
            f"Resumen regional: {region_notes[0]} {region_notes[1]} {region_notes[2]} {region_notes[3]}"
            f"{warning_text} Este resultado es orientativo y no sustituye valoracion medica."
        )

    def _set_interpretation_text(self, text: str) -> None:
        self.interpretation_label.setText(text)

    def _update_region_findings(self, summary: dict[str, tuple[str, str, str]]) -> None:
        for key, (badge_text, tone, detail_text) in summary.items():
            badge, detail = self.region_rows[key]
            badge.setText(badge_text)
            badge.set_tone(tone)
            detail.setText(detail_text)

    def _update_region_findings_default(self, detail_text: str) -> None:
        for badge, detail in self.region_rows.values():
            badge.setText("Sin lectura")
            badge.set_tone("muted")
            detail.setText(detail_text)

    def _update_metric_rows(self, metrics: SymmetryMetrics) -> None:
        for key, (bar, value_label) in self.metric_rows.items():
            value = metrics.normalized_metrics.get(key, 0.0)
            percent = max(0.0, min(100.0, value * 100.0))
            bar.setValue(int(round(percent)))
            value_label.setText(f"{percent:4.1f}%")

            if percent >= 35.0:
                value_label.setStyleSheet("color: #ffb4bd;")
            elif percent >= 22.0:
                value_label.setStyleSheet("color: #ffd79f;")
            elif percent >= 12.0:
                value_label.setStyleSheet("color: #9edcff;")
            else:
                value_label.setStyleSheet("color: #9ef0c2;")

    def _reset_metric_rows(self) -> None:
        for bar, value_label in self.metric_rows.values():
            bar.setValue(0)
            value_label.setText("--")
            value_label.setStyleSheet("color: #b8c9d9;")

    def _update_hero(
        self,
        tone: str,
        badge_text: str,
        title: str,
        subtitle: str,
        next_step: str,
    ) -> None:
        self.result_badge.setText(badge_text)
        self.result_badge.set_tone(tone)
        self.hero_title_label.setText(title)
        self.hero_subtitle_label.setText(subtitle)
        self.hero_next_step_label.setText(next_step)

    def _update_kpis_no_face(self) -> None:
        self.kpi_cards["score"].update_data("--", "Sin rostro detectable", "muted")
        self.kpi_cards["quality"].update_data("--", "No aplica", "muted")
        self.kpi_cards["reliability"].update_data("--", "No se puede estimar", "muted")
        self.kpi_cards["attention"].update_data("Repetir captura", "Se requiere muestra valida", "warn")
        self.kpi_cards["alerts"].update_data("1", "No se detecto rostro en la muestra", "warn")

    def _update_kpis_error(self) -> None:
        self.kpi_cards["score"].update_data("--", "No disponible", "muted")
        self.kpi_cards["quality"].update_data("--", "No disponible", "muted")
        self.kpi_cards["reliability"].update_data("--", "Error de procesamiento", "risk")
        self.kpi_cards["attention"].update_data("Reintentar", "Verificar captura y repetir", "warn")
        self.kpi_cards["alerts"].update_data("Tecnico", "Error interno durante analisis", "risk")

    def _set_technical_details(self, result: AnalysisResult) -> None:
        lines = [
            f"status={result.status.value}",
            f"user_message={result.user_message}",
            f"technical_message={result.technical_message or 'n/a'}",
        ]

        if result.detection is not None:
            lines.append(f"quality_score={result.detection.quality_score:.4f}")
            lines.append(f"warnings={result.detection.warnings}")
            lines.append(f"face_bbox={result.detection.face_bbox}")

        if result.metrics is not None:
            lines.append(f"composite_score={result.metrics.composite_score:.3f}")
            lines.append(f"interpretation_level={result.metrics.interpretation_level}")
            lines.append("normalized_metrics:")
            for key, value in sorted(result.metrics.normalized_metrics.items()):
                lines.append(f"  - {key}: {value:.6f}")
            lines.append("raw_metrics:")
            for key, value in sorted(result.metrics.raw_metrics.items()):
                lines.append(f"  - {key}: {value:.6f}")

        if result.timings_ms:
            lines.append("timings_ms:")
            for key, value in sorted(result.timings_ms.items()):
                lines.append(f"  - {key}: {value:.2f}")

        self.tech_text.setPlainText("\n".join(lines))

    def _reset_result_dashboard(self) -> None:
        self._update_hero(
            "muted",
            "Resultado orientativo",
            "Analisis pendiente",
            "Ejecuta una captura valida para obtener hallazgos orientativos de simetria facial.",
            "Siguiente paso: presiona 'Analizar captura'.",
        )
        self.kpi_cards["score"].update_data("--", "Pendiente", "muted")
        self.kpi_cards["quality"].update_data("--", "Pendiente", "muted")
        self.kpi_cards["reliability"].update_data("--", "Pendiente", "muted")
        self.kpi_cards["attention"].update_data("Pendiente", "Aun no hay lectura", "muted")
        self.kpi_cards["alerts"].update_data("--", "Sin eventos", "muted")
        self._set_interpretation_text("La lectura orientativa aparecera aqui tras analizar una muestra valida.")
        self._update_region_findings_default("Pendiente de analisis")
        self._reset_metric_rows()
        self.tech_text.setPlainText("Sin detalle tecnico disponible.")

    def _refresh_preview(self) -> None:
        frame = self._resolve_preview_frame()
        if frame is None:
            self.image_label.setText("Sin captura activa")
            return

        rendered = frame
        if self.last_result is not None and self.last_result.detection is not None:
            rendered = draw_analysis_overlay(
                image_bgr=frame,
                landmarks=self.last_result.detection.landmarks,
                primitives=self.last_result.overlay_primitives,
                show_landmarks=self.show_landmarks_checkbox.isChecked(),
                show_axis=self.show_axis_checkbox.isChecked(),
                show_pairs=self.show_pairs_checkbox.isChecked(),
                face_bbox=self.last_result.detection.face_bbox,
                metrics=self.last_result.metrics,
                show_guides=self.show_guides_checkbox.isChecked(),
            )

        self.preview_frame = rendered
        target_width = max(self.image_label.width() - 8, 1)
        target_height = max(self.image_label.height() - 8, 1)
        resized = resize_for_display(rendered, target_width, target_height)
        self.image_label.setPixmap(bgr_to_qpixmap(resized))

    def _resolve_preview_frame(self) -> np.ndarray | None:
        if self._camera_source_active and self._is_frozen and self.frozen_frame is not None:
            return self.frozen_frame.copy()
        if self._camera_source_active and self.current_frame is not None:
            return self.current_frame.copy()
        if self.frozen_frame is not None:
            return self.frozen_frame.copy()
        if self.current_frame is not None:
            return self.current_frame.copy()
        return None

    def _on_profile_changed(self, profile: str) -> None:
        try:
            # Convert to lowercase to match PROFILE_SETTINGS keys
            profile_key = profile.lower()
            self.face_detector.set_profile(profile_key)  # type: ignore[arg-type]
            self._set_status(f"Perfil de analisis activo: {profile}")
            self._set_system_state("info", "Perfil actualizado", f"Perfil '{profile}' activo.")
        except Exception as exc:  # pragma: no cover
            self.logger.exception("Failed to switch detector profile")
            self._set_status(f"No se pudo cambiar perfil: {exc}")
            self._set_system_state("risk", "Error al cambiar perfil", str(exc))

    def _set_status(self, text: str) -> None:
        self.status_label.setText(text)

    def _set_system_state(self, tone: str, headline: str, detail: str) -> None:
        self.system_badge.setText("Sistema")
        self.system_badge.set_tone(tone)
        self.system_headline_label.setText(headline)
        self.system_detail_label.setText(detail)

    def _set_workflow_badge(self, text: str, tone: str) -> None:
        self.workflow_badge.setText(text)
        self.workflow_badge.set_tone(tone)

    def _refresh_control_states(self) -> None:
        running = self.webcam_service.is_running
        self.start_camera_button.setEnabled(not running)
        self.stop_camera_button.setEnabled(running)
        self.freeze_button.setEnabled(running)
        if not running:
            self.freeze_button.setText("Congelar captura")

    def _apply_responsive_geometry(self) -> None:
        if not hasattr(self, 'body_splitter') or self.body_splitter is None:
            return

        width = max(self.width(), 1024)
        # Columna derecha ocupa 60% del espacio disponible (sin margins)
        usable_width = width - 50  # Descontar márgenes
        right_target = int(usable_width * 0.58)
        left_target = int(usable_width * 0.42)
        
        # Mínimos para que no se corten
        left_target = max(left_target, 420)
        right_target = max(right_target, 520)
        
        self.body_splitter.setSizes([left_target, right_target])

        if self.left_splitter is not None:
            content_height = max(self.height() - 210, 520)
            if self.height() <= 950:
                image_target = int(content_height * 0.68)
            else:
                image_target = int(content_height * 0.72)
            image_target = max(420, min(image_target, 980))
            controls_target = max(content_height - image_target, 260)
            self.left_splitter.setSizes([image_target, controls_target])

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        self._apply_responsive_geometry()
        self._refresh_preview()

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self._stop_thinking_animation()
        self._stop_camera()
        self.face_detector.close()
        super().closeEvent(event)
    
    # =========================================================================
    # ANIMACIONES Y EFECTOS VISUALES
    # =========================================================================
    
    def _start_thinking_animation(self) -> None:
        """Inicia la animación de 'pensando' durante el análisis."""
        if self._thinking_indicator is not None:
            self._thinking_indicator.show()
            self._thinking_dots = 0
            
            # Timer para animar los puntos
            if self._thinking_timer is None:
                self._thinking_timer = QTimer(self)
                self._thinking_timer.timeout.connect(self._update_thinking_animation)
            self._thinking_timer.start(300)
    
    def _update_thinking_animation(self) -> None:
        """Actualiza el texto animado del indicador de pensamiento."""
        if self._thinking_indicator is None:
            return
        
        self._thinking_dots = (self._thinking_dots + 1) % 4
        dots = "." * self._thinking_dots
        icons = ["⚡", "🧠", "✨", "🔍"]
        icon = icons[self._thinking_dots]
        self._thinking_indicator.setText(f"{icon} Analizando{dots}")
    
    def _stop_thinking_animation(self) -> None:
        """Detiene la animación de pensamiento."""
        if self._thinking_timer is not None:
            self._thinking_timer.stop()
        if self._thinking_indicator is not None:
            self._thinking_indicator.hide()
    
    def _pulse_result_card(self) -> None:
        """Efecto de pulso sutil en el resultado para captar atención."""
        try:
            # Buscar el hero card
            hero_card = self.findChild(QFrame, "ResultHeroCard")
            if hero_card is None:
                return
            
            # Crear efecto de opacidad
            opacity_effect = QGraphicsOpacityEffect(hero_card)
            hero_card.setGraphicsEffect(opacity_effect)
            
            # Animación de fade-in
            self._pulse_animation = QPropertyAnimation(opacity_effect, b"opacity")
            self._pulse_animation.setDuration(400)
            self._pulse_animation.setStartValue(0.7)
            self._pulse_animation.setEndValue(1.0)
            self._pulse_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._pulse_animation.start()
        except Exception:
            pass  # Silently ignore animation errors
