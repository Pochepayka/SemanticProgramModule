from enum import Enum
from MorphModule import MorphAnalyzer
from VisualizeTree import visualize_tree
from ClauseSpliter import ClauseSplitter
from old_version.SMdef import print_tree


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


class SintaxisAnalyzer:
    def __init__(self):
        self.predicate_nodes = []
        self.subject_node = None
        self.definition_node = None
        self.circumstance_node = None
        self.morph_analyzer = MorphAnalyzer()

    def analyze(self, text):

        splitter = ClauseSplitter()
        clauses = splitter.split_into_clauses(text)

        root_sintax_tree = SyntaxNode("ROOT", "ROOT")

        sent_end = False
        hyp = False

        independent_roots = []
        independent_nodes = []

        nodes = []
        predicate_nodes = []
        k = 0
        count_clauses = 0

        for clause in clauses:
            tokens = clause["tokens"]
            separator = clause["separator"]
            descriptor = clause["descriptor"]
            parsed = [self.morph_analyzer.analyze_word(word) for word in tokens]
            root_clause, nodes_clause, pred_nodes = self.build_syntax_tree(parsed)
            if self.is_independent_clause(nodes_clause):
                independent_roots += [root_clause]
                independent_nodes += [nodes_clause]
            # else:
            #     nodes += nodes_clause

            nodes += nodes_clause
            pred_nodes = [[p_n[0], p_n[1] + k] for p_n in pred_nodes]
            predicate_nodes += pred_nodes
            k += len(clause.get("tokens"))
            count_clauses += 1

            if "SENT_END" in descriptor:
                if count_clauses > 1:
                    root, _, _ = self.build_syntax_tree(nodes, False, predicate_nodes)
                    sent_root = SyntaxNode("SENT", "SENT")
                    sent_root.add_connection(root, "INDEPENDENT")
                    root_sintax_tree.add_connection(sent_root, 'sentence')
                    nodes = []
                    predicate_nodes = []
                    k = 0
                    count_clauses = 0
                else:
                    root_sintax_tree.add_connection(root_clause, "SENT")
            else:

                if "HYP" in descriptor:
                    hyp = True

                else:
                    hyp = False

            # отладка
            # print(parsed)
            # self.print_tree(root_clause)

        return root_sintax_tree

    def is_independent_clause(self, nodes):
        has_subject = any(node.part_of_sentence == PartOfSpeech.SUBJECT for node in nodes)
        has_predicate = any(node.part_of_sentence == PartOfSpeech.PREDICATE for node in nodes)
        return has_subject and has_predicate

    def check_common_word(self, arr1, arr2):
        return len(set(arr1) & set(arr2)) > 0

    def check_homogeneous_agreement(self, node1, node2):
        if node1.type != node2.type:
            return False
        if node1.type in ["NPRO"] and not (self.check_common_word(node1.features.get("case"), ["nomn"])):
            return False
        if node1.type in ['NOUN', 'ADJF', 'NPRO']:
            if not (self.check_common_word(node1.features.get('case'), node2.features.get('case'))):
                return False
        if node1.features.get('number') != node2.features.get('number'):
            return False
        if node1.type == 'VERB':
            if node1.features.get('tense') != node2.features.get('tense'):
                return False
        return True

    def find_homogeneous_groups(self, nodes):
        conjunctions = {'и', 'или', 'а', 'но'}
        homogeneous_groups = []
        used_indices = set()
        independent_pos = ['VERB', 'NOUN', 'ADVB', "NUMR", "INFI", "NPRO", "ADJF", "ADV_PARTICIPLE"]

        for i, node in enumerate(nodes):
            if nodes[i].lemma.lower() in conjunctions and i not in used_indices:
                flag_for_left = False
                for left in range(i - 1, -1, -1):
                    if left in used_indices:
                        continue
                    if nodes[left].type in independent_pos:
                        for right in range(i + 1, len(nodes)):
                            if right in used_indices:
                                continue
                            if (nodes[right].type in independent_pos and
                                    self.check_homogeneous_agreement(nodes[left], nodes[right])):
                                group = [nodes[left], nodes[i], nodes[right]]
                                homogeneous_groups.append(group)
                                used_indices.update({left, i, right})
                                flag_for_left = True
                                break
                    if flag_for_left:
                        break
        return homogeneous_groups

    def handle_homogeneous(self, nodes):
        homogeneous_groups = self.find_homogeneous_groups(nodes)
        for group in homogeneous_groups:
            parent = group[0]
            for node in group[1:]:
                parent.add_connection(node, 'homogeneous')
            self.print_tree(parent)
        return nodes

    def connect_pp_to_n(self, node_pp, node_n):
        return self.check_common_word(node_n.features.get('case'), node_pp.features.get("case"))

    def conect_to_predicate(self, i, default_pred, node, info):
        pred = default_pred
        maxI = 0
        for predicate in self.predicate_nodes:
            if predicate[1] < i and predicate[1] > maxI:
                pred = predicate[0]
                maxI = predicate[1]
        pred.add_connection(node, info)

    def build_syntax_tree(self, parsed_tokens, first_flag=True, p_n=[]):
        """Построение синтаксического дерева."""
        if first_flag:
            # for token in parsed_tokens:
            #     print(token)
            # print("-"*100 +"\n\n")
            nodes = [SyntaxNode(feat['pos'], feat['lemma'], feat) for feat in parsed_tokens]
            self.predicate_nodes = []

        else:
            nodes = parsed_tokens
            self.predicate_nodes = p_n

        predicate_node = None
        subject_node = None
        definition_node = None
        circumstance_node = None

        # Поиск сказуемого (глагол в изъявительном наклонении)
        for i, node in enumerate(nodes):
            if node.type == 'VERB' and node.features.get('tense') is not None:
                node.change_part_of_sent(PartOfSpeech.PREDICATE)
                predicate_node = node
                self.predicate_nodes += [[node, i]]
                break

        # перебор всех нодов
        for i, node in enumerate(nodes):
            if node.parent == None:

                # Поиск подлежащего (существительное в именительном падеже)
                if node.type in ['NOUN', 'NPRO'] and "nomn" in node.features.get('case') and subject_node == None:
                    subject_node = node
                    if predicate_node:
                        node.change_part_of_sent(PartOfSpeech.SUBJECT)
                        self.conect_to_predicate(i, predicate_node, node, 'subject')


                # Обработка однородных сказуемых
                elif node.type == 'VERB' and node != predicate_node:
                    node.change_part_of_sent(PartOfSpeech.PREDICATE)
                    self.predicate_nodes += [[node, i]]
                    if predicate_node:
                        predicate_node.add_connection(node, 'homogeneous')


                # обработка инфинитива
                elif node.type == 'INFI':
                    node.change_part_of_sent(PartOfSpeech.PREDICATE)
                    self.predicate_nodes += [[node, i]]
                    if predicate_node:
                        self.conect_to_predicate(i, predicate_node, node, 'predicate')


                elif node.type in ["PRCL", "PART"]:
                    if i + 1 < len(nodes):
                        nodes[i + 1].add_connection(node, "participle")


                # Обработка определений (прилагательные)
                elif (node.type == 'ADJF' and node.features.get('case') != []) or node.type == "PARTICIPLE":
                    node.change_part_of_sent(PartOfSpeech.DEFINITION)
                    closest_noun = next((n for n in nodes[i + 1:]
                                         if n.type in ['NOUN', 'NPRO']), None)
                    if closest_noun:
                        closest_noun.add_connection(node, 'attribute')
                    else:
                        definition_node = node


                # Обработка дополнений с предлогами
                elif node.type == 'PREP':  # Если это предлог
                    node.change_part_of_sent(PartOfSpeech.OBJECT)

                    # Ищем следующее существительное (дополнение)
                    next_noun = next((n for n in nodes[i + 1:]
                                      if n.type in ['NOUN', 'NPRO'] and self.connect_pp_to_n(node, n)), None)

                    # Связываем предлог с дополнением
                    if next_noun and not (next_noun.parent):
                        next_noun.change_part_of_sent(PartOfSpeech.OBJECT)
                        node.add_connection(next_noun, 'object')
                    # Связываем предлог с глаголом (сказуемым)
                    if predicate_node:
                        self.conect_to_predicate(i, predicate_node, node, 'prepositional_object')

                    # next_noun = None
                    # for n in nodes[i + 1:]:
                    #     if n.type in ['NOUN', 'NPRO'] and self.connect_pp_to_n(node, n):
                    #         n.change_part_of_sent(PartOfSpeech.OBJECT)
                    #         next_noun = n
                    #         break



                # Обработка обстоятельств
                elif (node.type in ['ADVB', "ADJF_SHORT"]) or (
                        node.type == 'ADJF' and node.features.get('case') == []):  # Если это наречие (обстоятельство)
                    node.change_part_of_sent(PartOfSpeech.CIRCUMSTANCE)
                    if predicate_node:
                        self.conect_to_predicate(i, predicate_node, node, 'adverbial')


                # обраьотка дополнений в родительном падеже
                elif ((node.type == 'NOUN' or node.type == 'NPRO') and 'gent' in node.features.get('case')):
                    node.change_part_of_sent(PartOfSpeech.OBJECT)
                    for n in nodes[i - 1::-1]:
                        if n.type in ['NOUN', 'NPRO', "VERB", "INFI"]:
                            n.add_connection(node, 'genitive')
                            break


                elif (node.type == "ADVB_PARTICIPLE"):
                    node.change_part_of_sent(PartOfSpeech.CIRCUMSTANCE)
                    if circumstance_node:
                        circumstance_node.add_connection(node, 'homogeneous')
                    elif predicate_node:
                        self.conect_to_predicate(i, predicate_node, node, 'circumstance')
                        circumstance_node = node
                    else:
                        circumstance_node = node

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

        return root_node, nodes, self.predicate_nodes

    def print_tree(self, node, level=0, relation=''):
        """Визуализация синтаксического дерева."""
        if not node:
            return

        print(' ' * level + f'└─ {relation} {node}')

        for child, rel in node.connections:
            self.print_tree(child, level + 1, rel)


