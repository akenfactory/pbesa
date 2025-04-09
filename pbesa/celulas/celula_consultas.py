import logging

PROMPT = """
Eres un clasificador de intenciones. Tu tarea es analizar el siguiente texto y determinar si representa una **pregunta** o **solicitud de información**.

Responde solo con:
- PREGUNTA_O_SOLICITUD
- NO_PREGUNTA

**Definiciones:**
- **PREGUNTA_O_SOLICITUD**: El texto expresa claramente una intención de obtener información, ya sea mediante una pregunta directa ("¿Qué hora es?") o una solicitud indirecta ("Quisiera saber el estado del pedido").
- **NO_PREGUNTA**: El texto no busca información. Puede ser un saludo, afirmación, comentario, instrucción, etc.

**Ejemplos:**
1. "¿Cuál es el horario de atención?" → PREGUNTA_O_SOLICITUD  
2. "Necesito saber cómo ingresar al sistema" → PREGUNTA_O_SOLICITUD  
3. "Hola, buen día" → NO_PREGUNTA  
4. "Ya envié el informe" → NO_PREGUNTA  
5. "¿Me puedes confirmar la dirección?" → PREGUNTA_O_SOLICITUD  
6. "Saludos" → NO_PREGUNTA  
7. "Explícame cómo hacerlo" → PREGUNTA_O_SOLICITUD  
8. "No tengo acceso" → NO_PREGUNTA

Texto: "%s"

Clasificación:
"""

# Efectua la inferencia del modelo.
def derive(service, text) -> any:
    try:
        logging.info(f"Procesando: {text}")
        tmp_work_memory = []
        prompt  = PROMPT % text
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
