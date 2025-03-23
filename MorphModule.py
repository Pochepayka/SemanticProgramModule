from pylem import MorphanHolder, MorphLanguage
import re
from LoadJsonDict import FromJSON, ToJSON
from ClauseSpliter import ClauseSplitter


class MorphAnalyzer:
    def __init__(self, lang=MorphLanguage.Russian,
                 prep_cases_path="json/PREPOSITION_CASES_ru.json",
                 morph_feat_path="json/MORPH_FEATURE_MAP.json",
                 pos_map_path="json/POS_MAP.json"):

        # Инициализация анализатора
        self.morphan = MorphanHolder(lang)

        # Загрузка словарей
        self.PREPOSITION_CASES = FromJSON(prep_cases_path)
        self.MORPH_FEATURE_MAP = FromJSON(morph_feat_path)
        self.POS_MAP = FromJSON(pos_map_path)

        self.spliter = ClauseSplitter()

    # def analyze_text(self, words):
    #     result = [self.analyze_word(word) for word in words]#self.spliter.split_into_words(graphems)]
    #     #print(f"Морфологический анализ:\n{result}\n")
    #     return result

    def analyze_word(self, word):
        """Основной метод морфологического анализа"""
        likely_option = 0
        weight = 0
        data = []
        is_correct, is_change, word = self.check_correct(word)
        if is_correct:
            for i, lemmInfo in enumerate(self.morphan.lemmatize(word)):
                pos = self.normalize_pos(lemmInfo.part_of_speech)
                lemma = lemmInfo.lemma
                morph_features = self.parse_morph_features(
                    lemmInfo.morph_features,
                    pos,
                    lemma,
                    word
                )

                features = {
                    "word": word,
                    "lemma": lemma,
                    "pos": pos,
                    "case": morph_features["case"],
                    "number": morph_features["number"],
                    "gender": morph_features["gender"],
                    "tense": morph_features["tense"],
                    "animacy": morph_features["animacy"],
                    "trans": morph_features["trans"],
                    #"pledge": morph_features["pledge"],
                    "type": morph_features["type"],
                    "variants": morph_features["variants"]
                }

                data.append(features)

                if lemmInfo.word_weight >= weight:
                    weight = lemmInfo.word_weight
                    likely_option = i
            if len(data)>0:
                return data[likely_option]

        return {"word": word,"lemma": word,"pos": [],"case": [],"number": [],"gender": [],"tense": [],"animacy": []}

    def parse_morph_features(self, morph_features, pos, lemma, word):
        """Преобразует морфологические признаки в структурированный словарь"""
        result = {
            'case': [],
            'number': [],
            'gender': [],
            'animacy': [],
            'tense': [],
            "trans" : [],
            "type" : [],
            # "pledge" : [],
            "variants": [],
        }

        VALID_CASES = {'nom', 'gen', 'dat', 'acc', 'ins', 'prp'}

        for feature in morph_features:
            if feature in VALID_CASES:
                result['case'].append(self.MORPH_FEATURE_MAP.get(feature))
            elif feature in {'sg', 'pl'}:
                result['number'].append(self.MORPH_FEATURE_MAP.get(feature))
            elif feature in {'mas', 'fem', 'neu'}:
                result['gender'].append(self.MORPH_FEATURE_MAP.get(feature))
            elif feature in {'anim', 'inanim'}:
                result['animacy'].append(self.MORPH_FEATURE_MAP.get(feature))
            elif feature in {'pres', 'past', 'futr'}:
                result['tense'].append(self.MORPH_FEATURE_MAP.get(feature))
            elif feature in {'trans', 'intrans'}:
                result['trans'].append(self.MORPH_FEATURE_MAP.get(feature))
            elif feature in {'perf','imperf'}:
                result['type'].append(self.MORPH_FEATURE_MAP.get(feature))
            # elif feature in {}:
            #     result['pledge'].append(self.MORPH_FEATURE_MAP.get(feature))


        if pos == "PREP":
            result["case"] += self.PREPOSITION_CASES.get(lemma.lower(), [])


        if pos in ["NOUN","NPRO"]:
            inverted_MORPH_FEATURE_MAP = {value: key for key, value in self.MORPH_FEATURE_MAP.items()}

            numbers = [inverted_MORPH_FEATURE_MAP.get(number) for number in result.get("number")]
            if not numbers:
                numbers = [""]
            cases = [inverted_MORPH_FEATURE_MAP.get(case) for case in result.get("case")]
            if not cases:
                cases = [""]
            genders = [inverted_MORPH_FEATURE_MAP.get(gender) for gender in result.get("gender")]
            if not genders:
                genders = [""]
            variants = []
            for num in numbers:
                for case in cases:
                    for gender in genders:
                        forms = self.morphan.synthesize(lemma, f"N  {case} {num} {gender}")["forms"]  # ,sg,gen ед.ч. р.п.
                        #print(f"Все словоформы слова {lemma} с их последующим описанием:{forms}")
                        for word_form in forms:
                            if word.lower() == word_form.lower() and \
                                    not([[self.MORPH_FEATURE_MAP.get(case), \
                                          self.MORPH_FEATURE_MAP.get(num),\
                                          self.MORPH_FEATURE_MAP.get(gender)]] in variants):

                                variants += [[self.MORPH_FEATURE_MAP.get(case),\
                                              self.MORPH_FEATURE_MAP.get(num),\
                                              self.MORPH_FEATURE_MAP.get(gender)]]
            result["variants"] = variants


        return result

    def normalize_pos(self, pos):
        """Нормализация частей речи"""
        return self.POS_MAP.get(pos, pos)

    def get_word_info(self, word):
        """Получение полной информации о слове"""
        results = []
        for lemmInfo in self.morphan.lemmatize(word):
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
            results.append(word_info)
        return results

    def check_correct(self, word):
        if self.morphan.is_in_dictionary(word):
            return True, False, word
        else:
            correctWord = self.morphan.correct_misspell(word)
            if len(correctWord) != 0:
                print(f"Слово {word} может быть исправленно на {correctWord}.")

                return True, True, correctWord[0]
        return False, False, word



# Пример использования
if __name__ == "__main__":
    analyzer = MorphAnalyzer()

    text = ["мой", "пятый" ]

    #word = "гуляю"
    for word in text:
        # Анализ слова
        print("\nАнализ слова:")
        print(analyzer.analyze_word(word))

        # Полная информация о слове
        print("\nПолная информация:")
        for info in analyzer.get_word_info(word):
            print(info)
