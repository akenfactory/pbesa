import logging

PROMPT = """
Eres un clasificador de saludos. Tu tarea es analizar el siguiente texto y determinar si es un saludo.

Responde únicamente con una de estas opciones:
- SALUDO
- NO_SALUDO

**Definición de saludo**: Un saludo es cualquier forma de cortesía o expresión inicial utilizada para iniciar una conversación. Esto incluye "Hola", "Buenos días", "Qué tal", "Ey", "Saludos", etc., incluso si van acompañados de una pregunta o comentario breve. No se consideran saludos las preguntas o afirmaciones que van directo al contenido sin intención de cortesía.

Ejemplos:
- "Hola, ¿cómo estás?" → SALUDO
- "Buenos días, equipo" → SALUDO
- "¿Cómo se hace este análisis?" → NO_SALUDO
- "Ey, qué más" → SALUDO
- "Necesito ayuda con el código" → NO_SALUDO
- "Saludos" → SALUDO

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
        logging.info(f"[Celula][Saludos][Respuesta]: {res}")
        if not res or res == "":
            res = text
            logging.warning(f"[Celula][Saludos]: No obtener una respuesta.")
        return res
    except Exception as e:
        logging.error(f"[Celula][Saludos]: Error al procesar: {text}")
        logging.error(e)
        return None
