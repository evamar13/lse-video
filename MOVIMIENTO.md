# Primera extracción real de movimiento — 26 de noviembre de 2026

Estado: muestra offline ejecutada; no es traducción ni generación de una persona. Un modelo preentrenado detecta puntos sobre el vídeo original. El modelo no se ha entrenado con el corpus.

## Resultado observado

- Un fragmento de 5,8 segundos, elegido entre los tres candidatos por tener más glosas anotadas, sin validación lingüística de la selección.
- 29 muestras a 5 Hz. En una muestra con detecciones completas: 33 puntos de cuerpo, 478 de rostro y 21 de cada mano.
- Cuerpo y rostro detectados en 29/29; mano derecha en 29/29; mano izquierda en 28/29. La ausencia se conserva como lista vacía, no se interpola ni se rellena.
- Tiempo de ejecución observado: aproximadamente 19,3 segundos, incluyendo comprobaciones y codificación. No es un benchmark de tiempo real ni de máxima velocidad; hay pausas y muestreo reducido.
- Delegate CPU explícito. Recursos globales muestreados seis veces: presión de RAM normal, sin aviso térmico, CPU entre 15,41 y 28,16 %, GPU global entre 0 y 5 %. La GPU global no se atribuye al modelo; estas muestras no prueban límites continuos de uso o temperatura.
- Se registraron operaciones de detección por fotograma, con proyecto/tarea/ejecutor y duración; no se inventan equivalencias de tokens.

Las cuentas de detección no miden error posicional ni comprensión. No se ha evaluado lingüísticamente la LSE, ni verificado orientación de palmas, contactos o movimientos rápidos. La baja frecuencia sirve para explorar, no como captura final de entrenamiento.

## Artefactos privados

- `outputs/movimiento/VALIDAR.html`: original y vista con puntos superpuestos, con traducción escrita de referencia. Sin audio. No están sincronizados automáticamente.
- `outputs/movimiento/seguimiento.mp4`: vídeo derivado con seguimiento superpuesto, codificado H.264.
- `outputs/movimiento/movimiento.json`: puntos, procedencia, modelo y tiempos. Es una observación, no un plan lingüístico ni un archivo listo para generar personas.
- `outputs/movimiento/resumen.json`: conteos, estado, duración y muestras de recursos.

Se comprobó decodificación de la vista previa y se inspeccionó una imagen. La página HTML se generó, pero no se probó su interacción en un navegador automatizado. Ninguno de estos artefactos se sube al repositorio público.

## Coordenadas y limitaciones

`x` e `y` se refieren a la imagen normalizada. `z` conserva la estimación del modelo y no debe interpretarse como distancia métrica común entre rostro, cuerpo y manos. No se guardan rotaciones de articulaciones ni contactos verificados. Los puntos de la boca y los blendshapes son geometría/expresión estimada; no etiquetan la función lingüística de la boca.

`t_ms` es el tiempo relativo de la secuencia remuestreada; `source_t_ms`, la posición solicitada al decodificador. En esta primera ejecución no se registró la cuantización de los fotogramas fuente. El código actualizado recoge también `decoded_source_t_ms` para futuras ejecuciones. No se repitió la inferencia para añadir ese campo.

## Herramientas y licencias

