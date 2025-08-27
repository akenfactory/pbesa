import logging

PROMPT = """
Eres un asistente jurídico experto. Tu tarea es analizar el caso que se te pŕesenta y generar una recomendación de que material probatorio se debe adjuntar.

Recibirás un texto que incluye:
- Un relato de la situación

Respuesta esperada:
- Una recomendación no mayor a 80 palabras del material probatorio que se debe adjuntar

---
"""

# Efectua la inferencia del modelo.
def derive(service, text, max_tkns=2000) -> any:
    try:
        logging.info(f"Procesando: {text}")
        tmp_work_memory = []
        user_prompt  = """
        CASO:
        %s
        ---

        RESPUESTA:
        """ % text
        tmp_work_memory.append({"role": "system", "content": PROMPT})
        tmp_work_memory.append({"role": "user", "content": user_prompt})
        res = service.generate(tmp_work_memory, max_tokens=max_tkns)
        logging.info(f"Respuesta: {res}")
        if not res or res == "":
            res = text
            logging.warning(f"No obtener una respuesta.")
        return res
    except Exception as e:
        logging.error(f"Error al procesar: {text}")
        logging.error(e)
        return None
