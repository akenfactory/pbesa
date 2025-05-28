import logging

PROMPT = """
Eres un clasificador de textos que determina a qué entidad o dependencia gubernamental colombiana corresponde un texto dado, basándose en la descripción de sus funciones. Tu tarea es analizar el siguiente texto y determinar la clase más apropiada.

Responde únicamente con el nombre completo de la clase o con "NO_CORRESPONDE" si el texto no se ajusta a ninguna de las clases descritas. No agregues explicaciones ni comentarios adicionales.

%s

Opciones de respuesta posibles:

DIMAR - Dirección General Marítima
DNDA - Dirección Nacional de Derecho de Autor
ICA - Instituto Colombiano Agropecuario
SFC - Superintendencia Financiera de Colombia
SIC - Superintendencia de Industria y Comercio - Competencia Desleal
SIC - Superintendencia de Industria y Comercio - Propiedad Industrial
SIC - Superintendencia de Industria y Comercio - Protección al Consumidor
Supersalud - Superintendencia Nacional de Salud - Cobertura Servicios
Supersalud - Superintendencia Nacional de Salud - Conflictos Devoluciones
Supersalud - Superintendencia Nacional de Salud - Conflicto Entidades
Supersalud - Superintendencia Nacional de Salud - Libre Elección
Supersalud - Superintendencia Nacional de Salud - Multiafiliación
Supersalud - Superintendencia Nacional de Salud - Reconocimiento Económico
Supersociedades - Superintendencia de Sociedades - Liquidación Insolvencia
Supersociedades - Superintendencia de Sociedades - Reorganización Insolvencia
Supersociedades - Superintendencia de Sociedades - Validación Judicial
Supersociedades - Superintendencia de Sociedades - Mercantiles
NO_CORRESPONDE
"""

# Efectua la inferencia del modelo.
def derive(service, text, conocimiento, max_tkns=4096) -> any:
    try:
        tmp_work_memory = []
        prompt  = PROMPT % conocimiento
        tmp_work_memory.append({"role": "system", "content": prompt})
        user_prompt = """
        Texto: "%s"

        Clasificación:
        """ % text
        tmp_work_memory.append({"role": "system", "content": prompt})
        tmp_work_memory.append({"role": "user", "content": user_prompt})
        res = service.generate(tmp_work_memory, max_tkns)
        logging.info("\n")
        logging.info(f"[Celula][Expertos][Text]: {text}")
        logging.info(f"[Celula][Expertos][Respuesta]: {res}")
        logging.info("\n")    
        if not res or res == "":
            res = text
            logging.warning(f"[Celula][Expertos]: No obtener una respuesta.")
        return res
    except Exception as e:
        logging.error(f"[Celula][Expertos]: Error al procesar: {text}")
        logging.error(e)
        return None
