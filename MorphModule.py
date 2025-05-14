from pylem import MorphanHolder, MorphLanguage # type: ignore
from LoadJsonDict import FromJSON

class MorphAnalyzer:
    def __init__(self, langRUS=MorphLanguage.Russian,
                 quantitative_numeral_path="json/QUANTITATIVE_NUMERAL.json",
                 collective_numeral_path="json/COLLECTIVE_NUMERAL.json",
                 prep_cases_path="json/PREPOSITION_CASES_ru.json",
                 morph_feat_path="json/MORPH_FEATURE_MAP.json",
                 pos_map_path="json/POS_MAP.json"):

        # Инициализация анализатора
        self.morphan = MorphanHolder(langRUS)
        #pylem.MorphanHolder(pylem.MorphLanguage.Russian)
        # Загрузка словарей
        self.QUANTITATIVE_NUMERAL = FromJSON(quantitative_numeral_path)
        self.COLLECTIVE_NUMERAL = FromJSON(collective_numeral_path)
        self.PREPOSITION_CASES = FromJSON(prep_cases_path)
        self.MORPH_FEATURE_MAP = FromJSON(morph_feat_path)
        self.POS_MAP = FromJSON(pos_map_path)

    # def analyze_text(self, words):
    #     result = [self.analyze_word(word) for word in words]#self.spliter.split_into_words(graphems)]
    #     #print(f"Морфологический анализ:\n{result}\n")
    #     return result

    def analyze_word(self, word, num_in_text=0,descriptors=["RLE"]):
        """Основной метод морфологического анализа"""
        likely_option = 0
        weight = -1
        max_len_features = 0
        data = []

        is_rus_lemma = "RLE" in descriptors
        is_eng_lemma = "LLE" in descriptors
        is_composite = "COMPOSITE" in descriptors
        is_maybe_name = "NAM?" in descriptors
        is_URL = "URL" in descriptors or "EA" in descriptors or "FILE" in descriptors
        is_digit = "DC" in descriptors or "DSC"in descriptors

        # if is_composite or is_URL or is_digit or is_eng_lemma:
        #     return {"word": word,"lemma": word,"pos": []}


        is_correct, is_change = False, False
        if is_rus_lemma:
            is_correct, is_change, word = self.check_correct(word)

        if is_correct or not is_change and (is_rus_lemma or is_digit or is_URL ):
            for i, lemmInfo in enumerate(self.morphan.lemmatize(word)):
                pos = self.normalize_pos(lemmInfo.part_of_speech)
                lemma = lemmInfo.lemma
                morph_features = self.parse_morph_features(
                    lemmInfo.morph_features, pos, lemma, word, is_correct)

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
                    "pledge": morph_features["pledge"],
                    "type": morph_features["type"],
                    "variants": morph_features["variants"],
                    "is_numeral": morph_features["is_numeral"],
                    "is_proper_name": morph_features["is_proper_name"],
                    "num_in_text": num_in_text,
                    "descriptors": descriptors
                }

                if not is_correct and not is_change:
                    features["is_proper_name"] = True

                data.append(features)

                if lemmInfo.word_weight > weight:
                    weight = lemmInfo.word_weight
                    max_len_features = len(lemmInfo.morph_features)
                    likely_option = i
                elif (lemmInfo.word_weight == weight and\
                      len(lemmInfo.morph_features) > max_len_features):
                    max_len_features = len(lemmInfo.morph_features)
                    likely_option = i



            if len(data)>0:
                return data[likely_option]

        return {
                    "word": word,
                    "lemma": "НЕИЗВЕСТНАЯ_ЛЕММА",
                    "pos": "НЕТ",
                    "case": [],
                    "number": [],
                    "gender": [],
                    "tense": [],
                    "animacy": [],
                    "trans": [],
                    "pledge": [],
                    "type": [],
                    "variants": [],
                    "is_numeral": False,
                    "is_proper_name": True,
                    "num_in_text": num_in_text,
                    "descriptors": descriptors
                }
    #{"word": word,"lemma": word,"pos": []}#None#

    def parse_morph_features(self, morph_features, pos, lemma, word, is_correct):
        """Преобразует морфологические признаки в структурированный словарь"""
        result = {
            'case': [],
            'number': [],
            'gender': [],
            'animacy': [],
            'tense': [],
            "trans" : [],
            "type" : [],
            "pledge" : [],
            "variants": [],
            "is_numeral" : False,
            "is_proper_name" : False,
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
            elif feature in {"pass", "act"}:
                result['pledge'].append(self.MORPH_FEATURE_MAP.get(feature))
            elif feature in {"loc", "name", "surname", "sing_tant"}:
                result['is_proper_name'] = True

        if pos == "NOUN" and not result["number"]:
            result["number"] += self.QUANTITATIVE_NUMERAL.get(lemma, [])
            result["number"] += self.COLLECTIVE_NUMERAL.get(lemma, [])
            result["is_numeral"] = True

        if pos == "NOUN_ADVB":
            result["is_numeral"] = True

        if pos == "PREP":
            result["case"] += self.PREPOSITION_CASES.get(lemma.lower(), [])


        if pos in ["NOUN","NPRO"] and is_correct:
            result = self.collect_variants(result, lemma, word, pos)

        return result

    def collect_variants(self,result, lemma, word, pos):

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
                    if pos == "NPRO":
                        forms = self.morphan.synthesize(lemma, f"NP {case} {num} {gender}")["forms"]
                    else:
                        forms = self.morphan.synthesize(lemma, f"N  {case} {num} {gender}")["forms"]
                    # print(f"Все словоформы слова {lemma} с их последующим описанием:{forms}")
                    for word_form in forms:
                        if (word.lower() == word_form.lower() or result.get("is_numeral")) and \
                                not ([[self.MORPH_FEATURE_MAP.get(case), \
                                       self.MORPH_FEATURE_MAP.get(num), \
                                       self.MORPH_FEATURE_MAP.get(gender)]] in variants):
                            variants += [[self.MORPH_FEATURE_MAP.get(case), \
                                          self.MORPH_FEATURE_MAP.get(num), \
                                          self.MORPH_FEATURE_MAP.get(gender)]]

                    if (result.get("is_numeral")) and \
                            not ([[self.MORPH_FEATURE_MAP.get(case), \
                                   self.MORPH_FEATURE_MAP.get(num), \
                                   self.MORPH_FEATURE_MAP.get(gender)]] in variants):
                        variants += [[self.MORPH_FEATURE_MAP.get(case), \
                                      self.MORPH_FEATURE_MAP.get(num), \
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
            correct_words = self.morphan.correct_misspell(word)
            if len(correct_words) != 0:
                #print(f"Слово {word} может быть исправленно на {correct_words}.")
                return True, True,  self.the_most_popular_word(correct_words)# self.find_most_similar_word(word, correctWord)#correctWord[0]
        return False, False, word

    def the_most_popular_word(self, list):
        output = ""
        max_weight = -1
        for correct_word in list:
            weight_lem = -1
            for i, lemmInfo in enumerate(self.morphan.lemmatize(correct_word)):
                if lemmInfo.word_weight >= weight_lem:
                    weight_lem = lemmInfo.word_weight

            if weight_lem > max_weight:
                max_weight = weight_lem
                output = correct_word
        return output

    def levenshtein_distance(self, s1, s2):
        """Вычисляет расстояние Левенштейна между двумя строками."""
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def find_most_similar_word(self,main_word, word_list):
        """Находит самое похожее слово из списка на основное слово."""
        min_distance = float('inf')
        most_similar_word = ""

        for word in word_list:
            distance = self.levenshtein_distance(main_word, word)
            if distance < min_distance:
                min_distance = distance
                most_similar_word = word

        return most_similar_word



# Пример использования
if __name__ == "__main__":
    analyzer = MorphAnalyzer()

    text = ["не", "бы", "же"]

    #print(analyzer.check_correct("чтл"))

    #print(analyzer.morphan.synthesize("ДЕСЯТЬ", f"N"))

    #word = "гуляю"
    for word in text:
        # Анализ слова
        print("\nАнализ слова:")
        print(analyzer.analyze_word(word))

        # Полная информация о слове
        print("\nПолная информация:")
        for info in analyzer.get_word_info(word):
            print(info)
