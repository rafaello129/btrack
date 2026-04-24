# B-Track Mobile v1 (Android)

Proyecto Android multi-modulo con analisis facial on-device.

## Modulos

- `app`: navegacion, ViewModel, CameraX, DI (Hilt), integracion MediaPipe
- `core-analysis`: motor de scoring y modelos de dominio en Kotlin puro
- `feature-capture`: pantalla de captura y controles
- `feature-results`: pantalla de resultado
- `feature-history`: pantalla de historial
- `data-local`: persistencia Room para sesiones (sin imagenes)

## Requisitos

- JDK 17
- Android SDK (API 35)
- Android Studio Iguana o superior

## Build

```bash
./gradlew :core-analysis:test
./gradlew :app:assembleDebug
./gradlew :app:assembleRelease
```

## Privacidad

- No guarda fotos ni video
- Solo guarda score, calidad, interpretacion, alertas y metricas en DB local

## Modelo de inferencia

El archivo `face_landmarker.task` ya esta incluido en:

- `app/src/main/assets/face_landmarker.task`

