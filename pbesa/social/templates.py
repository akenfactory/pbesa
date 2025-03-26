# -*- coding: utf-8 -*-
"""
----------------------------------------------------------
-------------------------- PBESA -------------------------
----------------------------------------------------------

@autor AKEN
@version 4.0.0
@date 05/02/25
"""

GET_DATE="""
 A partir la fecha actual: {fecha_actual}. A partir del siguiente texto: "{texto}" por favor identifica la fecha y hora. Responde solo en el siguiente formato: '%Y-%m-%d %H:%M:%S'. Si no puedes identificar la fecha responde solo con: 'N/A'
"""

AFIRMATIVE_RESPONSE="""
 Responde 'SI_ES' si el siguiente texto corresponde a una respuesta afirmativa a una pregunta cualquiera: "%s", Responde 'N/A' si no corresponde a una respuesta afirmativa o si no sabes.
"""