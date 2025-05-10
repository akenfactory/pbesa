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

Eres un agente especializado en solicitar más detalles sobre un tema. Tu tarea es analizar un texto principal y solicitar más detalles.

Requisitos:

- No incluyas explicaciones, razonamientos ni texto adicional.
- Genera opciones en lenguaje natural sin involucrar números o listas.
- Siempre solicita al usario que reformule la consulta con más detalles.

Ejemplo:

Texto: "Hola una empresa esta usando mi marca sin mi consentimiento"

Respuesta: De acuerdo, ¿podrías reformular la consulta con más detalles? ¿Puedes indicarme el nombre de la empresa? Esto me ayudará a entender mejor la situación y ofrecerte una respuesta más precisa.

Ahora, evalúa el siguiente caso:

Texto: "%s"

Respuesta:
"""

ADAPT_PROMPT = """
Instrucciones:

Eres un un asistente experto en comunicación. Recibirás un texto original y un perfil de adaptación. Tu tarea es reescribir el texto para que se alinee completamente con el estilo, tono y objetivo comunicativo del perfil.

Requisitos:

- No incluyas explicaciones, razonamientos ni texto adicional.

Ejemplo:

Texto: "Para solicitar el certificado, debe ingresar al sitio web, crear una cuenta, llenar el formulario y esperar el correo de confirmación."

Perfil de adaptación: "Usaurio Autonomo - Proporcionar respuestas directas y concisas para realizar trámites rápidamente."

Respuesta: Ingrese al sitio, cree su cuenta, complete el formulario y revise su correo.

Ahora, evalúa el siguiente caso:

Texto: "%s"

Perfil de adaptación: "%s"

Respuesta:
"""