
from SintaxisModule import PartOfSpeech
import matplotlib.pyplot as plt


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
        #PartOfSpeech.MAIN: {'color': 'red', 'linewidth': 3, 'linestyle': (0, (6, 2))},
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

                if connection_levels.get((parent_x, parent_y,  child_y)):
                    level = connection_levels.get((parent_x, parent_y,  child_y))

                else:
                    level = None
                    for i in range (1,max_levels+1):
                        if not(conections.get((parent_y,i))):
                            level = i
                            connection_levels[(parent_x, parent_y, parent_y)] = i
                            conections[(parent_y,i)]=(min(parent_x,child_x),max((parent_x,child_x)))
                            break
                        else:
                            beg, end = conections.get((parent_y,i),(10000000,-1))
                            if max(parent_x,child_x)<beg or min(parent_x,child_x)>end:
                                level = i
                                connection_levels[(parent_x, parent_y, parent_y)] = i
                                conections[(parent_y,i)]=(min(beg,parent_x,child_x),max((end,parent_x,child_x)))
                                break
                    if not level:
                        connection_levels[(parent_x, parent_y, parent_y)] = i_level
                        beg, end = conections.get((parent_y, i_level), (10000000, -1))
                        conections[(parent_y,i_level)]=(min(beg,parent_x,child_x),max((end,parent_x,child_x)))
                        level = i_level
                        i_level = 1 + ((i_level+1) % max_levels)

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


# Пример использования
if __name__ == "__main__":
    print()