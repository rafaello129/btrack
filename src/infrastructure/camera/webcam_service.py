from __future__ import annotations

import logging
from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(frozen=True)
class CameraSettings:
    width: int = 1280
    height: int = 720
    retries: int = 2


class WebcamService:
    def __init__(self, camera_index: int = 0, settings: CameraSettings | None = None) -> None:
        self.camera_index = camera_index
        self.settings = settings or CameraSettings()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._capture: cv2.VideoCapture | None = None
        self.last_error: str = ""

    @property
    def is_running(self) -> bool:
        return self._capture is not None and self._capture.isOpened()

    def set_camera_index(self, camera_index: int) -> None:
        if self.is_running:
            self.stop()
        self.camera_index = camera_index

    def start(self, camera_index: int | None = None) -> bool:
        if camera_index is not None:
            self.set_camera_index(camera_index)

        if self.is_running:
            return True

        self.last_error = ""

        for attempt in range(self.settings.retries + 1):
            cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
            if not cap.isOpened():
                cap.release()
                cap = cv2.VideoCapture(self.camera_index)

            if cap.isOpened():
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.settings.width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.settings.height)
                self._capture = cap
                self.logger.info(
                    "Camera started index=%s resolution=%sx%s attempt=%s",
                    self.camera_index,
                    self.settings.width,
                    self.settings.height,
                    attempt,
                )
                return True

            cap.release()
            self.last_error = f"Unable to open camera index {self.camera_index} (attempt {attempt + 1})"
            self.logger.warning(self.last_error)

        return False

    def get_frame(self) -> np.ndarray | None:
        if not self.is_running or self._capture is None:
            return None

        ok, frame = self._capture.read()
        if not ok:
            self.last_error = "Camera read failed"
            self.logger.warning(self.last_error)
            return None

        return frame

    def stop(self) -> None:
        if self._capture is not None:
            self._capture.release()
            self._capture = None
            self.logger.info("Camera stopped")

    @staticmethod
    def list_available_cameras(max_index: int = 6) -> list[int]:
        available: list[int] = []
        for index in range(max_index + 1):
            cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
            if cap.isOpened():
                available.append(index)
            cap.release()
        return available
