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

## Datos privados (26 de noviembre de 2026)

Eva autoriza ampliar fuentes para análisis de datos exclusivamente local, sin publicar materiales, transcripciones, coordenadas ni derivados y cumpliendo derechos y acceso. Esta autorización no sustituye permisos de terceros. Preferir licencias explícitas; no dar por aplicable automáticamente la excepción de minería ni equiparar acceso público a dominio público. Registrar condiciones por fuente y distinguir muestras incorporadas de candidatos. No transmitir el corpus a APIs externas ni incorporarlo a GitHub. No iniciar entrenamientos o descargas masivas como consecuencia de esta autorización. Usar muestras acotadas, respetar controles de recursos y mantener en espera accesos con login o derechos no resueltos.
