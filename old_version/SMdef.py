from enum import Enum

class PartOfSpeech(Enum):
    SUBJECT = "Подлежащее"
    PREDICATE = "Сказуемое"
    SUB_PREDICATE = "Инфинитив"
    OBJECT = "Дополнение"
    CIRCUMSTANCE = "Обстоятельство"
    DEFINITION = "Определение"
    NONE = "Не определено"


class SyntaxNode:
    """Класс для представления узла синтаксического дерева."""

    def __init__(self, word_type, lemma, features=None, children=None):
        self.type = word_type
        self.lemma = lemma
        self.features = features or {}
        self.part_of_sentence = PartOfSpeech.NONE
        self.children = children or []
        self.connections = []
        self.parent = None


    def change_part_of_sent(self, PartOfSpeech):
        self.part_of_sentence = PartOfSpeech


    def add_connection(self, node, relation):
        node.parent = self
        self.connections.append((node, relation))

    def __repr__(self):
        return f"{self.type}('{self.lemma}', {self.features})"


# def check_agreement(node1, node2):
#     """Проверка грамматического согласования."""
#     return all(
#         node1.features.get(k) == node2.features.get(k)
#         for k in ['gender', 'number']
#         if node1.features.get(k) and node2.features.get(k)
#     )



def check_common_word(arr1, arr2):
    return len(set(arr1) & set(arr2)) > 0

def check_homogeneous_agreement(node1, node2):
    """
    Проверяет, могут ли два узла быть однородными членами.
    Однородные члены должны иметь одинаковые:
    - часть речи (pos),
    - падеж (case),
    - число (number),
    - время (tense, для глаголов).
    """
    # Проверка части речи
    if node1.type != node2.type:
        return False

    if node1.type in ["NPRO"] and not(check_common_word(node1.features.get("case"),["nomn"])):
        return False

    # Проверка падежа (для существительных, прилагательных, местоимений)
    if node1.type in ['NOUN', 'ADJF', 'NPRO']:
        if not(check_common_word(node1.features.get('case'),node2.features.get('case'))):
        #if node1.features.get('case') != node2.features.get('case'):
            return False

    # Проверка числа
    if node1.features.get('number') != node2.features.get('number'):
        return False

    # Проверка времени (для глаголов)
    if node1.type == 'VERB':
        if node1.features.get('tense') != node2.features.get('tense'):
            return False



    return True

def find_homogeneous_groups(nodes):
    """
    Находит группы однородных членов в предложении.
    Возвращает список групп, где каждая группа — это список узлов.
    """
    conjunctions = {'и', 'или', 'а', 'но'}
    homogeneous_groups = []
    used_indices = set()  # Индексы узлов, которые уже включены в группы
    independent_pos = ['VERB', 'NOUN', 'ADVB', "NUMR", "INFI", "NPRO", "ADJF", "ADV_PARTICIPLE"]


    for i, node in enumerate(nodes):
        # Если текущий узел — союз и он не был использован
        if nodes[i].lemma.lower() in conjunctions and i not in used_indices:
            flag_for_left = False
            # Ищем левый и правый члены с помощью вложенного цикла
            for left in range(i - 1, -1, -1):  # Идем влево от союза

                if left in used_indices:
                    continue  # Пропускаем уже использованные узлы

                # Проверяем, что левый узел подходит для однородных членов
                if nodes[left].type in independent_pos:
                    for right in range(i + 1, len(nodes)):  # Идем вправо от союза
                        if right in used_indices:
                            continue  # Пропускаем уже использованные узлы

                        # Проверяем, что правый узел подходит для однородных членов
                        if (nodes[right].type in independent_pos and
                            check_homogeneous_agreement(nodes[left], nodes[right])):
                            # Создаем группу однородных членов
                            group = [nodes[left], nodes[i], nodes[right]]
                            homogeneous_groups.append(group)
                            used_indices.update({left, i, right})
                            flag_for_left=True
                            break  # Прерываем внутренний цикл после нахождения правого члена
                if flag_for_left:
                    break  # Прерываем внешний цикл после нахождения левого члена

    return homogeneous_groups

def handle_homogeneous(nodes):
    """Обработка однородных членов."""
    homogeneous_groups = find_homogeneous_groups(nodes)

    # Обрабатываем каждую группу однородных членов
    for group in homogeneous_groups:
        parent = group[0]
        for node in group[1:]:
            parent.add_connection(node, 'homogeneous')
        print_tree(parent)
    return nodes

def connect_pp_to_n(node_pp,node_n):
    if check_common_word(node_n.features.get('case'),node_pp.features.get("case")):
        return True
    return False

def conect_to_predicate(i,default_pred,predicate_nodes,node,info):
    pred = default_pred
    maxI = 0
    for predicate in predicate_nodes:
        if predicate[1] < i and predicate[1]>maxI:
            pred = predicate[0]
            maxI = predicate[1]

    pred.add_connection(node, info)