# Пример использования
if __name__ == "__main__":
    print("\nСинтаксический анализ:")
    text = """Дядя самых честных правил, когда не в шутку занемог, он уважать себя заставил, и лучше выдумать не мог."""
    text1 = """Две старые кошки, мурлыча и грациозно двигаясь, поймали трёх мелких мышей в саду, но потом убежали в тёмный лес, где всегда тихо."""

    text4 = """Я очень люблю читать разные, старые романы Бориса Акунина о подвигах статского советника Фондорина и его поручика Массы и представлять себя на месте главного героя этого замечательного романа."""
    analyzer = SintaxisAnalyzer()
    results = analyzer.analyze(text4)
    analyzer.print_tree(results)
    visualize_tree(results)


# Синтаксический анализ:
# └─  ROOT('ROOT', {})
#  └─ sentence SENT('SENT', {})
#   └─ INDEPENDENT VERB('ЗАНЕМОЧЬ', {'word': 'занемог', 'lemma': 'ЗАНЕМОЧЬ', 'pos': 'VERB', 'case': [], 'number': ['sing'], 'gender': [], 'tense': ['past'], 'animacy': []})
#    └─ prepositional_object PREP('В', {'word': 'в', 'lemma': 'В', 'pos': 'PREP', 'case': ['loct', 'accs', 'datv'], 'number': [], 'gender': [], 'tense': [], 'animacy': []})
#     └─ participle PART('НЕ', {'word': 'не', 'lemma': 'НЕ', 'pos': 'PART', 'case': [], 'number': [], 'gender': [], 'tense': [], 'animacy': []})
#     └─ object NOUN('ШУТКА', {'word': 'шутку', 'lemma': 'ШУТКА', 'pos': 'NOUN', 'case': ['accs'], 'number': ['sing'], 'gender': ['femn'], 'tense': [], 'animacy': ['inan']})
#    └─ subject NOUN('ДЯДЯ', {'word': 'Дядя', 'lemma': 'ДЯДЯ', 'pos': 'NOUN', 'case': ['nomn'], 'number': ['sing'], 'gender': [], 'tense': [], 'animacy': ['anim']})
#     └─ genitive NPRO('САМЫЙ', {'word': 'самых', 'lemma': 'САМЫЙ', 'pos': 'NPRO', 'case': ['accs', 'loct', 'gent'], 'number': ['plur'], 'gender': [], 'tense': [], 'animacy': ['inan', 'anim']})
#      └─ genitive NOUN('ПРАВИЛО', {'word': 'правил', 'lemma': 'ПРАВИЛО', 'pos': 'NOUN', 'case': ['gent'], 'number': ['plur'], 'gender': [], 'tense': [], 'animacy': ['inan']})
#       └─ attribute ADJF('ЧЕСТНЫЙ', {'word': 'честных', 'lemma': 'ЧЕСТНЫЙ', 'pos': 'ADJF', 'case': ['accs', 'loct', 'gent'], 'number': ['plur'], 'gender': [], 'tense': [], 'animacy': ['inan', 'anim']})
#    └─ homogeneous VERB('ЗАСТАВИТЬ', {'word': 'заставил', 'lemma': 'ЗАСТАВИТЬ', 'pos': 'VERB', 'case': [], 'number': ['sing'], 'gender': [], 'tense': ['past'], 'animacy': []})
#     └─ subject NPRO('ОН', {'word': 'он', 'lemma': 'ОН', 'pos': 'NPRO', 'case': ['nomn'], 'number': ['sing'], 'gender': [], 'tense': [], 'animacy': []})
#     └─ predicate INFI('УВАЖАТЬ', {'word': 'уважать', 'lemma': 'УВАЖАТЬ', 'pos': 'INFI', 'case': [], 'number': [], 'gender': [], 'tense': [], 'animacy': []})
#      └─ genitive NPRO('СЕБЯ', {'word': 'себя', 'lemma': 'СЕБЯ', 'pos': 'NPRO', 'case': ['accs', 'gent'], 'number': [], 'gender': [], 'tense': [], 'animacy': []})
#    └─ homogeneous VERB('МОЧЬ', {'word': 'мог', 'lemma': 'МОЧЬ', 'pos': 'VERB', 'case': [], 'number': ['sing'], 'gender': [], 'tense': ['past'], 'animacy': []})
#     └─ adverbial ADJF('ХОРОШИЙ', {'word': 'лучше', 'lemma': 'ХОРОШИЙ', 'pos': 'ADJF', 'case': [], 'number': [], 'gender': [], 'tense': [], 'animacy': ['inan', 'anim']})
#     └─ predicate INFI('ВЫДУМАТЬ', {'word': 'выдумать', 'lemma': 'ВЫДУМАТЬ', 'pos': 'INFI', 'case': [], 'number': [], 'gender': [], 'tense': [], 'animacy': []})
#     └─ participle PART('НЕ', {'word': 'не', 'lemma': 'НЕ', 'pos': 'PART', 'case': [], 'number': [], 'gender': [], 'tense': [], 'animacy': []})