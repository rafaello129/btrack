# Casos de Uso - B-Track Mobile v2

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

## CU-01 Registrar paciente
- Objetivo: Crear un paciente nuevo en brigada sin internet.
- Actor: Brigadista.
- Disparador: Tap en `Registrar paciente` desde `Pacientes`.
- Precondiciones: App abierta; DB local disponible.
- Postcondiciones: Paciente creado con `local_code`; perfil clinico base creado.
- Flujo principal:
1. Brigadista abre lista `Pacientes`.
2. Presiona `Registrar paciente`.
3. Sistema crea paciente con datos iniciales y perfil base.
4. Sistema muestra paciente en lista y habilita acceso a expediente.
- Flujos alternos:
1. Si no hay datos minimos, sistema usa defaults de brigada.
- Errores:
1. Falla de escritura en DB local.
2. Espacio insuficiente.
- Reglas de negocio:
1. `local_code` debe ser unico.
2. Paciente inicia en estado `active=true`.
- Estados UI:
1. Loading breve.
2. Exito con tarjeta nueva visible.
3. Error con CTA `Reintentar`.
- Criterios de aceptacion:
1. Se crea paciente en <2 segundos.
2. Aparece en lista sin refresco manual.

## CU-02 Editar expediente clinico
- Objetivo: Actualizar perfil clinico de seguimiento.
- Actor: Brigadista.
- Disparador: Abrir `ExpedientePaciente` tab `Resumen`.
- Precondiciones: Paciente seleccionado.
- Postcondiciones: Perfil clinico actualizado en Room.
- Flujo principal:
1. Brigadista abre expediente.
2. Revisa riesgo, comorbilidades, medicacion, alergias y notas.
3. Guarda cambios.
4. Sistema actualiza timestamp de perfil.
- Flujos alternos:
1. Si no existe perfil, sistema crea perfil por defecto.
- Errores:
1. Escritura rechazada por DB.
- Reglas de negocio:
1. Riesgo permitido: `LOW`, `MEDIUM`, `HIGH`.
2. No se guardan imagenes en expediente.
- Estados UI:
1. Estado editable.
2. Guardado exitoso.
3. Error de guardado.
- Criterios de aceptacion:
1. Cambios persisten tras cerrar y abrir app.

## CU-03 Captura rapida en brigada
- Objetivo: Ejecutar captura de analisis en campo, con camara o galeria.
- Actor: Brigadista.
- Disparador: `Nueva captura` desde expediente o `Captura rapida` desde pacientes.
- Precondiciones: Permiso de camara otorgado para modo camara.
- Postcondiciones: Resultado generado y sesion guardada con `patient_id` y `encounter_id`.
- Flujo principal:
1. Brigadista abre pantalla `Captura`.
2. Selecciona perfil (`Calidad`, `Balanceado`, `Rapido`).
3. Congela o toma foto, o selecciona imagen desde galeria.
4. Sistema analiza en dispositivo.
5. Navega a `Resultado`.
- Flujos alternos:
1. Camara denegada: usar galeria.
2. Baja calidad: bloqueo de score final con recomendacion.
- Errores:
1. No face detectada.
2. Imagen invalida/rota.
3. Excepcion de pipeline.
- Reglas de negocio:
1. Sin backend.
2. Sin guardado de foto/video.
- Estados UI:
1. Preview en vivo.
2. Congelado.
3. Analizando.
4. Error orientado a accion.
- Criterios de aceptacion:
1. Flujo completo captura->resultado funcional offline.

## CU-04 Revisar resultado orientativo
- Objetivo: Entender estado, causa y accion en <15s.
- Actor: Brigadista / Profesional de salud.
- Disparador: Fin de analisis.
- Precondiciones: Analisis ejecutado.
- Postcondiciones: Usuario decide recaptura o seguimiento.
- Flujo principal:
1. Sistema muestra hero score + confianza.
2. Muestra preview imagen/overlay.
3. Muestra narrativa guiada, region bars y top contributors.
4. Usuario vuelve a captura o expediente.
- Flujos alternos:
1. `NO_FACE`, `LOW_QUALITY`, `ERROR` muestran tarjeta de sistema con CTA.
- Errores:
1. Resultado incompleto por excepcion.
- Reglas de negocio:
1. Mantener aviso visible: orientativo/no diagnostico.
- Estados UI:
1. Estado analizado.
2. Estado sin rostro.
3. Estado baja calidad.
4. Estado error tecnico.
- Criterios de aceptacion:
1. Mensaje principal + recomendacion clara sin abrir detalle tecnico.