def build_syntax_tree(parsed_tokens, first_flag = True, p_n = []):
    """Построение синтаксического дерева."""
    if first_flag:
        for token in parsed_tokens:
            print(token)
        print("-"*100 +"\n\n")

        nodes = [SyntaxNode(feat['pos'], feat['lemma'], feat) for feat in parsed_tokens]
        #nodes = handle_homogeneous(nodes)
        predicate_nodes = []

    else:
        nodes = parsed_tokens
        predicate_nodes = p_n

    predicate_node = None
    subject_node = None
    definition_node = None
    circumstance_node = None

    # Поиск сказуемого (глагол в изъявительном наклонении)
    for i, node in enumerate(nodes):
        if node.type == 'VERB' and node.features.get('tense') is not None:
            node.change_part_of_sent(PartOfSpeech.PREDICATE)
            predicate_node = node
            predicate_nodes += [[node,i]]

            break


    #перебор всех нодов
    for i, node in enumerate(nodes):
        if node.parent == None:
            # Поиск подлежащего (существительное в именительном падеже)
            if node.type in ['NOUN', 'NPRO'] and "nomn" in node.features.get('case') and subject_node == None:
                    subject_node = node
                    if predicate_node:
                        node.change_part_of_sent(PartOfSpeech.SUBJECT)
                        conect_to_predicate(i, predicate_node, predicate_nodes, node, 'subject')
                        #predicate_node.add_connection(subject_node, 'subject')


            # Обработка однородных сказуемых
            elif node.type == 'VERB' and node != predicate_node:
                node.change_part_of_sent(PartOfSpeech.PREDICATE)
                predicate_nodes += [[node,i]]
                if predicate_node:
                    predicate_node.add_connection(node, 'homogeneous')


            # обработка инфинитива
            elif node.type == 'INFI':
                node.change_part_of_sent(PartOfSpeech.PREDICATE)
                predicate_nodes += [[node, i]]
                if predicate_node:
                    conect_to_predicate(i,predicate_node,predicate_nodes,node,'predicate')


            elif node.type in  ["PRCL", "PART"]:
                if nodes[i+1]:
                    nodes[i+1].add_connection(node, "participle")


            # Обработка определений (прилагательные)
            elif (node.type == 'ADJF'  and  node.features.get('case')!= []) or node.type == "PARTICIPLE":

                node.change_part_of_sent(PartOfSpeech.DEFINITION)
                closest_noun = next((n for n in nodes[i + 1:]
                                     if n.type in ['NOUN', 'NPRO']), None)
                if closest_noun:
                    closest_noun.add_connection(node, 'attribute')
                else:
                    definition_node = node


            # Обработка дополнений с предлогами
            elif node.type == 'PREP' :  # Если это предлог

                node.change_part_of_sent(PartOfSpeech.OBJECT)
                # Ищем следующее существительное (дополнение)
                next_noun = None
                for n in nodes[i + 1:]:
                    if n.type in ['NOUN', 'NPRO'] and connect_pp_to_n(node, n):
                        n.change_part_of_sent(PartOfSpeech.OBJECT)
                        next_noun = n
                        break
                if not(next_noun.parent):
                    node.add_connection(next_noun, 'object')
                # Связываем предлог с глаголом (сказуемым)
                if predicate_node:
                    conect_to_predicate(i, predicate_node, predicate_nodes, node, 'prepositional_object')


            # Обработка обстоятельств
            if (node.type in ['ADVB',"ADJF_SHORT"]) or (node.type == 'ADJF'  and node.features.get('case')== []):  # Если это наречие (обстоятельство)

                node.change_part_of_sent(PartOfSpeech.CIRCUMSTANCE)
                if predicate_node:
                    conect_to_predicate(i,predicate_node,predicate_nodes,node,'adverbial')


            # обраьотка дополнений в родительном падеже
            elif ((node.type == 'NOUN' or node.type == 'NPRO')
                  #and check_common_word(node.features.get('case'),['gent', 'datv', 'accs', 'ablt', 'loct'])):
                  and 'gent' in node.features.get('case')):

                node.change_part_of_sent(PartOfSpeech.OBJECT)
                for n in nodes[i - 1::-1]:
                    if n.type in ['NOUN', 'NPRO', "VERB","INFI"]:
                        n.add_connection(node, 'genitive')
                        break


            elif (node.type == "ADVB_PARTICIPLE"):
                node.change_part_of_sent(PartOfSpeech.CIRCUMSTANCE)

                if circumstance_node:
                    circumstance_node.add_connection(node, 'homogeneous')
                elif predicate_node:
                    conect_to_predicate(i,predicate_node,predicate_nodes,node,'circumstance')
                    circumstance_node = node
                else:
                    circumstance_node = node


        # elif node.type == 'NOUN' and check_common_word(node.features.get('case'),['gent', 'datv', 'accs', 'ablt', 'loct']):
        #     node.change_part_of_sent(PartOfSpeech.OBJECT)
        #     if predicate_node:
        #         conect_to_predicate(i,predicate_node,predicate_nodes,node,'object')



    root_node = None
    if predicate_node:
        root_node = predicate_node
    elif subject_node:
        root_node = subject_node
    elif circumstance_node:
        root_node = circumstance_node
    elif definition_node:
        root_node = definition_node
    else:
        root_node = nodes[0]

    print_tree(root_node)
    print("-" * 100 + "\n\n")

    return root_node, nodes, predicate_nodes



def print_tree(node, level=0, relation=''):
    """Визуализация синтаксического дерева."""
    if not node:
        return
    print('  ' * level + f'└─ {relation} {node}')
    for child, rel in node.connections:
        print_tree(child, level + 1, rel)
