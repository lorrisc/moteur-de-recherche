# Retourne le langage nltk correspondant à la langue du site
def lang_to_nltk_lang(lang):
    lang_mapping = {
        'en': 'english',
        'en-US': 'english',
        'en-us': 'english',
        'fr': 'french',
        'fr-FR': 'french',
        'zh': 'chinese',
        'de': 'german',
        'it': 'italian',
        'es': 'spanish',
        'ru': 'russian',
        'pt-BR': 'portuguese',
        'ar': 'arabic',
        
        'az': 'Azerbaijani',
        'eu': 'Basque',
        'bn': 'Bengali',
        'ca': 'Catalan',
        'da': 'Danish',
        'nl': 'Dutch',
        'fi': 'Finnish',
        'el': 'Greek',
        'he': 'Hebrew',
        'hu': 'Hungarian',
        'id': 'Indonesian',
        'kk': 'Kazakh',
        'ne': 'Nepali',
        'no': 'Norwegian',
        'ro': 'Romanian',
        'sl': 'Slovene',
        'sv': 'Swedish',
        'tg': 'Tajik',
        'tr': 'Turkish',
    }

    # Langue non supportée en 2024/01
    # 'uk': 'ukrainian',
    # 'fa': 'persian',
    # 'ja': 'japanese',
    # 'gl': 'galician',



    # Si langue non définie, retourner anglais
    return lang_mapping.get(lang, 'english')