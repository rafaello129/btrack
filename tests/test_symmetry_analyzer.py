from __future__ import annotations

import unittest

from src.domain.services.symmetry_analyzer import SymmetryAnalyzer
from tests.test_fixtures import build_landmarks, transform_landmarks


class SymmetryAnalyzerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.analyzer = SymmetryAnalyzer()

    def test_more_symmetric_landmarks_produce_higher_score(self) -> None:
        symmetric_metrics = self.analyzer.analyze(build_landmarks(False), (480, 640, 3))
        asymmetric_metrics = self.analyzer.analyze(build_landmarks(True), (480, 640, 3))

        self.assertGreater(symmetric_metrics.composite_score, asymmetric_metrics.composite_score)

    def test_score_is_stable_under_scale_and_translation(self) -> None:
        base_landmarks = build_landmarks(False)
        transformed = transform_landmarks(base_landmarks, scale=1.35, tx=140.0, ty=80.0)

        base_metrics = self.analyzer.analyze(base_landmarks, (480, 640, 3))
        transformed_metrics = self.analyzer.analyze(transformed, (720, 960, 3))

        self.assertAlmostEqual(
            base_metrics.composite_score,
            transformed_metrics.composite_score,
            delta=2.0,
        )

    def test_score_is_stable_under_small_rotation(self) -> None:
        base_landmarks = build_landmarks(False)
        rotated = transform_landmarks(base_landmarks, angle_deg=8.0)

        base_metrics = self.analyzer.analyze(base_landmarks, (480, 640, 3))
        rotated_metrics = self.analyzer.analyze(rotated, (640, 640, 3))

        self.assertAlmostEqual(
            base_metrics.composite_score,
            rotated_metrics.composite_score,
            delta=4.0,
        )


if __name__ == "__main__":
    unittest.main()
