from enum import Enum
from sympy import andre

class PartOfSpeech(Enum):
    SUBJECT = "Подлежащее"
    PREDICATE = "Сказуемое"
    SUB_PREDICATE = "Инфинитив"
    OBJECT = "Дополнение"
    CIRCUMSTANCE = "Обстоятельство"
    DEFINITION = "Определение"
    NONE = "Не определено"
    NOMINAL_PREDICATE = "Номинальное сказуемое"
    MAIN_PREDICATE = "Корневое сказуемое"
    MAIN_SUBJECT = "Корневое подлежащее"

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

    def analyze(self, clauses, parsed_morph_tokens):

        hyp = False
        col = False
        all_nodes = []

        nodes_in_sent = []
        sub_conj_sent = []
        coord_conj_sent = []

        separator = ""

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
            previous_separator = separator
            separator = clause["separator"]
            sub_conjunctions = clause["sub_conjunctions"]
            coord_conjunctions = clause["coord_conjunctions"]
            sub_conj_sent+=sub_conjunctions
            coord_conj_sent+=coord_conjunctions

            #parsed = [self.morph_analyzer.analyze_word(word) for word in tokens]
            parsed_morph = parsed_morph_tokens[i] #берем чписок соответствующий iй клаузе

            hyp = "HYP" in clause["descriptor"]
            indep = any(correct_sep in previous_separator for correct_sep in sub_conjunctions)

            clause_roots, clause_nodes= self.build_syntax_tree(parsed_morph,None, hyp, indep) #внутриклаузный анализ

            clause_root = clause_roots[0]
            if self.is_independent_clause(clause_nodes,clause_root,indep):
                nodes_in_sent +=[['indep', clause_root, clause_nodes]]
            else:
                nodes_in_sent +=[['dep', clause_root, clause_nodes]]

            #if "HYP" in descriptor:
            # #print("тире")
            #     if nodes_in_sent[-1][0] == "dep":
            #         hyp = True
            #
            # elif "COL" in descriptor:
            #     #print("двоеточие")
            #     col = True

            if "SENT_END" in descriptor:

                sent_root = SyntaxNode("SENT", "SENT")
                roots, nodes = self.build_syntax_tree([], nodes_in_sent) #повторный межклаузный анализ
                all_nodes += nodes

                for root in roots:
                    part_sent_root = SyntaxNode("PART_SENT", "PART_SENT")
                    part_sent_root.add_connection(root, "part")
                    sent_root.add_connection(part_sent_root, "indep+dep")

                root_sintax_tree.add_connection(sent_root, 'sentence')

                purpose_statement, intonation, complexity = self.collect_info_by_sent(separator, roots, sub_conj_sent)

                info_count_sent += 1
                info_count_part_sent += [len(roots)]
                info_two_part += [any(self.is_link_pred_subj(root)==True for root in roots)]
                info_purpose_statement += [purpose_statement]
                info_intonation += [intonation]
                info_complexity += [complexity]
                info_common += [any(self.is_link_common(root)==True for root  in roots)]
                info_homogeneous += [any(self.is_link_homogeneous(root)==True for root  in roots)]

                hyp = False
                col = False
                nodes_in_sent = []
                sub_conj_sent = []
                coord_conj_sent = []


            #отладка
            print(parsed_morph)
            print(self.print_tree(clause_root))

        text_info = info_count_sent, info_count_part_sent, info_two_part, info_purpose_statement, info_intonation,\
            info_complexity, info_common, info_homogeneous

        return root_sintax_tree, all_nodes, text_info, self.print_tree(root_sintax_tree)

    def collect_info_by_sent(self,separator,roots,sub_conj_sent):
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
        elif (len(sub_conj_sent) > 0):
            complexity = 0
        else:
            complexity = 1

        return purpose_statement, purpose_statement, complexity

    def init_sintax_nodes(self,parsed_tokens):
        nodes = []
        for feat in parsed_tokens:
            if feat:
                if feat["pos"]:
                    nodes += [SyntaxNode(feat['pos'], feat['lemma'], feat)]
                else:
                    nodes += [SyntaxNode("UNDEFIND", feat['lemma'], feat)]
        return nodes

    def reformat_sintax_nodes(self,parsed_list):
        nodes = []
        for clause_info in parsed_list:
            # nodes += clause_info[2]
            for node in clause_info[2]:
                if node == clause_info[1] and clause_info[0] == "indep":
                    if node.part_of_sentence == PartOfSpeech.NOMINAL_PREDICATE:
                        node.change_part_of_sent(PartOfSpeech.MAIN_PREDICATE)
                    if node.type == "VERB":
                        node.change_part_of_sent(PartOfSpeech.MAIN_PREDICATE)
                    if node.type in ["NOUN","NPRO"]:
                        node.change_part_of_sent(PartOfSpeech.MAIN_SUBJECT)
                nodes += [node]
        return nodes

    def collect_main_and_predicate(self,parsed_nodes):
        predicates = []
        main = []
        for i, node in enumerate(parsed_nodes):
            if node.part_of_sentence in [PartOfSpeech.PREDICATE, PartOfSpeech.SUB_PREDICATE]:
                predicates += [[node, i]]
            if node.part_of_sentence == PartOfSpeech.MAIN_PREDICATE:
                main += [[node, i]]
                predicates += [[node, i]]
            if node.part_of_sentence == PartOfSpeech.MAIN_SUBJECT:
                 main += [[node, i]]
        return main, predicates

    def build_syntax_tree(self, parsed_tokens, clauses_list=None, is_hyphen = False, is_indept = False):
        """Построение синтаксического дерева."""
        main = []
        nodes = []
        predicates = []
        main = []
        self.predicate_nodes = []
        self.is_hyphen = is_hyphen
        self.is_indept = is_indept

        if clauses_list is None:
            nodes = self.init_sintax_nodes(parsed_tokens)
            self.flag_finish_mode = False

        elif clauses_list:
            nodes = self.reformat_sintax_nodes(clauses_list)
            main, self.predicate_nodes = self.collect_main_and_predicate(nodes)
            self.flag_finish_mode = True

        predicate_node = self._find_primary_predicate(nodes,main)
        subject_node = self._find_subject_with_predicate(nodes)
        nominal_predicate_node = None
        definition_node = None
        circumstance_node = None

        for i, node in enumerate(nodes):
            if node.parent is None and \
                not(node.part_of_sentence in [PartOfSpeech.MAIN_PREDICATE,PartOfSpeech.MAIN_SUBJECT]):
                _, subject_node, definition_node, circumstance_node, nominal_predicate_node = \
                    self._process_node(node, i, nodes,predicate_node,\
                        subject_node,definition_node, circumstance_node,nominal_predicate_node)

        return self._determine_root_node(nodes, main, predicate_node, subject_node,nominal_predicate_node, circumstance_node,
                                         definition_node), nodes



    # Вспомогательные методы
    def connect_to_predicate(self, i, default_pred, node, link_type, numbers = [],genders = []):

        pred = None
        if default_pred:
            pred = default_pred#None#
        else:
            pred = self.predicate_nodes[0][0]
        maxI = 0
        maxDelt = 1000
        for predicate in self.predicate_nodes:
            #if int(i-predicate[1])<maxDelt and int(i-predicate[1])!=0:
            if predicate[1] < i and predicate[1] >= maxI :
                if self._can_connect(node,predicate[0],numbers,genders):
                    pred = predicate[0]
                    maxI = predicate[1]
                    maxDelt = i-predicate[1]
        if pred:
            if self._can_connect(node,pred,numbers,genders):
                pred.add_connection(node, link_type)
                return True
        return False

    def _can_connect(self,child,parent,numbers=[],genders=[]):
        if parent.part_of_sentence in [PartOfSpeech.PREDICATE, PartOfSpeech.MAIN_PREDICATE]:
            if child.part_of_sentence in [PartOfSpeech.PREDICATE]:
                num_connect = self.check_common_word(child.features.get("number"), parent.features.get("number")) or child.features.get("number") + parent.features.get("number") == []
                gender_connect = self.check_common_word(child.features.get("gender"), parent.features.get("gender")) or child.features.get("gender") + parent.features.get("gender") == []
                tense_connect = self.check_common_word(child.features.get("tense"), parent.features.get("tense")) or child.features.get("tense") + parent.features.get("tense") == []
                #type_connect = self.check_common_word(child.features.get("type"), parent.features.get("type")) or child.features.get("type") + parent.features.get("type") == []
                return num_connect and gender_connect and tense_connect #and type_connect

            elif child.part_of_sentence in [PartOfSpeech.SUB_PREDICATE]:
                #child_intrans = self.check_common_word(child.features.get("trans"),["intrans"]) or True
                parent_transe = self.check_common_word(parent.features.get("trans"), ["trans"])
                return  parent_transe #and child_intrans

            elif child.part_of_sentence in [PartOfSpeech.SUBJECT]:
                num_connect = self.check_common_word(parent.features.get("number"), numbers)
                num_null =  numbers == [] or parent.features.get("number") == []
                gender_connect = self.check_common_word(parent.features.get("gender"), genders)
                gender_null = genders == [] or parent.features.get("gender") == []
                return (num_connect or num_null) and (gender_connect or gender_null)

            elif child.part_of_sentence in [PartOfSpeech.OBJECT]:
                return True

            elif child.part_of_sentence in [PartOfSpeech.CIRCUMSTANCE]:
                return True

            elif child.part_of_sentence in [PartOfSpeech.DEFINITION]:
                return self.is_adjective_dependent_on_verb(parent,child)

            elif child.part_of_sentence in [PartOfSpeech.NONE]:
                return True

            elif child.part_of_sentence in [PartOfSpeech.MAIN_PREDICATE, PartOfSpeech.MAIN_SUBJECT]:
                return False

            return False

        elif parent.part_of_sentence in [PartOfSpeech.SUB_PREDICATE]:
            if child.part_of_sentence in [PartOfSpeech.PREDICATE,PartOfSpeech.SUBJECT,PartOfSpeech.SUB_PREDICATE,PartOfSpeech.DEFINITION]:
                return False
            return True

        elif parent.part_of_sentence in [PartOfSpeech.CIRCUMSTANCE]:
            if child.part_of_sentence in [PartOfSpeech.PREDICATE,PartOfSpeech.SUBJECT,PartOfSpeech.SUB_PREDICATE]:
                return False
            return True

        elif parent.part_of_sentence in [PartOfSpeech.DEFINITION]:
            if child.part_of_sentence in [PartOfSpeech.PREDICATE,PartOfSpeech.SUBJECT,PartOfSpeech.CIRCUMSTANCE] \
                    and not (child.type in ["PREP"]):
                return False
            return True





        else:
            if child.part_of_sentence in [PartOfSpeech.OBJECT]:
                return True
            return False


    def _find_primary_predicate(self, nodes, main):
        """Поиск основного сказуемого"""
        prime_pred = None


        prime_pred = next((pred[0] for pred in main if pred[0].type == "VERB"),None)
        if prime_pred:
            return prime_pred

        for i, node in enumerate(nodes):
            if node.type == 'VERB' and node.features.get('tense') is not None:
                node.change_part_of_sent(PartOfSpeech.PREDICATE)
                if not([node, i] in self.predicate_nodes):
                    self.predicate_nodes.append([node, i])
                if not prime_pred:
                    prime_pred = node
                    return prime_pred

        if len(main)>0 and not prime_pred:
            prime_pred = main[0][0]
            return prime_pred
        return prime_pred

    def _find_subject_with_predicate(self,nodes):
        for i, node in enumerate(nodes):
            if node.change_part_of_sent in [PartOfSpeech.SUBJECT,PartOfSpeech.MAIN_SUBJECT] and \
                    node.parent:
                if node.parent.change_part_of_sent in [PartOfSpeech.PREDICATE,PartOfSpeech.MAIN_PREDICATE]:
                    return node
        return None

    def _process_node(self, node, i, nodes, predicate_node, subject_node, definition_node, circumstance_node,nominal_predicate_node):
        """Обработка отдельного узла"""
        subject_node = \
        self._process_subject(node, i, predicate_node,subject_node)
        definition_node = \
        self._process_definition(node, i, nodes, definition_node, predicate_node)
        definition_node = \
        self._process_participle(node, i, nodes, definition_node,predicate_node)
        definition_node = \
        self._process_definition_N_A(node, i, nodes, definition_node,predicate_node)
        nominal_predicate_node = \
        self._process_nominal_predicate(node,nominal_predicate_node,subject_node,predicate_node)
        circumstance_node = \
        self._process_circumstance(node, i, predicate_node, circumstance_node)
        predicate_node = \
        self._process_verb(node, i, predicate_node)
        predicate_node = \
        self._process_infinitive(node, i, predicate_node)
        self._process_particle(node, i, nodes)
        self._process_preposition(node, i, nodes, predicate_node)
        subject_node = self._process_genitive(node, i, nodes, subject_node, nominal_predicate_node)
        self._process_adverbial_participle(node, nodes, circumstance_node, predicate_node, i)
        return predicate_node, subject_node, definition_node, circumstance_node, nominal_predicate_node

    def _process_nominal_predicate(self, node, nominal_predicate_node, subject_node, predicate_node):
        if (node!=subject_node and not predicate_node\
                and not nominal_predicate_node and not node.parent)\
                and ((self.is_indept )\
                or (self.is_hyphen and subject_node)) :
            if node.type in ["NOUN","NPRO"]:
                if "nomn" in node.features.get('case'):
                    # case_connect = self.check_common_word(node.features.get('case'),subject_node.features.get('case'))
                    # case_null = node.features.get('case') == [] or subject_node.features.get('case') == []
                    # num_connect = self.check_common_word(node.features.get('number'),subject_node.features.get('number'))
                    # num_null = node.features.get('number') == [] or subject_node.features.get('number') == []
                    # gender_connect = self.check_common_word(node.features.get('gender'),subject_node.features.get('gender'))
                    # gender_null = node.features.get('gender') == [] or subject_node.features.get('gender') == []
                    #if (case_connect or case_null) and (num_connect or num_null) and (gender_connect or gender_null):
                    nominal_predicate_node = node
                    node.change_part_of_sent(PartOfSpeech.NOMINAL_PREDICATE)
                    if subject_node:
                        subject_node.add_connection(nominal_predicate_node,"nominal_pred")
            elif node.type in ["ADJF_SHORT", "PARTICIPLE_SHORT", "PARTICIPLE", "ADJF"]:
                nominal_predicate_node = node
                node.change_part_of_sent(PartOfSpeech.NOMINAL_PREDICATE)
                if subject_node:
                    subject_node.add_connection(nominal_predicate_node, "nominal_pred")

        return nominal_predicate_node

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

            node.change_part_of_sent(PartOfSpeech.SUBJECT)
            if predicate_node:
                self.connect_to_predicate(i, predicate_node, node, 'subject',numbers,genders)

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
                self.connect_to_predicate(i, predicate_node, node,'homogeneous')
        return predicate_node

    def _process_infinitive(self, node, i, predicate_node):
        """Обработка инфинитивов"""
        if node.type == 'INFI':
            node.change_part_of_sent(PartOfSpeech.SUB_PREDICATE)
            self.predicate_nodes.append([node, i])
            if predicate_node :#or self.predicate_nodes:
                self.connect_to_predicate(i, predicate_node, node, 'predicate')
        return predicate_node

    def _process_particle(self, node, i, nodes):
        """Обработка частиц"""
        if node.type in ["PRCL", "PART"] and i + 1 < len(nodes):
            nodes[i + 1].add_connection(node, "participle")

    def _process_participle(self, node, i, nodes,definition_node,predicate_node):
        """Обработка причастий"""
        if node.type in ["PARTICIPLE"]:
            node.change_part_of_sent(PartOfSpeech.DEFINITION)
            self.predicate_nodes.append([node, i])
            closest_noun = next((n for n in nodes[i + 1:] if n.type in ['NOUN', 'NPRO'] and
                                 self.connect_adjf_to_n(node, n)), None)
            if not closest_noun:
                closest_noun = next((n for n in nodes if n.type in ['NOUN', 'NPRO'] and
                                 self.connect_adjf_to_n(node, n)), None)

            if closest_noun:
                closest_noun.add_connection(node, 'attribute')
            # elif predicate_node and self.flag_finish_mode:
            #     self.connect_to_predicate(i, predicate_node, node, 'sub_predicate')

            if definition_node == None:
                definition = node
                return definition
        return definition_node

    def _process_definition(self, node, i, nodes,definition_node,predicate_node):
        """Обработка определений"""
        if node.type == 'ADJF' and node.features.get('case') != []:
            node.change_part_of_sent(PartOfSpeech.DEFINITION)
            if not node.connections:
                closest_noun = next((n for n in nodes[i + 1:] if n.type in ['NOUN', 'NPRO'] and
                                     self.connect_adjf_to_n(node,n)), None)
                if closest_noun:
                    closest_noun.add_connection(node, 'attribute')
                elif predicate_node and self.flag_finish_mode:# or self.predicate_nodes:
                    self.connect_to_predicate(i, predicate_node, node, 'sub_predicate')

            if definition_node == None:
                definition = node
                return definition
        return definition_node

    def is_adjective_dependent_on_verb(self, verb, adj):
        # Списки лемм глаголов-связок и глаголов оценки
        linking_verbs = {"быть", "стать", "казаться", "являться", "считаться", "оставаться"}
        opinion_verbs = {"считать", "называть", "полагать", "признавать"}


        # Правило 1: Составное именное сказуемое
        if verb.lemma.lower() in linking_verbs:
            # Проверяем падеж прилагательного или краткую форму
            if ("ADJF_SHORT" in adj.type) or (self.check_common_word(adj.features.get('case') ,["nomn", "ablt"])):
                return True

        # Правило 2: Предикативное употребление (краткая форма или безличное -о)
        if ("ADJF" in adj.type \
                and self.check_common_word(adj.features.get('case') ,["accs"])\
                and adj.features.get('word').endswith("о")):
            return True

        # Правило 3: Глаголы оценки + творительный падеж
        if verb.lemma.lower() in opinion_verbs \
                and self.check_common_word(adj.features.get('case') ,["ablt"]):
            return True

        # Во всех остальных случаях — не зависит
        return False

    def _process_definition_N_A(self, node, i, nodes,definition_node,predicate_node):
        """Обработка определений"""
        if node.type == 'NPRO_ADJF' or node.type == 'NOUN_ADJF':
            node.change_part_of_sent(PartOfSpeech.DEFINITION)
            if not node.connections:
                closest_noun = next((n for n in nodes[i + 1:] if n.type in ['NOUN', 'NPRO'] and
                                     (self.connect_adjf_to_n(node,n) or 1)), None)
                if closest_noun:
                    closest_noun.add_connection(node, 'attribute')
                elif predicate_node:
                    if self.flag_finish_mode:
                        self.connect_to_predicate(i, predicate_node, node, 'sub_predicate')
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
            if  all(not(connect[0].type in ['NOUN', 'NPRO']) for connect in node.connections):
                next_noun = next((n for n in nodes[i + 1:]
                                  if n.type in ['NOUN', 'NPRO'] and not (n.parent) and self.connect_pp_to_n(node, n)), None)

                # Связываем предлог с дополнением
                if next_noun and not (next_noun.parent):
                    part_of_speech = self._choose_role_prep_noum(node,next_noun)
                    node.change_part_of_sent(part_of_speech)
                    next_noun.change_part_of_sent(part_of_speech)
                    node.add_connection(next_noun, 'object')
                    # Связываем предлог с глаголом (сказуемым)
            if predicate_node or self.predicate_nodes:
                self.connect_to_predicate(i, predicate_node, node, 'prepositional_object')

    def _choose_role_prep_noum(self,prep,noun):
        object_rules = [
            {"preposition": ["к", "ко"], "case": "datv"},
            {"preposition": ["по"], "case": "datv"},
            {"preposition": ["над"], "case": "ablt"},
            {"preposition": ["без"], "case": "gent"},
            {"preposition": ["для"], "case": "gent"},
            {"preposition": ["о", "об", "про"], "case": "loct"},
            {"preposition": ["с", "со"], "case": "ablt"},
            {"preposition": ["из"], "case": "gent"},  # если объект исключения (из группы)
            {"preposition": ["от"], "case": "gent"},
            {"preposition": ["у"], "case": "gent"},  # у дома (принадлежность)
        ]
        circumstance_rules = [
            {"preposition": ["в", "во", "на"], "case": "accs"},  # направление (в парк)
            {"preposition": ["в", "во", "на"], "case": "loct"},  # место (в парке)
            {"preposition": ["из"], "case": "gent"},  # источник (из леса)
            {"preposition": ["перед"], "case": "ablt"},  # время (перед закатом)
            {"preposition": ["после"], "case": "gent"},  # время (после дождя)
            {"preposition": ["ради"], "case": "gent"},  # цель (ради победы)
            {"preposition": ["из-за"], "case": "gent"},  # причина (из-за тумана)
            {"preposition": ["с"], "case": "accs"},  # время (с утра)
            {"preposition": ["под"], "case": "ablt"},  # место (под землёй)
            {"preposition": ["через"], "case": "accs"},  # время (через час)
            {"preposition": ["до"], "case": "gent"},  # предел (до рассвета)
        ]
        for rule in object_rules:
            if prep.features.get("word").lower() in rule["preposition"] \
                    and self.check_common_word(noun.features.get("case"),[rule["case"]]):
                return PartOfSpeech.OBJECT

            # Проверка правил для обстоятельства
        for rule in circumstance_rules:
            prep_in_rule = prep.features.get("word").lower() in rule["preposition"]
            case_connect = self.check_common_word(noun.features.get("case"),[rule["case"]])
            if prep_in_rule and case_connect:
                return PartOfSpeech.CIRCUMSTANCE

            # Если не найдено совпадений, вернуть "дополнение" как значение по умолчанию
        return PartOfSpeech.OBJECT

    def _process_circumstance(self, node, i, predicate_node, circumstance_node):
        """Обработка обстоятельств"""
        if (node.type in ['ADVB', "ADJF_SHORT","PARTICIPLE_SHORT"]) or (node.type == 'ADJF' and not node.features.get('case')):

            if not node.part_of_sentence:
                node.change_part_of_sent(PartOfSpeech.CIRCUMSTANCE)

            if predicate_node or self.predicate_nodes:
                if self.connect_to_predicate(i, predicate_node, node, 'adverbial'):
                    node.change_part_of_sent(PartOfSpeech.CIRCUMSTANCE)
            if circumstance_node == None:
                circumstance = node
                return circumstance
        return circumstance_node

    def _process_genitive(self, node, i, nodes, subject_node, nominal_pred):
        """Обработка родительного падежа"""
        if (node.type in ['NOUN', 'NPRO']
                and self.check_common_word(['gent', 'accs',"ablt"] ,node.features.get('case'))#and 'gent' in node.features.get('case')
                and not node.parent and node!=nominal_pred) :#and node != subject_node):#
            for n in reversed(nodes[:i]):
                if n.type in ['NOUN', 'NPRO', "VERB", "INFI"]:
                    node.change_part_of_sent(PartOfSpeech.OBJECT)
                    n.add_connection(node, 'genitive')
                    if node == subject_node:
                        subject_node = None
                        return subject_node
                    break
        return subject_node

    def _process_adverbial_participle(self, node, nodes, circumstance_node, predicate_node, i):
        """Обработка деепричастий"""
        if node.type == "ADVB_PARTICIPLE":
            node.change_part_of_sent(PartOfSpeech.CIRCUMSTANCE)
            self.predicate_nodes.append([node, i])
            if  "trans" in node.features.get("trans") and not node.connections:
                noun = next((n for n in nodes[i + 1:] if n.type in ['NOUN', 'NPRO'] and not (n.parent)), None)
                if noun:
                    noun.change_part_of_sent(PartOfSpeech.OBJECT)
                    node.add_connection(noun,'genitive')
            if circumstance_node:
                circumstance_node.add_connection(node, 'homogeneous')
            elif predicate_node:
                self.connect_to_predicate(i, predicate_node, node, 'circumstance')

    def _determine_root_node(self, nodes, main, predicate_node, subject_node, nominal_predicate_node, circumstance_node, definition_node):
        """Определение корневого узла"""
        if main:
            # if subject_node:
            #     subject_node.change_part_of_sent(PartOfSpeech.SUBJECT)
            main_nodes = [data[0] for data in main ]
            if predicate_node and not predicate_node in main_nodes:
                main_nodes += [predicate_node]
            return main_nodes
        if predicate_node:
            return [predicate_node]
        if subject_node:
            subject_node.change_part_of_sent(PartOfSpeech.SUBJECT)
            return [subject_node]
        if nominal_predicate_node:
            return [nominal_predicate_node]
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

    def is_independent_clause(self, nodes, root,correct_sep):
        has_subject = any(node.part_of_sentence == PartOfSpeech.SUBJECT for node in nodes)
        has_predicate = any(node.part_of_sentence in [PartOfSpeech.PREDICATE, PartOfSpeech.NOMINAL_PREDICATE] for node in nodes)
        root_is_predicate = (root.part_of_sentence in [PartOfSpeech.PREDICATE] )
        root_is_subject = (root.part_of_sentence in [PartOfSpeech.SUBJECT] )
        root_is_nominal_predicate = (root.part_of_sentence in [PartOfSpeech.NOMINAL_PREDICATE])
        partsent_has_correct_sep =correct_sep#any(correct_sep in previous_sep for correct_sep in list_sub_conj)

        return (((has_subject and has_predicate) or (partsent_has_correct_sep))
                and (root_is_predicate or root_is_subject or root_is_nominal_predicate))

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