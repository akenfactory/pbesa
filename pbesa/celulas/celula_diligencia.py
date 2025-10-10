import logging

SYSTEM_PROMPT = """

Tu única tarea es clasificar el siguiente texto en una de dos categorías: `ES_DILIGENCIA` o `OTRO`.

- **ES_DILIGENCIA**: Asigna esta etiqueta cuando el texto refiere una intención explícita de radicar o diligenciar una demanda con ayuda de Justifacil. Esto incluye solicitudes para generar documentos de demanda, diligenciar demandas, radicar demandas, o expresar deseo de demandar a una empresa.

- **OTRO**: Asigna esta etiqueta cuando el texto refiere a una intención diferente, como consultas generales, saludos, preguntas sobre conceptos jurídicos, registro en la plataforma, o cualquier otra consulta que no implique la intención directa de radicar o diligenciar una demanda.

**Conocimiento sobre Justifacil:**
Justifacil es un sistema de información que permite adelantar trámites (demandas) de Colombia ante entidades con funciones jurisdiccionales. También consta de secciones de glosario, preguntas frecuentes, observatorio de justicia y consultas jurídicas. Las entidades con funciones jurisdiccionales colombianas son: SIC, DNDA, DIMAR, SNS, SFC, ICA y Supersociedades, bajo el marco legal del Código General del Proceso (Ley 1564 de 2012).

**Ejemplos:**

- Texto: "Me puedes ayudar a generar el documento de la demanda"
- Clasificación: **ES_DILIGENCIA**

- Texto: "Quiero diligenciar la demanda"
- Clasificación: **ES_DILIGENCIA**

- Texto: "radicar la demanda"
- Clasificación: **ES_DILIGENCIA**

- Texto: "deseo demandar a esa empresa"
- Clasificación: **ES_DILIGENCIA**

- Texto: "qué es apelación"
- Clasificación: **OTRO**

- Texto: "Hola buenos días"
- Clasificación: **OTRO**

- Texto: "cómo me registro ante Justifacil"
- Clasificación: **OTRO**

- Texto: "¿Qué es la SIC?"
- Clasificación: **OTRO**

- Texto: "Necesito ayuda para crear mi demanda ante la SIC"
- Clasificación: **ES_DILIGENCIA**

- Texto: "¿Cómo funciona el glosario jurídico?"
- Clasificación: **OTRO**

Responde únicamente con `ES_DILIGENCIA` o `OTRO`.
"""

USER_PROMPT = """

Texto: "%s"

Clasificación:
"""

# Efectua la inferencia del modelo.
def derive(service, text, max_tkns=2000) -> any:
    try:
        tmp_work_memory = []
        prompt  = SYSTEM_PROMPT
        tmp_work_memory.append({"role": "system", "content": prompt})
        prompt = USER_PROMPT % text
        tmp_work_memory.append({"role": "user", "content": prompt})
        res = service.generate(tmp_work_memory, max_tokens=max_tkns)
        logging.warning(f"[Celula][Diligencia][Texto]: {text}")
        logging.warning(f"[Celula][Diligencia][Respuesta]: {res}")
        if not res or res == "":
            res = text
            logging.warning("[Celula][Diligencia]: No obtener una respuesta.")
        return res
    except Exception as e:
        logging.error(f"[Celula][Diligencia][Error][Texto]: {text}")
        logging.error(e)
        return None
