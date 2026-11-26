# Instrucciones del proyecto

- Mantener separados reproducción visual, traducción lingüística y emisión en directo. Describir únicamente capacidades verificadas.
- Empezar por una muestra offline pequeña. No iniciar entrenamientos ni descargar corpus completos por defecto.
- No versionar datos de terceros, vídeos, traducciones del corpus, fotografías personales, pesos ni credenciales. Revisar licencia/consentimiento y atribución antes de cualquier publicación de derivados.
- Conservar referencias y fuentes originales. No convertir detección de poses en una garantía de corrección de LSE.
- Requerir evaluación de comprensión con personas sordas signantes y especialistas antes de declarar accesibilidad validada.
- Procesos secuenciales y GPU de IA desactivada por defecto. No activar servicios pagados automáticamente; medir recursos y registrar uso real cuando haya inferencia.
- El auditor actual es un script determinista, no un agente autónomo ni un modelo de traducción.

- Seguir ARQUITECTURA.md: voz castellana → texto → plan lingüístico LSE → movimientos → vídeo. Boca y rostro siguen la LSE, no el audio castellano fonema a fonema. No usar un diccionario como traductor de frases.
- Eva revisa apariencia y uso, no corrección lingüística. Mantener esa revisión separada de la de personas competentes en LSE.

## Directo y presupuesto

Eva quiere mantenerse sin gasto en la prueba de vídeo. No alquilar GPU, comprar créditos, activar planes de pago o recurrir a servicios facturables automáticamente. No usar IA pesada local para sustituir un coste remoto sin respetar el confort del Mac. Seguir DIRECTO.md: Twitch requiere estudiar animación interactiva de una representación preparada, no generar vídeos por difusión a cada intervención. La prueba de apariencia offline no demuestra viabilidad en directo. Foto personalizada y movimientos correctos son criterios independientes; no prometer su combinación sin ensayo. No subir fotos ni corpus a un servicio gratuito por suponer que eso está autorizado.

## Preparación habitual de fotos (preferencia de Eva)

Revisión visual vigente: Eva rechazó el prototipo Canvas de figuras geométricas (cuello y manos artificiales). Es prueba interna de controles, no acabado aceptado. No continuar esa estética ni usar los tests geométricos como aprobación visual. Antes de extender otra implementación, validar un gesto corto con base corporal/manos realistas y proporciones estables. Mantener la salida 2D personalizable y evitar trabajo gráfico manual para la persona.

Seguir AVATAR_MODULAR.md: manos/brazos y estructura de cuerpo reutilizables, color/proporciones/ropa adaptables y cara/cuello personalizados. Preparar apariencia una vez y animar controles compartidos en directo. No impulsar difusión de vídeo como ruta de Twitch. No sustituir la salida fotográfica/2D por una estética 3D visible ni exigir trabajo gráfico manual a la persona. Boca/expresiones requieren controles LSE, y la adaptación de proporciones debe preservar contactos; no tratarlos como problemas ya resueltos.

Aceptar fotos cotidianas y preparar la referencia como parte del proceso, siguiendo PREPARACION_FOTOS.md. No exigir una foto perfecta. Revisar primero; reutilizar si sirve y usar imagegen para adaptar cuando haga falta, sin cargar IA local por defecto. Conservar identidad, original y versiones; señalar regiones reconstruidas. Máximo dos candidatas por caso, sin regeneración en cada vídeo. Solicitar revisión de apariencia antes de animar y no confundirla con validación de LSE. Usar preparar_referencia.py para los nuevos casos y resolver_referencia() para obtener la candidata aceptada. Nunca marcar una aceptación del usuario por suposición. El flujo asistido no equivale a una aplicación automática desplegada.

## Datos privados (26 de noviembre de 2026)

Eva autoriza ampliar fuentes para análisis de datos exclusivamente local, sin publicar materiales, transcripciones, coordenadas ni derivados y cumpliendo derechos y acceso. Esta autorización no sustituye permisos de terceros. Preferir licencias explícitas; no dar por aplicable automáticamente la excepción de minería ni equiparar acceso público a dominio público. Registrar condiciones por fuente y distinguir muestras incorporadas de candidatos. No transmitir el corpus a APIs externas ni incorporarlo a GitHub. No iniciar entrenamientos o descargas masivas como consecuencia de esta autorización. Usar muestras acotadas, respetar controles de recursos y mantener en espera accesos con login o derechos no resueltos.
