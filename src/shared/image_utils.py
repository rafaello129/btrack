from __future__ import annotations

import cv2
import numpy as np
from PySide6.QtGui import QImage, QPixmap

from src.domain.models.face_metrics import FacialLandmark, OverlayPrimitives, SymmetryMetrics

KEY_LANDMARK_GROUPS: dict[str, set[int]] = {
    "ocular": {33, 263, 133, 362, 159, 145, 386, 374},
    "brow": {70, 63, 105, 66, 107, 300, 293, 334, 296, 336},
    "oral": {61, 291, 13, 14, 78, 308},
    "midline": {10, 168, 1, 2, 152},
}
KEY_LANDMARKS = set().union(*KEY_LANDMARK_GROUPS.values())

COLOR_NEUTRAL = (142, 164, 182)
COLOR_AXIS = (82, 220, 255)
COLOR_OCULAR = (255, 196, 69)
COLOR_BROW = (134, 215, 87)
COLOR_ORAL = (102, 178, 255)
COLOR_BBOX = (98, 158, 205)


def _overlay_stroke_values(
    image_shape: tuple[int, int, int],
    face_bbox: tuple[int, int, int, int] | None,
) -> tuple[int, int, int, int]:
    if face_bbox is not None:
        x1, y1, x2, y2 = face_bbox
        reference = max(min(abs(x2 - x1), abs(y2 - y1)), 1)
    else:
        height, width = image_shape[:2]
        reference = max(min(height, width), 1)

    point_radius = max(1, min(2, int(round(reference / 260.0))))
    key_point_radius = max(point_radius + 1, min(3, point_radius + 1))
    line_thickness = max(1, min(2, int(round(reference / 360.0))))
    bbox_thickness = 1
    return point_radius, key_point_radius, line_thickness, bbox_thickness


def _landmark_map(landmarks: list[FacialLandmark]) -> dict[int, tuple[int, int]]:
    return {
        landmark.index: (int(round(landmark.x)), int(round(landmark.y)))
        for landmark in landmarks
    }


def _point_mean(points: list[tuple[int, int]]) -> tuple[int, int]:
    if not points:
        return 0, 0
    x = int(round(sum(point[0] for point in points) / len(points)))
    y = int(round(sum(point[1] for point in points) / len(points)))
    return x, y


def _draw_measurement_segment(
    image: np.ndarray,
    p1: tuple[int, int],
    p2: tuple[int, int],
    color: tuple[int, int, int],
    thickness: int,
) -> None:
    cv2.line(image, p1, p2, color, thickness, lineType=cv2.LINE_AA)


def bgr_to_qpixmap(image_bgr: np.ndarray) -> QPixmap:
    if image_bgr is None or image_bgr.size == 0:
        return QPixmap()

    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    height, width, channels = image_rgb.shape
    bytes_per_line = channels * width
    qimage = QImage(
        image_rgb.data,
        width,
        height,
        bytes_per_line,
        QImage.Format.Format_RGB888,
    )
    return QPixmap.fromImage(qimage.copy())


def resize_for_display(image_bgr: np.ndarray, max_width: int, max_height: int) -> np.ndarray:
    if image_bgr is None or image_bgr.size == 0:
        return image_bgr

    if max_width <= 0 or max_height <= 0:
        return image_bgr

    height, width = image_bgr.shape[:2]
    scale = min(max_width / width, max_height / height)
    if scale <= 0:
        return image_bgr

    if abs(scale - 1.0) < 1e-6:
        return image_bgr

    target_size = (max(int(width * scale), 1), max(int(height * scale), 1))
    interpolation = cv2.INTER_LINEAR if scale > 1.0 else cv2.INTER_AREA
    return cv2.resize(image_bgr, target_size, interpolation=interpolation)


