from __future__ import annotations

import unittest

import numpy as np

from src.application.analyze_face_use_case import AnalyzeFaceUseCase
from src.domain.models.face_metrics import (
    AnalysisStatus,
    DetectionResult,
    FacialLandmark,
    SymmetryMetrics,
)
from src.domain.services.symmetry_analyzer import SymmetryAnalyzer
from tests.test_fixtures import build_landmarks


class MockDetector:
    def __init__(self, detection: DetectionResult | None) -> None:
        self._detection = detection

    def detect(self, image_bgr: np.ndarray) -> DetectionResult | None:
        return self._detection


class FailingAnalyzer:
    def analyze(self, landmarks, image_shape):
        raise RuntimeError("forced analyzer error")


class SequenceAnalyzer:
    def __init__(self, scores: list[float]) -> None:
        self.scores = scores
        self.pointer = 0

    def analyze(self, landmarks, image_shape) -> SymmetryMetrics:
        score = self.scores[min(self.pointer, len(self.scores) - 1)]
        self.pointer += 1
        return make_metrics(score)


def make_metrics(score: float) -> SymmetryMetrics:
    asymmetry = max(0.0, min(1.0, (100.0 - score) / 100.0))
    normalized = {
        "asymmetry_distance": asymmetry,
        "eyebrow_height_diff": asymmetry,
        "eye_aperture_diff": asymmetry,
        "mouth_corner_height_diff": asymmetry,
        "mouth_tilt_component": asymmetry,
    }
    raw = {
        "asymmetry_distance": asymmetry * 100.0,
        "eyebrow_height_diff": asymmetry * 100.0,
        "eye_aperture_diff": asymmetry * 100.0,
        "mouth_corner_height_diff": asymmetry * 100.0,
        "mouth_tilt_component": asymmetry * 20.0,
    }

    return SymmetryMetrics(
        midline_x_raw=320.0,
        raw_metrics=raw,
        normalized_metrics=normalized,
        quality_flags=[],
        composite_score=score,
        interpretation_level="Alta simetria facial" if score >= 85 else "Simetria moderada",
    )


def sample_detection(quality_score: float = 0.9) -> DetectionResult:
    landmarks: list[FacialLandmark] = build_landmarks(False)
    return DetectionResult(
        landmarks=landmarks,
        image_shape=(480, 640, 3),
        quality_score=quality_score,
        warnings=[],
        face_bbox=(200, 120, 430, 430),
    )


class AnalyzeFaceUseCaseTestCase(unittest.TestCase):
    def test_execute_returns_no_face_status(self) -> None:
        use_case = AnalyzeFaceUseCase(detector=MockDetector(None), analyzer=SymmetryAnalyzer())

        result = use_case.execute(np.zeros((480, 640, 3), dtype=np.uint8), mode="single")

        self.assertEqual(result.status, AnalysisStatus.NO_FACE)
        self.assertIsNone(result.metrics)

    def test_execute_returns_low_quality_status(self) -> None:
        detection = sample_detection(quality_score=0.2)
        use_case = AnalyzeFaceUseCase(detector=MockDetector(detection), analyzer=SymmetryAnalyzer())

        result = use_case.execute(np.zeros((480, 640, 3), dtype=np.uint8), mode="single")

        self.assertEqual(result.status, AnalysisStatus.LOW_QUALITY)
        self.assertIsNone(result.metrics)
        self.assertIsNotNone(result.detection)

    def test_execute_returns_analyzed_status(self) -> None:
        detection = sample_detection(quality_score=0.9)
        use_case = AnalyzeFaceUseCase(detector=MockDetector(detection), analyzer=SymmetryAnalyzer())

        result = use_case.execute(np.zeros((480, 640, 3), dtype=np.uint8), mode="single")

        self.assertEqual(result.status, AnalysisStatus.ANALYZED)
        self.assertIsNotNone(result.metrics)
        self.assertTrue(result.has_face)

    def test_execute_returns_error_status_when_analyzer_fails(self) -> None:
        detection = sample_detection(quality_score=0.9)
        use_case = AnalyzeFaceUseCase(detector=MockDetector(detection), analyzer=FailingAnalyzer())

        result = use_case.execute(np.zeros((480, 640, 3), dtype=np.uint8), mode="single")

        self.assertEqual(result.status, AnalysisStatus.ERROR)
        self.assertIsNone(result.metrics)

    def test_live_mode_applies_temporal_smoothing(self) -> None:
        detection = sample_detection(quality_score=0.9)
        analyzer = SequenceAnalyzer([50.0, 90.0])
        use_case = AnalyzeFaceUseCase(detector=MockDetector(detection), analyzer=analyzer, smoothing_window=5)

        first = use_case.execute(np.zeros((480, 640, 3), dtype=np.uint8), mode="live")
        second = use_case.execute(np.zeros((480, 640, 3), dtype=np.uint8), mode="live")

        self.assertIsNotNone(first.metrics)
        self.assertIsNotNone(second.metrics)
        self.assertAlmostEqual(first.metrics.composite_score, 50.0, delta=0.1)
        self.assertAlmostEqual(second.metrics.composite_score, 70.0, delta=0.1)


if __name__ == "__main__":
    unittest.main()
