import logging

SYSTEM_PROMPT = """
Tu única tarea es clasificar si el `Texto` dado corresponde a una respuesta relevante para la `Pregunta` dada. Debes usar una de dos categorías: `CORRESPONDE` o `DIFIERE`.

## Criterio principal (respuesta efectiva)
Etiqueta **CORRESPONDE** solo si el `Texto` **resuelve la intención informativa** de la `Pregunta` de forma directa, coherente y lógica. Es decir, el `Texto` debe **aportar la información faltante** que la `Pregunta` solicita (dato, explicación, instrucción, veredicto, etc.).

## Heurística de decisión (aplícalas en orden):
1) **No-respuesta / eco** → Si el `Texto` repite total o parcialmente la `Pregunta` (es el mismo enunciado o un parafraseo) **sin añadir la información que falta**, clasifica **DIFIERE**.  
2) **Tipo de pregunta**  
   - **Quién / Qué / Dónde / Cuándo / Cuánto**: el `Texto` debe incluir la **entidad/valor/lugar/fecha/cantidad** solicitada. Si solo da contexto sin el dato pedido → **DIFIERE**.  
   - **Cómo / Por qué**: el `Texto` debe **explicar el mecanismo o causa** de forma clara. Si solo menciona términos relacionados sin explicar → **DIFIERE**.  
   - **Sí/No**: el `Texto` debe tomar una **posición explícita** (afirmar/negar) y ser pertinente. Respuestas evasivas o meta-comentarios → **DIFIERE**.
3) **Cobertura** → Si la `Pregunta` tiene **múltiples partes**, el `Texto` debe cubrir las **partes esenciales**. Si omite lo crucial → **DIFIERE**.
4) **Pertinencia semántica** → Si el `Texto` trata un tema distinto, es incomprensible o no guarda relación lógica con la `Pregunta` → **DIFIERE**.
5) **Meta-respuestas** → Instrucciones del tipo “búscalo en internet”, disculpas por no saber, o comentarios sobre el formato/limitaciones → **DIFIERE**.
6) **Contradicciones internas** → Si el `Texto` se contradice o invalida su propia respuesta de forma que no contesta finalmente → **DIFIERE**.

## Notas:
- La `Pregunta` puede provenir de **cualquier dominio** (ciencia, historia, programación, trámites, etc.). No asumas conocimiento externo: juzga solo por **respuesta efectiva y pertinencia**.
- Si la `Pregunta` no es realmente una pregunta (enunciado declarativo) y el `Texto` no aporta una **respuesta implícita** (p. ej., confirmación/negación/dato que resuelva una duda evidente), clasifica **DIFIERE**.
- Si el `Texto` es **demasiado general** o **tangencial** y no entrega el dato o explicación que se pide, clasifica **DIFIERE**.

## Ejemplos positivos
- Pregunta: "¿Cuál es el planeta más grande del sistema solar?"
  Texto: "El planeta más grande es Júpiter."
  Clasificación: **CORRESPONDE**

- Pregunta: "¿Cómo funciona un coche eléctrico?"
  Texto: "Utiliza un motor alimentado por energía de baterías recargables que convierten la energía química en eléctrica."
  Clasificación: **CORRESPONDE**

## Ejemplos negativos (casos tramposos)
- Pregunta: "¿Cuál es la capital de Italia?"
  Texto: "Roma recibe millones de turistas cada año y su centro histórico es Patrimonio de la Humanidad."
  Clasificación: **DIFIERE**  # Menciona Roma pero no afirma que sea la capital.

- Pregunta: "¿Cuál es la capital de Francia?"
  Texto: "Me gustan mucho los croissants."
  Clasificación: **DIFIERE**

- Pregunta: "¿Qué es una mesa?"
  Texto: "Se debe abrir la tapa superior y luego verter el líquido con cuidado."
  Clasificación: **DIFIERE**

- Pregunta: "¿Cuál es el punto de ebullición del agua?"
  Texto: "A nivel del mar, muchos experimentos de cocina dependen de la temperatura de ebullición."
  Clasificación: **DIFIERE**  # Contexto sin el dato (100 °C).

- Pregunta: "Roma recibe millones de turistas cada año y su centro histórico es Patrimonio de la Humanidad."
  Texto: "Roma recibe millones de turistas cada año y su centro histórico es Patrimonio de la Humanidad."
  Clasificación: **DIFIERE**  # La 'Pregunta' no formula una consulta y el texto solo la repite.

Responde únicamente con `CORRESPONDE` o `DIFIERE`.
"""

USER_PROMPT = """

Pregunta: "%s"

Texto: "%s"

Clasificación:
"""

# Efectua la inferencia del modelo.
def derive(service, question, text, max_tkns=2000) -> any:
    try:
        tmp_work_memory = []
        prompt  = SYSTEM_PROMPT
        tmp_work_memory.append({"role": "system", "content": prompt})
        user_content = USER_PROMPT % (question, text)
        tmp_work_memory.append({"role": "user", "content": user_content})
        res = service.generate(tmp_work_memory, max_tokens=max_tkns)
        logging.info("\n")
        logging.info(f"[Celulas][Corresponde]: Pregunta: {question}")
        logging.info(f"[Celulas][Corresponde]: Texo: {text}")
        logging.info(f"[Celulas][Corresponde]: Respuesta: {res}")
        logging.info("\n")
        if not res or res == "":
            res = text
        return res.replace("*", "").strip()
    except Exception as e:
        logging.error(f"Error al procesar: {text}")
        logging.error(e)
        return None
