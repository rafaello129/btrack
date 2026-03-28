from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ScoreWeights:
    asymmetry_distance: float = 0.18
    eyebrow_height: float = 0.08
    eye_aperture: float = 0.21
    mouth_corner_height: float = 0.18
    mouth_tilt: float = 0.15
    nasolabial_distance: float = 0.12
    oral_excursion: float = 0.08


@dataclass(frozen=True)
class ScoreCalibration:
    weighted_component_ratio: float = 0.65
    dominant_component_ratio: float = 0.35
    asymmetry_gain: float = 1.10


@dataclass(frozen=True)
class AsymmetryCaps:
    moderate_component: float = 0.20
    strong_component: float = 0.30
    very_strong_component: float = 0.40
    moderate_score_cap: float = 82.0
    strong_score_cap: float = 70.0
    very_strong_score_cap: float = 58.0
    oral_component: float = 0.22
    oral_strong_component: float = 0.32
    oral_score_cap: float = 78.0
    oral_strong_score_cap: float = 66.0


@dataclass(frozen=True)
class InterpretationThresholds:
    high_symmetry: float = 93.0
    moderate_symmetry: float = 80.0
    mild_asymmetry: float = 66.0


@dataclass(frozen=True)
class QualityThresholds:
    low_quality_min_score: float = 0.55
    min_brightness_mean: float = 45.0
    max_roll_angle_degrees: float = 18.0
    max_face_border_ratio: float = 0.08
    min_face_area_ratio: float = 0.08


@dataclass(frozen=True)
class SymmetryConfig:
    weights: ScoreWeights = field(default_factory=ScoreWeights)
    calibration: ScoreCalibration = field(default_factory=ScoreCalibration)
    caps: AsymmetryCaps = field(default_factory=AsymmetryCaps)
    thresholds: InterpretationThresholds = field(default_factory=InterpretationThresholds)
    quality: QualityThresholds = field(default_factory=QualityThresholds)


DEFAULT_SYMMETRY_CONFIG = SymmetryConfig()
