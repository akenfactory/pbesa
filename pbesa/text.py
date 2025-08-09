import string
import unicodedata
from fuzzywuzzy import fuzz

def sim(text1, text2) -> any:
    similitud = fuzz.ratio(text1.lower(), text2.lower())
    if similitud >= 79:
        return "SIMILAR"
    else:
        return "NO SIMILAR"

def normalizar_texto(stopwords_es, texto: str) -> str:
    """
    Normaliza el texto eliminando signos de puntuación y tildes.

    Args:
        texto: El string de entrada que se va a limpiar.

    Returns:
        El string limpiado.
    """
    texto = texto.lower() \
        .replace('¿', '') \
        .replace('?', '')
    texto_sin_tildes = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    puntuacion_a_eliminar = ''.join(c for c in string.punctuation if c not in '.,:')
    tabla_traduccion = str.maketrans('', '', puntuacion_a_eliminar)
    res = texto_sin_tildes.translate(tabla_traduccion)
    res = res.strip()
    res = res.split()
    res = [palabra for palabra in res if palabra not in stopwords_es]
    res = ' '.join(res)
    return res

def extractor_texto(query: str, textos: list) -> str:
    """
    Extrae el texto de la respuesta.
    """
    query_normalizado = normalizar_texto(query)
    query_split = query_normalizado.split()
    major = 0
    major_texto = ""
    for texto in textos:
        score = 0
        original_texto = texto
        texto = normalizar_texto(texto)
        texto_split = texto.split()
        for word in query_split:
            for word_texto in texto_split:
                if sim(word, word_texto) == "SIMILAR":
                    score += 1
                    break
        if score >= major and score > 0:
            major = score
            if score > major:
                major_texto = original_texto
            else:
                major_texto += " " + original_texto
    return major_texto
