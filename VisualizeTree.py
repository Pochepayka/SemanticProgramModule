import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout

from SintaxisModule import PartOfSpeech
from LoadJsonDict import FromJSON

# Цветовые схемы
json_pos_colors = FromJSON("json/POS_COLOR.json")
json_relation_colors = FromJSON("json/RELATION_COLORS.json")
class VisualResult:
    def __init__(self,
                 pos_colors = json_pos_colors,
                 relation_colors = json_relation_colors):
        self.pos_colors = pos_colors
        self.relation_colors = relation_colors

    def create_graph(self, root_node):
        G = nx.DiGraph()
        edge_labels = {}

        def traverse(node, parent=None):
            # Добавляем узел с атрибутами (включая цвет)
            node_color = self.pos_colors.get(node.type, "#555555")
            G.add_node(id(node),
                       label='\n'.join([
                           f"pos: {node.type}",
                           f"case: {node.features.get('case')}",
                           f"word: {node.features.get('word', '')[:10]}"
                       ]),
                       color=node_color  # Сохраняем цвет как атрибут
                       )

            # Обработка рёбер и их цветов
            if parent is not None:
                for rel in [r for n, r in parent.connections if n == node]:
                    edge_color = self.relation_colors.get(rel, '#000000')
                    G.add_edge(id(parent), id(node),
                               relation=rel,
                               color=edge_color  # Сохраняем цвет ребра
                               )
                    edge_labels[(id(parent), id(node))] = rel

            for child, _ in node.connections:
                traverse(child, node)

        traverse(root_node)
        return G

    def visualize_graph(self, G, root_node=None, labels=None, edge_labels=None):
        """Отрисовка графа (нового или загруженного)"""
        plt.figure(figsize=(20, 12))

        # Определение позиций узлов
        pos = graphviz_layout(G, prog='dot', root=root_node)

        # Получение цветов из атрибутов графа (если есть)
        node_colors = [G.nodes[n].get('color', '#555555') for n in G.nodes]
        edge_colors = [G.edges[e].get('color', '#000000') for e in G.edges]

        # Если метки не переданы - берём из атрибутов
        if labels is None:
            labels = {n: G.nodes[n].get('label', str(n)) for n in G.nodes}

        if edge_labels is None:
            edge_labels = {(u, v): G.edges[(u, v)].get('relation', '')
                           for u, v in G.edges}

        # Отрисовка
        nx.draw(G, pos,
                labels=labels,
                node_color=node_colors,
                edge_color=edge_colors,
                with_labels=True,
                node_size=1000,
                font_size=8,
                font_weight='bold',
                arrowsize=20,
                node_shape='s')

        # Подписи рёбер
        nx.draw_networkx_edge_labels(G, pos,
                                     edge_labels=edge_labels,
                                     font_color='#2E74B5',
                                     font_size=8)

        # Легенда (если заданы цветовые схемы)
        if self.pos_colors:
            legend_elements = [
                plt.Line2D([0], [0], marker='s', color='w', label=pos,
                           markerfacecolor=color, markersize=15)
                for pos, color in self.pos_colors.items()
            ]
            plt.legend(handles=legend_elements, bbox_to_anchor=(1, 1), loc='upper left')

        plt.title("Синтаксическое дерево", fontsize=14)
        plt.tight_layout()
        plt.show()
        return plt
    

    @staticmethod
    def visualize_syntax_links(nodes, tokens, max_tokens_per_line=8):

        if len(tokens) == 0:
            return 0

        # Разбиваем токены на строки
        lines = [tokens[i:i + max_tokens_per_line]
                 for i in range(0, len(tokens), max_tokens_per_line)]

        # Создаем координатную сетку
        line_height = 2.0
        fig, ax = plt.subplots(figsize=(15, 2 + len(lines) * 1.2))
        ax.set_xlim(-0.5, max_tokens_per_line + 0.5)
        ax.set_ylim(-len(lines) * line_height, line_height)
        ax.axis('off')

        # Стили для подчеркиваний
        styles = {
            PartOfSpeech.PREDICATE: {'color': 'red', 'linewidth': 3, 'linestyle': (0, (6, 2))},
            PartOfSpeech.MAIN_SUBJECT: {'color': 'blue', 'linewidth': 2},
            PartOfSpeech.MAIN_PREDICATE: {'color': 'red', 'linewidth': 3, 'linestyle': (0, (6, 2))},
            PartOfSpeech.SUB_PREDICATE: {'color': 'red', 'linewidth': 3, 'linestyle': (0, (6, 2))},
            PartOfSpeech.NOMINAL_PREDICATE: {'color': 'red', 'linewidth': 3, 'linestyle': (0, (6, 2))},
            # PartOfSpeech.MAIN: {'color': 'red', 'linewidth': 3, 'linestyle': (0, (6, 2))},
            PartOfSpeech.DEFINITION: {"linestyle": ":", "color": "purple", "linewidth": 2},
            PartOfSpeech.SUBJECT: {'color': 'blue', 'linewidth': 2},
            PartOfSpeech.CIRCUMSTANCE: {'color': 'green', 'linestyle': '-.'},
            PartOfSpeech.OBJECT: {"linestyle": (0, (3, 5)), "color": "orange", "linewidth": 2},
        }

        # Словарь для хранения позиций токенов (строка, позиция)
        token_positions = {}

        # Рисуем текст и подчеркивания
        for line_num, line_tokens in enumerate(lines):
            y_pos = -line_num * line_height

            # Рисуем слова
            for i, token in enumerate(line_tokens):
                x_pos = i + 0.5
                ax.text(x_pos, y_pos + 0.5, token[0],
                        ha='center', va='center', fontsize=12)
                token_positions[token[1]] = (x_pos, y_pos + 0.2)

            # Рисуем подчеркивания
            for node in nodes:
                if node.features.get("num_in_text") and node.features["num_in_text"] in token_positions:
                    part = node.part_of_sentence
                    if part in styles:
                        x, y = token_positions[node.features["num_in_text"]]
                        ax.hlines(
                            y=y,
                            xmin=x - 0.4,
                            xmax=x + 0.4,
                            **styles[part]
                        )

        # Рисуем связи между узлами
        connection_levels = {}  # Словарь для отслеживания уровней связей
        conections = {}
        max_levels = 5  # Максимальное количество уровней для смещения
        i_level = 3
        for node in nodes:
            # print(node.features.get("word"))
            if node.parent and node.parent.features.get("num_in_text"):
                try:
                    child_id = node.features["num_in_text"]
                    parent_id = node.parent.features["num_in_text"]

                    child_x, child_y = token_positions[node.features["num_in_text"]]
                    parent_x, parent_y = token_positions[node.parent.features["num_in_text"]]

                    # Пропускаем связи с одинаковыми координатами
                    if (child_x, child_y) == (parent_x, parent_y):
                        continue

                    if connection_levels.get((parent_x, parent_y, child_y)):
                        level = connection_levels.get((parent_x, parent_y, child_y))

                    else:
                        level = None
                        for i in range(1, max_levels + 1):
                            if not (conections.get((parent_y, i))):
                                level = i
                                connection_levels[(parent_x, parent_y, parent_y)] = i
                                conections[(parent_y, i)] = (min(parent_x, child_x), max((parent_x, child_x)))
                                break
                            else:
                                beg, end = conections.get((parent_y, i), (10000000, -1))
                                if max(parent_x, child_x) < beg or min(parent_x, child_x) > end:
                                    level = i
                                    connection_levels[(parent_x, parent_y, parent_y)] = i
                                    conections[(parent_y, i)] = (
                                    min(beg, parent_x, child_x), max((end, parent_x, child_x)))
                                    break
                        if not level:
                            connection_levels[(parent_x, parent_y, parent_y)] = i_level
                            beg, end = conections.get((parent_y, i_level), (10000000, -1))
                            conections[(parent_y, i_level)] = (
                            min(beg, parent_x, child_x), max((end, parent_x, child_x)))
                            level = i_level
                            i_level = 1 + ((i_level + 1) % max_levels)

                    # print (node.parent.features.get("word"),node.features.get("word"),level)
                    # print (connection_levels)

                    # Рассчитываем смещение
                    base_offset = 0.25
                    offset = base_offset * (level)
                    vertical_offset = offset

                    # Направление смещения (вверх или вниз)
                    # direction = 1 if level % 2 else -1
                    # vertical_offset = offset * direction

                    # Параметры соединения
                    connection_style = f"angle,angleA=0,angleB=90,rad={0.1 * level}"

                    # Рисуем стрелку
                    ax.annotate("",
                                xy=(child_x, child_y + 0.1 + vertical_offset),
                                xytext=(parent_x, parent_y + 0.1 + vertical_offset),
                                arrowprops=dict(
                                    arrowstyle="->",
                                    color="gray",
                                    lw=1,
                                    connectionstyle=connection_style,
                                    shrinkA=5,
                                    shrinkB=5
                                )
                                )

                except KeyError:
                    continue

        plt.title("Синтаксический разбор текста", pad=20)
        plt.tight_layout()
        plt.show()
        return plt

    @staticmethod
    def save_plt_png(plt, name_file):
        plt.savefig(f"results/png/{name_file}.png", dpi=300, bbox_inches='tight')
        return f"results/png/{name_file}.png"

    @staticmethod
    def save_txt(text, name_file):
        with open(f"results/txt/{name_file}.txt", 'w', encoding='utf-8') as file:
            file.write(text)

    @staticmethod
    def load_txt(path):
        with open(path, 'r', encoding='utf-8') as file:
            text = file.read()
        return text

    @staticmethod
    def load_graph(path):
        G_loaded = nx.read_graphml(path)
        return G_loaded

    @staticmethod
    def save_graph(G, name_file):
        nx.write_graphml(G, f"results/graphml/{name_file}.graphml")
        return f"results/graphml/{name_file}.graphml"



# Пример использования
if __name__ == "__main__":
    print()