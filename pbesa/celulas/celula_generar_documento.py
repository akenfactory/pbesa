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

TEXTO DE ENTRADA:
%s

---

DEMANDA FORMATEADA:
"""

# Efectua la inferencia del modelo.
def derive(service, formato, text) -> any:
    try:
        logging.info(f"Procesando: {text}")
        tmp_work_memory = []
        prompt  = PROMPT % (formato, text)
        tmp_work_memory.append({"role": "user", "content": prompt})
        res = service.generate(tmp_work_memory)
        logging.info(f"Respuesta: {res}")
        if not res or res == "":
            res = text
            logging.warning(f"No obtener una respuesta.")
        return res
    except Exception as e:
        logging.error(f"Error al procesar: {text}")
        logging.error(e)
        return None
