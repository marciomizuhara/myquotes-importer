import re


VOCABULARY_TYPE = 99

def get_type_and_note(note: str):
    note = note.strip()
    lower_note = note.lower()

    if lower_note.startswith('nota'):
        return -1, note

    if lower_note.startswith('vocab'):
        return VOCABULARY_TYPE, note[11:].strip()

    if lower_note.startswith('vermelho'):
        return 1, note[8:].strip()

    if lower_note.startswith('amarelo'):
        return 2, note[7:].strip()

    if lower_note.startswith('verde'):
        return 3, note[5:].strip()

    if lower_note.startswith('azul'):
        note_body = note[4:].strip()
        if 'hahaha' in lower_note or 'haha' in lower_note:
            return 4, note_body
        return 6, note_body

    if lower_note.startswith('ciano'):
        return 5, note[5:].strip()

    return 0, ''


def extract_rating_from_note(text: str):
    if not text:
        return None

    match = re.search(r'(\d+(?:\.\d+)?)', text)
    if not match:
        return None

    try:
        value = float(match.group(1))
        if 0.0 <= value <= 5.0:
            return round(value, 1)
    except ValueError:
        pass

    return None
