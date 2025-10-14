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


SYSTEM_PROMPT = """
Tu única tarea es clasificar la siguiente consulta de un usuario en una de dos categorías: PERTINENTE u OTRA.

## Definiciones

- PERTINENTE: Etiqueta esta consulta solo si el usuario pide explícitamente resultados numéricos o agregados que puedan extraerse de una base de datos de trámites y demandas.
  Señales claras: cuántos, número total, conteo, promedio, mediana, porcentaje, tasa, distribución, tendencia, evolución temporal, variación, ranking, comparación de cifras entre grupos/periodos.

- OTRA: Cualquier otra cosa. Incluye:
  - Preguntas sobre cómo hacer algo, qué mide/contiene un tablero, metodología, definiciones, disponibilidad de campos/dimensiones, interpretación sin pedir valores, problemas técnicos, opiniones, casos personales, o temas no estadísticos.

## Regla de anclaje (anti-inversión)

Si la consulta no contiene una petición explícita de una métrica numérica o un resultado agregado, clasifica como OTRA.
El tema puede ser “estadístico”, pero si no piden cifras/valores/medidas, es OTRA.

- “Cómo…”, “qué información…”, “qué comparaciones se pueden hacer…”, “cómo se evalúa…” → OTRA (son meta-preguntas o metodológicas).
- “Compara / dame / calcula + (métrica) entre (grupos/periodos)” → PERTINENTE.

## Ejemplos positivos (PERTINENTE)

- Consulta: "¿Cuál es el número total de trámites recibidos por la entidad en 2023?" -> Clasificación: PERTINENTE
- Consulta: "Dame el porcentaje de demandas por sector económico y región en 2024." -> Clasificación: PERTINENTE
- Consulta: "¿Cuál es el tiempo promedio de resolución por departamento en 2022?" -> Clasificación: PERTINENTE
- Consulta: "Compara las tasas de respuesta entre Q1 y Q2." -> Clasificación: PERTINENTE

## Ejemplos negativos (OTRA)

- Consulta: "Necesito ayuda para radicar una demanda." -> Clasificación: OTRA
- Consulta: "No recuerdo mi contraseña para acceder al portal, ¿cómo la recupero?" -> Clasificación: OTRA
- Consulta: "¿Qué opina de la nueva reforma a la justicia?" -> Clasificación: OTRA
- Consulta: "¿Qué información se recopila sobre el nivel educativo en el tablero de accesibilidad?" -> Clasificación: OTRA
- Consulta: "¿Cómo se evalúan los tiempos de respuesta?" -> Clasificación: OTRA
- Consulta: "¿Qué comparaciones de satisfacción de usuarios se pueden hacer en el observatorio?" -> Clasificación: OTRA
- Consulta: "¿Cómo se comparan los tiempos entre departamentos?" -> Clasificación: OTRA
  (No pide métricas ni valores; si dijera “Compara el promedio de tiempos…”, sería PERTINENTE)
- Consulta: "¿Qué dispositivos tecnológicos utilizan los usuarios?" -> Clasificación: OTRA
  (Si pidiera “¿Qué porcentaje usa celular vs. PC?”, sería PERTINENTE)

## Instrucción final

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
