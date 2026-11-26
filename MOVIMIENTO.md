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

### Reproducción geométrica 2D implementada

`reproducir_2d.py` genera `outputs/reproduccion-2d/VALIDAR.html` con original, seguimiento previo y figura SVG plana. Reutiliza los 29 fotogramas sin nuevas inferencias. Controles comunes: reproducir/pausar, velocidad 0,5× o 1×, barra y flechas por muestra. La figura y el seguimiento se actualizan según el reloj del original (consulta cada 100 ms solo al reproducir); no hay interpolación ni reproducción continua en segundo plano. El panel de seguimiento se desplaza por posiciones, no tiene un segundo reloj de reproducción independiente. No se garantiza sincronización exacta a fotograma del decodificador; sigue vigente la incertidumbre temporal de la primera extracción.

Se conserva la relación de aspecto del vídeo y se verifica su SHA-256 contra la observación. La mano izquierda ausente a los 2,6 s no se dibuja y se anuncia. Se dibujan articulaciones, contorno facial, labios, ojos y cejas observados; no se infieren contactos, profundidad, rotaciones de dedos ni función lingüística facial. La figura es una reproducción geométrica de referencia, no un avatar que traduce texto, una persona realista ni una prueba de comprensión. La traducción es la del fragmento original del corpus; no una descripción automática de lo que entiende la figura.

Ejecución: `.venv/bin/python reproducir_2d.py`. Requiere el OpenCV ya instalado para verificar dimensiones. No importa MediaPipe ni descarga modelos. Pruebas específicas: ausencia de mano sin relleno, coordenadas no finitas, tiempos duplicados y relación de aspecto. Datos, SVG, traducción y galería generados permanecen excluidos de Git. Antes de difusión de derivados, revisar las condiciones del corpus.

Verificación del 26 de noviembre: 17 pruebas Python correctas. Vista de escritorio inspeccionada mediante captura en Chrome headless con GPU desactivada. Autocomprobación local `?test=1`: carga de metadatos/dimensiones de ambos vídeos, navegación de muestras, ausencia de mano, actualización de figura y posición del seguimiento al cambiar el reloj del original, solicitud de reproducción y pausa sin temporizador residual. Ocho comprobaciones correctas. Esta prueba no mide deriva de sincronización durante reproducción prolongada ni comprensión lingüística.

Revisar la pérdida de seguimiento y visibilidad de manos/rostro. Definir el contrato de movimiento estimado separado del contrato lingüístico; después evaluar cómo convertir esos puntos en orientaciones, contactos y una representación utilizable por un generador. No usar todavía estos puntos como prueba de signos correctos ni como entrada definitiva de generación fotorrealista.