## CU-05 Monitorear evolucion
- Objetivo: Ver tendencia clinica por paciente.
- Actor: Brigadista.
- Disparador: Abrir tab `Evolucion` en expediente.
- Precondiciones: Paciente con >=1 sesion.
- Postcondiciones: Se identifica progreso, estancamiento o deterioro.
- Flujo principal:
1. Usuario entra a `ExpedientePaciente`.
2. Cambia a tab `Evolucion`.
3. Revisa curvas de score y calidad.
4. Contrasta con sesiones y alertas.
- Flujos alternos:
1. Si hay pocos datos, mostrar estado vacio guiado.
- Errores:
1. Datos historicos corruptos en JSON de metricas.
- Reglas de negocio:
1. No alterar DB para graficar tendencia.
- Estados UI:
1. Curvas renderizadas.
2. Estado vacio.
- Criterios de aceptacion:
1. Tendencia visible con interaccion fluida.

## CU-06 Crear tarea de seguimiento
- Objetivo: Definir accion clinica siguiente.
- Actor: Brigadista.
- Disparador: Tab `Plan` en expediente.
- Precondiciones: Paciente seleccionado.
- Postcondiciones: Tarea creada o actualizada (`PENDING`, `IN_PROGRESS`, `COMPLETED`).
- Flujo principal:
1. Usuario abre `Plan`.
2. Crea tarea rapida o cambia estado de una existente.
3. Sistema actualiza cumplimiento.
- Flujos alternos:
1. Reabrir tarea completada.
- Errores:
1. Falla al persistir tarea.
- Reglas de negocio:
1. Una tarea pertenece a un paciente.
2. No se elimina historico de tareas completadas.
- Estados UI:
1. Lista de tareas.
2. Sin tareas activas.
3. Confirmacion de estado.
- Criterios de aceptacion:
1. Cambio de estado visible en UI y dashboard.

## CU-07 Exportar para telemedicina
- Objetivo: Compartir paquete local para segunda opinion.
- Actor: Brigadista.
- Disparador: Pantalla `Exportar`.
- Precondiciones: Paciente seleccionado; al menos una sesion.
- Postcondiciones: Paquete generado (PDF + JSON + QR) y share intent abierto.
- Flujo principal:
1. Usuario abre `Exportar`.
2. Elige modo `Redactado` o `Completo`.
3. Presiona `Generar paquete`.
4. Sistema genera archivos locales y checksum.
5. Usuario presiona `Compartir`.
- Flujos alternos:
1. Si no hay paquete, `Compartir` deshabilitado.
- Errores:
1. FileProvider no configurado.
2. Error de escritura en cache.
- Reglas de negocio:
1. Default: redaccion activa.
2. Sin nube.
- Estados UI:
1. Generando.
2. Ultimo paquete visible.
3. Historial de exportaciones.
- Criterios de aceptacion:
1. Exportacion + share en <10s en gama media.

## CU-08 Revisar panel de cohorte
- Objetivo: Priorizar pacientes de brigada.
- Actor: Coordinador de brigada.
- Disparador: Abrir `Dashboard` desde pacientes.
- Precondiciones: Datos locales disponibles.
- Postcondiciones: Lista de prioridades definida.
- Flujo principal:
1. Usuario abre dashboard.
2. Revisa KPIs (activos, riesgo alto, pendientes, promedios).
3. Usa comparador de dos pacientes.
4. Revisa tendencia de cohorte y heatmap de alertas.
- Flujos alternos:
1. Si no hay suficiente data, mostrar estados vacios.
- Errores:
1. Falta de sesiones para comparador.
- Reglas de negocio:
1. Todo calculo es local y offline.
- Estados UI:
1. KPIs activos.
2. Comparador parcial.
3. Heatmap vacio.
- Criterios de aceptacion:
1. En <20s se entiende que pacientes priorizar.
