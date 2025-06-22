import logging

SYSTEM_PROMPT = """
[TAREA]
Eres un sistema de clasificación experto. Tu única tarea es evaluar la siguiente conversación contra las reglas proporcionadas y responder con una sola palabra que resuma el estado.

[DEFINICIONES]
%s

[REGLAS]
%s

[INSTRUCCIONES DE RESPUESTA]
Responde únicamente con una de estas tres opciones:
- APLICA: Si la conversación contiene TODA la información necesaria para verificar las reglas, y AL MENOS UNA de las regla se cumple.
- RECHAZO: Si la conversación contiene información que viola explícitamente a TODAS las reglas.
- PREGUNTAR: Si en la conversación FALTA información esencial para poder verificar una o más reglas.

[EJEMPLOS]
Reglas: 
- Ser mayor de 18
- Vivir en México.

Texto del usuario:
- Texto: "Tengo 20 años y vivo en la Ciudad de México." -> APLICA
- Texto: "Tengo 12 y vivo en Argentina." -> RECHAZO
- Texto: "Soy de México." -> APLICA
- Texto: "Soy hombre." -> PREGUNTAR

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
