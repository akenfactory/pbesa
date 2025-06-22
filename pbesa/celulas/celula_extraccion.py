import logging

SYSTEM_PROMPT = """
Eres un extractor de datos estructurados.  
Tu tarea es leer la **Descripción** (lo que se le pide al usuario) y la **Respuesta del usuario** y devolver **únicamente** un objeto JSON válido con las claves indicadas en la descripción y los valores dados por el usuario.

Reglas:
1. Usa exactamente el texto entre comillas o negritas de la descripción como nombre de la clave en el JSON.  
   • Ej.: si la descripción contiene **"Tipo de solicitante"**, la clave debe ser `"Tipo de solicitante"`.
2. El valor debe ser la respuesta del usuario:
   • Elimina saltos de línea y espacios al principio/fin.  
   • Respeta mayúsculas/minúsculas tal cual la escribió el usuario.  
   • Si responde varias opciones separadas (por comas, saltos de línea, “y”, etc.), devuelve una lista de cadenas.
3. Si falta información para alguna clave, pon el valor vacío: `""`.
4. No añadas texto extra, explicaciones ni código. Devuelve **solo** el objeto JSON.

Descripción:
\"\"\"%s\"\"\"

"""
USER_PROMPT = """
Respuesta del usuario:
\"\"\"%s\"\"\"

Salida JSON:
"""

# Efectua la inferencia del modelo.
def derive(service, query, max_tkns=2000) -> any:
    try:
        description = query.get("description", "")
        text = query.get("text", "")
        
        tmp_work_memory = []
        prompt = SYSTEM_PROMPT
        tmp_work_memory.append({"role": "system", "content": prompt})
        prompt = USER_PROMPT % description
        tmp_work_memory.append({"role": "user", "content": text})
        
        res = service.generate(tmp_work_memory, max_tokens=max_tkns)

        logging.info(f"[Celula][Extrac][Procesando]: {text}")        
        logging.info(f"[Celula][Extrac][Respuesta]: {res}")
        if not res or res == "":
            res = text
            logging.warning(f"[Celula][Extrac]: No obtener una respuesta.")
        return res.replace("*", "").strip()
    except Exception as e:
        logging.error(f"[Celula][Extrac]: Error al procesar: {text}")
        logging.error(e)
        return None
