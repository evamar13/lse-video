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
