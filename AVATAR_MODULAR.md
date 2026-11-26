# Avatar modular: preparar apariencia una vez y animar controles compartidos

Dirección preferida por Eva, 26 de noviembre de 2026. Mantener salida 2D de apariencia personalizable y evitar generación de vídeo por difusión en cada intervención. Esta arquitectura está definida, no implementada como avatar completo.

## Componentes

| Parte | Compartido entre personas | Adaptación al crear la referencia |
|---|---|---|
| Manos y brazos | Topología, articulaciones, límites y repertorio de movimientos | Color/material, escala y longitudes compatibles con el resto del cuerpo |
| Tronco y ropa | Estructura deformable y puntos de anclaje | Proporciones visibles, silueta, apariencia de ropa y textura de la foto preparada |
| Cara, pelo y cuello | Estructura de deformación y catálogo de controles | Rasgos visibles y texturas personales; ajuste de uniones y zonas reconstruidas |
| Movimiento | Formato de instrucciones, reloj, transiciones y canales | Transferencia al cuerpo ajustado, preservando contactos y posiciones relativas |

La geometría base de manos y cuerpo puede reutilizarse. No se necesita reconstruir las manos reales de cada persona para expresar signos, ni afirmar que esas manos genéricas son su anatomía verdadera. El color de piel se estima para la apariencia, corrigiendo luz/sombras y permitiendo ajuste: el color de la cara no es una medida exacta del de brazos/manos.

Al cambiar proporciones no basta con escalar cada pieza independientemente: recalcular alcance, posición de manos respecto a cara/cuerpo y contactos entre dedos o manos. La animación debe conservar la intención de esas restricciones al adaptarse al avatar.

## Alta de una persona

Foto cotidiana autorizada → revisión y preparación con IA si hace falta → referencia frontal → separación/ajuste de módulos y texturas → ajuste de proporciones visibles y anclajes → inspección de uniones, manos y expresiones → aceptación de apariencia → referencia animable reutilizable.

La preparación de foto sigue PREPARACION_FOTOS.md. La segmentación automática, rig compartido, ajuste de texturas y deformación facial están pendientes; no se atribuyen al gestor de fotos ya implementado. Usar IA para reconstruir zonas ocultas una vez cuando resulte útil, no en cada frase. Si una foto no aporta identidad suficiente, pedir otra toma concreta.

No exigir a la persona modelado manual, recorte de capas o uso de Blender. Es trabajo de integración del producto; el repertorio de movimientos y las plantillas se crean una vez. Tampoco prometer que cualquier foto pueda repararse conservando el parecido.

## Durante el directo

Voz o texto → interpretación LSE con contexto → plan de movimiento → controles de manos, brazos, torso, mirada, cabeza, cejas y boca → deformación de las piezas preparadas → imagen para OBS.

Se actualiza la imagen en cada fotograma, como en una animación convencional. Lo que se evita es volver a generar el aspecto de la persona mediante un modelo de vídeo para cada fotograma o intervención. Medir carga, memoria y latencia; el coste gráfico, reconocimiento de voz y traducción no desaparecen.

La cara no es un recorte estático colocado detrás del cuerpo. Necesita deformación coherente de boca, labios, ojos, cejas, mejillas y cabeza. Mostrar dientes/interior de boca, giros y superficies ocultas puede necesitar recursos adicionales preparados. La foto frontal inicial no contiene esos datos. Establecer límites de giro en la primera prueba y comunicar sus carencias.

Los movimientos faciales los manda el plan LSE; un detector facial no los decide por sí solo. No sincronizar toda la boca con fonemas castellanos ni copiar cualquier sonrisa por estética. Coordinar cara, cabeza y manos con el mismo reloj.

Las manos pueden pasar delante de cara y cuello. Resolver visibilidad y oclusión con capas dinámicas o geometría interna adecuada; un orden fijo «cara siempre detrás» daría errores. No derivar profundidad métrica fiable de las coordenadas crudas de grupos distintos.

## Componentes abiertos para evaluar

- [Inochi2D](https://github.com/inochi2d/inochi2d): deformación de mallas 2D a partir de arte en capas y parámetros; BSD-2-Clause. Candidato de motor, no preparador automático de fotos ni sistema LSE. Reutilizarlo no elimina la preparación de piezas y controles.
- [Performs](https://github.com/upf-gti/performs): animación manual/no manual mediante instrucciones y avatares preparados; MIT. Referencia para controles y ejecución. No aporta por sí mismo personalización fotográfica, traducción castellano–LSE ni la estética final solicitada. No importar su diccionario NGT como LSE.
- [MediaPipe Face Landmarker](https://developers.google.com/edge/mediapipe/solutions/vision/face_landmarker): puntos faciales, coeficientes de expresión y matrices; puede ayudar a preparar/observar una cara. No transforma automáticamente una foto en un rostro animable ni convierte coeficientes en gramática de LSE. Código, pesos y recursos se revisan por separado.
- [MPFB](https://github.com/makehumancommunity/mpfb2): generador humano para Blender, candidato secundario de plantilla interna si hace falta geometría. No se instala ni convierte Blender en requisito de usuario; revisar licencias de código y activos por separado.

Priorizar una prueba de representación plana o híbrida que conserve la apariencia. Una estructura 3D interna es una opción técnica para orientación/oclusiones, no una decisión de mostrar un personaje de estética 3D ni una elección de motor ya hecha.

## Ensayo de aceptación siguiente

Una misma plantilla de manos/brazos y tronco con dos configuraciones de apariencia, inicialmente sintéticas, sin duplicar el repertorio de movimiento. Comprobar cambio de proporciones, contacto mano-cara, cruce de manos, pérdida de visibilidad, apertura/cierre de boca y cejas. Integrar después la referencia personal aceptada. Esta prueba no traduce voz ni acredita comprensión en LSE.

Para avanzar: comparar original, controles y resultado; medir tiempo de preparación por foto, latencia gráfica, carga del equipo, errores visibles, identidad y comprensión por separado. Mantener gasto cero, archivos privados y ausencia de modelos pesados simultáneos. No iniciar inferencias, instalar motores o alquilar GPU por aprobar esta dirección.
