# NeuroFace - Manual de Usuario

## Sistema de Monitoreo y Análisis Temprano de Simetría Facial

---

## 📋 Índice

1. [Introducción](#introducción)
2. [Requisitos del Sistema](#requisitos-del-sistema)
3. [Instalación](#instalación)
4. [Interfaz de Usuario](#interfaz-de-usuario)
5. [Guía de Uso](#guía-de-uso)
6. [Interpretación de Resultados](#interpretación-de-resultados)
7. [Configuración Avanzada](#configuración-avanzada)
8. [Solución de Problemas](#solución-de-problemas)
9. [Aviso Legal](#aviso-legal)

---

## Introducción

**NeuroFace** es una aplicación de escritorio diseñada para el tamizaje temprano de asimetría facial. Utiliza inteligencia artificial y visión por computadora para analizar la simetría del rostro en tiempo real o mediante imágenes estáticas.

### Propósito
- Detección temprana de posibles asimetrías faciales
- Apoyo al tamizaje clínico inicial
- Monitoreo de cambios en la simetría facial a lo largo del tiempo

### ⚠️ Aviso Importante
Este software es una **herramienta de apoyo orientativo** y **NO sustituye** la valoración médica profesional. Ante cualquier síntoma o hallazgo relevante, consulte con un profesional de la salud.

---

## Requisitos del Sistema

### Hardware Mínimo
- Procesador: Intel Core i3 o AMD Ryzen 3 (o superior)
- RAM: 4 GB mínimo (8 GB recomendado)
- Espacio en disco: 500 MB
- Cámara web (opcional, para análisis en vivo)

### Sistema Operativo
- Windows 10/11 (64-bit)

### Para desarrollo (opcional)
- Python 3.10 o superior
- Dependencias listadas en `requirements.txt`

---

## Instalación

### Opción 1: Ejecutable Portable (Recomendado)
1. Descargue el archivo `NeuroFace.exe`
2. Colóquelo en cualquier carpeta de su preferencia
3. Haga doble clic para ejecutar

### Opción 2: Desde código fuente
```bash
# Clonar o descargar el proyecto
cd btrack_prototype

# Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python -m src.main
```

---

## Interfaz de Usuario

### Estructura General

```
┌─────────────────────────────────────────────────────────────────┐
│  🧠 NEUROFACE          [Sistema] [Estado del Análisis]         │
│  Monitoreo y análisis temprano de simetría facial              │
├────────────────────────────┬────────────────────────────────────┤
│                            │                                    │
│   CAPTURA FACIAL           │   RESULTADO PRINCIPAL              │
│   ┌──────────────────┐     │   ┌────────────────────────────┐   │
│   │                  │     │   │ Estado de simetría         │   │
│   │   Vista previa   │     │   │ Interpretación clínica     │   │
│   │   de cámara      │     │   └────────────────────────────┘   │
│   │                  │     │                                    │
│   └──────────────────┘     │   INDICADORES DE TAMIZAJE          │
│                            │   [Puntaje] [Calidad] [Confianza]  │
│   [Abrir imagen] [Cámara]  │                                    │
│   [Iniciar] [Detener]      │   HALLAZGOS POR REGIÓN             │
│                            │   • Región ocular                  │
│   ACCIONES PRINCIPALES     │   • Cejas                          │
│   [Analizar captura]       │   • Boca y comisuras               │
│   [Reanudar captura]       │   • Alineación general             │
│                            │                                    │
│   PERFIL DE ANÁLISIS       │   MÉTRICAS AVANZADAS               │
│   [Quality ▼]              │   • Distancia global               │
│   ☑ Suavizado temporal     │   • Apertura ocular                │
│                            │   • Altura de cejas                │
│                            │   • (y más métricas...)            │
└────────────────────────────┴────────────────────────────────────┘
```

### Secciones Principales

#### 1. Barra Superior (Top Bar)
- **Logo NeuroFace**: Identidad de la aplicación
- **Badge Sistema**: Estado del sistema (listo, procesando, error)
- **Badge Análisis**: Estado del análisis actual

#### 2. Panel Izquierdo - Captura Facial

**Visor de Imagen/Cámara**
- Muestra la imagen o video en tiempo real
- Superpone los landmarks faciales detectados
- Indica la calidad de la captura

**Controles de Cámara**
| Botón | Función |
|-------|---------|
| Abrir imagen | Cargar una foto desde archivo |
| Cámara (selector) | Elegir cámara disponible |
| Iniciar cámara | Activar captura en vivo |
| Detener cámara | Pausar captura |

**Acciones Principales**
| Botón | Función |
|-------|---------|
| Analizar captura | Ejecutar análisis de simetría |
| Congelar/Reanudar | Pausar video para análisis |

**Perfil de Análisis**
- **Quality**: Máxima precisión, más lento
- **Balanced**: Equilibrio velocidad/precisión
- **Fast**: Rápido, menor precisión

#### 3. Panel Derecho - Resultados

**Resultado Principal (Hero Card)**
- Clasificación general de simetría
- Interpretación en lenguaje clínico
- Siguiente paso recomendado

**Indicadores de Tamizaje (KPIs)**
| Indicador | Descripción |
|-----------|-------------|
| PUNTAJE | Score global de simetría (0-100) |
| CALIDAD | Calidad de la captura analizada |
| CONFIABILIDAD | Nivel de confianza del resultado |
| ATENCIÓN | Nivel de atención requerido |
| ALERTAS | Número de alertas detectadas |

**Hallazgos por Región Facial**
Análisis detallado de cada zona:
- Región ocular
- Cejas
- Boca y comisuras
- Alineación general

**Métricas Avanzadas**
Valores técnicos de cada parámetro medido:
| Métrica | Descripción |
|---------|-------------|
| Dist. global | Distancia euclidiana de asimetría |
| Apertura ocular | Diferencia entre apertura de ojos |
| Altura de cejas | Diferencia de posición vertical |
| Comisuras | Diferencia en comisuras labiales |
| Inclinación oral | Ángulo de inclinación de la boca |
| Dif. nasolabial | Diferencia en surcos nasolabiales |
| Excursión oral | Diferencia en movimiento bucal |
| Inclinación general | Rotación general del rostro |

---

## Guía de Uso

### Análisis con Imagen Estática

1. **Cargar imagen**
   - Clic en "Abrir imagen"
   - Seleccionar archivo (PNG, JPG, JPEG, BMP)
   - La imagen aparecerá en el visor

2. **Ejecutar análisis**
   - Clic en "Analizar captura"
   - Esperar procesamiento (indicador animado)
   - Revisar resultados en panel derecho

### Análisis con Cámara en Vivo

1. **Configurar cámara**
   - Seleccionar índice de cámara (0, 1, 2...)
   - Clic en "Iniciar cámara"

2. **Capturar momento**
   - Posicionar rostro de frente
   - Clic en "Congelar captura" para pausar
   - Clic en "Analizar captura"

3. **Análisis continuo**
   - Activar "Suavizado temporal"
   - Clic en "Analizar captura" sin congelar
   - Los resultados se actualizan en vivo

### Recomendaciones para Mejores Resultados

✅ **Hacer:**
- Posición frontal del rostro
- Buena iluminación uniforme
- Rostro completamente visible
- Expresión neutral o natural

❌ **Evitar:**
- Iluminación lateral fuerte
- Rostro parcialmente oculto
- Gafas de sol o accesorios que cubran el rostro
- Movimiento durante la captura

---

## Interpretación de Resultados

### Clasificaciones de Simetría

| Clasificación | Score | Significado |
|---------------|-------|-------------|
| 🟢 Simetría conservada | 90-100 | Simetría facial dentro de parámetros normales |
| 🟡 Variación menor | 75-89 | Ligera variación, generalmente no significativa |
| 🟠 Atención sugerida | 60-74 | Asimetría notable, considerar seguimiento |
| 🔴 Evaluación recomendada | <60 | Asimetría significativa, consultar profesional |

### Tonos de Severidad

| Tono | Color | Significado |
|------|-------|-------------|
| good | 🟢 Verde | Normal/Conservado |
| info | 🔵 Azul | Informativo |
| warn | 🟡 Ámbar | Atención/Advertencia |
| risk | 🔴 Rojo | Alerta/Riesgo |
| muted | ⚪ Gris | Sin datos/Pendiente |

### Indicadores de Calidad

| Calidad | Descripción |
|---------|-------------|
| Excelente | Captura óptima para análisis |
| Buena | Captura adecuada |
| Aceptable | Resultados con reservas |
| Limitada | Considerar repetir captura |

---

## Configuración Avanzada

### Ajustar Proporciones de Pantalla

El splitter central es arrastrable. Para modificar valores por defecto:

**Archivo:** `src/ui/main_window.py`

```python
# Línea ~155-156 - Proporción inicial
self.body_splitter.setStretchFactor(0, 3)  # Izquierda
self.body_splitter.setStretchFactor(1, 7)  # Derecha

# Línea ~1294-1302 - Tamaños responsivos
right_target = int(usable_width * 0.58)  # Porcentaje derecha
left_target = int(usable_width * 0.42)   # Porcentaje izquierda
```

### Perfiles de Detección

**Archivo:** `src/infrastructure/vision/mediapipe_face_detector.py`

```python
PROFILE_SETTINGS = {
    "quality": _ProfileSettings(True, 0.60, 0.60),   # Alta precisión
    "balanced": _ProfileSettings(True, 0.50, 0.50),  # Equilibrado
    "fast": _ProfileSettings(False, 0.40, 0.40),     # Rápido
}
```

### Personalizar Colores

**Archivo:** `src/ui/theme.py`

```python
class NeuroFaceColors:
    BACKGROUND_BASE = "#101012"      # Fondo principal
    AMBER = "#C9A66B"                # Color de acento
    TEXT_PRIMARY = "#F0F0F2"         # Texto principal
    # ... más colores
```

---

## Solución de Problemas

### La cámara no se detecta
1. Verificar que la cámara esté conectada
2. Probar diferentes índices de cámara (0, 1, 2)
3. Cerrar otras aplicaciones que usen la cámara

### No se detecta rostro
1. Mejorar iluminación
2. Posicionar rostro más centrado y frontal
3. Acercarse o alejarse de la cámara
4. Cambiar a perfil "Quality"

### Error "_graph is None"
- El detector se reinicia automáticamente
- Si persiste, reiniciar la aplicación

### Aplicación lenta
1. Cambiar a perfil "Fast"
2. Desactivar "Suavizado temporal"
3. Cerrar otras aplicaciones pesadas

### El .exe no abre
1. Verificar que sea Windows 64-bit
2. Ejecutar como administrador
3. Desactivar antivirus temporalmente (falso positivo)

---

## Aviso Legal

### Descargo de Responsabilidad

Este software es una **herramienta de apoyo orientativo** para el tamizaje inicial de asimetría facial. 

**NO ES UN DISPOSITIVO MÉDICO** y no debe utilizarse para:
- Diagnóstico de enfermedades
- Sustitución de evaluación médica profesional
- Toma de decisiones clínicas sin supervisión médica

### Uso Apropiado

✅ Tamizaje inicial orientativo
✅ Monitoreo de cambios a lo largo del tiempo
✅ Apoyo a profesionales de salud
✅ Investigación y educación

### Limitaciones

- Los resultados dependen de la calidad de la imagen
- Factores externos (iluminación, posición) afectan la precisión
- No detecta todas las condiciones médicas
- Requiere validación clínica profesional

### Recomendación

Ante **cualquier síntoma reciente** o **hallazgo relevante** detectado por esta herramienta, se recomienda **evaluación clínica oportuna** por un profesional de la salud calificado.

---

## Información Técnica

### Stack Tecnológico
- **Python 3.10+**: Lenguaje base
- **PySide6**: Interfaz gráfica (Qt6)
- **MediaPipe**: Detección de landmarks faciales
- **OpenCV**: Procesamiento de imagen
- **NumPy**: Cálculos matemáticos

### Arquitectura
```
src/
├── main.py                 # Punto de entrada
├── application/            # Casos de uso
├── domain/                 # Lógica de negocio
├── infrastructure/         # Cámara, detección
├── ui/                     # Interfaz gráfica
│   ├── main_window.py      # Ventana principal
│   ├── theme.py            # Estilos visuales
│   └── widgets/            # Componentes UI
└── img/                    # Recursos gráficos
```

### Generar Ejecutable
```bash
# Activar entorno virtual
.venv\Scripts\activate

# Generar .exe
pyinstaller NeuroFace.spec

# El ejecutable estará en dist/NeuroFace.exe
```

---

## Contacto y Soporte

Para reportar problemas o sugerencias, contacte al equipo de desarrollo.

---

*NeuroFace v1.0 - Sistema de Monitoreo de Simetría Facial*
*Desarrollado con ❤️ y tecnología de vanguardia*
