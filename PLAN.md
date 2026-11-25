# Plan de desarrollo

Arquitectura canónica: [ARQUITECTURA.md](ARQUITECTURA.md), acordada el 26 de noviembre de 2026.

## Flujo objetivo

Voz en castellano de España → texto → traducción lingüística a LSE → planificación temporal de manos, rostro y cuerpo → vídeo fotorrealista 2D → futura salida OBS/Twitch.

La boca sigue la LSE, no una sincronización labial literal del castellano. Diccionarios y ejemplos aportan evidencia; no definen un único movimiento por palabra. La apariencia y la planificación se desarrollan por separado.

## Hitos

1. **Inventario y representación intermedia.** Inspeccionar las anotaciones disponibles, sus referencias y carencias. Definir el contrato del plan lingüístico y su realización temporal sin inventar traducciones validadas. Cierre: campos, coordenadas, unidades, estados y evidencias definidos; plan lingüístico separado de poses estimadas.
2. **Muestra lingüística acotada.** Seleccionar textos y ejemplos relacionados; preparar un plan revisado con personas competentes en LSE. Cierre: significado, estructura, referencias espaciales y canales no manuales revisados. Si no hay colaboración experta, mantener la validación pendiente y continuar con tareas técnicas independientes.
3. **Movimiento controlado.** Extraer o representar secuencias de muestra y comprobar dedos, orientaciones, contactos, rostro y transiciones. Cierre: errores documentados y representación reproducible. Coincidencia de puntos no equivale a comprensión.
4. **Apariencia fotorrealista fija.** Auditar un generador existente y comparar original, movimiento y resultado. Cierre: fidelidad técnica y comprensión evaluadas; no se requiere modelado gráfico manual ni personaje 3D visible.
5. **Personalización.** Cambiar la apariencia sobre secuencias revisadas, con permisos y consentimiento adecuados. Medir material de referencia necesario; no prometer que una foto baste.
6. **Voz y directo.** Añadir reconocimiento de voz, segmentación, contexto, sincronización y salida OBS. Medir la cadena completa antes de una integración distribuida con Twitch.

## Qué revisa cada persona

- Eva: objetivo, facilidad de uso y apariencia. No se le pide validar lingüísticamente LSE.
- Verificación técnica: datos, geometría, integridad, sincronización, recursos y fidelidad de movimientos.
- Personas sordas signantes y especialistas: comprensión, significado y calidad lingüística.

## Estado real

Implementados: auditor ELAN, descarga parcial de tres originales, página local de revisión, contrato 0.1 de observaciones con exportador/validador, e inventario de glosas presentes en los tres fragmentos. Pruebas de metadatos, referencias y acceso parcial al ZIP. Los originales no tienen audio; las traducciones están en anotaciones escritas. No hay transcripción de voz, traductor, extractor de poses, generador, avatar personalizado ni integración Twitch implementados.

Preparado: especificación de arquitectura y plan. Pendientes: completar inventario de evidencia, definir contratos de planificación y movimiento, elegir extractor y probar un fragmento con requisitos y licencia revisados. Los hitos de traducción, generación y evaluación siguen pendientes.

## Límites

Lotes pequeños, secuenciales y GPU de IA desactivada por defecto. Comprobar recursos antes de modelos; no iniciar entrenamiento ni cómputo remoto pagado automáticamente. Medir renderizado por separado. Instrumentar llamadas de IA con identidad de proyecto/tarea/ejecutor y contadores reales; ausencia de datos significa desconocido, no cero. No prometer ahorro ni calidad sin evaluación.

Vídeos, datos, traducciones extraídas, fotografías y resultados no se publican por defecto. Revisar condiciones de cada recurso; la licencia MIT del código no cambia las licencias de terceros. No ampliar datasets ni ejecutar modelos como consecuencia automática de aprobar este plan.
