# LSE Video

Investigación abierta para representar lengua de signos española (LSE) mediante vídeo fotorrealista 2D, con una futura integración en OBS/Twitch.

**Estado: primera extracción CPU realizada.** Hay herramientas de auditoría, muestra local, exportación de evidencia ELAN y seguimiento experimental de manos, rostro y cuerpo. No sintetiza personas, no traduce voz a LSE ni entrena modelos; la extracción usa un modelo preentrenado externo. No hay todavía una evaluación de comprensión con personas signantes.

## Arquitectura acordada

**Voz en castellano de España → texto → traducción a LSE → plan de movimientos → vídeo fotorrealista 2D → OBS/Twitch.**

La representación intermedia incluirá significado, signos/variantes, referencias espaciales, movimientos de ambas manos y dedos, brazos, rostro, mirada y boca, con sus tiempos y evidencias. La boca seguirá las necesidades de la LSE, no una sincronización labial literal del audio castellano. Un diccionario no basta para construir frases.

Primero se diseña ese contrato y el inventario de ejemplos. Después se evalúan por separado traducción, movimiento y apariencia. No se requiere un personaje 3D visible ni modelado manual. El detalle está en [ARQUITECTURA.md](ARQUITECTURA.md) y los hitos en [PLAN.md](PLAN.md).

Los tres originales descargados son un banco inicial de observación. Eva revisa apariencia y experiencia; la corrección lingüística necesita personas competentes en LSE. No se le pide certificar una lengua que no conoce.

## Qué se puede ejecutar hoy

Requiere Python 3.10 o posterior; solo biblioteca estándar. El script no descarga archivos, no carga modelos ni realiza llamadas a IA.

El corpus de referencia es [LSE-Health-UVigo](https://zenodo.org/records/10234465), de Alba-Castro y colaboradores. Obtener `ELAN-LSE-Health-UVigo.zip` de la fuente oficial conforme a sus condiciones, y guardarlo localmente como `datos/anotaciones.zip`.

```sh
mkdir -p datos
python3 auditar_anotaciones.py
```

O indicar rutas propias:

```sh
python3 auditar_anotaciones.py --zip /ruta/anotaciones.zip --output /ruta/auditoria.json
```

El script verifica el MD5 publicado para esa versión, cuenta capas de anotación y preselecciona tres candidatos de archivos diferentes. La selección es mecánica: duración de 5–12 segundos, longitud de texto y puntuación. Puede contener frases dependientes del contexto o listas; necesita revisión visual y lingüística.

La auditoría local inicial del 26 de noviembre de 2026 encontró 273 archivos ELAN, 609 candidatos que pasan ese filtro y tres preseleccionados. Esos recuentos describen anotaciones; no son resultados de traducción ni de generación. Posteriormente se han obtenido solo tres vídeos mediante rangos HTTP del ZIP oficial y verificado su tamaño/CRC; la extracción posterior con un modelo preentrenado se documenta en [MOVIMIENTO.md](MOVIMIENTO.md).

## Licencias

- Código original de este repositorio: [MIT](LICENSE).
- Dataset de referencia: CC BY-NC 4.0 según la ficha institucional. No se redistribuye aquí. La licencia del código no modifica las condiciones de datos, imágenes, pesos ni herramientas externas.
- Los recursos externos son candidatos, no dependencias integradas. Ver [datos y referencias](FUENTES.md).

`datos/`, vídeos, fotografías personales, pesos, resultados y credenciales quedan fuera de Git. El repositorio público no contiene las traducciones extraídas ni los archivos del corpus.

## Recursos y siguiente etapa

El auditor utiliza CPU y archivos pequeños. No se ha medido todavía el coste de generación, la latencia o la viabilidad de tiempo real. No presupone que el pipeline completo funcione en un ordenador personal. El trabajo gráfico manual no forma parte del objetivo.

[Arquitectura y próximos hitos](PLAN.md).

## Revisar la muestra local

```sh
# Consulta tamaños sin descargar vídeos completos; obtiene metadatos parciales del ZIP.
python3 muestra_videos.py
# Descarga únicamente los vídeos de los tres candidatos, con presupuesto de transferencia.
python3 muestra_videos.py --descargar --max-mb 100
python3 crear_revision.py
```

Abrir `outputs/VALIDAR.html` en el navegador. Los vídeos, traducciones extraídas y la página de revisión permanecen locales e ignorados por Git. Los tres originales no tienen pista de audio; la traducción se muestra por escrito. La página no valida comprensión ni genera vídeo: permite reproducir intervalos y ampliar contexto. No ha sido comprobada en un navegador automatizado.

El descargador exige HTTP Range y un máximo de tres vídeos. Reutiliza archivos locales solo si coinciden con tamaño y CRC de la entrada remota; no descarga el corpus completo como alternativa si falla. Verifica las entradas extraídas, no el MD5 de todo el ZIP de vídeos. `datos/descarga-muestra.json` registra procedencia, SHA-256 y transferencia de la última ejecución; no representa necesariamente el total acumulado de reintentos.

```sh
python3 -m unittest discover -s . -p 'test_*.py' -q
```

## Representación intermedia de la evidencia

```sh
python3 contrato_lse.py
```

Genera tres paquetes locales en `datos/contratos/`, con traducción, intervalos, glosas/variantes presentes y campos de movimiento explícitamente ausentes. Comprueba integridad y correspondencia con la fuente; no crea signos nuevos ni ejecuta modelos.

Formato, límites y resultado de la muestra: [CONTRATO.md](CONTRATO.md). No confundir observaciones estructuradas con una traducción o secuencia de movimientos validada.

## Primera extracción de manos, rostro y cuerpo

Se ejecutó una muestra CPU de 5,8 segundos: 29 fotogramas con resultados y pérdidas explícitas. La vista local está en `outputs/movimiento/VALIDAR.html`. Muestra el original con puntos superpuestos, no un signante sintético. El código no asume que detectar puntos valide la LSE.

[Resultado, límites, requisitos y reproducción](MOVIMIENTO.md). Los modelos están fuera del repositorio; vídeos, puntos y vistas siguen excluidos de Git.