def draw_analysis_overlay(
    image_bgr: np.ndarray,
    landmarks: list[FacialLandmark],
    primitives: OverlayPrimitives,
    show_landmarks: bool = True,
    show_axis: bool = True,
    show_pairs: bool = True,
    face_bbox: tuple[int, int, int, int] | None = None,
    metrics: SymmetryMetrics | None = None,
    show_guides: bool = True,
) -> np.ndarray:
    if image_bgr is None or image_bgr.size == 0:
        return image_bgr

    base = image_bgr.copy()
    overlay = image_bgr.copy()
    points = _landmark_map(landmarks)
    point_radius, key_point_radius, line_thickness, bbox_thickness = _overlay_stroke_values(
        image_bgr.shape,
        face_bbox,
    )

    if show_pairs:
        for start, end in primitives.symmetry_pairs:
            cv2.line(
                overlay,
                start,
                end,
                (80, 160, 214),
                line_thickness,
                lineType=cv2.LINE_AA,
            )

    if show_landmarks:
        for landmark in landmarks:
            center = (int(round(landmark.x)), int(round(landmark.y)))
            if landmark.index in KEY_LANDMARKS:
                if landmark.index in KEY_LANDMARK_GROUPS["ocular"]:
                    key_color = COLOR_OCULAR
                elif landmark.index in KEY_LANDMARK_GROUPS["brow"]:
                    key_color = COLOR_BROW
                elif landmark.index in KEY_LANDMARK_GROUPS["oral"]:
                    key_color = COLOR_ORAL
                else:
                    key_color = COLOR_AXIS

                cv2.circle(
                    overlay,
                    center,
                    key_point_radius + 1,
                    (10, 22, 34),
                    -1,
                    lineType=cv2.LINE_AA,
                )
                cv2.circle(
                    overlay,
                    center,
                    key_point_radius,
                    key_color,
                    -1,
                    lineType=cv2.LINE_AA,
                )
            else:
                cv2.circle(
                    overlay,
                    center,
                    point_radius,
                    COLOR_NEUTRAL,
                    -1,
                    lineType=cv2.LINE_AA,
                )

    if show_axis and primitives.axis_line is not None:
        cv2.line(
            overlay,
            primitives.axis_line[0],
            primitives.axis_line[1],
            COLOR_AXIS,
            line_thickness,
            lineType=cv2.LINE_AA,
        )

    if show_guides:
        if all(index in points for index in (159, 145)):
            p1 = points[159]
            p2 = points[145]
            _draw_measurement_segment(
                overlay,
                p1,
                p2,
                COLOR_OCULAR,
                line_thickness + 1,
            )

        if all(index in points for index in (386, 374)):
            p1 = points[386]
            p2 = points[374]
            _draw_measurement_segment(
                overlay,
                p1,
                p2,
                COLOR_OCULAR,
                line_thickness + 1,
            )

        if all(index in points for index in (61, 291)):
            left = points[61]
            right = points[291]
            _draw_measurement_segment(
                overlay,
                left,
                right,
                COLOR_ORAL,
                line_thickness + 1,
            )

        brow_left_points = [points[index] for index in KEY_LANDMARK_GROUPS["brow"] if index in points and index < 200]
        brow_right_points = [points[index] for index in KEY_LANDMARK_GROUPS["brow"] if index in points and index > 200]
        if brow_left_points and brow_right_points:
            left_center = _point_mean(brow_left_points)
            right_center = _point_mean(brow_right_points)
            _draw_measurement_segment(
                overlay,
                left_center,
                right_center,
                COLOR_BROW,
                line_thickness,
            )

        if 1 in points and 61 in points and 291 in points:
            nose = points[1]
            cv2.line(overlay, nose, points[61], COLOR_ORAL, line_thickness, lineType=cv2.LINE_AA)
            cv2.line(overlay, nose, points[291], COLOR_ORAL, line_thickness, lineType=cv2.LINE_AA)

    if face_bbox is not None:
        x1, y1, x2, y2 = face_bbox
        cv2.rectangle(
            overlay,
            (x1, y1),
            (x2, y2),
            COLOR_BBOX,
            bbox_thickness,
            lineType=cv2.LINE_AA,
        )

    _ = metrics  # Reserved for future non-text visual encodings.

    return cv2.addWeighted(base, 0.42, overlay, 0.58, 0)
