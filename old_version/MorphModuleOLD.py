from fontTools.misc.cython import returns
from pylem import MorphanHolder, MorphLanguage, MorphSourceDictHolder #from pylem import Lemmatizer, Tagger
import re

import json
import itertools


morphan = MorphanHolder(MorphLanguage.Russian)

def MorphAnalisNEW(word):
    """Морфологический анализ слова."""
    data = []
    for lemmInfo in morphan.lemmatize(word):
        #morph_features = parse_morph_features(lemmInfo.morph_features)
        features = {
            "word": word,
            "lemma": lemmInfo.lemma,
            "pos": lemmInfo.part_of_speech,
            "morph_features": lemmInfo.morph_features,
        }
        data.append(features)
    print(data)
    return data

def MorphAnalis(word, morphan = MorphanHolder(MorphLanguage.Russian)):
    data = []
    for lemmInfo in morphan.lemmatize(word):
        data+=[f"{lemmInfo.lemma} : {lemmInfo.morph_features}"]
    return data

def GetPartOfSpeech(word, morphan = MorphanHolder(MorphLanguage.Russian)):
    data = []
    for lemmInfo in morphan.lemmatize(word):
        data+=[f"{lemmInfo.lemma} : {lemmInfo.part_of_speech}"]
    return data


def GenerateAllTokens(data):
    # Генерация всех возможных комбинаций токенов
    combinations = list(itertools.product(*data))
    return combinations





def SplitToWord (sentence):
    words = re.findall(r'\b\w+\b', sentence)
    return words


def FromJSON(name_dict):
    """Импортирование словаря из JSON-файла."""
    with open(name_dict, 'r', encoding='utf-8') as f:
        loaded_dict = json.load(f)
    return loaded_dict


def ToJSON(my_dict, name_dict="new_dict"):
    """Сохранение словаря в JSON-файл."""

    # Преобразуем множества в списки
    def convert_sets_to_lists(obj):
        if isinstance(obj, dict):
            return {key: convert_sets_to_lists(value) for key, value in obj.items()}
        elif isinstance(obj, set):
            return list(obj)  # Преобразуем множество в список
        elif isinstance(obj, list):
            return [convert_sets_to_lists(item) for item in obj]
        else:
            return obj

    # Преобразуем входной словарь
    my_dict = convert_sets_to_lists(my_dict)

    # Сохраняем преобразованный словарь в JSON
    with open(name_dict + '.json', 'w', encoding='utf-8') as f:
        json.dump(my_dict, f, ensure_ascii=False)

    return name_dict + '.json'


def ExpandAbbreviations(data, lang="ru"):
    # Словарь с сокращениями и их полными формами


    expanded_data = []

    for entry in data:
        expanded_entry = []

        for item in entry:
            # Разделяем слово и его характеристики
            word, traits = item.split(': ')
            traits_set = eval(traits)  # Преобразуем строку в множество

            if lang == "ru":
                abbreviations = FromJSON("abbreviations_ru.json")
            elif lang == "eg":
                abbreviations = FromJSON("abbreviations_eg.json")
            else:
                abbreviations = FromJSON("abbreviations_ru.json")
                print("Нет такого языка")

            # Заменяем сокращения на полные формы
            expanded_traits = {abbreviations.get(trait, trait) for trait in traits_set}
            expanded_entry += [f"{word}: {expanded_traits}"]

        expanded_data += [expanded_entry]

    return expanded_data



PREPOSITION_CASES = {
    "без": {"gen"},  # Родительный падеж [9]
    "вне": {"gen"},  # Родительный падеж [9]
    "возле": {"gen"}, # Родительный падеж [9]
    "впереди": {"gen"}, # Родительный падеж [9]
    "вроде": {"gen"}, # Родительный падеж [9]
    "вокруг": {"gen"}, # Родительный падеж [9]
    "в продолжение": {"gen"}, # Родительный падеж [9]
    "вследствие": {"gen"}, # Родительный падеж [9]
    "в течение": {"gen"}, # Родительный падеж [9]
    "до": {"gen"},  # Родительный падеж [9]
    "для": {"gen"},  # Родительный падеж [9]
    "из": {"gen"},  # Родительный падеж [9]
    "из-за": {"gen"},  # Родительный падеж [9]
    "из-под": {"gen"}, # Родительный падеж [9]
    "кроме": {"gen"}, # Родительный падеж [9]
    "между": {"gen", "ins"},  # Родительный или творительный падеж (в зависимости от значения) [9]
    "от": {"gen"},  # Родительный падеж [9]
    "около": {"gen"}, # Родительный падеж [9]
    "за": {"acc", "ins"}, # Винительный или творительный падеж (в зависимости от значения) [4]
    "на": {"acc", "dat", "prep"}, # Винительный, дательный или предложный падеж (в зависимости от значения) [2]
    "в": {"acc", "prep"}, # Винительный или предложный падеж (в зависимости от значения) [2, 7]
    "по": {"dat", "acc", "prep"}, # Дательный, винительный или предложный падеж (в зависимости от значения)
    "с": {"gen", "acc", "ins"}, # Родительный, винительный или творительный падеж (в зависимости от значения)
    "над": {"ins"}, # Творительный падеж
    "перед": {"ins"} # Творительный падеж
}
#ToJSON(PREPOSITION_CASES,"PREPOSITION_CASES_ru")