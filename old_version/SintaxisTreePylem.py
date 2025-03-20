from pylem import MorphanHolder, MorphLanguage
import re

class DependencyTreeBuilder:
    def __init__(self, language=MorphLanguage.Russian):
        self.morphan = MorphanHolder(language)

    def check_correct(self, word):
        if self.morphan.is_in_dictionary(word):
            return True, word
        else:
            correct_word = self.morphan.correct_misspell(word)
            if len(correct_word) != 0:
                print(f"Слово {word} было исправленно на {correct_word}.")
                return True, correct_word
        return False, word

    def lemmatize_word(self, word):
        correct, word = self.check_correct(word)
        if correct:
            return [lemm_info for lemm_info in self.morphan.lemmatize(word)]  # Возвращаем список объектов LemmInfo
        else:
            print(f"Слово {word} не удалось найти")
            return None

    def build_dependency_tree(self, sentence):
        """
        Строит простое дерево зависимостей на основе морфологического анализа pylem.

        Примечание: Этот метод строит упрощенное дерево, опираясь на порядок слов и
        морфологические признаки. Для более точного синтаксического анализа
        потребуются дополнительные правила и/или статистические методы.
        """
        tokens = re.findall(r'\b\w+\b', sentence)
        lemmas = []
        for token in tokens:
            lemmas_info = self.lemmatize_word(token)
            if lemmas_info:
                lemmas.append(lemmas_info[0]) # Берем первую лемму
            else:
                lemmas.append(None) # Если слово не найдено

        # Создаем корневой узел (ROOT), к которому будет крепиться главное слово
        tree = {"ROOT": None}
        dependencies = []

        # Определяем главное слово (обычно глагол или существительное)
        head_index = -1
        for i, lemma_info in enumerate(lemmas):
            if lemma_info and lemma_info.part_of_speech in ("VERB", "NOUN"):  # Пример: ищем глагол или существительное
                head_index = i
                break

        if head_index == -1:
            print("Не удалось определить главное слово в предложении.")
            return tree, dependencies

        tree["ROOT"] = tokens[head_index]

        # Устанавливаем зависимости для остальных слов
        for i, lemma_info in enumerate(lemmas):
            if i != head_index and lemma_info:
                dependencies.append((tokens[i], tokens[head_index])) # слово -> главное слово
        return tree, dependencies

    def print_dependency_tree(self, tree, dependencies):
        print("Дерево зависимостей:")
        print(f"  ROOT: {tree['ROOT']}")
        for dependent, head in dependencies:
            print(f"  {dependent} --> {head}")


# Пример использования
sentence = "Мама мыла раму."
tree_builder = DependencyTreeBuilder()
tree, dependencies = tree_builder.build_dependency_tree(sentence)
tree_builder.print_dependency_tree(tree, dependencies)
