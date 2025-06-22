import logging

SYSTEM_PROMPT = """
[TAREA]
Eres un sistema de clasificación experto. Tu única tarea es evaluar la siguiente conversación contra las reglas proporcionadas y responder con la justificación de RECHAZO.

[DEFINICIONES]
%s

[REGLAS]
%s

[INSTRUCCIONES DE RESPUESTA]
Responde únicamente bajo las siguientes condiciones:
- Con la justificación de RECHAZO si la conversación no cumple con las reglas argumentando por qué no aplica.
- Con la justificación de RECHAZO parafrasea el concepto de reglas por el de marco normativo.
- Si la conversación cumple AL MENOS UNA de las reglas responde unicamente: SIN_COMENTARIOS.

[EJEMPLOS]
Reglas: 
- Ser mayor de 18
- Vivir en México.

Texto del usuario:
- Texto: "Tengo 20 años y vivo en la Ciudad de México." -> SIN_COMENTARIOS
- Texto: "Tengo 12 y vivo en Argentina." -> RECHAZO: "No cumple con la regla de ser mayor de 18 y vivir en México."
- Texto: "Soy de México." -> SIN_COMENTARIOS

"""

USER_PROMPT = """

[EVALUACIÓN ACTUAL]
Conversación: 
"%s"

Respuesta:
"""

# Efectua la inferencia del modelo.
def derive(service, definiciones, reglas, text, max_tkns=2000) -> any:
    try:
        tmp_work_memory = []
        prompt  = SYSTEM_PROMPT % (definiciones, reglas)
        tmp_work_memory.append({"role": "system", "content": prompt})
        prompt = USER_PROMPT % text
        tmp_work_memory.append({"role": "user", "content": prompt})
        res = service.generate(tmp_work_memory, max_tokens=max_tkns)
        logging.info(f"\n\n\nProcesando:\nDefiniciones: {definiciones}\nReglas: {reglas}\nTexto: {text}")        
        logging.info(f"Respuesta: {res}")
        if not res or res == "":
            res = text
            logging.warning(f"No obtener una respuesta.")
        return res
    except Exception as e:
        logging.error(f"Error al procesar: {text}")
        logging.error(e)
        return None
