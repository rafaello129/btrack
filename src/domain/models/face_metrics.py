from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class AnalysisStatus(str, Enum):
    NO_FACE = "NO_FACE"
    LOW_QUALITY = "LOW_QUALITY"
    ANALYZED = "ANALYZED"
    ERROR = "ERROR"


@dataclass(frozen=True)
class FacialLandmark:
    index: int
    x: float
    y: float


@dataclass(frozen=True)
class DetectionResult:
    landmarks: list[FacialLandmark]
    image_shape: tuple[int, int, int]
    quality_score: float
    warnings: list[str] = field(default_factory=list)
    face_bbox: Optional[tuple[int, int, int, int]] = None


@dataclass(frozen=True)
class SymmetryMetrics:
    midline_x_raw: float
    raw_metrics: dict[str, float]
    normalized_metrics: dict[str, float]
    quality_flags: list[str]
    composite_score: float
    interpretation_level: str


@dataclass(frozen=True)
class OverlayPrimitives:
    axis_line: Optional[tuple[tuple[int, int], tuple[int, int]]] = None
    symmetry_pairs: list[tuple[tuple[int, int], tuple[int, int]]] = field(default_factory=list)


@dataclass(frozen=True)
class AnalysisResult:
    status: AnalysisStatus
    user_message: str
    technical_message: str
    detection: Optional[DetectionResult] = None
    metrics: Optional[SymmetryMetrics] = None
    overlay_primitives: OverlayPrimitives = field(default_factory=OverlayPrimitives)
    timings_ms: dict[str, float] = field(default_factory=dict)

    @property
    def has_face(self) -> bool:
        return self.status in {AnalysisStatus.LOW_QUALITY, AnalysisStatus.ANALYZED}
