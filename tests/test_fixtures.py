from __future__ import annotations

import math

from src.domain.models.face_metrics import FacialLandmark


BASE_POINTS: dict[int, tuple[float, float]] = {
    10: (320.0, 120.0),
    168: (320.0, 180.0),
    1: (320.0, 220.0),
    2: (320.0, 250.0),
    152: (320.0, 420.0),
    33: (255.0, 230.0),
    263: (385.0, 230.0),
    133: (285.0, 235.0),
    362: (355.0, 235.0),
    61: (275.0, 325.0),
    291: (365.0, 325.0),
    93: (245.0, 295.0),
    323: (395.0, 295.0),
    132: (260.0, 305.0),
    361: (380.0, 305.0),
    234: (220.0, 280.0),
    454: (420.0, 280.0),
    70: (245.0, 205.0),
    63: (260.0, 203.0),
    105: (275.0, 202.0),
    66: (290.0, 203.0),
    107: (305.0, 205.0),
    300: (335.0, 205.0),
    293: (350.0, 203.0),
    334: (365.0, 202.0),
    296: (380.0, 203.0),
    336: (395.0, 205.0),
    159: (305.0, 224.0),
    145: (305.0, 240.0),
    386: (335.0, 224.0),
    374: (335.0, 240.0),
}


def build_landmarks(asymmetric: bool = False) -> list[FacialLandmark]:
    points = dict(BASE_POINTS)

    if asymmetric:
        points.update(
            {
                263: (403.0, 230.0),
                362: (370.0, 236.0),
                291: (374.0, 312.0),
                323: (408.0, 296.0),
                361: (392.0, 307.0),
                454: (435.0, 282.0),
                70: (245.0, 194.0),
                63: (260.0, 192.0),
                105: (275.0, 191.0),
                66: (290.0, 192.0),
                107: (305.0, 194.0),
                300: (335.0, 214.0),
                293: (350.0, 212.0),
                334: (365.0, 211.0),
                296: (380.0, 212.0),
                336: (395.0, 214.0),
                145: (305.0, 244.0),
                374: (335.0, 236.0),
                61: (275.0, 336.0),
            }
        )

    return [
        FacialLandmark(index=index, x=coords[0], y=coords[1])
        for index, coords in sorted(points.items())
    ]


def transform_landmarks(
    landmarks: list[FacialLandmark],
    scale: float = 1.0,
    tx: float = 0.0,
    ty: float = 0.0,
    angle_deg: float = 0.0,
) -> list[FacialLandmark]:
    radians = math.radians(angle_deg)
    cos_t = math.cos(radians)
    sin_t = math.sin(radians)

    transformed: list[FacialLandmark] = []
    for landmark in landmarks:
        x = landmark.x * scale
        y = landmark.y * scale

        rx = x * cos_t - y * sin_t
        ry = x * sin_t + y * cos_t

        transformed.append(
            FacialLandmark(
                index=landmark.index,
                x=rx + tx,
                y=ry + ty,
            )
        )

    return transformed
