from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Literal

import cv2
import mediapipe as mp
import numpy as np

from src.domain.config.scoring_config import DEFAULT_SYMMETRY_CONFIG
from src.domain.models.face_metrics import DetectionResult, FacialLandmark

DetectorProfile = Literal["quality", "balanced", "fast"]


@dataclass(frozen=True)
class _ProfileSettings:
    refine_landmarks: bool
    min_detection_confidence: float
    min_tracking_confidence: float


PROFILE_SETTINGS: dict[DetectorProfile, _ProfileSettings] = {
    "quality": _ProfileSettings(True, 0.60, 0.60),
    "balanced": _ProfileSettings(True, 0.50, 0.50),
    "fast": _ProfileSettings(False, 0.40, 0.40),
}


class MediapipeFaceDetector:
    def __init__(
        self,
        profile: DetectorProfile = "quality",
        static_image_mode: bool = False,
        max_num_faces: int = 1,
    ) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self._static_image_mode = static_image_mode
        self._max_num_faces = max_num_faces
        self._profile: DetectorProfile = profile
        self._face_mesh = self._create_face_mesh(profile)

    @property
    def profile(self) -> DetectorProfile:
        return self._profile

    def set_profile(self, profile: DetectorProfile) -> None:
        if profile == self._profile:
            return

        self.close()
        self._profile = profile
        self._face_mesh = self._create_face_mesh(profile)

    def detect(self, image_bgr: np.ndarray) -> DetectionResult | None:
        if image_bgr is None or image_bgr.size == 0:
            return None
        if image_bgr.ndim != 3 or image_bgr.shape[2] != 3:
            return None

        # Reinitialize FaceMesh if it was closed or corrupted
        if self._face_mesh is None:
            self._face_mesh = self._create_face_mesh(self._profile)

        height, width = image_bgr.shape[:2]
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        
        try:
            results = self._face_mesh.process(image_rgb)
        except ValueError as e:
            # Handle "_graph is None" error by reinitializing
            if "_graph is None" in str(e):
                self.logger.warning("FaceMesh graph was None, reinitializing...")
                self._face_mesh = self._create_face_mesh(self._profile)
                results = self._face_mesh.process(image_rgb)
            else:
                raise
        
        if not results.multi_face_landmarks:
            return None
            return None

        face_landmarks = results.multi_face_landmarks[0]
        landmarks = [
            FacialLandmark(index=index, x=landmark.x * width, y=landmark.y * height)
            for index, landmark in enumerate(face_landmarks.landmark)
        ]

        quality_score, warnings, face_bbox = self._calculate_quality(image_bgr, landmarks)
        return DetectionResult(
            landmarks=landmarks,
            image_shape=image_bgr.shape,
            quality_score=quality_score,
            warnings=warnings,
            face_bbox=face_bbox,
        )

    def close(self) -> None:
        if self._face_mesh is not None:
            try:
                self._face_mesh.close()
            except Exception:
                pass
            self._face_mesh = None

    def _create_face_mesh(self, profile: DetectorProfile):
        settings = PROFILE_SETTINGS[profile]
        face_mesh_cls = self._resolve_face_mesh_class()

        self.logger.info(
            "Initializing MediaPipe detector with profile=%s, static_image_mode=%s",
            profile,
            self._static_image_mode,
        )

        return face_mesh_cls(
            static_image_mode=self._static_image_mode,
            max_num_faces=self._max_num_faces,
            refine_landmarks=settings.refine_landmarks,
            min_detection_confidence=settings.min_detection_confidence,
            min_tracking_confidence=settings.min_tracking_confidence,
        )

    def _resolve_face_mesh_class(self):
        if hasattr(mp, "solutions") and hasattr(mp.solutions, "face_mesh"):
            return mp.solutions.face_mesh.FaceMesh

        try:
            from mediapipe.python.solutions.face_mesh import FaceMesh  # type: ignore

            return FaceMesh
        except Exception as exc:  # pragma: no cover - runtime compatibility fallback
            raise RuntimeError(
                "MediaPipe installed without FaceMesh solutions API. "
                "Use mediapipe==0.10.14 (or compatible) for this prototype."
            ) from exc

    def _calculate_quality(
        self,
        image_bgr: np.ndarray,
        landmarks: list[FacialLandmark],
    ) -> tuple[float, list[str], tuple[int, int, int, int]]:
        points = np.array([[lm.x, lm.y] for lm in landmarks], dtype=np.float32)

        min_x, min_y = np.min(points, axis=0)
        max_x, max_y = np.max(points, axis=0)

        min_x_i = int(max(0, round(min_x)))
        min_y_i = int(max(0, round(min_y)))
        max_x_i = int(round(max_x))
        max_y_i = int(round(max_y))
        bbox = (min_x_i, min_y_i, max_x_i, max_y_i)

        height, width = image_bgr.shape[:2]
        bbox_w = max(max_x - min_x, 1.0)
        bbox_h = max(max_y - min_y, 1.0)
        bbox_area_ratio = (bbox_w * bbox_h) / float(width * height)

        border_margin_x = min_x / width
        border_margin_y = min_y / height
        border_margin_right = (width - max_x) / width
        border_margin_bottom = (height - max_y) / height

        grayscale = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        brightness_mean = float(np.mean(grayscale))

        left_eye = next((lm for lm in landmarks if lm.index == 33), None)
        right_eye = next((lm for lm in landmarks if lm.index == 263), None)
        roll_angle = 0.0
        if left_eye and right_eye:
            roll_angle = math.degrees(math.atan2(right_eye.y - left_eye.y, right_eye.x - left_eye.x))

        warnings: list[str] = []
        score = 1.0
        quality_cfg = DEFAULT_SYMMETRY_CONFIG.quality

        if brightness_mean < quality_cfg.min_brightness_mean:
            warnings.append("low_illumination")
            score -= 0.20

        if abs(roll_angle) > quality_cfg.max_roll_angle_degrees:
            warnings.append("extreme_head_roll")
            score -= 0.25

        border_limit = quality_cfg.max_face_border_ratio
        if (
            border_margin_x < border_limit
            or border_margin_y < border_limit
            or border_margin_right < border_limit
            or border_margin_bottom < border_limit
        ):
            warnings.append("partial_face_frame")
            score -= 0.25

        if bbox_area_ratio < quality_cfg.min_face_area_ratio:
            warnings.append("face_too_small")
            score -= 0.20

        if self._profile == "fast":
            warnings.append("fast_profile_active")
            score -= 0.05

        score = max(0.0, min(score, 1.0))
        return score, sorted(set(warnings)), bbox
