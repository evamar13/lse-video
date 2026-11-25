# Contrato intermedio 0.1 — observaciones de LSE

Implementación: `contrato_lse.py`, biblioteca estándar de Python. Esta versión organiza evidencia existente: no convierte castellano a LSE, no produce un plan lingüístico nuevo ni genera coordenadas. Es un formato interno del proyecto, no un estándar lingüístico externo.

## Bloques

| Campo | Contenido y significado |
|---|---|
| `schema_version`, `kind` | `0.1`, `observed_lse_segment`. Otros tipos/versiones se rechazan. |
| `evidence` | Dataset, fuente, licencia, SHA-256 del ZIP de anotaciones, archivo ELAN, ID e intervalo original. |
| `input` | Texto de referencia del corpus, etiqueta castellano `es-ES`, procedencia `corpus_translation_of_lse_not_asr` y audio desconocido/no aportado como `null`. No implica que se haya validado una variedad oral. |
| `linguistic` | Glosas que realmente aparecen anotadas dentro del intervalo y sus variantes vinculadas. Cobertura parcial explícita; espacio y elementos no manuales quedan `null`. |
| `motion` | Estado `unavailable`, sin coordenadas ni fotogramas; lista de canales que faltan. |
| `review` | Revisión lingüística pendiente, revisión técnica limitada a metadatos; no está listo para traducir ni renderizar. |

## Tiempo y recortes

Los tiempos de evidencia son milisegundos absolutos en el vídeo fuente. Los de cada glosa son relativos al inicio del fragmento; se conservan además los originales. Si una glosa atraviesa el límite, se marca `clipped`. Una glosa que solo toca un extremo sin solapamiento se excluye. Ese recorte no se interpreta como un signo completo.

El adaptador conserva las variantes de la capa VAR vinculadas por `ANNOTATION_REF`. Referencias que no sabe resolver producen error, no desaparición silenciosa. La traducción y tiempos de la preselección deben coincidir con la anotación original.

## Campos ausentes

Las capas inspeccionadas aportan etiquetas, traducciones y tiempos, no articulaciones. Las coordenadas, orientaciones, contactos, trayectorias, mirada, cejas y boca requieren evidencia adicional. No inventar esos valores ni considerar una glosa un movimiento completo.

La versión 0.1 rechaza paquetes que afirmen estar revisados, listos para renderizar o contener movimiento. Un contrato futuro para planes y secuencias deberá versionarse y tener su propia validación. `validate()` comprueba invariantes de esta estructura interna; no sustituye una auditoría lingüística ni es un validador genérico de cualquier JSON.

## Ejecutar

Con las anotaciones y auditoría obtenidas por el procedimiento del README:

```sh
python3 contrato_lse.py
python3 -m unittest discover -s . -p 'test_*.py' -q
```

Las observaciones y el inventario se escriben en `datos/contratos/`, fuera de Git. El código y las pruebas usan únicamente fixtures sintéticos cuando se ejecuta la suite; no publican traducciones del corpus. No hay descargas ni llamadas a modelos en este exportador.

## Resultado de la muestra actual

Tres fragmentos exportados y validados estructuralmente. Sus intervalos contienen respectivamente 0, 1 y 4 glosas anotadas y una variante en el tercero. Esto refleja el repertorio selectivo anotado del corpus: no prueba que el primer fragmento carezca de signos ni que los otros estén completamente anotados.

No hay coordenadas de dedos o boca ni revisión de comprensión. Es un inventario de evidencia, no un resultado del traductor.

## Siguiente implementación

Ya se ha probado extracción CPU de un fragmento corto: ver [MOVIMIENTO.md](MOVIMIENTO.md). El contrato 0.1 de observaciones ELAN no cambia sus campos vacíos: el movimiento estimado se guarda aparte y no se convierte automáticamente en un plan revisado. Definir articulaciones, unidades, coordenadas y canales faciales antes de convertir su salida. Mantener separado el movimiento estimado de un plan lingüístico revisado. El generador fotorrealista seguirá pendiente hasta disponer de una secuencia comprobable.
