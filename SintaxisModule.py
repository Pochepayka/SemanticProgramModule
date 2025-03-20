from enum import Enum


class PartOfSpeech(Enum):
    SUBJECT = "Подлежащее"
    PREDICATE = "Сказуемое"
    SUB_PREDICATE = "Инфинитив"
    OBJECT = "Дополнение"
    CIRCUMSTANCE = "Обстоятельство"
    DEFINITION = "Определение"
    NONE = "Не определено"
    MAIN_PREDICATE = "Корневое сказуемое"
    MAIN_SUBJECT = "Корневое подлежащее"
    MAIN = "Главный корень"

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

    def analyze(self, clauses, parseds):#text):

        # splitter = ClauseSplitter()
        # clauses = splitter.split_into_clauses(text)

        # hyp = False
        all_nodes = []

        nodes_in_sent = []
        sub_conj_sent = []
        coord_conj_sent = []

        info_count_sent = 0
        info_count_part_sent = [] # list of int
        info_two_part = [] # list of list of bool [[True,False],[True],[True,True,False]]
        info_purpose_statement = [] # list of [повествовательное/побудительное/вопросительное]
        info_intonation = [] # list of [невосклицательное/восклицательное]
        info_complexity = [] # list of [difficult-subordinate/difficult-to-compose/simple]
        info_common = [] # list of [True/False]
        info_homogeneous = [] #list ot [True/False]


        root_sintax_tree = SyntaxNode("ROOT", "ROOT")

        for i, clause in enumerate(clauses):

            tokens = clause["tokens"]
            descriptor = clause["descriptor"]
            separator = clause["separator"]
            sub_conjunctions = clause["sub_conjunctions"]
            sub_conj_sent+=sub_conjunctions
            coord_conjunctions = clause["coord_conjunctions"]
            coord_conj_sent+=coord_conjunctions

            #parsed = [self.morph_analyzer.analyze_word(word) for word in tokens]
            parsed_morph = parseds[i]

            clause_roots, clause_nodes= self.build_syntax_tree(parsed_morph)
            clause_root = clause_roots[0]
            if self.is_independent_clause(clause_nodes,clause_root):
                nodes_in_sent +=[['indep', clause_root, clause_nodes]]
            else:
                nodes_in_sent +=[['dep', clause_root, clause_nodes]]


            if "SENT_END" in descriptor:

                sent_root = SyntaxNode("SENT", "SENT")

                roots, nodes = self.build_syntax_tree([], nodes_in_sent)
                all_nodes += nodes

                for root in roots:
                    part_sent_root = SyntaxNode("PART_SENT", "PART_SENT")
                    part_sent_root.add_connection(root, "part")
                    sent_root.add_connection(part_sent_root, "indep+dep")

                root_sintax_tree.add_connection(sent_root, 'sentence')

                purpose_statement = 0
                if "?" in separator:
                    purpose_statement = 2
                elif "!" in separator:
                    purpose_statement = 1
                else:
                    purpose_statement = 0

                intonation = 0
                if "!" in separator:
                    intonation = 1
                else:
                    intonation = 0

                complexity = 0
                if (len(roots) == 1):
                    complexity = 2
                elif (len(sub_conj_sent)>0):
                    complexity = 0
                else:
                    complexity = 1


                info_count_sent += 1
                info_count_part_sent += [len(roots)]
                info_two_part += [any(self.is_link_pred_subj(root)==True for root in roots)]
                info_purpose_statement += [purpose_statement]
                info_intonation += [intonation]
                info_complexity += [complexity]
                info_common += [any(self.is_link_common(root)==True for root  in roots)]
                info_homogeneous += [any(self.is_link_homogeneous(root)==True for root  in roots)]


                nodes_in_sent = []
                sub_conj_sent = []
                coord_conj_sent = []


            #отладка
            # print(parsed_morph)
            # print(self.print_tree(clause_root))

        text_info = info_count_sent, info_count_part_sent, info_two_part, info_purpose_statement, info_intonation,\
            info_complexity, info_common, info_homogeneous

        return root_sintax_tree, all_nodes, text_info, self.print_tree(root_sintax_tree)

    def build_syntax_tree(self, parsed_tokens, clauses_list=None):
        """Построение синтаксического дерева."""
        main = []
        nodes = []
        if clauses_list is None:
            for feat in parsed_tokens:
                if feat["pos"]:
                    nodes += [SyntaxNode(feat['pos'], feat['lemma'], feat)]
                else:
                    nodes += [SyntaxNode("UNDEFIND", feat['lemma'], feat)]
            self.predicate_nodes = []
        elif clauses_list:
            nodes = []

            for clause_info in clauses_list:
                # nodes += clause_info[2]
                for node in clause_info[2]:
                    if node == clause_info[1] and clause_info[0] == "indep":
                        if node.type == "VERB":
                            node.change_part_of_sent(PartOfSpeech.MAIN_PREDICATE)
                        if node.type == "NOUN":
                            node.change_part_of_sent(PartOfSpeech.MAIN_SUBJECT)
                    nodes += [node]

            predicates = []
            main = []
            for i, node in enumerate(nodes):
                if node.part_of_sentence in [PartOfSpeech.PREDICATE,PartOfSpeech.SUB_PREDICATE]:
                    predicates += [[node, i]]
                if node.part_of_sentence == PartOfSpeech.MAIN_PREDICATE:
                    main += [[node, i]]
                    predicates += [[node, i]]
                # if node.part_of_sentence == PartOfSpeech.MAIN_SUBJECT:
                #     main += [[node, i]]
            self.predicate_nodes = predicates

        predicate_node = self._find_primary_predicate(nodes,main)
        subject_node = self._find_subject_with_predicate(nodes)
        definition_node = None
        circumstance_node = None

        for i, node in enumerate(nodes):
            if node.parent is None and \
                    not(node.part_of_sentence in [PartOfSpeech.MAIN_PREDICATE,PartOfSpeech.MAIN_SUBJECT]):
                _,subject_node,definition_node,circumstance_node =\
                    self._process_node(
                    node, i, nodes,
                    predicate_node, subject_node,
                    definition_node, circumstance_node
                )

        return self._determine_root_node(nodes, main, predicate_node, subject_node, circumstance_node,
                                         definition_node), nodes


    # Вспомогательные методы
    def conect_to_predicate(self, i, default_pred, node, link_type, numbers = [],genders = []):
        pred = default_pred#None#
        maxI = 0
        maxDelt = 1000
        for predicate in self.predicate_nodes:
            #if int(i-predicate[1])<maxDelt and int(i-predicate[1])!=0:
            if predicate[1] < i and predicate[1] >= maxI :
                if not(node.type == "VERB" and predicate[0].type == "INFI") and \
                        ((self.check_common_word(predicate[0].features.get("number"), numbers) or \
                        numbers == [] or \
                        predicate[0].features.get("number") == []) and \
                        (self.check_common_word(predicate[0].features.get("gender"), genders) or \
                         genders == [] or \
                         predicate[0].features.get("gender") == [])):
                    pred = predicate[0]
                    maxI = predicate[1]
                    maxDelt = i-predicate[1]
        if pred:
            pred.add_connection(node, link_type)

    def _find_primary_predicate(self, nodes, main):
        """Поиск основного сказуемого"""
        prime_pred = None

        if len(main)>0 and not prime_pred:
            prime_pred = main[0][0]
            return prime_pred

        for i, node in enumerate(nodes):
            if node.type == 'VERB' and node.features.get('tense') is not None:
                node.change_part_of_sent(PartOfSpeech.PREDICATE)
                if not([node, i] in self.predicate_nodes):
                    self.predicate_nodes.append([node, i])
                if not prime_pred:
                    prime_pred = node
                    #return prime_pred
        return prime_pred

    def _find_subject_with_predicate(self,nodes):
        for i, node in enumerate(nodes):
            if node.change_part_of_sent in [PartOfSpeech.SUBJECT,PartOfSpeech.MAIN_SUBJECT] and \
                    node.parent:
                if node.parent.change_part_of_sent in [PartOfSpeech.PREDICATE,PartOfSpeech.MAIN_PREDICATE]:
                    return node
        return None

    def _process_node(self, node, i, nodes, predicate_node, subject_node, definition_node, circumstance_node):
        """Обработка отдельного узла"""
        subject_node = self._process_subject(node, i, predicate_node,subject_node)
        definition_node = self._process_definition(node, i, nodes, definition_node)
        circumstance_node = self._process_circumstance(node, i, predicate_node, circumstance_node)
        predicate_node = self._process_verb(node, i, predicate_node)
        predicate_node = self._process_infinitive(node, i, predicate_node)
        self._process_particle(node, i, nodes)
        self._process_preposition(node, i, nodes, predicate_node)
        self._process_genitive(node, i, nodes)
        self._process_adverbial_participle(node, nodes, circumstance_node, predicate_node, i)
        return predicate_node, subject_node, definition_node, circumstance_node

    def _process_subject(self, node, i, predicate_node, subject_node):
        """Обработка подлежащего"""

        if (node.type in ['NOUN', 'NPRO']
                and "nomn" in node.features.get('case')
                and not node.parent):
            numbers = []
            genders = []
            for var in node.features.get("variants"):
                if "nomn" in var:
                    numbers += [var[1]]
                    genders += [var[2]]
            #print("!!!!",node.lemma,numbers,genders)
            node.change_part_of_sent(PartOfSpeech.SUBJECT)
            if predicate_node:
                self.conect_to_predicate(i, predicate_node, node, 'subject',numbers,genders)

            if subject_node == None:
                subject = node
                return subject

        return subject_node

    def _process_verb(self, node, i, predicate_node):
        """Обработка глаголов и однородных сказуемых"""
        if node.type == 'VERB' and node != predicate_node:
            node.change_part_of_sent(PartOfSpeech.PREDICATE)
            self.predicate_nodes.append([node, i])
            if predicate_node:
                # predicate_node.add_connection(node, 'homogeneous')
                self.conect_to_predicate(i, predicate_node, node,'homogeneous')
        return predicate_node

    def _process_infinitive(self, node, i, predicate_node):
        """Обработка инфинитивов"""
        if node.type == 'INFI':
            node.change_part_of_sent(PartOfSpeech.PREDICATE)
            self.predicate_nodes.append([node, i])
            if predicate_node:
                self.conect_to_predicate(i, predicate_node, node, 'predicate')
        return predicate_node

    def _process_particle(self, node, i, nodes):
        """Обработка частиц"""
        if node.type in ["PRCL", "PART"] and i + 1 < len(nodes):
            nodes[i + 1].add_connection(node, "participle")

    def _process_definition(self, node, i, nodes,definition_node):
        """Обработка определений"""
        if (node.type == 'ADJF' and node.features.get('case') != []) or node.type == "PARTICIPLE":
            node.change_part_of_sent(PartOfSpeech.DEFINITION)
            if node.type == "PARTICIPLE":
                self.predicate_nodes.append([node, i])
            if not node.connections:
                closest_noun = next((n for n in nodes if n.type in ['NOUN', 'NPRO'] and
                                     self.connect_adjf_to_n(node,n)), None)
                if closest_noun:
                    closest_noun.add_connection(node, 'attribute')
            if definition_node == None:
                definition = node
                return definition

        return definition_node

    def connect_adjf_to_n(self,node,n):

        numbers = []
        genders = []
        for var in n.features.get("variants"):
            if self.check_common_word(node.features.get("case") ,var):
                numbers += [var[1]]
                genders += [var[2]]

        return( self.check_common_word(node.features.get("case") ,n.features.get("case")) and (self.check_common_word(node.features.get("number"), numbers) or \
          numbers == [] or \
          node.features.get("number") == []) and \
         (self.check_common_word(node.features.get("gender"), genders) or \
          genders == [] or \
          node.features.get("gender") == []))
        # print (n.lemma,[node.features.get("case")[0],node.features.get("number")[0],node.features.get("gender")[0]],
        #     n.features.get("variants"))
        return ([node.features.get("case")[0],node.features.get("number")[0],node.features.get("gender")[0]] in
            n.features.get("variants"))

    def _process_preposition(self, node, i, nodes, predicate_node):
        """Обработка предложных конструкций"""
        if node.type == 'PREP':
            node.change_part_of_sent(PartOfSpeech.OBJECT)
            if not node.connections:
                next_noun = next((n for n in nodes[i + 1:]
                                  if n.type in ['NOUN', 'NPRO'] and not (n.parent) and self.connect_pp_to_n(node, n)), None)

                # Связываем предлог с дополнением
                if next_noun and not (next_noun.parent):
                    next_noun.change_part_of_sent(PartOfSpeech.OBJECT)
                    node.add_connection(next_noun, 'object')
                    # Связываем предлог с глаголом (сказуемым)
            if predicate_node:
                self.conect_to_predicate(i, predicate_node, node, 'prepositional_object')

    def _process_circumstance(self, node, i, predicate_node, circumstance_node):
        """Обработка обстоятельств"""
        if (node.type in ['ADVB', "ADJF_SHORT"]) or (node.type == 'ADJF' and not node.features.get('case')):
            node.change_part_of_sent(PartOfSpeech.CIRCUMSTANCE)

            if predicate_node:
                self.conect_to_predicate(i, predicate_node, node, 'adverbial')
            if circumstance_node == None:
                circumstance = node
                return circumstance
        return circumstance_node

    def _process_genitive(self, node, i, nodes):
        """Обработка родительного падежа"""
        if (node.type in ['NOUN', 'NPRO']
                and self.check_common_word(['gent', 'accs'] ,node.features.get('case'))#and 'gent' in node.features.get('case')
                and not node.parent):
            node.change_part_of_sent(PartOfSpeech.OBJECT)
            for n in reversed(nodes[:i]):
                if n.type in ['NOUN', 'NPRO', "VERB", "INFI"]:
                    n.add_connection(node, 'genitive')
                    break

    def _process_adverbial_participle(self, node, nodes, circumstance_node, predicate_node, i):
        """Обработка деепричастий"""
        if node.type == "ADVB_PARTICIPLE":
            node.change_part_of_sent(PartOfSpeech.CIRCUMSTANCE)
            self.predicate_nodes.append([node, i])
            if  "trans" in node.features.get("trans") and not node.connections:
                noun = next((n for n in nodes[i + 1:] if n.type in ['NOUN', 'NPRO'] and not (n.parent)), None)
                if noun:
                    node.add_connection(noun,'genitive')
            if circumstance_node:
                circumstance_node.add_connection(node, 'homogeneous')
            elif predicate_node:
                self.conect_to_predicate(i, predicate_node, node, 'circumstance')

    def _determine_root_node(self, nodes, main, predicate_node, subject_node, circumstance_node, definition_node):
        """Определение корневого узла"""
        main_nodes = [data[0] for data in main ]
        if main:
            return main_nodes
        if predicate_node:
            return [predicate_node]
        if subject_node:
            return [subject_node]
        if circumstance_node:
            return [circumstance_node]
        if definition_node:
            return [definition_node]
        return [nodes[0]]

    def collect_all_nodes(self, root_node):
        """Рекурсивно собирает все узлы синтаксического дерева"""
        nodes = []

        def _traverse(node):
            if not(node.type in ["ROOT","SENT","PART_SENT"]):
                nodes.append(node)
            for child, _ in node.connections:
                _traverse(child)

        if root_node:
            _traverse(root_node)
        return nodes

    def is_link_pred_subj(self,root):
        for child, link_type in root.connections:
            if link_type == "subject":
                return True
        return False

    def is_link_homogeneous(self,root):
        def _traverse(node):
            link_types = []
            for child, link_type in node.connections:
                if link_type == "homogeneous" or link_type in link_types:
                    return True
                link_types += [link_type]

            for child, _ in node.connections:
                _traverse(child)

        if root:
            if _traverse(root):
                return True
        return False

    def is_link_common(self,root):
        def _traverse(node):
            for child, link_type in node.connections:
                if not(link_type in ["subject","homogeneous"]):
                    return True

            for child, _ in node.connections:
                _traverse(child)

        if root:
            if _traverse(root):
                return True
        return False

    def is_independent_clause(self, nodes, root):
        has_subject = any(node.part_of_sentence == PartOfSpeech.SUBJECT for node in nodes)
        has_predicate = any(node.part_of_sentence == PartOfSpeech.PREDICATE for node in nodes)
        root_is_predicate = (root.part_of_sentence == PartOfSpeech.PREDICATE)
        return has_subject and has_predicate and root_is_predicate

    def check_common_word(self, arr1, arr2):
        return len(set(arr1) & set(arr2)) > 0

    def check_homogeneous_agreement(self, node1, node2):
        if node1.type != node2.type:
            return False
        if node1.type in ["NPRO"] and not(self.check_common_word(node1.features.get("case"), ["nomn"])):
            return False
        if node1.type in ['NOUN', 'ADJF', 'NPRO']:
            if not(self.check_common_word(node1.features.get('case'), node2.features.get('case'))):
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

    def print_tree(self, root_node):
        """Визуализация синтаксического дерева."""

        text = []
        def _traverse(node,level=0,relation=''):
            text.append(' ' * level + f'└─ {relation} {node}')
            # print(' ' * level + f'└─ {relation} {node}')

            for child, rel in node.connections:
                _traverse(child, level + 1, rel)

        if root_node:
            _traverse(root_node)

        return "\n".join(text)



# Пример использования
if __name__ == "__main__":

    from MorphModule import MorphAnalyzer
    from ClauseSpliter import ClauseSplitter
    from GraphematicModule import GraphematicAnalyzer

    text = """
    Когда солнце взошло, мы отправились в путь, и дорога оказалась удивительно красивой. 
    Я знал, что он придёт, но всё равно волновался. 
    Она улыбнулась мне, потому что была рада встрече, и я почувствовал тепло её взгляда.
    """

    graph_analyzer = GraphematicAnalyzer()
    spliter = ClauseSplitter()
    morph_analyzer = MorphAnalyzer()

    graphems =graph_analyzer.analyze(text)
    clauses = spliter.split_into_clauses(graphems)

    morph_res_for_clauses = []
    for clause in clauses:
        morph_res_i_clause = []
        for word in clause.get("tokens"):
            morph_res_i_clause += [morph_analyzer.analyze_word(word)]
        morph_res_for_clauses += [morph_res_i_clause]

    analyzer = SintaxisAnalyzer()
    root, nodes, info = analyzer.analyze(clauses, morph_res_for_clauses)

    print("\nСинтаксический анализ:")
    print(analyzer.print_tree(root))