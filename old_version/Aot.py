from pylem import MorphanHolder, MorphLanguage, MorphSourceDictHolder #from pylem import Lemmatizer, Tagger
import pylem
import re
import os
#from pylem.pylem_binary import PredictSuffixVector


def Sintaxis(text, morphan = MorphanHolder(MorphLanguage.English)):
    tokens = re.findall(r'\b\w+\b', text)
    #pos_tags = [tagger.tag(token) for token in tokens]
    mwz_path = os.path.join(os.path.dirname(__file__), '.venv/lib/python3.10/site-packages/pylem/morph_dict/data/Russian/project.mwz')
    holder = MorphSourceDictHolder(mwz_path)
    ells = MorphSourceDictHolder.predict_lemm(holder,"мама", 3,2)
    #for ell in ells:
    print(dir(ells))
    return tokens


#проверка корректности слова и исправление
def CheckCorrect(word, morphan = MorphanHolder(MorphLanguage.Russian)):
    if morphan.is_in_dictionary(word):
        return True,word
    else:
        correctWord = morphan.correct_misspell(word)
        if len(correctWord)!=0:
            print(f"Слово {word} было исправленно на {correctWord}.")
            return True, correctWord
    return False, word

def MorphAnalis(word, morphan = MorphanHolder(MorphLanguage.Russian)):
    data = list()
    for lemmInfo in morphan.lemmatize(word):
        data.append(f"{lemmInfo.lemma} : {lemmInfo.morph_features}")
    return data

#инф-я о слове
def WordLems(word, morphan = MorphanHolder(MorphLanguage.Russian)):
    correct, word = CheckCorrect(word, morphan)
    if correct:
        for lemmInfo in morphan.lemmatize(word):
            print(f"Информация о слове '{word}': {lemmInfo.lemma}, {lemmInfo.morph_features}")
        return morphan.lemmatize(word)
    else:
        print(f"Слово {word} не удалось найти")
        return None

#проход по каждому слову из предложения
def GetAtributsWordInText(text, morphan = MorphanHolder(MorphLanguage.Russian)):
    words_to_test = re.findall(r'\b\w+\b', text) #["mother", "father", "child", "unicorn","football","walking"]
    for word in words_to_test:
        WordLems(word, morphan)

#все словоформы слова с их описанием
def WordForms(word, morphan = MorphanHolder(MorphLanguage.Russian)):
    correct, word = CheckCorrect(word, morphan)
    if correct:
        momsRus = morphan.synthesize(word, "N fem")["forms"]  # ,sg,gen ед.ч. р.п.
        print(f"Все словоформы слова {word} с их последующим описанием:")
        for form in momsRus:
            for lemmInfo in morphan.lemmatize(form):
                # вывод информации о форме
                print(f"{form}: {lemmInfo.lemma}, {lemmInfo.morph_features},{lemmInfo.part_of_speech}, {lemmInfo.word_weight}, {lemmInfo.homonym_weight}, {lemmInfo.predicted}, {lemmInfo.predicted_by}")
        return momsRus
    else:
        print(f"Слово {word} не удалось найти")
        return None

#инф-я о слове в формате JSON
def WordLemsJSON(word, morphan = MorphanHolder(MorphLanguage.Russian)):
    for lemmInfoJson in morphan.lemmatize_json(word):
        print(f"Инф-я о слове {word} в формате json:\n {lemmInfoJson}")
    #print(f"Инф-я о слове {word} в формате json:\n {morphan.lemmatize_json(word)}")
    return morphan.lemmatize_json(word)

def test_pylem():
    textRUS = "Всем привет, этот файл отвечает за проверку библиотеки pylem."
    textENG = "Hello everyone, this file is responsible for checking the library"

    #print(    Sintaxis(textRUS))
    #print ("\nТЕСТ WordInText RUS:")
    #GetAtributsWordInText(textRUS, MorphanHolder(MorphLanguage.Russian))

    #print ("\nТЕСТ WordInText ENG:")
    #GetAtributsWordInText(textENG, MorphanHolder(MorphLanguage.English))

    #print ("\nТЕСТ WordForms:")
    WordForms("маму")

    #print ("\nТЕСТ LemaJSON:")
    #WordLemsJSON("папе")


if __name__ == "__main__":
    test_pylem()