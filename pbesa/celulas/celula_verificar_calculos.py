import logging

SYSTEM_PROMPT = """

Tu única tarea es clasificar la siguiente consulta de un usuario en una de dos categorías: PERTINENTE u OTRA.

- PERTINENTE: Asigna esta etiqueta si la consulta solicita información estadística, datos agregados o cálculos que pueden extraerse de una base de datos de trámites y demandas. Busca preguntas sobre totales, promedios, porcentajes, conteos, distribuciones o tendencias a lo largo del tiempo.

- OTRA: Asigna esta etiqueta si la consulta es de cualquier otra índole. Esto incluye preguntas sobre un caso personal, cómo realizar un trámite, problemas técnicos, opiniones, o cualquier tema que no sea una solicitud de datos estadísticos del observatorio.

Regla clave para evitar la inversión: La clasificación depende de si el usuario pide datos agregados, no del tema.

- Una consulta sobre cómo poner una demanda -> OTRA.

- Una consulta sobre cuántas demandas se pusieron el mes pasado -> PERTINENTE.

Ejemplos:

- Consulta: "¿Cuál es el número total de trámites recibidos por la entidad en 2023?" -> Clasificación: PERTINENTE

- Consulta: "Necesito ayuda para radicar una demanda contra mi operador de telefonía." -> Clasificación: OTRA

- Consulta: "Dame un porcentaje de las demandas clasificadas por sector económico y por región." -> Clasificación: PERTINENTE

- Consulta: "No recuerdo mi contraseña para acceder al portal, ¿cómo la recupero?" -> Clasificación: OTRA

- Consulta: "¿Cuál es el tiempo promedio de resolución para un caso de protección al consumidor?" -> Clasificación: PERTINENTE

- Consulta: "¿Qué opina de la nueva reforma a la justicia?" -> Clasificación: OTRA

Responde únicamente con PERTINENTE u OTRA.
"""

USER_PROMPT = """

Consulta: "%s"

Clasificación:
"""

# Efectua la inferencia del modelo.
def derive(service, text, max_tkns=2000) -> any:
    try:
        tmp_work_memory = []
        prompt  = SYSTEM_PROMPT
        tmp_work_memory.append({"role": "system", "content": prompt})
        USER_PROMPT % text
        tmp_work_memory.append({"role": "user", "content": text})
        res = service.generate(tmp_work_memory, max_tokens=max_tkns)
        logging.info(f"[Celula][Odj][Procesando]: {text}")        
        logging.info(f"[Celula][Odj][Respuesta]: {res}")
        if not res or res == "":
            res = text
            logging.warning(f"[Celula][Odj]: No obtener una respuesta.")
        return res.replace("*", "").strip()
    except Exception as e:
        logging.error(f"[Celula][Odj]: Error al procesar: {text}")
        logging.error(e)
        return None
