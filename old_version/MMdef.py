from pylem import MorphanHolder, MorphLanguage
import re
from LoadJsonDict import FromJSON, ToJSON

# Инициализация морфологического анализатора
morphan = MorphanHolder(MorphLanguage.Russian)

# Инициализация json словарей
PREPOSITION_CASES = FromJSON("json/PREPOSITION_CASES_ru.json")
MORPH_FEATURE_MAP = FromJSON("json/MORPH_FEATURE_MAP.json")
POS_MAP = FromJSON("json/POS_MAP.json")


def parse_morph_features(morph_features, pos, lemma):
    """
    Преобразует множество морфологических признаков в словарь с удобными ключами.
    :param morph_features: Множество морфологических признаков, например {'fem', 'nom', 'sg', 'inanim'}.
    :return: Словарь с ключами 'case', 'number', 'gender', 'animacy', 'tense'.
    """

    # Инициализация словаря для результата
    result = {
        'case': [],#None,
        'number': [],#None,
        'gender': [],#None,
        'animacy': [],#None,
        'tense': [],#None
    }

    # Преобразование признаков
    VALID_CASES = {'nom', 'gen', 'dat', 'acc', 'ins','prp'}
    for feature in morph_features:

        if feature in VALID_CASES:
            result['case'] += [MORPH_FEATURE_MAP.get(feature)]

        elif feature in {'sg', 'pl'}:
            result['number'] += [MORPH_FEATURE_MAP.get(feature)]

        elif feature in {'masc', 'fem', 'neut'}:
            result['gender'] += [MORPH_FEATURE_MAP.get(feature)]

        elif feature in {'anim', 'inanim'}:
            result['animacy'] += [MORPH_FEATURE_MAP.get(feature)]

        elif feature in {'pres', 'past', 'futr'}:
            result['tense'] += [MORPH_FEATURE_MAP.get(feature)]

    if pos == "PREP":
        result["case"]+=PREPOSITION_CASES[lemma.lower()]

    return result


def normalize_pos(pos):
    """Нормализация частей речи."""
    return POS_MAP.get(pos, pos)  # Возвращаем нормализованную часть речи или исходное значение, если не найдено


def MorphAnalis(word):
    """Морфологический анализ слова."""

    likely_option = 0
    weight = 0
    data = []

    for i, lemmInfo in enumerate(morphan.lemmatize(word)):
        pos = normalize_pos(lemmInfo.part_of_speech)
        lemma = lemmInfo.lemma
        morph_features = parse_morph_features(lemmInfo.morph_features,pos,lemma)

        features = {
            "word": word,
            "lemma": lemma,
            "pos": pos,  # Нормализуем часть речи
            "case": morph_features["case"],
            "number": morph_features["number"],
            "gender": morph_features["gender"],
            "tense": morph_features["tense"],
            "animacy": morph_features["animacy"]
        }

        data.append(features)

        if lemmInfo.word_weight > weight:
            weight = lemmInfo.word_weight
            likely_option = i

    return data[likely_option]


def WordInfo(word, morphan = MorphanHolder(MorphLanguage.Russian)):
    #momsRus = morphan.synthesize(word, "N fem")["forms"]  # ,sg,gen ед.ч. р.п.
    date = []
    for lemmInfo in morphan.lemmatize(word):
        word_info = {
            "word": word,
            "lemma": lemmInfo.lemma,
            "morph": lemmInfo.morph_features,
            "pos": lemmInfo.part_of_speech,
            "weight": lemmInfo.word_weight,
            "homonym_weight": lemmInfo.homonym_weight,
            "predicted": lemmInfo.predicted,
            "predicted_by": lemmInfo.predicted_by
        }
        date +=[word_info]
        print(f"{word}: {lemmInfo.lemma}, {lemmInfo.morph_features},{lemmInfo.part_of_speech}, {lemmInfo.word_weight}, {lemmInfo.homonym_weight}, {lemmInfo.predicted}, {lemmInfo.predicted_by}")
    return date


def SplitToWord(sentence):
    """Разделение предложения на слова."""
    return re.findall(r'\b\w+\b', sentence)


#print(WordInfo("воды"))
#print("--------------------------------------------------------------------------------------------\n\n")