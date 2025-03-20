import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout

from LoadJsonDict import FromJSON

# Цветовые схемы
pos_colors = FromJSON("json/POS_COLOR.json")
relation_colors = FromJSON("json/RELATION_COLORS.json")

def visualize_tree(root_node):
    """Улучшенная визуализация с цветовым кодированием и краткой информацией"""

    G = nx.DiGraph()
    node_colors = []
    edge_colors = []
    labels = {}
    edge_labels = {}

    def traverse(node, parent=None):
        nonlocal node_colors, edge_colors

        # Формируем краткую информацию для узла
        if not(node.type and node.features.get('word')):
            if node.type:
                features = [
                    f"{node.type}"
                ]
            else:
                features = ["NONE"]
        else:
            features = [
                f"pos: {node.type}",
                f"case: {node.features.get('case')}",
                f"word: {node.features.get('word')[:10]}"
            ]


        labels[id(node)] = '\n'.join(features)
        # Цвет узла по части речи
        node_colors.append(pos_colors.get(node.type, "#555555"))

        # Обработка связей
        if parent is not None:
            for rel in [r for n, r in parent.connections if n == node]:
                edge_labels[(id(parent), id(node))] = rel
                edge_colors.append(relation_colors.get(rel, '#000000'))
                G.add_edge(id(parent), id(node))

        for child, _ in node.connections:
            traverse(child, node)

    traverse(root_node)

    # Создание графа
    pos = graphviz_layout(G, prog='dot', root=id(root_node))

    # Рисование
    plt.figure(figsize=(20, 12))
    nx.draw(G, pos,
            labels=labels,
            node_color=node_colors,
            edge_color=edge_colors,
            with_labels=True,
            node_size=1000,
            font_size=8,
            font_weight='bold',
            arrowsize=20,
            node_shape='s',
            edge_cmap=plt.cm.Blues)

    # Рисование подписей связей
    nx.draw_networkx_edge_labels(G, pos,
                                 edge_labels=edge_labels,
                                 font_color='#2E74B5',
                                 font_size=8)

    # Добавление легенды
    legend_elements = [
        plt.Line2D([0], [0], marker='s', color='w', label=f'{pos}',
                   markerfacecolor=color, markersize=15)
        for pos, color in pos_colors.items()
    ]

    plt.legend(handles=legend_elements, bbox_to_anchor=(1, 1), loc='upper left')
    plt.title("Синтаксическое дерево с цветовым кодированием", fontsize=14)
    plt.tight_layout()
    plt.show()

# Пример использования
if __name__ == "__main__":
    print()