- MediaPipe 1.2.3, paquete con licencia Apache 2.0. [Documentación oficial Holistic](https://developers.google.com/edge/mediapipe/solutions/vision/holistic_landmarker) y [configuración Python/CPU](https://developers.google.com/edge/mediapipe/solutions/setup_python).
- Modelo oficial versión 1: `https://storage.googleapis.com/mediapipe-models/holistic_landmarker/holistic_landmarker/float16/1/holistic_landmarker.task`. 13,05 MiB; SHA-256 `e2dab61191e2dcd0a15f943d8e3ed1dce13c82dfa597b9dd39f562975a50c3f8`. No se redistribuye; las condiciones de pesos se revisan separadamente del código propio.
- OpenCV 5.1.0.95 y un ejecutable FFmpeg existente para codificación CPU. No se incorpora el ejecutable a Git.
- Fuente de datos: LSE-Health-UVigo, según [FUENTES.md](FUENTES.md), con sus condiciones no comerciales. No publicar automáticamente vídeos, poses ni derivados.

## Reproducir de forma controlada

La prueba se ejecutó en un entorno aislado con Python 3.13.18 y las versiones de `requirements-motion.txt`. El núcleo de auditoría no requiere estas dependencias; se usan solo en extracción.

El ejecutor actual integra `recursos_locales.py` y `telemetria.py` del espacio de trabajo AI Tools. Requiere ese adaptador mediante `--guard-tools` y rechaza la ejecución si falta. El adaptador portátil independiente todavía no está empaquetado en este repositorio; no se elimina la guardia para hacer funcionar una instalación externa.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-motion.txt
# Obtener el modelo oficial por separado, fuera del repositorio, y verificar el SHA-256.
.venv/bin/python extraer_movimiento.py --task ID_DE_TAREA --ffmpeg /ruta/a/ffmpeg --guard-tools /ruta/a/AI-Tools/tools
```

Debe existir la muestra, auditoría y contratos del README. Por defecto el modelo se busca en `~/AI Models/mediapipe/holistic-v1/`, o bajo `AI_MODELS_DIR`. La inferencia no descarga modelos automáticamente.

El bloqueo compartido y las métricas se consultan antes de cargar el modelo y entre grupos de cinco fotogramas. Se aplican instrucciones de hasta dos hilos a bibliotecas y OpenCV; la API usada no expone un límite duro de hilos de MediaPipe. CPU y GPU globales no tienen un tope de driver. La duración máxima se comprueba entre iteraciones, no cancela una llamada nativa bloqueada.

Máximo seis segundos y cinco muestras/s por ejecución. No sobrescribe un resultado existente ni amplía el lote o el presupuesto automáticamente. Si falla una condición, conserva artefactos con estado incompleto explícito. No abrir varias inferencias para acelerar la prueba.

## Siguiente paso

### Perfil de mayor frecuencia aprobado visualmente

Eva considera adecuada visualmente la muestra de manos y autoriza continuar. Esta aprobación de apariencia no se registra como exactitud medida ni validación lingüística. Se añade `--perfil fluido` al extractor: 15 Hz explícitos, máximo seis segundos/90 muestras, salida independiente `outputs/movimiento-15fps/`. El perfil predeterminado conserva sus límites de 1–5 Hz. No se modifican el bloqueo, delegate CPU, consultas de recursos cada cinco fotogramas, pausa entre llamadas, descarga del modelo al terminar ni presupuesto temporal de 90 segundos.

Ejecución del 26 de noviembre: 87 observaciones del mismo fragmento de 5,8 s, 48,4 s de ejecución completa. Cuerpo, rostro y mano derecha detectados en 87/87; izquierda en 83/87, ausente en 1.133, 1.200, 2.600 y 3.533 ms relativos. Se conservan las ausencias. Los tiempos reportados por el decodificador corresponden a 87 fotogramas distintos; desviación máxima observada respecto al seek solicitado: 17 ms. El SHA-256 del JSON de la captura inicial permanece idéntico. No se interpola ni se entrena.

Dieciocho muestras de recursos globales: GPU 0 %, CPU 12,02–29,14 %, presión de RAM normal, sin aviso térmico. No son garantías continuas ni mediciones de temperatura. Las 87 inferencias llevan proyecto, tarea `movimiento-fluido-20261126` y ejecutor `motion.extractor` en contabilidad.

Visor: `outputs/reproduccion-2d-15fps/VALIDAR.html`. Reconstrucción sin inferencia: `.venv/bin/python reproducir_2d.py --fluido`. Enlaces entre las versiones de 5 y 15 Hz; controles ajustados a la frecuencia y tolerancia de sincronización reducida a media muestra. La segunda captura experimental de recortes permanece en la versión de 5 Hz y no se mezcla con la nueva extracción. Ambos visores incluyen una imagen de vista previa del original, almacenada localmente.

Verificación: 29 pruebas Python, ocho comprobaciones de interacción en Chrome para el perfil nuevo y vista de escritorio inspeccionada. La prueba detectó una tolerancia de sincronización heredada demasiado amplia para 15 Hz; se corrigió y la comprobación pasó. Las pruebas no cuantifican deriva prolongada, error de articulaciones ni comprensión en LSE. Más frecuencia temporal no demuestra mayor precisión espacial.

### Detalle de dedos y segunda observación de manos

El visor incorpora ampliaciones separadas con 21 puntos identificados por mano y cinco cadenas de dedos en colores distintos. La muñeca del brazo se ancla visualmente al punto 0 de la mano para eliminar separaciones de dibujo; no se modifica la observación original ni se presenta el anclaje como una mejora medida del detector. La ampliación ajusta el encuadre de cada mano, por lo que no conserva una escala fija entre fotogramas.

`refinar_manos.py` añade una segunda observación experimental: recortes individuales del vídeo original 1920×1080, Hand Landmarker en CPU, transformación de coordenadas del recorte a la imagen y asociación espacial a los canales previos. Se conservan todos los candidatos. No se acepta una asociación ambigua, excesivamente desplazada de la muñeca o insuficiente; los canales inicialmente ausentes no se recuperan inventando lateralidad. `z_crop` conserva la profundidad cruda del modelo, sin equipararla a profundidad física o a la de otros grupos. Las etiquetas de lateralidad y su puntuación se guardan como observaciones, no como confianza en la posición de cada dedo.

Modelo externo: [documentación y mapa de articulaciones](https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker?tab=Python), [bundle oficial versión 1](https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task). SHA-256 observado y fijado `fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1`; ubicación `~/AI Models/mediapipe/hand-v1/`. No se distribuyen pesos. Descargar y comprobar la versión por separado; el ejecutor no descarga modelos.

Dos pilotos de tres fotogramas compararon recorte conjunto e individual. Después se ejecutaron 29 fotogramas con recortes individuales: 57 operaciones de inferencia registradas en telemetría; 21 fotogramas con candidatos asociables, siete con detección insuficiente y uno con desplazamiento de muñeca rechazado. Tiempo completo observado 17,9 s. Seis muestras globales: GPU 0 %, CPU 13,4–23,8 %, presión RAM normal y sin aviso térmico. Son observaciones muestreadas, no techos de recursos ni garantía térmica. Se usa bloqueo compartido, métricas entre tandas, indicación de dos hilos y delegate CPU explícito; MediaPipe no expone aquí un tope universal de hilos. El proceso termina y descarga el modelo.

La captura inicial sigue siendo la predeterminada. El selector «Recortes individuales · experimental» permite comparar en el visor; no se ha demostrado menor error ni mayor comprensión. La galería `outputs/manos-detalle/VALIDAR.html` compara original, detección inicial y candidata, incluso en casos rechazados. Ninguno de estos datos o derivados se publica en Git.

Reproducción: `.venv/bin/python refinar_manos.py` obtiene tres muestras piloto; `--all` procesa como máximo las 29 muestras existentes. No sobrescribe una ejecución completa. Las nuevas ejecuciones conservan un checkpoint parcial tras cada fotograma antes de completar el resultado. `python3 refinar_manos.py --all --galeria` reconstruye solo el HTML sin modelo ni inferencias. Después `.venv/bin/python reproducir_2d.py` actualiza el visor sin inferencia.

Verificación: 23 pruebas Python; nueve comprobaciones de interacción en Chrome headless, incluida la vista ampliada experimental. Captura del visor y comparación fotográfica inspeccionadas. Las pruebas cubren transformación recorte→imagen, ambigüedad, ausencia, encuadre, asociación y conservación de los datos originales; no constituyen verdad de referencia sobre dedos o LSE. La fuente tiene desenfoque y oclusiones que el zoom no resuelve. Para demostrar precisión hará falta anotación manual de una muestra y medir errores frente a ella.

### Reproducción geométrica 2D implementada

`reproducir_2d.py` genera `outputs/reproduccion-2d/VALIDAR.html` con original, seguimiento previo y figura SVG plana. Reutiliza los 29 fotogramas sin nuevas inferencias. Controles comunes: reproducir/pausar, velocidad 0,5× o 1×, barra y flechas por muestra. La figura y el seguimiento se actualizan según el reloj del original (consulta cada 100 ms solo al reproducir); no hay interpolación ni reproducción continua en segundo plano. El panel de seguimiento se desplaza por posiciones, no tiene un segundo reloj de reproducción independiente. No se garantiza sincronización exacta a fotograma del decodificador; sigue vigente la incertidumbre temporal de la primera extracción.

Se conserva la relación de aspecto del vídeo y se verifica su SHA-256 contra la observación. La mano izquierda ausente a los 2,6 s no se dibuja y se anuncia. Se dibujan articulaciones, contorno facial, labios, ojos y cejas observados; no se infieren contactos, profundidad, rotaciones de dedos ni función lingüística facial. La figura es una reproducción geométrica de referencia, no un avatar que traduce texto, una persona realista ni una prueba de comprensión. La traducción es la del fragmento original del corpus; no una descripción automática de lo que entiende la figura.

Ejecución: `.venv/bin/python reproducir_2d.py`. Requiere el OpenCV ya instalado para verificar dimensiones. No importa MediaPipe ni descarga modelos. Pruebas específicas: ausencia de mano sin relleno, coordenadas no finitas, tiempos duplicados y relación de aspecto. Datos, SVG, traducción y galería generados permanecen excluidos de Git. Antes de difusión de derivados, revisar las condiciones del corpus.

Verificación del 26 de noviembre: 17 pruebas Python correctas. Vista de escritorio inspeccionada mediante captura en Chrome headless con GPU desactivada. Autocomprobación local `?test=1`: carga de metadatos/dimensiones de ambos vídeos, navegación de muestras, ausencia de mano, actualización de figura y posición del seguimiento al cambiar el reloj del original, solicitud de reproducción y pausa sin temporizador residual. Ocho comprobaciones correctas. Esta prueba no mide deriva de sincronización durante reproducción prolongada ni comprensión lingüística.

Revisar la pérdida de seguimiento y visibilidad de manos/rostro. Definir el contrato de movimiento estimado separado del contrato lingüístico; después evaluar cómo convertir esos puntos en orientaciones, contactos y una representación utilizable por un generador. No usar todavía estos puntos como prueba de signos correctos ni como entrada definitiva de generación fotorrealista.
