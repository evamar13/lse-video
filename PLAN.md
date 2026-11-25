# Arquitectura y criterios de avance

## Objetivo

Castellano hablado → traducción a LSE → movimiento de manos, rostro y cuerpo → vídeo fotorrealista → OBS/Twitch. Se investiga una apariencia personalizable; no se promete que una fotografía baste.

## Primera etapa: reproducción offline

Entrada: una secuencia real de LSE con traducción y tiempos, usada conforme a sus permisos. Salida prevista: un comparador de original, movimiento estimado y vídeo generado con identidad fija.

- Tres fragmentos revisados, con contexto suficiente y manos/rostro visibles. Los tres primeros del auditor no son una selección validada.
- Registro de procedencia, licencia, versión, intervalo temporal y atribución.
- Medir defectos de dedos, orientación, contactos, expresión facial, continuidad e identidad. La coincidencia de puntos no reemplaza la revisión de comprensión.
- No desplegar un resultado como accesibilidad validada sin evaluación con personas sordas signantes y especialistas de LSE.

## Componentes por evaluar

- Extracción de poses: por seleccionar, incluyendo manos y rostro; las estimaciones pueden fallar.
- Generación de vídeo: Pose-to-Video es candidato, no dependencia validada. Auditar licencias de código, pesos, requisitos y control de identidad antes de instalar.
- Performs/Animics: opcionales para preparar o inspeccionar movimiento; no resuelven la traducción castellano→LSE por sí solos. Ningún personaje 3D visible es obligatorio en la salida.
- Revisión: interfaz o informe comparativo offline, todavía no implementado.

## Etapas posteriores

1. Probar cambio de identidad manteniendo una secuencia validada. Consentimiento y condiciones de uso de la imagen antes de tratar fotografías.
2. Investigar traducción castellano→LSE en dominio acotado con evaluación separada por signantes y contenidos. Datos de salud no equivalen a vocabulario suficiente para directos generales.
3. Capturar audio autorizado del emisor y mostrar la salida mediante una fuente de navegador de OBS. La API de Twitch no se supone una fuente general de audio de un directo.
4. Medir sincronización, latencia y consumo antes de plantear una extensión de Twitch o entrenamiento más amplio.

## Límites operativos

Procesamiento secuencial, etapas acotadas y GPU de IA desactivada por defecto. No se inicia entrenamiento, descarga masiva o cómputo remoto de pago automáticamente. Comprobar recursos y presupuesto antes de ejecutar modelos. El renderizado también consume recursos y debe medirse por separado.

Registrar proyecto/tarea/ejecutor y contadores reales cuando se incorporen llamadas de IA. Contadores ausentes son desconocidos, no cero. El auditor actual no hace inferencias. No anunciar ahorro sin comparación ni presentar simulaciones como resultados reales.

## Estado

Implementado: auditor, descarga parcial de tres vídeos originales, página local para revisar intervalos y traducciones, y documentación. Pendiente: revisión visual y lingüística de la selección, extracción de poses, generador, comparador de resultados, evaluación de comprensión e integración OBS/Twitch.
