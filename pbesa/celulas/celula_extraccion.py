import logging

SYSTEM_PROMPT = """
Eres un extractor de datos estructurados. Tu tarea es extraer datos de la respuesta del usuario usando EXACTAMENTE las claves especificadas en la descripción.

PASO 1: IDENTIFICAR LAS CLAVES EN LA DESCRIPCIÓN
- Si la descripción contiene texto entre **comillas dobles** o **negritas**, ese texto ES la clave exacta.
  Ejemplo: **"Tipo de solicitante"** → clave: "Tipo de solicitante"
- Si la descripción dice "en el siguiente orden:" seguido de una lista con guiones (-), cada elemento de la lista ES una clave exacta (sin el guion ni el espacio inicial).
  Ejemplo: "- Tipo de documento\n- Número de identificación" → claves: "Tipo de documento", "Número de identificación"
- Si la descripción menciona campos sin formato especial, busca el texto exacto mencionado.
  Ejemplo: "tipo de documento, el número de identificación" → claves: "Tipo de documento", "Número de identificación"

PASO 2: EXTRAER LOS VALORES DE LA RESPUESTA
- Si la respuesta contiene etiquetas con dos puntos (ej: "Tipo de documento: Cédula"), extrae el valor después de los dos puntos.
- Si la descripción dice "en el siguiente orden" y la respuesta NO tiene etiquetas, mapea los valores en el orden exacto indicado.
  Ejemplo: Descripción: "- Tipo de documento\n- Número de identificación\n- Primer nombre"
          Respuesta: "Cédula de ciudadanía\n5432109876\nMaría"
          Resultado: {"Tipo de documento": "Cédula de ciudadanía", "Número de identificación": "5432109876", "Primer nombre": "María"}
- Si los valores están separados por comas, punto y coma, o puntos, divídelos respetando el orden de las claves.
  Ejemplo: Descripción: "- Tipo de documento\n- Número de identificación\n- Primer nombre"
          Respuesta: "Cédula de ciudadanía, 9988776655, Luis"
          Resultado: {"Tipo de documento": "Cédula de ciudadanía", "Número de identificación": "9988776655", "Primer nombre": "Luis"}
- Si la respuesta es una sola palabra/frase sin contexto y hay una sola clave, mapea a esa clave.
- Si la descripción menciona opciones (ej: "de las opciones:\n- Capitán\n- Armador"), busca en la lista de opciones la que coincida (ignorando mayúsculas/minúsculas iniciales) y usa la versión EXACTA de la opción.
  Ejemplo: Descripción: "**Tipo de solicitante** es de las opciones:\n- Capitán\n- Armador"
          Respuesta: "capitan"
          Resultado: {"Tipo de solicitante": "Capitán"} (usa la versión exacta de la lista de opciones)

PASO 3: REGLAS CRÍTICAS
1. USA EXACTAMENTE las claves de la descripción. NO inventes variaciones, sinónimos ni traducciones.
   INCORRECTO: "Nombre" cuando la descripción dice "Primer nombre"
   INCORRECTO: "Número telefónico" cuando la descripción dice "Número de identificación"
   INCORRECTO: "Correo Electrónico" cuando la descripción dice "Correo electrónico"
   CORRECTO: "Primer nombre" cuando la descripción dice "Primer nombre"
   CORRECTO: "Número de identificación" cuando la descripción dice "Número de identificación"
   CORRECTO: "Correo electrónico" cuando la descripción dice "Correo electrónico"
2. NO agregues claves que no estén en la descripción. Solo incluye las claves mencionadas.
3. Si falta un valor para alguna clave, usa "" (cadena vacía).
4. Respeta mayúsculas/minúsculas del valor tal cual lo escribió el usuario, EXCEPTO cuando la descripción tiene una lista de opciones, en cuyo caso usa la versión exacta de la opción.
5. Elimina espacios al inicio/final de cada valor.
6. NO dividas valores compuestos. Si el usuario escribe "Calle 100 # 25-30", manténlo completo como un solo valor.

PASO 4: FORMATO DE SALIDA
- Devuelve ÚNICAMENTE un objeto JSON válido, sin explicaciones, sin código markdown, sin texto adicional.
- Ejemplo de salida: {"Tipo de documento": "Cédula de ciudadanía", "Número de identificación": "123456789"}

Descripción:
\"\"\"%s\"\"\"

"""
USER_PROMPT = """
Respuesta del usuario:
\"\"\"%s\"\"\"

Extrae los datos usando EXACTAMENTE las claves de la descripción. Devuelve solo el JSON sin explicaciones:

"""

# Efectua la inferencia del modelo.
def derive(service, query, max_tkns=2000) -> any:
    try:
        description = query.get("description", "")
        text = query.get("text", "")
        
        tmp_work_memory = []
        prompt = SYSTEM_PROMPT % description
        tmp_work_memory.append({"role": "system", "content": prompt})
        prompt = USER_PROMPT % text
        tmp_work_memory.append({"role": "user", "content": prompt})
        
        res = service.generate(tmp_work_memory, max_tokens=max_tkns)

        logging.info(f"[Celula][Extrac][Procesando]: {text}")        
        logging.info(f"[Celula][Extrac][Respuesta]: {res}")
        if not res or res == "":
            res = text
            logging.warning(f"[Celula][Extrac]: No obtener una respuesta.")
        return res.replace("*", "").strip()
    except Exception as e:
        logging.error(f"[Celula][Extrac]: Error al procesar: {text}")
        logging.error(e)
        return None
