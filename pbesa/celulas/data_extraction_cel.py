import re
import json
import logging

SYSTEM_PROMPT = """
Eres un generador de JSON. Tu tarea es extraer la información proporcionada por el usuario, basándose en la descripción de los campos requeridos, y formatearla como un objeto JSON.

**Descripción de los campos requeridos:**
%s

**Instrucciones para la extracción y formato JSON:**
1.  Identifica cada valor proporcionado por el usuario y asócialo con su campo correspondiente de la descripción.
2.  Los nombres de los campos en el JSON deben ser exactamente los de la "Descripción de los campos requeridos", sin las llaves ni guiones.
3.  Si un campo no tiene un valor claro en la respuesta del usuario, omítelo del JSON.
4.  Asegúrate de que el JSON sea válido.

**Ejemplo de cómo el usuario podría responder y cómo debe ser el JSON resultante (basado en la descripción de campos "datos del Demandante: - Correo electrónico - Primer Nombre - Segundo Nombre - Primer Apellido - Segundo Apellido - Tipo de documento - Identificación - País donde se hace la solicitud - Departamento / Estado / Provincia donde se hace la solicitud - Municipio / Ciudad donde se hace la solicitud - Dirección notificación judicial"):**

**Respuesta del usuario:** "micorreo@correo.com, Fabian, Jose, Roldan, Piñeros, CC, 123456789, Colombia, Cundinamarca, Bogotá, Calle 100 #10-20"
**JSON resultante:**
```json
{
  "Correo electrónico": "micorreo@correo.com",
  "Primer Nombre": "Fabian",
  "Segundo Nombre": "Jose",
  "Primer Apellido": "Roldan",
  "Segundo Apellido": "Piñeros",
  "Tipo de documento": "CC",
  "Identificación": "123456789",
  "País donde se hace la solicitud": "Colombia",
  "Departamento / Estado / Provincia donde se hace la solicitud": "Cundinamarca",
  "Municipio / Ciudad donde se hace la solicitud": "Bogotá",
  "Dirección notificación judicial": "Calle 100 #10-20"
}
"""

USER_PROMPT = """

Texto: "%s"

Clasificación:
"""

def extract_field_constraints(text):    
    field_constraints = {}
    start_index = text.find(':')
    if start_index != -1:
        text = text[start_index+1:].strip()
    lines = text.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        clean_line = line.lstrip('- ').strip()
        is_obligatorio = True
        if '(obligatorio)' in clean_line:
            is_obligatorio = True
            field_name = clean_line.replace('(obligatorio)', '').strip()
        elif '(no obligatorio)' in clean_line:
            is_obligatorio = False
            field_name = clean_line.replace('(no obligatorio)', '').strip()
        else:
            field_name = clean_line.strip()
        field_constraints[field_name] = is_obligatorio
    return field_constraints

def validar_campo(validaciones_campos, nombre_campo, valor):
    if nombre_campo in validaciones_campos:
        config = validaciones_campos[nombre_campo]
        regex = config["validacion"]
        mensaje = config["mensaje_error"]
        if re.fullmatch(regex, valor):
            return True, None
        else:
            return False, mensaje
    else:
        return False, f"No se encontró configuración de validación para el campo: {nombre_campo}"

def procesar_datos(validaciones_campos, description, datos):
    """ Procesa los datos extraídos y valida cada campo """
    # Obtiene los campos
    field_constraints = extract_field_constraints(description)
    logging.info("Campos extraídos:")
    logging.info(json.dumps(field_constraints, indent=4))
    for field, is_required in field_constraints.items():
        if is_required and field not in datos:
            logging.error(f"Falta el campo obligatorio: {field}")
            return None
        if field not in datos:
            datos[field] = None
    logging.info("Los campos estan completos.")
    # Validar los campos extraídos
    errores = []
    resultado = {}
    for campo, valor in datos.items():
        valido, mensaje_error = validar_campo(validaciones_campos, campo, str(valor))
        if not valido:
            errores.append(f"Error en '{campo}': {mensaje_error}")
        else:
            resultado[campo] = valor
    if errores:
        logging.error("Errores de validación encontrados:")
        for error in errores:
            logging.error(error)
        return None, error
    else:
        logging.info("Todos los campos validados correctamente.")
        return resultado, None

def get_struct(text):
    json_start = text.find('{')
    json_end = text.rfind('}') + 1
    json_string = text[json_start:json_end]
    return json.loads(json_string)

# Efectua la inferencia del modelo.
def call_engine(service, description, text) -> any:
    try:
        tmp_work_memory = []
        system_prompt  = SYSTEM_PROMPT % description
        tmp_work_memory.append({"role": "system", "content": system_prompt})
        user_prompt = USER_PROMPT % text
        tmp_work_memory.append({"role": "user", "content": user_prompt})
        logging.info(f"Enviando solicitud al modelo...")
        res = service.generate(tmp_work_memory)
        result = get_struct(res)
        logging.info(f"El model ha respondido con éxito.")
        return result
    except Exception as e:
        logging.error(f"El modelo ha fallado al procesar la solicitud.")
        logging.error(f"Error al procesar: {text}")
        logging.error(e)
        return None

def derive(description, text) -> any:
    result = derive(description, text)
    if result:
        logging.info("\n" *3)
        logging.info(f"Descripción: {description}")
        logging.info(f"Texto: {text}")
        logging.info(f"Resultado:")            
        logging.info(json.dumps(result, indent=4))
        logging.info(f"Esperado:")
        expected = json.loads(expected)
        logging.info(json.dumps(expected, indent=4))
        logging.info("\n" *3)
        return procesar_datos(description, result)
    return None, "no pude identificar los datos en el texto proporcionado."
