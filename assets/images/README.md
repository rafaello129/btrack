# Test Assets

Estos archivos se usan en pruebas de integracion del detector:

- `no_face.png`: imagen sin rostro (incluida en repo).
- `frontal_face.jpg`: rostro frontal completo (opcional, capturar localmente).
- `partial_face.jpg`: rostro parcial/recortado (opcional, capturar localmente).

Puedes generar `frontal_face.jpg` y `partial_face.jpg` con:

```powershell
.\.venv\Scripts\python.exe scripts\capture_test_assets.py
```
