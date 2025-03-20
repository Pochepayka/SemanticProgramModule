
import matplotlib
matplotlib.use('TkAgg')# Используйте бэкенд 'Agg', если Tkinter вызывает проблемы
import spacy
import networkx as nx
import matplotlib.pyplot as plt

class SyntaxTreeBuilder:
    def __init__(self):
        # Загрузка модели русского языка
        self.nlp = spacy.load("ru_core_news_sm")

    def analyze_sentence(self, sentence):
        # Обработка предложения
        doc = self.nlp(sentence)

        # Создание графа связей
        graph = nx.DiGraph()

        # Словарь для хранения информации о словах
        word_info = {}

        # Цвета для частей речи (улучшено)
        self.pos_colors = {
            'NOUN': 'skyblue',  # Существительное
            'VERB': 'lightgreen',  # Глагол
            'ADJ': 'lightcoral',  # Прилагательное
            'ADV': 'gold',  # Наречие
            'PRON': 'plum',  # Местоимение
            'ADP': 'lightgray',  # Предлог
            'DET': 'khaki',  # Определитель (артикль, указательное местоимение и т.д.)
            'NUM': 'peachpuff',  # Числительное
            'CONJ': 'lavender',  # Союз
            'SCONJ': 'lavender',  # Подчинительный союз
            'INTJ': 'wheat',  # Междометие
            'PART': 'seashell',  # Частица
            'PUNCT': 'white',  # Пунктуация
            'SYM': 'whitesmoke',  # Символ
            'X': 'gainsboro'  # Другое
        }

        # Анализ каждого слова
        for token in doc:
            info = {
                'text': token.text,
                'lemma': token.lemma_,
                'pos': token.pos_,  # Часть речи
                'tag': token.tag_,  # Грамматическая характеристика
                'dep': token.dep_,  # Синтаксическая роль
                'head': token.head.text  # Головное слово
            }

            # Добавление ребра в графе
            graph.add_edge(token.head.text, token.text)

            word_info[token.text] = info

        return graph, word_info

    def visualize_graph(self, graph, word_info):
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(graph, seed=42)  # Для воспроизводимости

        # Получение цветов для узлов на основе части речи
        node_colors = [self.pos_colors.get(word_info[node]['pos'], 'white') for node in graph.nodes()]

        # Проверка правильности раскраски (соседние вершины должны иметь разные цвета)
        for u, v in graph.edges():
            if node_colors[list(graph.nodes()).index(u)] == node_colors[list(graph.nodes()).index(v)]:
                print(f"Внимание: вершины '{u}' и '{v}' имеют одинаковый цвет!")
                # Можно добавить логику для автоматического изменения цвета в случае конфликта
        nx.draw(graph, pos, with_labels=True, node_color=node_colors ,
                node_size=1500, font_size=10, font_weight='bold')
        plt.title("Синтаксическое дерево")
        plt.show()

def string_to_lowercase_substrings(text):
    """
    Разбивает строку на подстроки, разделенные точками, и преобразует их в нижний регистр.

    Args:
      text: Входная строка.

    Returns:
      Массив подстрок в нижнем регистре.
    """

    substrings = text.split(".")
    lowercase_substrings = [s.lower() for s in substrings]
    return lowercase_substrings

# Пример использования
def main():
    text = " Я люблю гулять осенью. Потому что осенью красиво падают жёлтые листья."
    #"Весна так красива. Лето лучшее время года. Зимой холодно."
    #"Мой дядя самых честных правил, когда не в шутку занемог, он уважать себя заставил и лучше выдумать не мог."

    sentences = string_to_lowercase_substrings(text)


    tree_builder = SyntaxTreeBuilder()
    graph, word_details = tree_builder.analyze_sentence(text)#sentences[0])

    # Вывод детальной информации о словах
    for word, details in word_details.items():
        print(f"Слово: {word}")
        for key, value in details.items():
            print(f"  {key}: {value}")
        print("---")

    # Визуализация графа связей
    tree_builder.visualize_graph(graph, word_details)


if __name__ == "__main__":
    main()