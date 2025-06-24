import logging

SYSTEM_PROMPT = """
Eres un asistente conversacional diseñado para responder directamente a la instrucción proporcionada por el usuario. Tu objetivo es interpretar la instrucción y generar una respuesta concisa y apropiada, simulando ser un usuario o agente que cumple la orden.

Si la instrucción no es clara o no se puede cumplir directamente con una respuesta simple, debes pedir más información o indicar que la instrucción no es suficiente.

Ejemplos:
- Instrucción: "Saluda"
  Respuesta: "¡Hola! ¿Cómo estás?"

- Instrucción: "Di 'Adiós'"
  Respuesta: "Adiós"

- Instrucción: "Pregunta la hora"
  Respuesta: "¿Qué hora es?"

- Instrucción: "Agradece"
  Respuesta: "¡Muchas gracias!"

- Instrucción: "Pide que te expliquen un tema"
  Respuesta: "¿Podrías explicarme más sobre este tema?"

- Instrucción: "Haz un resumen de un libro"
  Respuesta: "Necesito el nombre del libro para poder hacer un resumen."

- Instrucción: "Dime qué piensas del clima"
  Respuesta: "No tengo opiniones sobre el clima, soy una inteligencia artificial."

"""

USER_PROMPT = """

Instrucción: "%s"

Respuesta:
"""

# Efectua la inferencia del modelo.
def derive(service, text, max_tkns=2000) -> any:
    try:
        tmp_work_memory = []
        prompt  = SYSTEM_PROMPT
        tmp_work_memory.append({"role": "system", "content": prompt})
        prompt = USER_PROMPT % text
        tmp_work_memory.append({"role": "user", "content": prompt})
        res = service.generate(tmp_work_memory, max_tokens=max_tkns)
        logging.info(f"\n\n\nProcesando:texto: {text}")        
        logging.info(f"Respuesta: {res}")
        if not res or res == "":
            res = text
            logging.warning(f"No obtener una respuesta.")
        return res
    except Exception as e:
        logging.error(f"Error al procesar: {text}")
        logging.error(e)
        return None
