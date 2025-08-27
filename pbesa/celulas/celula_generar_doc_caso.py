import logging

PROMPT = """
Eres un asistente jurídico experto. Tu tarea es redactar de una mejor manera y con ortografía el caso que se te presenta.

Recibirás un texto que incluye:
- Un relato de la situación

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
