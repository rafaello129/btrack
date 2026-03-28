from __future__ import annotations

import logging
from collections import deque
from statistics import fmean
from time import perf_counter
from typing import Literal, Protocol

import numpy as np

from src.domain.config.scoring_config import DEFAULT_SYMMETRY_CONFIG
from src.domain.models.face_metrics import (
    AnalysisResult,
    AnalysisStatus,
    DetectionResult,
    OverlayPrimitives,
    SymmetryMetrics,
)
from src.domain.services.symmetry_analyzer import SymmetryAnalyzer

AnalyzeMode = Literal["single", "live"]


class FaceDetector(Protocol):
    def detect(self, image_bgr: np.ndarray) -> DetectionResult | None:
        ...


class Analyzer(Protocol):
    def analyze(self, landmarks, image_shape) -> SymmetryMetrics:
        ...


class AnalyzeFaceUseCase:
    OVERLAY_PAIRS = [
        (33, 263),
        (133, 362),
        (61, 291),
        (93, 323),
        (132, 361),
        (234, 454),
    ]

    def __init__(
        self,
        detector: FaceDetector,
        analyzer: Analyzer,
        smoothing_window: int = 5,
    ) -> None:
        self.detector = detector
        self.analyzer = analyzer
        self.logger = logging.getLogger(self.__class__.__name__)
        self._history: deque[SymmetryMetrics] = deque(maxlen=max(1, smoothing_window))
        self._quality_threshold = getattr(
            getattr(self.analyzer, "config", DEFAULT_SYMMETRY_CONFIG),
            "quality",
            DEFAULT_SYMMETRY_CONFIG.quality,
        ).low_quality_min_score

    def execute(self, image_bgr: np.ndarray, mode: AnalyzeMode = "single") -> AnalysisResult:
        timings: dict[str, float] = {}
        total_start = perf_counter()

        detect_start = perf_counter()
        try:
            detection = self.detector.detect(image_bgr)
        except Exception as exc:  # pragma: no cover - defensive runtime guard
            self.logger.exception("Face detector crashed during execute")
            timings["detect"] = (perf_counter() - detect_start) * 1000.0
            timings["total"] = (perf_counter() - total_start) * 1000.0
            return AnalysisResult(
                status=AnalysisStatus.ERROR,
                user_message="Ocurrio un error al detectar el rostro.",
                technical_message=str(exc),
                timings_ms=self._round_timings(timings),
            )

        timings["detect"] = (perf_counter() - detect_start) * 1000.0

        if detection is None:
            timings["total"] = (perf_counter() - total_start) * 1000.0
            self._history.clear()
            return AnalysisResult(
                status=AnalysisStatus.NO_FACE,
                user_message="No se detecto rostro. Ajusta encuadre e iluminacion.",
                technical_message="Detector returned no landmarks.",
                timings_ms=self._round_timings(timings),
            )

        if detection.quality_score < self._quality_threshold:
            timings["total"] = (perf_counter() - total_start) * 1000.0
            self._history.clear()
            return AnalysisResult(
                status=AnalysisStatus.LOW_QUALITY,
                user_message="Rostro detectado con baja calidad. Corrige pose/iluminacion.",
                technical_message=", ".join(detection.warnings) or "Low quality sample",
                detection=detection,
                overlay_primitives=self._build_overlay_primitives(detection),
                timings_ms=self._round_timings(timings),
            )

        analyze_start = perf_counter()
        try:
            metrics = self.analyzer.analyze(detection.landmarks, detection.image_shape)
            if mode == "live":
                metrics = self._smooth_metrics(metrics)
            else:
                self._history.clear()
        except Exception as exc:
            self.logger.exception("Symmetry analyzer crashed during execute")
            timings["analyze"] = (perf_counter() - analyze_start) * 1000.0
            timings["total"] = (perf_counter() - total_start) * 1000.0
            return AnalysisResult(
                status=AnalysisStatus.ERROR,
                user_message="No fue posible completar el analisis.",
                technical_message=str(exc),
                detection=detection,
                overlay_primitives=self._build_overlay_primitives(detection),
                timings_ms=self._round_timings(timings),
            )

        timings["analyze"] = (perf_counter() - analyze_start) * 1000.0
        timings["total"] = (perf_counter() - total_start) * 1000.0

        warnings = detection.warnings + metrics.quality_flags
        guidance = "Analisis completado." if not warnings else "Analisis completado con advertencias."

        return AnalysisResult(
            status=AnalysisStatus.ANALYZED,
            user_message=guidance,
            technical_message=", ".join(sorted(set(warnings))),
            detection=detection,
            metrics=metrics,
            overlay_primitives=self._build_overlay_primitives(detection),
            timings_ms=self._round_timings(timings),
        )

    def _build_overlay_primitives(self, detection: DetectionResult) -> OverlayPrimitives:
        points = {landmark.index: landmark for landmark in detection.landmarks}

        midline_samples = [
            points[index].x
            for index in SymmetryAnalyzer.MIDLINE_INDICES
            if index in points
        ]

        height, width = detection.image_shape[:2]
        if midline_samples:
            axis_x = int(round(fmean(midline_samples)))
        else:
            axis_x = width // 2
        axis_x = max(0, min(axis_x, width - 1))

        pairs: list[tuple[tuple[int, int], tuple[int, int]]] = []
        for left_idx, right_idx in self.OVERLAY_PAIRS:
            if left_idx in points and right_idx in points:
                pairs.append(
                    (
                        (int(round(points[left_idx].x)), int(round(points[left_idx].y))),
                        (int(round(points[right_idx].x)), int(round(points[right_idx].y))),
                    )
                )

        return OverlayPrimitives(
            axis_line=((axis_x, 0), (axis_x, max(0, height - 1))),
            symmetry_pairs=pairs,
        )

    def _smooth_metrics(self, metrics: SymmetryMetrics) -> SymmetryMetrics:
        self._history.append(metrics)

        raw_keys = metrics.raw_metrics.keys()
        norm_keys = metrics.normalized_metrics.keys()

        raw_avg = {
            key: fmean(item.raw_metrics[key] for item in self._history)
            for key in raw_keys
        }
        norm_avg = {
            key: fmean(item.normalized_metrics[key] for item in self._history)
            for key in norm_keys
        }
        score = fmean(item.composite_score for item in self._history)

        return SymmetryMetrics(
            midline_x_raw=fmean(item.midline_x_raw for item in self._history),
            raw_metrics=raw_avg,
            normalized_metrics=norm_avg,
            quality_flags=metrics.quality_flags,
            composite_score=score,
            interpretation_level=self._interpret_score(score),
        )

    def _interpret_score(self, score: float) -> str:
        thresholds = getattr(
            getattr(self.analyzer, "config", DEFAULT_SYMMETRY_CONFIG),
            "thresholds",
            DEFAULT_SYMMETRY_CONFIG.thresholds,
        )
        if score >= thresholds.high_symmetry:
            return "Alta simetria facial"
        if score >= thresholds.moderate_symmetry:
            return "Asimetria leve"
        if score >= thresholds.mild_asymmetry:
            return "Asimetria moderada"
        return "Asimetria marcada"

    def _round_timings(self, timings: dict[str, float]) -> dict[str, float]:
        return {key: round(value, 2) for key, value in timings.items()}
