# Demo Script - B-Track Mobile v2 (3 minutos)

## Objetivo de la demo
Mostrar en vivo que la app funciona offline para brigada multipaciente: alta, captura, interpretacion visual, monitoreo y exportacion telemedica.

## Setup previo
- Dispositivo Android 10+ en modo avion.
- Base demo con 12 pacientes cargada.
- Camara y galeria disponibles.
- APK instalada en dispositivo fisico.

## Storyline (3:00)

### 0:00 - 0:20 | Apertura
- Mensaje: "Esta app esta disenada para brigadas y pacientes en casa, sin internet."
- Mostrar banner offline activo en pantalla `Pacientes`.

### 0:20 - 0:55 | Alta + expediente
- Tap en `Registrar paciente`.
- Abrir `ExpedientePaciente`.
- Mostrar tabs `Resumen`, `Evolucion`, `Sesiones`, `Plan`.
- Mensaje: "Cada captura queda vinculada al expediente, no solo a una sesion aislada."

### 0:55 - 1:35 | Captura + resultado orientativo
- Tap `Nueva captura`.
- Tomar foto rapida o seleccionar de galeria.
- Abrir `Resultado` y explicar:
1. Hero score y confianza.
2. Preview imagen/overlay.
3. Hallazgos guiados y top contribuyentes.
4. CTA a siguiente accion.
- Mensaje: "No es diagnostico, es soporte orientativo para decision rapida."

### 1:35 - 2:15 | Monitoreo y panel de cohorte
- Volver a `Expediente` tab `Evolucion` para mostrar tendencia.
- Ir a `Panel` y mostrar:
1. KPIs de cohorte.
2. Comparador de 2 pacientes.
3. Tendencia global y heatmap de alertas.
- Mensaje: "En menos de 20 segundos se identifica a quien priorizar."

### 2:15 - 2:50 | Telemedicina offline
- Abrir `Exportar`.
- Mantener `Redactado` por defecto.
- Tap `Generar paquete`.
- Mostrar checksum, QR y historial.
- Tap `Compartir` (share intent nativo).
- Mensaje: "Se comparte PDF+JSON sin nube y sin exponer datos sensibles por defecto."

### 2:50 - 3:00 | Cierre
- Mensaje final:
1. "Offline end-to-end."
2. "Expediente multipaciente accionable."
3. "Telemedicina lista para segunda opinion."

## Preguntas de jueces (respuestas cortas)
- Privacidad: "No guardamos fotos ni video, solo metricas y metadatos locales."
- Conectividad: "Todo el flujo funciona sin red; la conectividad solo mejora transferencia externa."
- Clinico: "Resultado orientativo/no diagnostico con trazabilidad en expediente."
