from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import fmean

from src.domain.config.scoring_config import DEFAULT_SYMMETRY_CONFIG, SymmetryConfig
from src.domain.models.face_metrics import FacialLandmark, SymmetryMetrics


@dataclass(frozen=True)
class _Point:
    x: float
    y: float


class SymmetryAnalyzer:
    """Pure geometric analyzer based on 2D landmarks."""

    MIDLINE_INDICES = [10, 168, 1, 2, 152]
    LEFT_EYEBROW_INDICES = [70, 63, 105, 66, 107]
    RIGHT_EYEBROW_INDICES = [300, 293, 334, 296, 336]
    DISTANCE_PAIRS = [
        (33, 263),
        (133, 362),
        (61, 291),
        (93, 323),
        (132, 361),
        (234, 454),
    ]

    LEFT_EYE_UPPER = 159
    LEFT_EYE_LOWER = 145
    RIGHT_EYE_UPPER = 386
    RIGHT_EYE_LOWER = 374
    LEFT_MOUTH_CORNER = 61
    RIGHT_MOUTH_CORNER = 291
    NOSE_TIP = 1
    UPPER_LIP_CENTER = 13
    LOWER_LIP_CENTER = 14
    REQUIRED_INDICES = {
        33,
        263,
        LEFT_EYE_UPPER,
        LEFT_EYE_LOWER,
        RIGHT_EYE_UPPER,
        RIGHT_EYE_LOWER,
        LEFT_MOUTH_CORNER,
        RIGHT_MOUTH_CORNER,
    }

    def __init__(self, config: SymmetryConfig | None = None) -> None:
        self.config = config or DEFAULT_SYMMETRY_CONFIG

    def analyze(
        self,
        landmarks: list[FacialLandmark],
        image_shape: tuple[int, int, int],
    ) -> SymmetryMetrics:
        if not landmarks:
            raise ValueError("No landmarks were provided for analysis.")

        height, width = image_shape[:2]
        if width <= 0 or height <= 0:
            raise ValueError("Invalid image dimensions.")

        raw_points = {landmark.index: _Point(landmark.x, landmark.y) for landmark in landmarks}
        missing = sorted(index for index in self.REQUIRED_INDICES if index not in raw_points)
        if missing:
            raise ValueError(f"Landmarks missing for metrics: {missing}")

        normalized_points, roll_angle_deg, norm_scale = self._normalize_landmarks(raw_points)

        raw_metrics = self._compute_metric_bundle(raw_points)
        normalized_metrics = self._compute_metric_bundle(normalized_points)
        normalized_metrics["roll_angle_component"] = min(abs(roll_angle_deg) / 30.0, 1.0)

        quality_flags = self._derive_quality_flags(roll_angle_deg, norm_scale)
        composite_score = self._compute_score(normalized_metrics)
        composite_score, cap_flags = self._apply_asymmetry_caps(normalized_metrics, composite_score)
        if cap_flags:
            quality_flags.extend(cap_flags)
        interpretation = self._interpret_score(composite_score)

        return SymmetryMetrics(
            midline_x_raw=round(self._estimate_midline(raw_points), 3),
            raw_metrics={key: round(value, 6) for key, value in raw_metrics.items()},
            normalized_metrics={key: round(value, 6) for key, value in normalized_metrics.items()},
            quality_flags=quality_flags,
            composite_score=round(composite_score, 2),
            interpretation_level=interpretation,
        )

    def _normalize_landmarks(
        self,
        points: dict[int, _Point],
    ) -> tuple[dict[int, _Point], float, float]:
        left_eye = points[33]
        right_eye = points[263]

        dx = right_eye.x - left_eye.x
        dy = right_eye.y - left_eye.y
        eye_distance = math.hypot(dx, dy)
        if eye_distance <= 1e-6:
            raise ValueError("Eye distance is too small for normalization.")

        angle = math.atan2(dy, dx)
        cos_theta = math.cos(-angle)
        sin_theta = math.sin(-angle)

        center_x = (left_eye.x + right_eye.x) / 2.0
        center_y = (left_eye.y + right_eye.y) / 2.0

        normalized_points: dict[int, _Point] = {}
        for index, point in points.items():
            tx = (point.x - center_x) / eye_distance
            ty = (point.y - center_y) / eye_distance

            rx = tx * cos_theta - ty * sin_theta
            ry = tx * sin_theta + ty * cos_theta
            normalized_points[index] = _Point(rx, ry)

        return normalized_points, math.degrees(angle), eye_distance

    def _compute_metric_bundle(self, points: dict[int, _Point]) -> dict[str, float]:
        face_width = self._estimate_face_width(points)
        face_height = self._estimate_face_height(points)
        midline_x = self._estimate_midline(points)

        asymmetry_distance = self._pairwise_distance_asymmetry(points, midline_x, face_width)
        eyebrow_height = self._eyebrow_height_diff(points, face_height)
        eye_aperture = self._eye_aperture_diff(points, face_height)
        mouth_corner = self._mouth_corner_height_diff(points, face_height)
        mouth_tilt_abs = self._mouth_tilt_component(points)
        nasolabial_distance = self._nasolabial_distance_diff(points, face_width)
        oral_excursion = self._oral_excursion_diff(points)

        return {
            "asymmetry_distance": asymmetry_distance,
            "eyebrow_height_diff": eyebrow_height,
            "eye_aperture_diff": eye_aperture,
            "mouth_corner_height_diff": mouth_corner,
            "mouth_tilt_component": mouth_tilt_abs,
            "nasolabial_distance_diff": nasolabial_distance,
            "oral_excursion_diff": oral_excursion,
        }

    def _derive_quality_flags(self, roll_angle_deg: float, norm_scale: float) -> list[str]:
        flags: list[str] = []
        if abs(roll_angle_deg) > self.config.quality.max_roll_angle_degrees:
            flags.append("pose_roll_extrema")

        if norm_scale < 20.0:
            flags.append("face_too_small")

        return flags

    def _compute_score(self, normalized_metrics: dict[str, float]) -> float:
        weights = self.config.weights
        weighted_asymmetry = (
            weights.asymmetry_distance * normalized_metrics["asymmetry_distance"]
            + weights.eyebrow_height * normalized_metrics["eyebrow_height_diff"]
            + weights.eye_aperture * normalized_metrics["eye_aperture_diff"]
            + weights.mouth_corner_height * normalized_metrics["mouth_corner_height_diff"]
            + weights.mouth_tilt * normalized_metrics["mouth_tilt_component"]
            + weights.nasolabial_distance * normalized_metrics["nasolabial_distance_diff"]
            + weights.oral_excursion * normalized_metrics["oral_excursion_diff"]
        )
        dominant_component = max(
            normalized_metrics["asymmetry_distance"],
            normalized_metrics["eyebrow_height_diff"],
            normalized_metrics["eye_aperture_diff"],
            normalized_metrics["mouth_corner_height_diff"],
            normalized_metrics["mouth_tilt_component"],
            normalized_metrics["nasolabial_distance_diff"],
            normalized_metrics["oral_excursion_diff"],
        )

        calibration = self.config.calibration
        asymmetry = (
            calibration.weighted_component_ratio * weighted_asymmetry
            + calibration.dominant_component_ratio * dominant_component
        ) * calibration.asymmetry_gain
        asymmetry = self._clamp(asymmetry, 0.0, 1.0)
        return (1.0 - asymmetry) * 100.0

    def _apply_asymmetry_caps(
        self,
        normalized_metrics: dict[str, float],
        score: float,
    ) -> tuple[float, list[str]]:
        caps = self.config.caps
        flags: list[str] = []

        dominant_component = max(
            normalized_metrics["asymmetry_distance"],
            normalized_metrics["eyebrow_height_diff"],
            normalized_metrics["eye_aperture_diff"],
            normalized_metrics["mouth_corner_height_diff"],
            normalized_metrics["mouth_tilt_component"],
            normalized_metrics["nasolabial_distance_diff"],
            normalized_metrics["oral_excursion_diff"],
        )
        oral_component = max(
            normalized_metrics["mouth_corner_height_diff"],
            normalized_metrics["mouth_tilt_component"],
            normalized_metrics["nasolabial_distance_diff"],
            normalized_metrics["oral_excursion_diff"],
        )

        capped_score = score
        if dominant_component >= caps.very_strong_component:
            capped_score = min(capped_score, caps.very_strong_score_cap)
            flags.append("focal_asymmetry_very_strong")
        elif dominant_component >= caps.strong_component:
            capped_score = min(capped_score, caps.strong_score_cap)
            flags.append("focal_asymmetry_strong")
        elif dominant_component >= caps.moderate_component:
            capped_score = min(capped_score, caps.moderate_score_cap)
            flags.append("focal_asymmetry_moderate")

        if oral_component >= caps.oral_strong_component:
            capped_score = min(capped_score, caps.oral_strong_score_cap)
            flags.append("oral_asymmetry_strong")
        elif oral_component >= caps.oral_component:
            capped_score = min(capped_score, caps.oral_score_cap)
            flags.append("oral_asymmetry_moderate")

        return capped_score, sorted(set(flags))

    def _interpret_score(self, score: float) -> str:
        thresholds = self.config.thresholds
        if score >= thresholds.high_symmetry:
            return "Alta simetria facial"
        if score >= thresholds.moderate_symmetry:
            return "Asimetria leve"
        if score >= thresholds.mild_asymmetry:
            return "Asimetria moderada"
        return "Asimetria marcada"

    def _estimate_face_width(self, points: dict[int, _Point]) -> float:
        if 234 in points and 454 in points:
            return max(abs(points[454].x - points[234].x), 1e-6)
        return max(abs(points[263].x - points[33].x), 1e-6)

    def _estimate_face_height(self, points: dict[int, _Point]) -> float:
        if 10 in points and 152 in points:
            return max(abs(points[152].y - points[10].y), 1e-6)
        upper = min(point.y for point in points.values())
        lower = max(point.y for point in points.values())
        return max(abs(lower - upper), 1e-6)

    def _estimate_midline(self, points: dict[int, _Point]) -> float:
        midline_samples = [points[index].x for index in self.MIDLINE_INDICES if index in points]
        if not midline_samples:
            return (points[33].x + points[263].x) / 2.0
        return fmean(midline_samples)

    def _pairwise_distance_asymmetry(
        self,
        points: dict[int, _Point],
        midline_x: float,
        face_width: float,
    ) -> float:
        values: list[float] = []
        for left_index, right_index in self.DISTANCE_PAIRS:
            if left_index not in points or right_index not in points:
                continue

            left_distance = abs(midline_x - points[left_index].x)
            right_distance = abs(points[right_index].x - midline_x)
            values.append(abs(left_distance - right_distance) / face_width)

        if not values:
            return 1.0
        return self._clamp(fmean(values), 0.0, 1.0)

    def _eyebrow_height_diff(self, points: dict[int, _Point], face_height: float) -> float:
        left = [points[index].y for index in self.LEFT_EYEBROW_INDICES if index in points]
        right = [points[index].y for index in self.RIGHT_EYEBROW_INDICES if index in points]
        if not left or not right:
            return 1.0
        return self._clamp(abs(fmean(left) - fmean(right)) / face_height, 0.0, 1.0)

    def _eye_aperture_diff(self, points: dict[int, _Point], face_height: float) -> float:
        left_aperture = abs(points[self.LEFT_EYE_LOWER].y - points[self.LEFT_EYE_UPPER].y)
        right_aperture = abs(points[self.RIGHT_EYE_LOWER].y - points[self.RIGHT_EYE_UPPER].y)
        return self._clamp(abs(left_aperture - right_aperture) / face_height, 0.0, 1.0)

    def _mouth_corner_height_diff(self, points: dict[int, _Point], face_height: float) -> float:
        return self._clamp(
            abs(points[self.LEFT_MOUTH_CORNER].y - points[self.RIGHT_MOUTH_CORNER].y) / face_height,
            0.0,
            1.0,
        )

    def _mouth_tilt_component(self, points: dict[int, _Point]) -> float:
        left = points[self.LEFT_MOUTH_CORNER]
        right = points[self.RIGHT_MOUTH_CORNER]
        angle = math.degrees(math.atan2(right.y - left.y, right.x - left.x))
        return self._clamp(abs(angle) / 20.0, 0.0, 1.0)

    def _nasolabial_distance_diff(self, points: dict[int, _Point], face_width: float) -> float:
        if self.NOSE_TIP not in points:
            return 0.0

        nose = points[self.NOSE_TIP]
        left = points[self.LEFT_MOUTH_CORNER]
        right = points[self.RIGHT_MOUTH_CORNER]

        left_distance = math.hypot(left.x - nose.x, left.y - nose.y)
        right_distance = math.hypot(right.x - nose.x, right.y - nose.y)
        return self._clamp(abs(left_distance - right_distance) / face_width, 0.0, 1.0)

    def _oral_excursion_diff(self, points: dict[int, _Point]) -> float:
        left = points[self.LEFT_MOUTH_CORNER]
        right = points[self.RIGHT_MOUTH_CORNER]
        mouth_width = max(math.hypot(right.x - left.x, right.y - left.y), 1e-6)

        center = self._mouth_center(points)
        left_excursion = math.hypot(left.x - center.x, left.y - center.y)
        right_excursion = math.hypot(right.x - center.x, right.y - center.y)
        return self._clamp(abs(left_excursion - right_excursion) / mouth_width, 0.0, 1.0)

    def _mouth_center(self, points: dict[int, _Point]) -> _Point:
        if self.UPPER_LIP_CENTER in points and self.LOWER_LIP_CENTER in points:
            upper = points[self.UPPER_LIP_CENTER]
            lower = points[self.LOWER_LIP_CENTER]
            return _Point((upper.x + lower.x) / 2.0, (upper.y + lower.y) / 2.0)

        left = points[self.LEFT_MOUTH_CORNER]
        right = points[self.RIGHT_MOUTH_CORNER]
        return _Point((left.x + right.x) / 2.0, (left.y + right.y) / 2.0)

    def _clamp(self, value: float, lower: float, upper: float) -> float:
        return max(lower, min(value, upper))
