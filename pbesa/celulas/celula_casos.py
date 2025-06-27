import logging

PROMPT = """
Eres un clasificador que identifica si un texto corresponde a una queja o demanda que debe ser radicada ante un ente de control del Estado colombiano.

Responde únicamente con:
- QUEJA_DEMANDA
- NO_QUEJA_DEMANDA

**Definición de QUEJA_DEMANDA**: El texto describe hechos, situaciones o infracciones por parte de una empresa, entidad o persona que pueden requerir la intervención de entidades como:

- Superintendencia de Sociedades  
- Superintendencia de Industria y Comercio  
- Supersalud  
- Dirección General Marítima  
- Superintendencia Financiera de Colombia  
- Instituto Colombiano Agropecuario (ICA)  
- Dirección Nacional de Derecho de Autor  
- Autoridades de protección al consumidor  
- Casos de competencia desleal o propiedad industrial

**NO_QUEJA_DEMANDA**: El texto no describe una inconformidad, infracción ni intención de denuncia. Puede ser una pregunta, saludo, comentario o solicitud de orientación.

---

**Ejemplos:**

1. "Quiero presentar una denuncia contra la empresa Colmédica por incumplimiento en la prestación de servicios de salud." → QUEJA_DEMANDA  
2. "La empresa Navemar ha incurrido en prácticas marítimas irregulares y omisión de protocolos de seguridad." → QUEJA_DEMANDA  
3. "Explícame cómo radicar una queja" → NO_QUEJA_DEMANDA  
4. "Hola, buen día" → NO_QUEJA_DEMANDA  
5. "Evacol S.A.S. está copiando diseños registrados de Crocs Inc. y aprovechando su reputación." → QUEJA_DEMANDA  
6. "¿Dónde puedo radicar una demanda?" → NO_QUEJA_DEMANDA  
7. "El supermercado está vendiendo productos vencidos que afectaron mi salud." → QUEJA_DEMANDA  
8. "Necesito orientación sobre propiedad industrial" → NO_QUEJA_DEMANDA

---
"""

# Efectua la inferencia del modelo.
def derive(service, text, max_tkns=2000) -> any:
    try:
        logging.info(f"Procesando: {text}")
        tmp_work_memory = []
        user_prompt  = """
        Texto: "%s"

        Clasificación:
        """ % text
        tmp_work_memory.append({"role": "system", "content": PROMPT})
        tmp_work_memory.append({"role": "user", "content": user_prompt})
        res = service.generate(tmp_work_memory, max_tokens=max_tkns)
        logging.info(f"[Celula][Casos][Respuesta]: {res}")
        if not res or res == "":
            res = text
            logging.warning(f"[Celula][Casos]: No obtener una respuesta.")
        return res.replace("*", "").strip()
    except Exception as e:
        logging.error(f"[Celula][Casos]: Error al procesar: {text}")
        logging.error(e)
        return None