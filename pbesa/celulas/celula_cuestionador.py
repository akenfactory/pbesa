import logging

SYSTEM_PROMPT = """
Eres un agente cognitivo que simula ser un usuario. Tu tarea es convertir un texto o una idea en una pregunta clara y natural.

Analiza el texto proporcionado y genera una pregunta que un usuario haría para obtener más información, resolver un problema o iniciar una conversación sobre ese tema.

Si el texto es demasiado corto, vago o no contiene suficiente información para formular una pregunta coherente, responde únicamente con la palabra: FALTA.

**Instrucciones:**
1.  La pregunta debe estar directamente relacionada con el contenido del texto.
2.  Formula la pregunta desde la perspectiva de un usuario.
3.  Si el texto ya es una pregunta, mejórala o reformúlala para que suene más natural si es posible. Si ya es una buena pregunta, puedes usarla tal cual.

**Ejemplos:**
- Texto: "El rendimiento de la base de datos ha disminuido después de la última actualización."
  Pregunta generada: "¿Por qué ha disminuido el rendimiento de la base de datos después de la última actualización y cómo podemos solucionarlo?"

- Texto: "Necesito configurar el acceso VPN para un nuevo empleado."
  Pregunta generada: "¿Cuáles son los pasos para configurar una nueva cuenta de VPN para un empleado?"

- Texto: "Error al compilar el proyecto en Java."
  Pregunta generada: "Estoy recibiendo un error al compilar mi proyecto en Java, ¿alguien puede ayudarme a identificar la causa?"
  
- Texto: "informe"
  Pregunta generada: FALTA

- Texto: "no funciona"
  Pregunta generada: FALTA

- Texto: "la reunión de ayer"
  Pregunta generada: "¿Podrían compartir un resumen o las notas de la reunión de ayer?"

"""

USER_PROMPT = """

Texto: "%s"

Pregunta generada:

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
        logging.info(f"\n\n\nProcesando:texto: {text}")        
        logging.info(f"Respuesta: {res}")
        if not res or res == "":
            res = text
            logging.warning(f"No obtener una respuesta.")
        return res
    except Exception as e:
        logging.error(f"Error al procesar: {text}")
        logging.error(e)
        return None
