import logging

SYSTEM_PROMPT = """

Tu única tarea es clasificar el siguiente texto en una de dos categorías: `VEROSIMIL` o `ABSURDO`.

- **VEROSIMIL**: Asigna esta etiqueta si la situación descrita es lógicamente posible en el mundo real. No importa si la queja es tonta, extraña o legalmente débil. Si involucra sujetos y acciones que pueden existir y ocurrir, es verosímil.
- **ABSURDO**: Asigna esta etiqueta si la situación se basa en fantasía, viola las leyes de la física o la lógica, o aplica un concepto a un sujeto fundamentalmente incorrecto (ej. derechos humanos a un animal, acciones legales a un objeto inanimado).

**Regla clave para evitar la inversión:** La clasificación es sobre la **posibilidad lógica**, no sobre si el tema corresponde a la SIC, DIMAR, SNS, etc.
- Un caso sobre la SIC que es imposible -> `ABSURDO`.
- Un caso que NO es de la SIC pero es posible (ej. "el perro del vecino ladra") -> `VEROSIMIL`.

**Ejemplos:**

- Texto: "Quiero entablar una demanda ante la SNS porque mi EPS no me da medicamentos para mi Gato."
- Clasificación: **ABSURDO**

- Texto: "No puedo entrar a mi cuenta de Justifacil, olvidé la contraseña."
- Clasificación: **VEROSIMIL**

- Texto: "Quiero demandar al Banco porque no me genera un préstamo ya que soy un extraterrestre."
- Clasificación: **ABSURDO**

- Texto: "Quiero demandar a una empresa ante la SIC porque su logo es feo."
- Clasificación: **VEROSIMIL** (Es una queja posible, aunque subjetiva y probablemente sin futuro legal).

- Texto: "El perro de mi vecino ladra toda la noche y quiero poner una queja."
- Clasificación: **VEROSIMIL** (Es un problema real y posible, aunque no sea competencia de las entidades usuales).

- Texto: "Quiero demandar a la luna por seguirme a casa, ¿me ayuda la Dirección de Derecho de Autor?"
- Clasificación: **ABSURDO**

Responde únicamente con `VEROSIMIL` o `ABSURDO`.
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
        logging.info(f"[Celula][Saludos][Respuesta]: {res}")
        if not res or res == "":
            res = text
            logging.warning(f"[Celula][Saludos]: No obtener una respuesta.")
        return res.replace("*", "").strip()
    except Exception as e:
        logging.error(f"[Celula][Saludos]: Error al procesar: {text}")
        logging.error(e)
        return None
