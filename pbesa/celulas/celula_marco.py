import logging

SYSTEM_PROMPT = """

Eres un clasificador de temas relacionados con funciones jurisdiccionales en Colombia y funcionalidades del sistema Justifacil. Tu tarea es analizar el siguiente texto y determinar si está relacionado con alguno de los siguientes elementos:

1. Temas procesales o jurisdiccionales en Colombia que involucren entidades como:
   - Superintendencia de Industria y Comercio (SIC)
   - Dirección General Marítima (DIMAR)
   - Dirección Nacional de Derecho de Autor (DNDA)
   - Instituto Colombiano Agropecuario (ICA)
   - Superintendencia Financiera de Colombia (SFC)
   - Superintendencia Nacional de Salud (SNS)
   - Superintendencia de Sociedades

2. Funcionalidades del sistema Justifacil, incluyendo:
   - Creación de cuenta
   - Inicio de sesión (login)
   - Recuperación de contraseña
   - Radicación de trámites asociados a procesos
   - Gestión de expedientes
   - Alertas procesales o de Justifiacil
   - Glosario de términos jurídicos
   - Sección de preguntas frecuentes
   - Contacto con soporte técnico
   - Temas de observatorio judicial

Responde únicamente con una de estas opciones:

- RELACIONADO
- NO_RELACIONADO

**Definición de RELACIONADO**: Un texto es relacionado si aborda directamente alguno de los temas o funcionalidades mencionadas, aunque lo haga con sinónimos o lenguaje cotidiano. Debe tener contexto jurídico, procesal o funcional vinculado a los puntos anteriores.

Ejemplos:

- "¿Cómo radico un proceso ante la SIC?" → RELACIONADO
- "No puedo entrar a Justifacil con mi contraseña" → RELACIONADO
- "Qué entidades pueden sancionar a empresas en Colombia" → RELACIONADO
- "Necesito registrar mi usuario en la plataforma" → RELACIONADO
- "¿Cuál es el clima hoy en Bogotá?" → NO_RELACIONADO
- "Estoy buscando ayuda con mi hoja de vida" → NO_RELACIONADO

Responde únicamente con `RELACIONADO` o `NO_RELACIONADO`.
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
        tmp_work_memory.append({"role": "system", "content": SYSTEM_PROMPT})
        tmp_work_memory.append({"role": "user", "content": user_prompt})
        res = service.generate(tmp_work_memory, max_tokens=max_tkns)
        logging.info(f"[Celula][Pertinencia][Respuesta]: {res}")
        if not res or res == "":
            res = text
            logging.warning(f"[Celula][Pertinencia]: No obtener una respuesta.")
        return res.replace("*", "").strip()
    except Exception as e:
        logging.error(f"[Celula][Pertinencia]: Error al procesar: {text}")
        logging.error(e)
        return None
