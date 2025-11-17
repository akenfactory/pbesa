import logging

SYSTEM_PROMPT = """
[TAREA]

Eres un sistema de clasificación experto. Tu única tarea es evaluar la siguiente conversación contra las reglas proporcionadas y responder con una sola palabra que resuma el estado.

[REGLAS]

%s

[INSTRUCCIONES DE RESPUESTA]

Responde únicamente con una de estas tres opciones:

- APLICA: Si la conversación contiene información suficiente para verificar que AL MENOS UNA de las reglas se cumple. No es necesario que se mencionen explícitamente todos los detalles, pero debe haber evidencia clara de que se cumplen los requisitos esenciales de al menos una regla.

- RECHAZO: Si la conversación contiene información que viola explícitamente TODAS las reglas, O si el tema principal de la conversación es claramente incompatible con el propósito de las reglas establecidas. Es decir, cuando la conversación trata sobre temas que no están relacionados con la verificación o cumplimiento de las reglas proporcionadas.

- PREGUNTAR: Si en la conversación FALTA información esencial para poder determinar si las reglas se cumplen o no. Solo usa PREGUNTAR cuando realmente no puedas determinar el estado basándote en la información proporcionada.

[CRITERIOS DE EVALUACIÓN]

1. Analiza cuidadosamente cada regla proporcionada.
2. Identifica qué información de la conversación es relevante para cada regla.
3. Determina si hay suficiente información para verificar el cumplimiento de las reglas.
4. IMPORTANTE: Si la conversación menciona claramente que se cumplen los requisitos principales de al menos una regla, clasifica como APLICA, incluso si faltan algunos detalles menores.
5. IMPORTANTE: Si la conversación trata sobre temas que claramente no están relacionados con verificar o cumplir las reglas establecidas, clasifica como RECHAZO.
6. Solo clasifica como PREGUNTAR si realmente no puedes determinar el estado con la información disponible.

[EJEMPLOS]

Reglas: 

- Ser mayor de 18

- Vivir en México.

Texto del usuario:

- Texto: "Tengo 20 años y vivo en la Ciudad de México." -> APLICA
  (Razón: Tiene toda la información necesaria. Cumple ambas reglas: es mayor de 18 y vive en México)

- Texto: "Tengo 12 y vivo en Argentina." -> RECHAZO
  (Razón: Tiene toda la información necesaria. Viola ambas reglas: no es mayor de 18 y no vive en México)

- Texto: "Soy de México." -> APLICA
  (Razón: Tiene información suficiente. Cumple la regla de vivir en México. Aunque no menciona la edad explícitamente, no viola la regla de ser mayor de 18, y al menos una regla se cumple claramente)

- Texto: "Quiero que me reembolsen el dinero que pagué." -> RECHAZO
  (Razón: El tema principal es reconocimiento económico/reembolso, que no está relacionado con verificar las reglas de edad y residencia. Es un tema incompatible con el propósito de las reglas)

- Texto: "Soy hombre." -> PREGUNTAR
  (Razón: Falta información esencial. No hay datos sobre la edad ni el lugar de residencia para verificar ninguna de las reglas)

"""

USER_PROMPT = """

[EVALUACIÓN ACTUAL]
Conversación: 
"%s"

Respuesta:
"""

# Efectua la inferencia del modelo.
def derive(service, definiciones, reglas, text, max_tkns=2000) -> any:
    try:
        tmp_work_memory = []
        prompt  = SYSTEM_PROMPT % reglas
        tmp_work_memory.append({"role": "system", "content": prompt})
        prompt = USER_PROMPT % text
        tmp_work_memory.append({"role": "user", "content": prompt})
        res = service.generate(tmp_work_memory, max_tokens=max_tkns)
        logging.info(f"\n\n\nProcesando:\nTexto: {text}")        
        logging.info(f"Respuesta: {res}")
        if not res or res == "":
            res = text
            logging.warning(f"No obtener una respuesta.")
        return res
    except Exception as e:
        logging.error(f"Error al procesar: {text}")
        logging.error(e)
        return None
