import logging

PROMPT = """
Eres un clasificador de intenciones de texto. Debes analizar el texto proporcionado y clasificarlo en una de las siguientes categorías:

1. SALUDO: El texto contiene un saludo inicial como "hola", "buen día", "buenas tardes", "qué tal", "saludos", etc.
2. PREGUNTA_O_SOLICITUD: El texto busca obtener información, ya sea mediante una pregunta directa ("¿Qué hora es?") o una solicitud indirecta ("Necesito saber cómo ingresar").
3. QUEJA_DEMANDA: El texto describe una inconformidad o denuncia que debe ser radicada ante un ente de control estatal, como la Superintendencia de Industria y Comercio, Supersalud, ICA, Dirección Nacional de Derecho de Autor, etc.
4. NINGUNA: El texto no encaja en ninguna de las categorías anteriores.

Responde solo con una de estas cuatro categorías, en mayúsculas.

---

**Ejemplos:**

- "Hola, buen día" → SALUDO  
- "¿Dónde puedo radicar una queja?" → PREGUNTA_O_SOLICITUD  
- "Quiero demandar a una empresa que está usando mi marca registrada" → QUEJA_DEMANDA  
- "Ya envié el documento que solicitaste" → NINGUNA  
- "Explícame cómo hacerlo" → PREGUNTA_O_SOLICITUD  
- "Evacol S.A.S. está copiando diseños de Crocs Inc. para confundir a los consumidores" → QUEJA_DEMANDA  
- "Saludos cordiales" → SALUDO  
- "Estoy confirmando la reunión de mañana" → NINGUNA

---

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
