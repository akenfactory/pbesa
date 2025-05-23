import logging

PROMPT = """
Eres un clasificador de preguntas. Tu tarea es analizar el siguiente texto y determinar si contiene preguntas.

Responde únicamente con una de estas opciones:
- CONTIENE
- NO_CONTIENE

**Definición de pregunta**: Una pregunta es una expresión que busca obtener información o aclaración sobre un tema específico. Esto incluye preguntas directas, indirectas y retóricas. No se consideran preguntas las afirmaciones o comentarios que no buscan respuesta.

Ejemplos:
- "Hola, ¿cómo estás?" → CONTIENE
- "Buenos días, equipo" → NO_CONTIENE
- "¿Cómo se hace este análisis?" → CONTIENE
- "Ey, qué más" → NO_CONTIENE
- "Necesito ayuda con el código" → NO_CONTIENE
- "Saludos" → NO_CONTIENE

---
"""

# Efectua la inferencia del modelo.
def derive(service, text, max_tkns=4096) -> any:
    try:
        logging.info(f"Procesando: {text}")
        tmp_work_memory = []
        user_prompt  = """
        Texto: "%s"

        Clasificación:
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
