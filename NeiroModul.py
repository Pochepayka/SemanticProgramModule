from DownloadModels import load_w2v_rus
import numpy as np


w2v_rus = load_w2v_rus()


from typing import List, Dict, Any

class HomonymResolver:
    def __init__(self, rules: List[Dict[str, Any]]):
        self.rules = rules  # Правила для разных типов омонимов

    def resolve(self, sentence: List[Dict], target_index: int) -> Dict:
        target_word = sentence[target_index]
        possible_analyses = target_word["possible_analyses"]

        # Применяем правила по приоритету
        for rule in self.rules:
            if self._check_rule(sentence, target_index, rule["conditions"]):
                return self._select_analysis(possible_analyses, rule["filters"])

        # Резервный вариант: выбор наиболее вероятного анализа
        return max(possible_analyses, key=lambda x: x.get("prob", 0))

    def _check_rule(self, sentence, target_index, conditions) -> bool:
        # Проверка контекстных условий
        context = {
            "prev_words": sentence[:target_index],
            "next_words": sentence[target_index+1:],
            "target": sentence[target_index]
        }
        return all(
            condition["func"](context, **condition.get("params", {}))
            for condition in conditions
        )

    def _select_analysis(self, analyses, filters) -> Dict:
        # Выбор анализа по фильтрам
        for filter_cond in filters:
            filtered = [a for a in analyses if all(
                a.get(k) == v for k, v in filter_cond.items()
            )]
            if filtered:
                return filtered[0]
        return analyses[0]

# Пример правил для разных типов омонимов
RULES = [
    {   # Правило для глагол/существительное (печь, стекло и т.д.)
        "conditions": [
            {
                "func": lambda ctx: any(
                    w.get("lemma") in {"НАЧАТЬ", "ПРОДОЛЖИТЬ", "ПЕРЕСТАТЬ"}
                    and w.get("pos") == "VERB"
                    for w in ctx["prev_words"][-2:]
                ),
                "params": {}
            }
        ],
        "filters": [{"pos": "INFI"}]
    },
    {
        "conditions": [
            {
                "func": lambda ctx: any(
                    w.get("pos") == "PREP"
                    for w in ctx["prev_words"][-1:]
                ),
                "params": {}
            }
        ],
        "filters": [{"pos": "NOUN"}]
    },
    {   # Общее правило для прямого дополнения
        "conditions": [
            {
                "func": lambda ctx: any(
                    w.get("case") == "accs" and w.get("pos") == "NOUN"
                    for w in ctx["next_words"][:2]
                ),
                "params": {}
            }
        ],
        "filters": [{"pos": "INFI"}]
    }
]

# Пример использования
sentence = [
    {"word": "Он", "lemma": "ОН", "pos": "NPRO"},
    {"word": "начал", "lemma": "НАЧАТЬ", "pos": "VERB"},
    {
        "word": "печь",
        "possible_analyses": [
            {"pos": "INFI", "lemma": "ПЕЧЬ", "prob": 0.6},
            {"pos": "NOUN", "lemma": "ПЕЧЬ", "case": "accs", "prob": 0.4}
        ]
    },
    {"word": "хлеб", "lemma": "ХЛЕБ", "pos": "NOUN", "case": "accs"}
]

resolver = HomonymResolver(RULES)
result = resolver.resolve(sentence, target_index=2)
print(result)  # {'pos': 'INFI', ...}





























# for index, word in enumerate(w2v_rus.index_to_key ):
#     if index == 200:
#         break
#     print(f"word #{index}/{len(w2v_rus.index_to_key )} is {word}")
# print(w2v_rus['печь_NOUN'])
#
# print(w2v_rus.most_similar(['печь_NOUN']))
# print(w2v_rus.most_similar(['печь_VERB']))
#
# def predict_missing_word(sentence, model):
#     # Удаляем пропущенное слово и токенизируем
#     context = sentence.replace("___", "").split()
#     print(context)
#     # Получаем векторы контекста
#     vectors = [model[word] for word in context if word in model]
#     if not vectors:
#         return []
#     # Усредняем векторы
#     print(vectors)
#     avg_vector = np.mean(vectors, axis=0)
#     # Ищем ближайшие слова
#     #return model.similar_by_vector(avg_vector, topn=5)
#     # Ищем ближайшие слова
#     return model.similar_by_vector(avg_vector)
#
# # Пример использования
# result = predict_missing_word("продавец_NOUN  человек_NOUN", w2v_rus)
# print(result)



#
# from transformers import AutoTokenizer, AutoModelForMaskedLM
# import torch
#
#
# class MaskedWordPredictor:
#     def __init__(self, model_name="cointegrated/rubert-tiny"):
#         self.tokenizer = AutoTokenizer.from_pretrained(model_name)
#         self.model = AutoModelForMaskedLM.from_pretrained(model_name)
#
#     def predict_masked_word(self, sentence, mask_token="[MASK]", top_k=5):
#         # Заменяем целевое слово на маску
#         inputs = self.tokenizer(sentence, return_tensors="pt")
#
#         # Получаем предсказания
#         with torch.no_grad():
#             outputs = self.model(**inputs)
#
#         # Находим позицию маски
#         mask_token_index = torch.where(inputs["input_ids"][0] == self.tokenizer.mask_token_id)[0]
#
#         # Извлекаем предсказания для маски
#         predictions = outputs.logits[0, mask_token_index]
#         top_tokens = torch.topk(predictions, top_k, dim=1).indices[0].tolist()
#
#         # Декодируем токены
#         return [self.tokenizer.decode([token]) for token in top_tokens]


# # Пример использования
# predictor = MaskedWordPredictor()
#
# # Тестовые предложения с маской
# sentences = [
#     "Старая [MASK] дымит из-за плохой тяги.",
#     "Он начал [MASK] хлеб ранним утром."
# ]
#
# for sentence in sentences:
#     predictions = predictor.predict_masked_word(sentence)
#     print(f"Предложение: {sentence}")
#     print(f"Топ-5 предсказаний: {predictions}\n")
#
#



#
# import pandas as pd
# import pymorphy3
# import nltk
# from nltk.tokenize import word_tokenize
# from nltk.corpus import stopwords
#
# nltk.download('punkt')
# nltk.download('stopwords')

#
# def preprocess(text, stop_words, punctuation_marks, morph):
#     tokens = word_tokenize(text.lower())
#     preprocessed_text = []
#     for token in tokens:
#         if token not in punctuation_marks:
#             lemma = morph.parse(token)[0].normal_form
#             if lemma not in stop_words:
#                 preprocessed_text.append(lemma)
#     return preprocessed_text
#
# punctuation_marks = ['!', ',', '(', ')', ':', '-', '?', '.', '..', '...']
# stop_words = stopwords.words("russian")
# morph = pymorphy3.MorphAnalyzer()
