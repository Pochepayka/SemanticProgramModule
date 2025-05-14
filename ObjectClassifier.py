from DownloadModels import load_w2v_rus
from typing import List, Dict, Optional

class ObjectClassifier:
    def __init__(
        self,
        word2vec_model_path: str = "word2vec-ruscorpora-300",
        use_bert: bool = False,
        custom_exceptions: Optional[Dict] = None,
        custom_rules: Optional[List[Dict]] = None
    ):
        """
        Инициализация классификатора.
        
        :param word2vec_model_path: путь к модели Word2Vec
        :param use_bert: использовать ли BERT для контекстного анализа
        :param custom_exceptions: пользовательские исключения
        :param custom_rules: пользовательские правила
        """
        # Загрузка модели Word2Vec
        self.model = load_w2v_rus()
        
        # Инициализация BERT (опционально)
        self.use_bert = use_bert
        if use_bert:
            from transformers import pipeline
            self.ner_pipeline = pipeline("ner", model="DeepPavlov/rubert-base-cased")
        
        # База исключений
        self.exceptions = {
            # Инструменты
            "балалайке": "инструмент",
            "гитаре": "инструмент",
            "молотке": "инструмент",
            "компьютере": "инструмент",
            
            # Локации
            "столе": "локация",
            "улице": "локация",
            "комнате": "локация",
            "площади": "локация",
            
            # Время
            "минуте": "время",
            "году": "время",
            "сутках": "время",
            
            # Объекты действия
            "документе": "объект_действия",
            "книге": "объект_действия",
        }

        
        if custom_exceptions:
            self.exceptions.update(custom_exceptions)
        
        # Контекстные правила
        self.context_rules = [
            # === Локация ===
            {
                "prepositions": ["на", "в", "под", "над"],
                "case": "prepositional",
                "semantic_keywords": ["место", "город", "помещение", "улица"],
                "category": "локация"
            },
            {
                "prepositions": ["к", "от"],
                "case": "dative",
                "semantic_keywords": ["направление", "точка"],
                "category": "локация"
            },

            # === Инструмент ===
            {
                "prepositions": ["с", "при помощи"],
                "case": "instrumental",
                "semantic_keywords": ["инструмент", "орудие", "устройство"],
                "category": "инструмент"
            },
            {
                "prepositions": ["на"],
                "case": "prepositional",
                "semantic_keywords": ["музыкальный_инструмент"],
                "category": "инструмент"
            },

            # === Время ===
            {
                "prepositions": ["в", "за", "в течение"],
                "case": ["accusative", "genitive"],
                "semantic_keywords": ["время", "период", "длительность"],
                "category": "время"
            },
            {
                "prepositions": ["до", "после"],
                "case": "genitive",
                "semantic_keywords": ["событие", "момент"],
                "category": "время"
            },

            # === Объект действия ===
            {
                "prepositions": [],
                "case": "accusative",
                "semantic_keywords": ["предмет", "цель"],
                "category": "объект_действия"
            }
        ]
        
        if custom_rules:
            self.context_rules.extend(custom_rules)
        
        # Семантические маркеры
        self.semantic_keywords = {
            "локация": ["место", "город", "улица", "дом", "комната", "лес", "площадь","парк","лес","природа","помещение","локация"],
            "инструмент": ["инструмент", "орудие", "прибор", "меч", "компьютер", "скрипка"],
            "время": ["время", "час", "минута", "год", "сутки", "период","ночь", "день","вечер", "утро","полдень"],
            "объект_действия": ["предмет", "книга", "документ", "задача", "цель"]
        }

    def semantic_check(self, word: str, keywords: List[str], threshold: float = 0.2,pos: str="NOUN") -> bool:
        """Проверка семантической близости слова к набору ключевых слов."""
        if (word+"_"+pos) not in self.model:

            print("err 1.1")
            return False
        try:
            similarities = [
                self.model.similarity(word+"_"+pos, kw+"_"+pos)
                for kw in keywords
                if kw+"_"+pos in self.model
            ]

            print(sum(similarities) / len(similarities),"1.0")
            return sum(similarities) / len(similarities) > threshold
        except ZeroDivisionError:
            print("err 1.2")
            return False

    def get_bert_context(self, text: str, word: str) -> Optional[str]:
        """Анализ контекста с помощью BERT."""
        if not self.use_bert:
            return None
        entities = self.ner_pipeline(text)
        for ent in entities:
            if ent["word"] == word:
                return ent["entity"].split("-")[-1]
        return None

    def classify(self, obj: Dict, context_text: Optional[str] = None) -> str:
        """
        Классификация объекта.
        
        :param obj: словарь с полями "word", "prep", "case"
        :param context_text: исходный текст для контекстного анализа (опционально)
        """
        word = obj["word"]
        prep = obj.get("prep")
        case = obj["case"]
        pos = obj["pos"]

        # 1. Проверка исключений
        if word in self.exceptions:
            return self.exceptions[word],1

        # 2. Контекстный анализ BERT
        if self.use_bert and context_text:
            bert_category = self.get_bert_context(context_text, word)
            if bert_category:
                return bert_category,2

        # 3. Контекстные правила
        for rule in self.context_rules:
            if (prep in rule["prepositions"] and 
                case in rule.get("case", [case]) and 
                self.semantic_check(word, rule["semantic_keywords"])):
                return rule["category"],3

        # 4. Общие паттерны
        general_patterns = [
            (["на", "в"], "prepositional", "локация"),
            (["с"], "instrumental", "инструмент"),
        ]
        for preps, pattern_case, category in general_patterns:
            if prep in preps and case == pattern_case:
                return category,4

        # 5. Семантический резерв
        for category, keywords in self.semantic_keywords.items():
            if self.semantic_check(word, keywords):
                return category,5

        return "не определено",-1

    def update_exceptions(self, new_exceptions: Dict) -> None:
        """Динамическое обновление исключений."""
        self.exceptions.update(new_exceptions)

    def add_rule(self, rule: Dict) -> None:
        """Добавление нового правила."""
        self.context_rules.append(rule)


