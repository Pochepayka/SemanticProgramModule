import spacy
import networkx as nx
import matplotlib.pyplot as plt

# Загрузка модели spaCy для русского языка
nlp = spacy.load("ru_core_news_sm")

def resolve_coreferences(text):
    """
    Простая реализация кореференции для замены "он" на последнее подлежащее.
    """
    sentences = text.split(". ")
    resolved_text = []
    last_subject = None

    for sentence in sentences:
        if "Она" in sentence or "она" in sentence:
            if last_subject:
                sentence = sentence.replace("Она", last_subject).replace("она", last_subject)
        # Ищем подлежащее в предложении
        doc = nlp(sentence)
        for token in doc:
            if token.dep_ in ["nsubj","obj"] and token.morph.get('Gender') == nlp("Она")[0].morph.get('Gender'):
                last_subject = token.text
        resolved_text.append(sentence)
    return ". ".join(resolved_text)

def extract_semantic_relations(text):
    """
    Извлекает семантические связи из текста.
    Возвращает список связей в формате (кто, действие, над кем).
    """
    doc = nlp(text)
    relations = []

    for token in doc:
        # Ищем подлежащее (кто?)
        if token.dep_ == "nsubj":
            subject = token.text
            action = token.head.text  # Глагол (что делает?)
            # Ищем дополнение (над кем?)
            obj = ""
            for child in token.head.children:
                if child.dep_ == "obj":
                    obj = child.text
            relations.append((subject, action, obj))
    return relations

def create_semantic_graph(relations):
    """
    Создает ориентированный граф на основе семантических связей.
    """
    G = nx.DiGraph()
    for relation in relations:
        subject, action, obj = relation
        G.add_edge(subject, action)  # Кто -> Что делает
        G.add_edge(action, obj)      # Что делает -> Над кем
    return G

def draw_graph(G):
    """
    Визуализирует граф с помощью matplotlib.
    """
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=3000, node_color="lightblue", font_size=12, font_weight="bold", arrows=True)
    plt.show()

# Пример использования
text = "Мама мыла раму. Папа поднимал кровать. Она предавила собаку, Когда собака грызла кость."

# Разрешаем кореференцию
resolved_text = resolve_coreferences(text)
print("Текст после разрешения кореференции:", resolved_text)

# Извлекаем семантические связи
relations = extract_semantic_relations(resolved_text)
print("Семантические связи:", relations)

# Создаем граф
G = create_semantic_graph(relations)

# Визуализация графа
draw_graph(G)