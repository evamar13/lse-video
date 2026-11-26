# Uso en Twitch: separar animación interactiva de generación offline

Decisión técnica del 26 de noviembre de 2026, ante la pregunta de Eva sobre viabilidad del directo. El objetivo sigue siendo salida 2D con apariencia personalizable; no se sustituye por un personaje 3D visible sin acordarlo. Presupuesto vigente: sin gasto y sin IA pesada en el Mac.

## Cómo lo usaría una persona

Una aplicación acompañante obtiene el micrófono con autorización o recibe texto/subtítulos disponibles. Estabiliza una unidad de significado, produce una interpretación LSE revisable y la convierte a instrucciones de movimiento. Un reproductor anima una representación ya preparada y OBS la incorpora como fuente de navegador. La API de Twitch no se presume un acceso general al micrófono. La primera prueba no necesita conectar credenciales de Twitch.

Hay tres trabajos diferentes: reconocer voz, interpretar a LSE y representar movimientos. Cada uno tiene latencia y errores propios. La animación de una escena no resuelve la traducción, y una traducción rápida no garantiza signos comprensibles. La LSE puede reorganizar el mensaje: se necesita un búfer y medir retraso acumulado/cola. No prometer simultaneidad exacta, retraso máximo ni fluidez con habla arbitraria.

## Dos rutas que no deben confundirse

| Ruta | Uso razonable | Estado |
|---|---|---|
| Animación controlada de representación preparada | Directo, tras medir latencia y calidad | Candidato de arquitectura; no traductor implementado |
| Generación de vídeo por difusión desde foto y poses | Prueba offline de apariencia, clips pregrabados | MimicMotion estudiado; no ejecutado ni integrado |

[MimicMotion](https://github.com/Tencent/MimicMotion) documenta una prueba de 35 s que tarda 20 minutos en una RTX 4090; ese resultado no sirve como promesa de directo. Sus pesos se restringen a investigación/educación, aunque el código tenga otra licencia. Es un candidato para investigación privada de apariencia, no el backend elegido para Twitch o producción. Fuente: [licencia de los pesos](https://huggingface.co/tencent/MimicMotion/blob/main/LICENSE).

[Performs](https://github.com/upf-gti/performs) declara animación de componentes manuales y no manuales en tiempo real, con instrucciones SiGML/BML. Es candidato para estudiar ejecución de movimiento; usa avatares preparados glTF/GLB y no convierte una foto en un signante realista ni proporciona traducción castellano–LSE. Sus ejemplos de diccionario NGT no se adoptan como LSE. No se ha medido en el equipo ni integrado al proyecto.

[OBS Browser Source](https://obsproject.com/kb/browser-source) admite una página local o URL para mostrar gráficos y vídeo; es una vía de integración visual, no un traductor. No se ha probado todavía con OBS.

## La foto no sustituye al modelo animable

Concreción aportada por Eva: [avatar modular](AVATAR_MODULAR.md), con manos/brazos y estructura de cuerpo comunes, adaptaciones de color/proporciones/ropa y cara/cuello personales. Es la dirección prioritaria para investigar la representación animable; todavía no hay un ensamblador o renderizador de este avatar implementado.

Preparar una imagen frontal mejora la referencia de apariencia. Para animarla en directo hace falta además una representación deformable o un renderizador de persona suficientemente rápido. Una imagen fija no aporta superficies ocultas, articulaciones ni expresiones listas para ejecutar. La preparación con IA no demuestra fidelidad de manos o identidad durante el movimiento.

Se pueden investigar representación 2D deformable, estructura 3D interna con salida 2D o renderizado neural rápido. Ninguna se presenta como solución ya elegida que conserve una foto y LSE con bajo consumo. La personalización por una sola fotografía, realismo, directo, código/modelos reutilizables y operación sin gasto son requisitos que deben evaluarse conjuntamente.

## Siguiente ensayo prioritario

Medir primero reproducción interactiva de una secuencia existente, cola/búfer y fidelidad de manos/canales faciales. Puede empezar con movimientos grabados y mensajes cerrados revisados, sin llamarlo traducción general. Mantener subtítulos o estado de incapacidad cuando falte una interpretación; no concatenar signos de diccionario y presentarlos como frases válidas.

La prueba generativa de dos segundos queda como ensayo offline secundario de apariencia. No se han descargado pesos, preparado un cuaderno ejecutable, subido imágenes/corpus ni alquilado GPU. La investigación de su interfaz y licencias queda registrada; no se confunde con vídeo generado.

Colab ofrece recursos gratuitos no garantizados, pero su FAQ restringe crear deepfakes; no se adopta para esta personalización sin aclarar el alcance. Kaggle documenta GPU gratuita limitada y puede estudiarse para un ensayo privado conforme a sus condiciones; no está contratado ni autorizado el envío de datos por haber pedido gasto cero. Ningún recurso gratuito eventual constituye una infraestructura de producción garantizada.

Fuentes: [FAQ Colab](https://research.google.com/colaboratory/faq.html), [notebooks Kaggle](https://www.kaggle.com/docs/notebooks), [uso aceptable Kaggle](https://www.kaggle.com/aup). La disponibilidad y condiciones requieren comprobarse antes de usar un servicio.
