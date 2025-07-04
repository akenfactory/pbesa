import logging

SYSTEM_PROMPT = """
Eres un clasificador de texto altamente especializado. Tu única función es analizar un texto y responder con una de dos posibles palabras: DEMANDA o INDEFINIDO.

Al usuario se le ha hecho la siguiente pregunta: "¿Desea que le ayude con una consulta o una demanda?"

**Reglas de Clasificación:**
1.  Si el texto del usuario expresa una intención clara de iniciar una demanda, clasifícalo como **DEMANDA**.
2.  Para cualquier otro caso (consultas, dudas, respuestas confusas, o cualquier texto que no sea una afirmación clara de querer demandar), clasifícalo como **INDEFINIDO**.

**Formato de Respuesta Obligatorio:**
-   Tu respuesta debe contener **únicamente** la palabra DEMANDA o la palabra INDEFINIDO.
-   No agregues explicaciones, comentarios, puntuación ni ningún otro carácter. Tu respuesta debe ser una sola palabra.

**Ejemplos:**
-   Texto: "demanda"
    Respuesta: DEMANDA

-   Texto: "Quiero poner una demanda"
    Respuesta: DEMANDA

-   Texto: "Es una consulta"
    Respuesta: INDEFINIDO

-   Texto: "No estoy seguro"
    Respuesta: INDEFINIDO

"""

USER_PROMPT = """

Texto: "%s"

Respuesta:

"""

def derive(service, text, max_tkns=2000) -> any:
    try:
        tmp_work_memory = []
        prompt  = SYSTEM_PROMPT
        tmp_work_memory.append({"role": "system", "content": prompt})
        prompt = USER_PROMPT % text
        tmp_work_memory.append({"role": "user", "content": prompt})
        res = service.generate(tmp_work_memory, max_tokens=max_tkns)
        logging.info(f"\n[Celula][Saludos][Proceso]: {text}")        
        logging.info(f"[Celula][Saludos][Respuesta]: {res}")
        if not res or res == "":
            res = text
            logging.warning(f"No obtener una respuesta.")
        return res
    except Exception as e:
        logging.error(f"Error al procesar: {text}")
        logging.error(e)
        return None
