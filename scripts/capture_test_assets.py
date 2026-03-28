from __future__ import annotations

from pathlib import Path

import cv2


OUTPUT_DIR = Path("assets/images")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main() -> int:
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("No se pudo abrir la camara para capturar assets.")
        return 1

    print("Controles:")
    print("  f -> guardar frontal_face.jpg")
    print("  p -> guardar partial_face.jpg")
    print("  q -> salir")

    while True:
        ok, frame = cap.read()
        if not ok:
            continue

        cv2.imshow("Capture Test Assets", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("f"):
            path = OUTPUT_DIR / "frontal_face.jpg"
            cv2.imwrite(str(path), frame)
            print(f"Guardado: {path}")

        if key == ord("p"):
            path = OUTPUT_DIR / "partial_face.jpg"
            cv2.imwrite(str(path), frame)
            print(f"Guardado: {path}")

        if key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
