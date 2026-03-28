from __future__ import annotations

import unittest

from src.infrastructure.camera.webcam_service import WebcamService


class CameraSmokeTestCase(unittest.TestCase):
    def test_start_stop_camera_if_available(self) -> None:
        available = WebcamService.list_available_cameras(max_index=3)
        if not available:
            self.skipTest("No camera available on this machine")

        service = WebcamService(camera_index=available[0])
        self.assertTrue(service.start())
        frame = service.get_frame()
        service.stop()

        self.assertIsNotNone(frame)


if __name__ == "__main__":
    unittest.main()
