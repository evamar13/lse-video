# Plan de desarrollo

Arquitectura canónica: [ARQUITECTURA.md](ARQUITECTURA.md), acordada el 26 de noviembre de 2026.

## Flujo objetivo

Voz en castellano de España → texto → propuesta de interpretación LSE con explicación en castellano → plan estructurado → compilación de movimientos de manos, rostro y cuerpo → vídeo fotorrealista 2D → futura salida OBS/Twitch. Ampliación de diseño: [GLOSARIO.md](GLOSARIO.md).

La boca sigue la LSE, no una sincronización labial literal del castellano. Diccionarios y ejemplos aportan evidencia; no definen un único movimiento por palabra. La apariencia y la planificación se desarrollan por separado.

## Hitos

Prioridad de viabilidad de directo: [DIRECTO.md](DIRECTO.md). Evaluar reproducción interactiva y latencia antes de convertir el ensayo offline de apariencia en dependencia de Twitch. El presupuesto de pruebas es cero; no sustituirlo por cómputo local pesado ni infraestructura gratuita supuesta.

1. **Inventario y representación intermedia.** Inspeccionar las anotaciones disponibles, sus referencias y carencias. Definir el glosario de conceptos/signos/construcciones, descripción legible, fuentes y mapeo de movimiento; después el contrato del plan y su compilador. No inventar traducciones validadas ni datos que faltan en la fuente. Cierre: campos, coordenadas, unidades, estados y evidencias definidos; plan lingüístico separado de poses estimadas.
2. **Muestra lingüística acotada.** Seleccionar textos y ejemplos relacionados; preparar un plan revisado con personas competentes en LSE. Cierre: significado, estructura, referencias espaciales y canales no manuales revisados. Si no hay colaboración experta, mantener la validación pendiente y continuar con tareas técnicas independientes.
3. **Movimiento controlado.** Extraer o representar secuencias de muestra y comprobar dedos, orientaciones, contactos, rostro y transiciones. Cierre: errores documentados y representación reproducible. Coincidencia de puntos no equivale a comprensión.
4. **Apariencia fotorrealista fija.** Auditar un generador existente y comparar original, movimiento y resultado. Cierre: fidelidad técnica y comprensión evaluadas; no se requiere modelado gráfico manual ni personaje 3D visible.
5. **Personalización.** Aceptar fotos cotidianas y preparar la referencia como etapa habitual según PREPARACION_FOTOS.md: revisión, reutilización o adaptación con IA, conservación de originales, identificación de reconstrucciones y aceptación de apariencia. Cambiar la apariencia sobre secuencias revisadas, con permisos adecuados. Medir material necesario; pedir otra toma solo si no se consigue una referencia utilizable, sin prometer que cualquier foto baste.
6. **Voz y directo.** Añadir reconocimiento de voz, segmentación, contexto, sincronización y salida OBS. Medir la cadena completa antes de una integración distribuida con Twitch.

## Qué revisa cada persona

- Eva: objetivo, facilidad de uso y apariencia. No se le pide validar lingüísticamente LSE.
- Verificación técnica: datos, geometría, integridad, sincronización, recursos y fidelidad de movimientos.
- Personas sordas signantes y especialistas: comprensión, significado y calidad lingüística.

## Estado real

Preparación de fotos: requisito habitual incorporado a arquitectura e instrucciones. Implementados el gestor privado `preparar_referencia.py` y el prompt reutilizable; el asistente ejecuta la edición con imagegen cuando procede. La primera candidata de apariencia ya se generó; no se ha animado. La aplicación automática de subida/preparación, evaluación automática de identidad y generación fotorrealista siguen pendientes.

Implementados: auditor ELAN, descarga parcial de tres originales, página local de revisión, contrato 0.1 de observaciones con exportador/validador, e inventario de glosas presentes en los tres fragmentos. Primera extracción Holistic CPU ejecutada en un fragmento de 5,8 segundos, con coordenadas observadas y vista de seguimiento; ver MOVIMIENTO.md. Pruebas de metadatos, referencias y acceso parcial al ZIP. Los originales no tienen audio; las traducciones están en anotaciones escritas. No hay transcripción de voz, traductor, generador de personas, avatar personalizado ni integración Twitch implementados. El extractor experimental no equivale a un plan de movimientos validado.

Preparado: especificación de arquitectura y plan; propuesta de glosario e instrucciones legibles, aún sin implementar. Pendientes: completar inventario de evidencia, definir contratos de planificación y movimiento, revisar las pérdidas de seguimiento del extractor y convertir sus estimaciones en un contrato de movimiento explícito. Los hitos de traducción, generación y evaluación siguen pendientes.

## Límites

Lotes pequeños, secuenciales y GPU de IA desactivada por defecto. Comprobar recursos antes de modelos; no iniciar entrenamiento ni cómputo remoto pagado automáticamente. Medir renderizado por separado. Instrumentar llamadas de IA con identidad de proyecto/tarea/ejecutor y contadores reales; ausencia de datos significa desconocido, no cero. No prometer ahorro ni calidad sin evaluación.

Vídeos, datos, traducciones extraídas, fotografías y resultados no se publican por defecto. Revisar condiciones de cada recurso; la licencia MIT del código no cambia las licencias de terceros. No ampliar datasets ni ejecutar modelos como consecuencia automática de aprobar este plan.
