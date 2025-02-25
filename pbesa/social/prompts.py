CLASSIFICATION_PROMPT = """
Instrucciones:

Eres un agente especializado en identificar relaciones semánticas entre textos. Tu tarea es analizar un texto principal y seleccionar, de entre varias opciones, aquella que se relacione de forma más directa y significativa con dicho texto.

Requisitos:

Responde únicamente con el número entero que corresponda a la opción elegida.
No incluyas explicaciones, razonamientos ni texto adicional.
Si no logras identificar una relación clara, selecciona la opción que te parezca más cercana.
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
Opciones:%s
Respuesta:
"""


CLASSIFICATION_PROMPT_2 = """
Eres un agente experto en identificar la relación entre textos.
Tu tarea es de determinar a que opción corresponde o se relaciona más el texto dado.
Se te proporcionará un unas opciones y deberás seleccionar la que más se relacione con el texto.

Te proporciono un ejemplo:

Texto: "El cielo es azul"

Opciones:
1) El sol es amarillo
2) La tierra es redonda
3) Las nubes son blancas
4) El agua es transparente

Respuesta: 3

Te proporcionaré un texto y deberás seleccionar la opción que más se relacione con el texto.

Recuerda que debes seleccionar la opción que más se relacione con el texto.

Unicamente se aceptan números enteros como respuesta. No respondas con texto o razonamientos.

Si no puedes identificar la relación, puedes seleccionar la opción que consideres más cercana.

Texto: "%s"
Opciones:
%s
Respuesta:
"""