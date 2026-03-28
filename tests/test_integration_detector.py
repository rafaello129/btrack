from __future__ import annotations

from pathlib import Path
import unittest

import cv2

from src.infrastructure.vision.mediapipe_face_detector import MediapipeFaceDetector


class DetectorIntegrationTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.detector = MediapipeFaceDetector(profile="quality", static_image_mode=True)
        cls.assets_dir = Path("assets/images")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.detector.close()

    def test_no_face_image_returns_none(self) -> None:
        image_path = self.assets_dir / "no_face.png"
        image = cv2.imread(str(image_path))
        self.assertIsNotNone(image, "Expected assets/images/no_face.png to exist")

        detection = self.detector.detect(image)
        self.assertIsNone(detection)

    def test_frontal_face_image_detects_face(self) -> None:
        image_path = self.assets_dir / "frontal_face.jpg"
        if not image_path.exists():
            self.skipTest("assets/images/frontal_face.jpg not present")

        image = cv2.imread(str(image_path))
        self.assertIsNotNone(image)

        detection = self.detector.detect(image)
        self.assertIsNotNone(detection)
        self.assertGreater(detection.quality_score, 0.3)

    def test_partial_face_image_reports_warning(self) -> None:
        image_path = self.assets_dir / "partial_face.jpg"
        if not image_path.exists():
            self.skipTest("assets/images/partial_face.jpg not present")

        image = cv2.imread(str(image_path))
        self.assertIsNotNone(image)

        detection = self.detector.detect(image)
        self.assertIsNotNone(detection)
        self.assertTrue(
            any(w in detection.warnings for w in ["partial_face_frame", "face_too_small"]),
            f"Expected partial face warning, got {detection.warnings}",
        )


if __name__ == "__main__":
    unittest.main()
