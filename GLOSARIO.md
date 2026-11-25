# Propuesta: glosario de LSE, instrucciones legibles y comandos

Ampliación del diseño planteada el 26 de noviembre de 2026. Este documento es una especificación, no un glosario validado ni un traductor implementado.

## Flujo propuesto

Voz castellana → texto con contexto → IA que propone una interpretación en LSE con explicación en castellano → plan estructurado verificable → compilador de movimientos → generador de persona fotorrealista en vídeo 2D.

La explicación permite inspeccionar qué pretende hacer el sistema. La ejecución necesita además identificadores, unidades, tiempos, referencias y restricciones inequívocos. Una prosa plausible no demuestra que la traducción o la colocación de dedos sea correcta.

## Glosario como base de evidencia

No es una tabla de palabras castellanas con un gesto fijo. Distinguir signos/variantes, construcciones lingüísticas, componentes no manuales y primitivas de movimiento. Las frases requieren organización, espacio, contexto y transiciones que un inventario de signos aislados no proporciona.

Cada entrada propuesta debe describir:

| Bloque | Campos o evidencias |
|---|---|
| Identidad | ID estable, versión, lengua LSE, tipo de entrada y variante cuando se conozca. |
| Significado y uso | Conceptos, contexto, restricciones, referencias espaciales y ejemplos traducidos. No atribuir cobertura universal. |
| Descripción en castellano | Explicación legible de configuración de dedos, mano dominante/no dominante, orientación, ubicación, trayectoria, contactos, rostro y boca. Marcar lo que no se sabe. |
| Realización | Secuencia observada o plantilla de movimiento identificada, parámetros permitidos y referencias de coordenadas/unidades/tiempo. Una descripción no se convierte por sí sola en una trayectoria válida. |
| Fuentes | Diccionario o corpus, versión, vídeo/intervalo, anotación, licencia y condiciones de derivados. No publicar material de terceros por defecto. |
| Revisión | Separar observación, descripción propuesta por IA, corrección técnica y revisión lingüística. Nunca convertir confianza del modelo en aprobación humana. |
| Compilación | Operaciones soportadas, argumentos, límites, canales simultáneos y transiciones. Indicar elementos aún no ejecutables. |

Guardar por separado la descripción original del recurso, una descripción generada por IA y las revisiones. Si una fuente solo aporta el nombre de un signo, no atribuirle una configuración de dedos que no describe.

## Qué decide la IA

Con el texto y contexto del mensaje, recuperar únicamente entradas y ejemplos pertinentes. Proponer cómo expresar su significado en LSE: signos/variantes, organización, loci, direcciones y componentes no manuales. Explicar las elecciones en castellano y citar IDs de evidencia. Puede componer recursos existentes; la composición tampoco se presume lingüísticamente correcta por ser técnicamente ejecutable.

Si faltan recursos, puede elaborar una hipótesis de trabajo con estado de borrador y carencias explícitas, pero no registrarla como signo validado ni inventarle una fuente. Las propuestas no se incorporan automáticamente a las entradas revisadas.

La descripción de boca debe representar los componentes propios de la LSE. No imponerle lectura labial literal del castellano ni inferir una función gramatical solo de los puntos del detector facial.

## Lenguaje natural → comandos

La capa de ejecución debe usar un plan tipado. Opciones a probar: lenguaje natural controlado con gramática y parámetros definidos, o salida conjunta de explicación y plan estructurado. El lenguaje natural libre no se ejecuta directamente.

Para reducir ambigüedad y llamadas, preferir inicialmente una única propuesta de IA con IDs/parámetros estructurados, y producir la descripción ejecutiva legible desde esos mismos campos mediante plantillas. Puede conservarse una explicación libre adicional del razonamiento lingüístico, sin que esa prosa cambie los comandos.

El compilador determinista resolvería IDs de movimientos y parámetros en articulaciones, trayectorias, contactos y canales faciales admitidos. No ejecutaría Python ni JavaScript redactado por el modelo. No requeriría una segunda llamada de IA para convertir una plantilla conocida a comandos.

Expresiones como «mueve un poco la mano» son insuficientes hasta fijar dirección, referencia, amplitud y duración. Si faltan parámetros, referencias o primitivas, devolver un diagnóstico; no completarlos silenciosamente. Mantener separados permisos para visualizar un borrador experimental y la validación necesaria para declarar un servicio accesible fiable.

## Comprobaciones

- Existencia/versionado de IDs y permisos de uso del material asociado.
- Tiempos, unidades, sistema de coordenadas y coherencia de referencias.
- Rangos articulares, continuidad, contactos y sincronización de manos/rostro cuando esos datos estén disponibles. La representación actual de puntos todavía no aporta todo esto.
- Concordancia entre descripción ejecutiva y plan; no permitir dos instrucciones distintas según se lea la prosa o el JSON.
- Fidelidad del vídeo generado al movimiento especificado y comprensión del significado, evaluadas por separado.

Pasar estas comprobaciones técnicas no certifica la lengua. Eva revisa apariencia y experiencia; personas sordas signantes competentes y especialistas revisan comprensión y LSE.

## Reutilizar lo realizado

El contrato 0.1 conserva evidencia ELAN sin inventar movimiento. La extracción CPU conserva posiciones estimadas en un fragmento; todavía no define rotaciones de dedos, contactos o función de la boca. Ambos aportan referencias para documentar las primeras entradas, pero no constituyen automáticamente el glosario descrito aquí.

Empezar con un puñado de entradas sustentadas por la muestra, marcar sus huecos y definir el contrato de planificación/compilación. Elegir un caso descriptivo con cobertura suficiente antes de generar frases nuevas. Conservar vídeos y derivaciones en local según su licencia.

No cargar todos los diccionarios en cada petición. Recuperar solo evidencia relevante, reutilizar plantillas compiladas y registrar modelo/versión y consumo real al incorporar IA. No hay entrenamiento, nueva inferencia ni activación de GPU por esta propuesta.
