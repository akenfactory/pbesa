CLASSIFICATION_PROMPT = """
Instrucciones:

Eres un agente especializado en identificar relaciones semánticas entre textos. Tu tarea es analizar un texto principal y seleccionar, de entre varias opciones, aquella que se relacione de forma más directa y significativa con dicho texto.

Requisitos:

Responde únicamente con el número entero que corresponda a la opción elegida.
No incluyas explicaciones, razonamientos ni texto adicional.
Si no logras identificar una relación clara, responde con el número 0.
Ejemplo:

Texto: "El cielo es azul"

Opciones:

1) El sol es amarillo
2) La tierra es redonda
3) Las nubes son blancas
4) El agua es transparente

Respuesta: 3

Ahora, evalúa el siguiente caso:

Texto: "%s"
Opciones:
%s
Respuesta:
"""

DERIVE_PROMPT = """
A partir de la siguiente información: "%s".

Ahora, evalúa el siguiente caso:

Texto: "%s"

Respuesta:
"""

RECOVERY_PROMPT = """
Instrucciones:

Eres un agente especializado en parafrasear. Tu tarea es analizar un texto principal y parafrasearlo generando opciones al usuario.

Requisitos:

- No incluyas explicaciones, razonamientos ni texto adicional.
- Genera opciones en lenguaje natural sin involucrar números o listas.
- Si no logras parafrasear el texto principal, responde solicitando más información.

Ejemplo:

Texto: "Hola mi caso esta relacionado con la Superfinanciera"

Respuesta: Perdona, tu solicitud ¿Es sobre la Superintendencia Financiera de Colombia o sobre la Superintendencia de Sociedades?

Ahora, evalúa el siguiente caso:

Texto: "%s"

Respuesta:
"""