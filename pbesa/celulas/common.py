import re
import unicodedata

PHRASES = [
    "Qué", "que", "cómo", "por qué", "podrías decirme", "cuántas", "cuándo", "dónde", "quién", "cuál", "cuáles",
    "podrías informarme", "me podrías decir", "necesito saber", "es posible saber", "puedes explicarme",
    "tienes información sobre", "en qué consiste", "a qué se refiere", "de qué manera", "con qué propósito",
    "cuál es la razón", "qué cantidad", "qué tipo", "qué clase", "qué función", "qué uso", "qué implicaciones",
    "qué consecuencias", "qué efectos", "qué beneficios", "qué desventajas", "qué características", "qué requisitos",
    "qué procedimientos", "qué pasos", "qué alternativas", "qué opciones", "qué soluciones", "qué recomendaciones",
    "qué opiniones", "qué perspectivas", "qué punto de vista", "qué diferencia hay entre", "qué relación tiene con",
    "qué papel juega", "qué rol desempeña", "qué impacto tiene", "qué se sabe sobre", "qué se conoce de",
    "qué se entiende por", "qué significado tiene", "qué tan cierto es", "qué tan probable es", "qué tan frecuente es",
    "qué tan importante es", "qué tan grande es", "qué tan pequeño es", "qué tan lejos está", "qué tan cerca está",
    "qué tan rápido es", "qué tan lento es", "qué tan difícil es", "qué tan fácil es", "qué tan bueno es", "qué tan malo es",
    "qué tan efectivo es", "qué tan eficiente es"
]

def strip_accents(s: str) -> str:
    """Quita tildes/diacríticos dejando solo letras base."""
    return ''.join(ch for ch in unicodedata.normalize('NFD', s)
                   if unicodedata.category(ch) != 'Mn')

def to_regex_fragment(phrase: str) -> str:
    """Convierte una frase en un fragmento regex, permitiendo espacios variables."""
    norm = strip_accents(phrase).casefold()
    frag = re.escape(norm).replace(r'\ ', r'\s+')
    return frag

def make_pattern(phrases=PHRASES) -> re.Pattern:
    """Compila una sola regex que detecta cualquiera de las frases."""
    seen, frags = set(), []
    for p in phrases:
        f = to_regex_fragment(p)
        if f not in seen:
            seen.add(f)
            frags.append(f)
    # límites de palabra para evitar falsos positivos dentro de otras palabras
    pattern = r'\b(?:' + '|'.join(frags) + r')\b'
    return re.compile(pattern)

TRIGGER_RE = make_pattern()

def contains_trigger(text: str) -> bool:
    """True si el texto contiene alguna de las frases (con o sin tildes, cualquier may/min)."""
    tnorm = strip_accents(text).casefold()
    return bool(TRIGGER_RE.search(tnorm))
