# Flujos UX Operativos - B-Track Mobile v2

## Plantilla estandar (obligatoria)
- Objetivo
- Actor
- Disparador
- Precondiciones
- Postcondiciones
- Flujo principal
- Flujos alternos
- Errores
- Reglas de negocio
- Estados UI
- Criterios de aceptacion

## FL-01 Alta paciente
- Objetivo: Dar de alta paciente nuevo en campo en menos de 60 segundos.
- Actor: Brigadista.
- Disparador: Tap `Registrar paciente`.
- Precondiciones: Modulo `Pacientes` visible.
- Postcondiciones: Paciente disponible para captura y expediente.
- Flujo principal:
1. Abrir `Pacientes`.
2. Tap `Registrar paciente`.
3. Sistema crea registro base.
4. Navegar a `ExpedientePaciente`.
- Flujos alternos:
1. Registrar desde modo demo con datos semilla.
- Errores:
1. Falla DB local.
- Reglas de negocio:
1. Crear perfil clinico default con riesgo inicial.
- Estados UI:
1. Loading corto.
2. Exito con expediente.
3. Error con reintento.
- Criterios de aceptacion:
1. Alta completada sin internet.

## FL-02 Captura a resultado
- Objetivo: Capturar y analizar sin backend.
- Actor: Brigadista.
- Disparador: Tap `Nueva captura`.
- Precondiciones: Paciente seleccionado.
- Postcondiciones: Resultado renderizado + sesion guardada.
- Flujo principal:
1. Entrar a `Captura`.
2. Elegir perfil de deteccion.
3. Tomar foto o elegir galeria.
4. Sistema analiza.
5. Navega a `Resultado`.
- Flujos alternos:
1. Camara denegada -> galeria.
2. Congelar preview antes de disparar.
- Errores:
1. No se detecta rostro.
2. Baja calidad de imagen.
3. Excepcion del pipeline.
- Reglas de negocio:
1. Si calidad < umbral, bloquear score final.
- Estados UI:
1. Analizando.
2. Resultado normal.
3. Estado especial (`NO_FACE`, `LOW_QUALITY`, `ERROR`).
- Criterios de aceptacion:
1. No crashes en camara/galeria.

## FL-03 Resultado a expediente
- Objetivo: Convertir resultado en accion de seguimiento.
- Actor: Brigadista.
- Disparador: CTA principal en `Resultado`.
- Precondiciones: Resultado generado.
- Postcondiciones: Usuario vuelve a `ExpedientePaciente` para decidir plan.
- Flujo principal:
1. Revisar score y narrativa.
2. Revisar barras por region y top contributors.
3. Tap CTA principal.
4. Navegar a expediente.
- Flujos alternos:
1. Si estado especial, CTA regresa a captura.
- Errores:
1. Resultado sin metrica utilizable.
- Reglas de negocio:
1. Aviso orientativo siempre visible.
- Estados UI:
1. Resultado explicativo.
2. Resultado de recaptura.
- Criterios de aceptacion:
1. Usuario entiende siguiente accion en <15 segundos.

## FL-04 Expediente a exportacion
- Objetivo: Generar paquete telemedico sin nube.
- Actor: Brigadista.
- Disparador: Tap `Exportar` desde expediente o dashboard.
- Precondiciones: Paciente seleccionado.
- Postcondiciones: Archivos PDF/JSON/QR listos para compartir.
- Flujo principal:
1. Abrir `Exportar`.
2. Elegir `Redactado` (default) o `Completo`.
3. Tap `Generar paquete`.
4. Validar checksum y vista previa.
5. Tap `Compartir`.
- Flujos alternos:
1. Solo generar sin compartir.
- Errores:
1. Fallo de permisos URI para share.
2. Falta de almacenamiento temporal.
- Reglas de negocio:
1. Redaccion por defecto.
2. Sin persistir fotos.
- Estados UI:
1. Generando.
2. Ultimo paquete.
3. Historial.
- Criterios de aceptacion:
1. Share sheet abre correctamente con archivos adjuntos.

## FL-05 Dashboard comparativo
- Objetivo: Priorizar atencion de cohorte.
- Actor: Coordinador de brigada.
- Disparador: Tap `Panel` desde pacientes.
- Precondiciones: Minimo un paciente activo.
- Postcondiciones: Priorizacion definida.
- Flujo principal:
1. Abrir dashboard.
2. Leer KPIs globales.
3. Seleccionar paciente A y B.
4. Revisar tendencia cohorte y heatmap.
5. Decidir siguiente paciente a intervenir.
- Flujos alternos:
1. Sin datos de comparador -> mostrar estado vacio.
- Errores:
1. Muestras insuficientes para tendencia.
- Reglas de negocio:
1. Datos agregados calculados localmente.
- Estados UI:
1. Visualizacion completa.
2. Parcial sin datos.
- Criterios de aceptacion:
1. Decisiones de priorizacion en <20 segundos.

## FL-06 Gestion de tareas
- Objetivo: Operar seguimiento clinico diario.
- Actor: Brigadista.
- Disparador: Tab `Plan` en expediente.
- Precondiciones: Paciente seleccionado.
- Postcondiciones: Estado de tareas actualizado y reflejado en dashboard.
- Flujo principal:
1. Abrir tab `Plan`.
2. Crear tarea rapida o alternar estado.
3. Confirmar estado final.
- Flujos alternos:
1. Reabrir tarea completada por recaida.
- Errores:
1. Escritura fallida.
- Reglas de negocio:
1. Tareas deben conservar fecha de creacion.
- Estados UI:
1. Lista con estados.
2. Lista vacia.
- Criterios de aceptacion:
1. Dashboard actualiza `pendientes` sin reiniciar app.
