import logging

PROMPT = """
Eres un asistente jurídico experto. Tu tarea es **extraer los datos** y generar el documento siguiendo una plantilla predefinida.

Recibirás un texto que incluye:
- Un relato de hechos sobre una posible infracción
- Datos personales del demandante y del demandado (pueden venir con nombre de campo o en texto libre)
- Información de contacto
- Algunas veces: el nombre de la entidad ante la cual se presenta la demanda

Usa el siguiente formato para estructurar tu respuesta. Si hay datos que no se encuentran, déjalos como estan en el formato.

---

%s

---
"""

# Efectua la inferencia del modelo.
def derive(service, formato, text, max_tkns=4096) -> any:
    try:
        logging.info(f"Procesando: {text}")
        tmp_work_memory = []
        user_prompt  = """
        TEXTO DE ENTRADA:
        %s
        ---

        DEMANDA FORMATEADA:
        """ % text
        tmp_work_memory.append({"role": "system", "content": PROMPT % formato})
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