if __name__ == "__main__":
    # Инициализация
    classifier = ObjectClassifier(
        word2vec_model_path="ruwikiruscorpora.model.bin",
        use_bert=False,
        custom_exceptions={"ноутбуке": "инструмент"}
    )

    # Объект для классификации
    objs:List[Dict] = [
    {"word": "рассвет", "prep": "о", "case": "prepositional", "pos": "NOUN"},
    {"word": "месяц", "prep": None, "case": "genitive", "pos": "NOUN"},
    {"word": "фандорин", "prep": None, "case": "genitive", "pos": "NOUN"},
    {"word": "он", "prep": None, "case": "genitive", "pos": "NPRO"},
    {"word": "поручик", "prep": None, "case": "genitive", "pos": "NOUN"},
    {"word": "масса", "prep": None, "case": "genitive", "pos": "NOUN"},
    {"word": "роман", "prep": None, "case": "accusative", "pos": "NOUN"},
    {"word": "борис", "prep": None, "case": "genitive", "pos": "NOUN"},
    {"word": "акунин", "prep": None, "case": "genitive", "pos": "NOUN"},
    {"word": "я", "prep": None, "case": "accusative", "pos": "NPRO"},
    {"word": "место", "prep": "на", "case": "prepositional", "pos": "NOUN"},
    {"word": "герой", "prep": None, "case": "genitive", "pos": "NOUN"},
    {"word": "этот", "prep": None, "case": "genitive", "pos": "NPRO"},
    {"word": "роман", "prep": None, "case": "genitive", "pos": "NOUN"}
]
    for obj in objs:
        # Классификация
        category, flag = classifier.classify(obj)
        print(obj["prep"], obj["word"], f"Категория: {category, flag}")  # Output: "локация"

    # Добавление нового правила динамически
    classifier.add_rule({
        "prepositions": ["под"],
        "case": "instrumental",
        "semantic_keywords": ["хранилище"],
        "category": "локация"
    })


model = load_w2v_rus()

for index, word in enumerate(model.index_to_key ):
    if index == 200:
        break
    #print(f"word #{index}/{len(model.index_to_key )} is {word}")

print(model.most_similar(['печь_NOUN']))
print(model.most_similar(['печь_VERB']))