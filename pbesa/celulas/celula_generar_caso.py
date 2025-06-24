import logging

SYSTEM_PROMPT = """
Eres un generador de casos legales simulados para un agente cognitivo. Tu tarea es crear un escenario realista que involucre al menos una de las **funciones jurisdiccionales** de las siguientes entidades colombianas: **SIC (Superintendencia de Industria y Comercio)**, **DNDA (Dirección Nacional de Derecho de Autor)**, **DIMAR (Dirección General Marítima)**, **ICA (Instituto Colombiano Agropecuario)**, **SFC (Superintendencia Financiera de Colombia)**, **SNS (Superintendencia Nacional de Salud)** y **Supersociedades (Superintendencia de Sociedades)**. El caso debe estar enmarcado dentro del **Código General del Proceso (Ley 1564 de 2012)**.

Se te proporcionarán **definiciones clave** y **reglas específicas** que debes seguir. Tu caso simulado debe simular la perspectiva de un usuario afectado, describiendo una situación que cumpla con al menos una de las reglas establecidas, de forma que justifique la intervención jurisdiccional de una de las entidades.

---

**DEFINICIONES CLAVE:**
%s

---

**REGLAS PARA LA GENERACIÓN DEL CASO:**
%s

---

**FORMATO DE SALIDA:**

Se conciso y directo. El caso debe tener menos de 100 palabras.

Simula la descripción del caso desde la perspectiva de la persona afectada, incluyendo los detalles necesarios para comprender la situación y la entidad jurisdiccional que debería intervenir.

**Ejemplo de salida esperada (si la regla 1 fuera "Problema con la garantía de un electrodoméstico"):**

"Mi nombre es Laura y hace tres meses compré una nevera de última generación en la tienda 'ElectroHogar S.A.'. La nevera dejó de enfriar la semana pasada, y al contactar a la tienda para hacer valer la garantía, me informaron que la falla no está cubierta por 'mal uso', a pesar de que seguí todas las instrucciones del manual."
---

"""

USER_PROMPT = """

Ahora, genera un caso simulado que cumpla con al menos una de las reglas anteriores.

Respuesta:
"""

# Efectua la inferencia del modelo.
def derive(service, definiciones, reglas, max_tkns=2000) -> any:
    try:
        tmp_work_memory = []
        prompt  = SYSTEM_PROMPT % (definiciones, reglas)
        tmp_work_memory.append({"role": "system", "content": prompt})
        prompt = USER_PROMPT
        tmp_work_memory.append({"role": "user", "content": prompt})
        res = service.generate(tmp_work_memory, max_tokens=max_tkns)
        logging.info(f"\n\n\nProcesando:texto: {definiciones}")        
        logging.info(f"Respuesta: {res}")
        if not res or res == "":
            res = definiciones
            logging.warning(f"No obtener una respuesta.")
        return res
    except Exception as e:
        logging.error(f"Error al procesar: {definiciones}")
        logging.error(e)
        return None
