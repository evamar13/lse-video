# Datos y referencias

## Incorporación práctica — 26 de noviembre de 2026

Eva autoriza aprovechar los recursos reutilizables. La autorización no sustituye los permisos de sus titulares. No se inicia entrenamiento ni descarga masiva.

### BancoLSE: referencia educativa no comercial incorporada

[Condiciones específicas de Fundación CNSE](https://www.fundacioncnse.org/educa/bancolse/condiciones-de-uso.php): recursos [CC BY-NC-SA 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/). Permite compartir y adaptar con atribución, uso no comercial y compartir igual en las adaptaciones distribuidas. Conservar fuente, titular, licencia y modificaciones. El aviso legal general contiene restricciones distintas; las condiciones específicas y el pie de la web identifican expresamente estos recursos como CC. Archivar la evidencia aplicada a cada muestra.

`preparar_bancolse.py` incorpora seis PNG originales: fotografía y dibujo de las entradas hola, gracias y por favor, sin modificaciones. Descarga secuencial, tres entradas fijas, presupuesto de 20 MiB y SHA-256 por recurso. Comprueba la declaración de licencia esperada antes de obtener las imágenes. No usa IA ni extrae movimientos. Datos, fichas, condiciones e inventario permanecen locales en `datos/bancolse/`; galería en `outputs/bancolse/VALIDAR.html`. No se publican recursos de terceros en GitHub.

Las imágenes sirven como referencia léxica, no como trayectorias completas o gramática de frases. Este uso educativo no comercial no acredita autorización para cualquier entrenamiento, publicación de pesos, clonación de apariencia o explotación en Twitch monetizado. Revisar cada operación antes de realizarla. El código propio permanece separado bajo MIT.

### DILSE: candidato pendiente

[DILSE](https://fundacioncnse-dilse.org/): los textos aportados y el aviso legado presentan diferencias sobre adaptación y distribución. No se incorpora como corpus. No extender la licencia de BancoLSE a otro servicio de la misma entidad.

### YouTube: candidato pendiente

[Personas sordas y lengua de signos](https://www.youtube.com/watch?v=JOpFHf5efe0), I.E.S. Victoria Kent. Título/canal confirmados por oEmbed; licencia, contenido audiovisual completo, permisos de imagen y alineación no comprobados. No descargado ni utilizado para extracción o entrenamiento. [Tipos de licencia de YouTube](https://support.google.com/youtube/answer/2797468?hl=es): la licencia estándar no concede reutilización general. Si se verifica CC BY, registrar versión y procedencia; no presumir excepciones legales por estar publicado en YouTube.

### Complementariedad

- UVigo: ejemplos continuos con traducción alineada y extracción técnica experimental ya realizada; condiciones no comerciales propias.
- BancoLSE: referencia visual de vocabulario.
- Cervantes, DILSE y YouTube: candidatos documentados, pendientes de comprobar derechos y correspondencia lingüística antes de incorporarlos como corpus.

No unificar licencias incompatibles ni presentar la colección como dataset validado. Etiqueta léxica, traducción de una frase y descripción generada por IA son evidencias distintas.

Consultadas durante la investigación del 25–26 de noviembre de 2026. Las fuentes evolucionan; fijar versiones y revisar condiciones antes de reutilizar recursos.

## Corpus de referencia

**LSE-Health-UVigo**, Alba-Castro, José L. y colaboradores (2023), versión preliminar: [registro y archivos](https://zenodo.org/records/10234465), DOI 10.5281/zenodo.10234465. Autores, afiliaciones y atribución completa en el registro original.

La [ficha institucional de la Universidade de Vigo](https://portalcientifico.uvigo.gal/documentos/668fc42bb9e7c03b01bd5792?lang=es) indica CC BY-NC 4.0. Incluye vídeos de LSE sobre salud y traducciones al castellano alineadas. Se usa como referencia para un experimento no comercial. Ni el corpus ni sus anotaciones están incluidos en este repositorio.

El auditor acepta el archivo `ELAN-LSE-Health-UVigo.zip` con MD5 publicado `c3ca411d1ec24c4d4c39c250a60903da`. Es una comprobación de integridad/versionado, no una auditoría de derechos o exactitud lingüística. Si cambia la versión, revisar el cambio antes de modificar el valor.

Que los datos estén disponibles no implica que se pueda redistribuir cualquier derivado o comercializar el resultado sin revisar sus condiciones. No asumir que extraer poses elimina derechos sobre el material de origen.

## Candidatos técnicos, sin integración todavía

- [Pose-to-Video](https://github.com/sign-language-processing/pose-to-video): generación de vídeo a partir de poses. Revisar por separado código, pesos y recursos.
- [Performs](https://github.com/upf-gti/performs): animación controlada de avatares; sucesor de trabajo realizado en SignON.
- [Animics](https://github.com/upf-gti/animics): preparación/edición de animaciones.
- [Fuente de navegador en OBS](https://obsproject.com/kb/browser-source): posible salida para el prototipo.
- [Twitch Extensions](https://dev.twitch.tv/docs/extensions/): posible integración posterior, con sus requisitos de desarrollo y revisión.

Código, datos, pesos y apariencia de personas requieren revisiones independientes. No se afirma equivalencia funcional con productos comerciales ni colaboración con las entidades citadas.

## Biblioteca Virtual Miguel de Cervantes — candidata, no incorporada al entrenamiento

Fuente aportada por Eva y revisada el 26 de noviembre de 2026: [obras por materia LSE](https://www.cervantesvirtual.com/obras/materia/lengua-de-signos-espanola-77). En la consulta figuraban 107 registros, 106 etiquetados como vídeo signado. Son registros de catálogo, no un recuento verificado de vídeos únicos descargables. No se ha recorrido ni auditado toda la colección.

La muestra consultada incluye ponencias y literatura signada. Podría ampliar temas y estilos respecto al corpus sanitario. Esa utilidad es una hipótesis; no se ha medido cobertura ni calidad audiovisual.

Ejemplos revisados por sus páginas y metadatos, sin descargar o reproducir los vídeos completos:

- [Ponencia sobre planificación lingüística de LSE](https://www.cervantesvirtual.com/obra/acciones-orientadas-hacia-una-planificacion-linguistica-de-la-lse-en-espana--0/): registro y visor de vídeo; traducción textual alineada no comprobada.
- [Adaptación del poema Vila de Allariz](https://www.cervantesvirtual.com/obra/adaptacion-del-poema-vila-de-allariz--0/): recurso literario; no asumir equivalencia literal de la adaptación con un texto escrito.
- [Ai flores, ai flores do verde pino](https://www.cervantesvirtual.com/portales/literatura/254153_flores/): página con texto y vídeo enlazado. El texto mostrado no es castellano; la presencia en una materia LSE no acredita un par castellano–LSE alineado.

### Condiciones y trabajo pendiente

El [marco legal](https://www.cervantesvirtual.com/marco-legal/) distingue acceso gratuito de derechos de explotación. Describe usos personales privados y condiciones para otros usos; no se ha identificado una licencia abierta general de entrenamiento aplicable a estos vídeos. No interpretar el carácter abierto de los metadatos del catálogo como permiso sobre las grabaciones. Revisar condiciones específicas y base jurídica del uso previsto antes de incorporar material al entrenamiento o redistribuirlo.

No se han descargado vídeos, creado poses ni entrenado con esta fuente. Se registra como catálogo candidato con derechos pendientes, no como dataset autorizado.

Para decidir su incorporación: comprobar una pequeña muestra por vídeo, lengua del texto, correspondencia de significado, sincronización/subtítulos, visibilidad de manos y rostro, resolución, atribución y permisos. No generar una transcripción por ASR y tratarla como traducción de referencia de LSE sin revisión.

## Ejemplo concreto BVMC.Labs: presentación del diccionario de Pinedo

Registro aportado por Eva: manifestación 242342, ítem 149043, obra 21958 y expresión 169428. [Ficha bibliográfica consultada](https://www.cervantesvirtual.com/obra/diccionario-de-la-lengua-de-signos-espanola-presentacion--0/) y [visor](https://www.cervantesvirtual.com/obra-visor/diccionario-de-la-lengua-de-signos-espanola-presentacion--0/video/). El registro identifica una presentación del diccionario de Félix Jesús Pinedo Peydró, no acredita que incluya todas sus entradas.

El visor enlaza un recurso que responde como vídeo MP4. No se ha reproducido ni descargado el vídeo; audio, resolución, subtítulos, transcripción y alineación no comprobados. Los metadatos aportados describen la obra, no lo que se signa frase a frase.

Las [condiciones específicas de BVMC.Labs](https://data.cervantesvirtual.com/condiciones-de-uso/) publican los metadatos bajo CC0 1.0. Es una confirmación de reutilización de fichas bibliográficas; no extender esa declaración al vídeo enlazado. Los permisos del vídeo siguen pendientes de comprobar.

La [documentación de datos enlazados](https://data.cervantesvirtual.com/datos-enlazados) ofrece RDF y SPARQL. Posible aplicación determinista: inventario de títulos, autores, identificadores, enlaces y estado de derechos. No usar título, resumen o materia como traducción supervisada del vídeo. Para entrenar traducción hacen falta parejas de segmentos de LSE y su significado en castellano, revisadas y alineadas.
