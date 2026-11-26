# Preparación habitual de fotografías

Requisito de Eva, 26 de noviembre de 2026: aceptar fotos cotidianas. Preparar la referencia es responsabilidad del proceso; no exigir al usuario una fotografía perfecta como condición de entrada.

## Flujo obligatorio de apariencia

1. **Conservar el original.** Copia privada sin modificar, huella SHA-256 y caso independiente por persona/foto. No publicar originales, candidatas ni prompts que describan personas. No mezclar material personal con corpus lingüísticos.
2. **Revisión visual.** Comprobar rostro reconocible, encuadre, manos/brazos visibles, oclusiones, desenfoque, luz, ropa y fondo. La comprobación de dimensiones es automática; la revisión visual actual la realiza el asistente. No afirmar detección automática de estos defectos.
3. **Elegir intervención mínima.** Si la foto ya sirve para el generador elegido, reutilizarla. Si presenta brazos cruzados, fondo complejo, recortes u otras limitaciones reparables, crear una candidata con IA. Una foto de cara puede requerir reconstruir el cuerpo; no presentar esa anatomía como un dato real de la persona.
4. **Preparar con IA cuando proceda.** Usar el generador integrado y la skill imagegen, conservando identidad, edad aparente y rasgos visibles. Fondo neutro, frontal, luz uniforme, espacio para movimiento y manos separadas y completas cuando el generador lo requiera. Evitar cambios estéticos ajenos a la tarea. El encuadre final depende del generador; no imponer un formato universal.
5. **Comprobar la candidata.** Identidad aparente, cinco dedos por mano, articulaciones, muñecas, ausencia de solapes graves y coherencia de ropa/cuerpo. Mostrar qué se reconstruyó. Esta inspección no prueba identidad biométrica, anatomía verdadera ni capacidad de signar.
6. **Validación de apariencia por la persona.** Mostrar candidata y pedir aceptación o corrección de parecido. Registrar la revisión explícita. Una buena evaluación del movimiento anterior no valida automáticamente una nueva cara generada. Rechazar una candidata aceptada previamente revoca su disponibilidad.
7. **Entregar solo una referencia aceptada.** La animación debe solicitar el archivo mediante `resolver_referencia()`, que comprueba estado y hash. Conservar originales, versiones, cambios y resultado de revisión. Después se evalúa el vídeo generado, especialmente manos, boca, cejas e identidad durante el movimiento.

No repetir permiso para una adaptación ya autorizada dentro del mismo encargo. El uso de IA para esta preparación habitual está autorizado por Eva; no autoriza nuevos servicios pagados, entrenamiento o envío de corpus a proveedores. Fotografías de otras personas requieren autorización adecuada. La aplicación futura deberá informar del procesamiento de su imagen y del destino del tratamiento.

## Límites de calidad y consumo

Máximo dos candidatas por caso: una preparación y una corrección dirigida. Reutilizar una candidata aceptada si su hash coincide; no regenerarla en cada vídeo. No cargar modelos locales o activar GPU para preparar una foto por defecto. Registrar una operación por generación y los contadores reales si el proveedor los entrega; desconocido no es cero.

Si no se puede conservar razonablemente el parecido, hay demasiado poco detalle o las manos reconstruidas siguen siendo defectuosas, explicar el fallo y pedir otra foto corriente o una toma complementaria concreta. No fabricar una falsa validación para completar el flujo.

Las partes reconstruidas sirven como apariencia candidata. Las coordenadas de signos proceden de movimientos revisados; no se obtienen del aspecto de una foto generada. La boca sigue componentes de LSE, no una sincronización literal con el castellano.

## Herramientas disponibles y alcance real

`preparar_referencia.py` gestiona expedientes privados, originales, hasta dos candidatas, revisiones y resolución de una referencia aceptada con integridad comprobada. `PROMPT_REFERENCIA.txt` es la especificación reutilizable para el generador.

```sh
python3 preparar_referencia.py nuevo --foto /ruta/a/foto.jpg
python3 preparar_referencia.py adjuntar --caso ID --imagen /ruta/a/candidata.png --origen ia --cambio 'Brazos reconstruidos y fondo neutro'
python3 preparar_referencia.py revisar --caso ID --candidata ID --decision aceptar
python3 preparar_referencia.py resolver --caso ID
```

El asistente utiliza la skill imagegen para ejecutar la preparación y adjunta el resultado. El script no llama a APIs, no edita píxeles, no evalúa identidad automáticamente y no es un agente autónomo. La conexión automática desde una aplicación de subida de fotos y el generador de vídeo siguen pendientes. No se presenta este flujo asistido como una función desplegada para terceros.

La primera candidata de Eva permanece en `datos/avatar-personal/referencia-frontal-v1.png`, con prompt y procedencia privados; se realizó antes del gestor de casos. No se inventa una copia local del original adjunto en la conversación ni se marca aceptación explícita sin revisión. Se conserva como ejemplo de preparación, no como prueba de animación.
