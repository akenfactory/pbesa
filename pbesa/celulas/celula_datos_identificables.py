import logging

PROMPT = """
Eres un clasificador de datos. Tu tarea es clasificar si el siguiente texto contiene **datos personales** o **datos identificables de una entidad**.

Responde únicamente con:
- CONTIENE_DATOS
- NO_CONTIENE_DATOS

**Se considera que el texto CONTIENE_DATOS si incluye:**
- Nombres completos de personas
- Razón social o nombre de una empresa
- Números de documento (cédula, NIT, etc.)
- Direcciones físicas (calle, carrera, avenida, etc.)
- Teléfonos o celulares
- Correos electrónicos

---

**Ejemplos:**

1. "Mi nombre es Carlos Ramírez y mi cédula es 1032478992." → CONTIENE_DATOS  
2. "Quiero demandar a la empresa Alimentos S.A.S. ubicada en la Calle 45 #10-20." → CONTIENE_DATOS  
3. "Puedes contactarme al correo johana.perez@gmail.com o al 3105678901." → CONTIENE_DATOS  
4. "Necesito información sobre cómo presentar una queja." → NO_CONTIENE_DATOS  
5. "Hola, buen día" → NO_CONTIENE_DATOS  
6. "La empresa Agropecuaria S.A. está usando marcas similares a las nuestras." → CONTIENE_DATOS  
7. "¿Cuál es el procedimiento para radicar una solicitud?" → NO_CONTIENE_DATOS

---
"""

# Efectua la inferencia del modelo.
def derive(service, text, max_tkns=4096) -> any:
    try:
        tmp_work_memory = []
        user_prompt  = """
        Texto: "%s"

        Clasificación:
        """ % text
        tmp_work_memory.append({"role": "system", "content": PROMPT})
        tmp_work_memory.append({"role": "user", "content": user_prompt})
        res = service.generate(tmp_work_memory, max_tokens=max_tkns)
        logging.info(f"Procesando: {text}")
        logging.info(f"Respuesta: {res}")
        if not res or res == "":
            res = text
            logging.warning(f"No obtener una respuesta.")
        return res
    except Exception as e:
        logging.error(f"Error al procesar: {text}")
        logging.error(e)
        return None
