from enum import Enum

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
        self.link_to_parent = ""

    def change_part_of_sent(self, part_of_speech):
        self.part_of_sentence = part_of_speech

    def add_connection(self, node, relation):
        node.parent = self
        node.link_to_parent = relation
        self.connections.append((node, relation))

    def __repr__(self):
        return f"{self.type}('{self.lemma}', {self.features})"

class SintaxisAnalyzer:
    def __init__(self):
        self.predicate_node = None
        self.subject_node = None
        self.nominal_predicate_node = None
        self.definition_node = None
        self.circumstance_node = None

        self.predicate_nodes = []
        self.subject_nodes = []
        self.nominal_predicate_nodes = []
        self.definition_nodes = []
        self.circumstance_nodes = []

        self.main = []
        self.nodes = []
        self.means_action = []



        self.is_hyphen = None
        self.is_indept = None
        self.flag_finish_mode = None

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

            parsed_morph = parsed_morph_tokens[i] #берем чписок соответствующий iй клаузе

            hyp = "HYP" in clause["descriptor"]
            col = "COL" in clause["descriptor"]
            indep = any(correct_sep in previous_separator for correct_sep in sub_conjunctions)

            clause_roots, clause_nodes = self.build_syntax_tree(
                                    parsed_morph,None, hyp, indep) #внутриклаузный анализ

            clause_root = clause_roots[0]
            if self.is_independent_clause(clause_nodes,clause_root,indep):
                nodes_in_sent +=[['indep', clause_root, clause_nodes]]
            else:
                nodes_in_sent +=[['dep', clause_root, clause_nodes]]


            if "SENT_END" in descriptor:

                sent_root = SyntaxNode("SENT", "SENT")
                roots, nodes = self.build_syntax_tree([], nodes_in_sent)
                #повторный межклаузный анализ
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
            # print(parsed_morph)
            # print(self.print_tree(clause_root))

        text_info = info_count_sent, info_count_part_sent, info_two_part, info_purpose_statement, info_intonation,\
            info_complexity, info_common, info_homogeneous

        return root_sintax_tree, all_nodes, text_info, self.print_tree(root_sintax_tree)


    @staticmethod
    def init_sintax_nodes(parsed_tokens):
        new_nodes = []
        for feat in parsed_tokens:
            if feat:
                if feat["pos"]:
                    new_nodes += [SyntaxNode(feat['pos'], feat['lemma'], feat)]
                else:
                    new_nodes += [SyntaxNode("UNDEFIND", feat['lemma'], feat)]

        return new_nodes

    @staticmethod
    def reformat_sintax_nodes(parsed_list):
        ref_nodes = []
        main = []
        prime_subject = None
        prime_predicate = None
        i = 0
        for clause_info in parsed_list:

            #print(clause_info)

            for node in clause_info[2]:
                if node == clause_info[1] and clause_info[0] == "indep":
                    main += [[node, i]]
                    if (node.part_of_sentence == PartOfSpeech.PREDICATE
                            and (prime_predicate is None or prime_subject is None)):

                        prime_predicate = node
                        prime_subject = next((subj[0]
                                for subj in node.connections
                                    if subj[0].part_of_sentence is PartOfSpeech.SUBJECT),None)


                ref_nodes += [node]
                i+=1

        return ref_nodes, main, prime_subject, prime_predicate



    def build_syntax_tree(self, parsed_tokens, clauses_list=None,
                          is_hyphen = False, is_indept = False):
        """Построение синтаксического дерева."""

        self.main = []
        self.nodes = []
        self.means_action = []

        self.predicate_nodes = []
        self.subject_nodes =[]
        self.nominal_predicate_nodes = []
        self.definition_nodes = []
        self.circumstance_nodes = []

        self.predicate_node = None
        self.subject_node = None
        self.nominal_predicate_node = None
        self.definition_node = None
        self.circumstance_node = None

        self.is_hyphen = is_hyphen
        self.is_indept = is_indept

        if clauses_list is None:
            self.nodes = self.init_sintax_nodes(parsed_tokens)
            self.flag_finish_mode = False
        elif clauses_list:
            self.nodes, self.main, self.subject_node, self.predicate_node = (
                self.reformat_sintax_nodes(clauses_list))
            self.flag_finish_mode = True


        for i, node in enumerate(self.nodes):
            #if node.parent is None:
                self._prep_process_node(node,i)

        for i, node in enumerate(self.nodes):
            if node.parent is None and \
                all(m_n[0] != node for m_n in self.main):
                    self._process_node(node, i)

        return self._determine_root_node(), self.nodes

    # Вспомогательные методы для analize



    """==========Методы соединения========="""
    def connect_to_predicate(self, i, node, link_type, numbers=None, genders=None):

        if genders is None:
            genders = []
        if numbers is None:
            numbers = []

        parent = None

        if self.predicate_node is not None and self._can_connect(node,self.predicate_node,numbers,genders):
            parent = self.predicate_node
        elif self.predicate_nodes != [] and node != self.predicate_nodes[0][0]:
            if self._can_connect(node,self.predicate_nodes[0][0],numbers,genders):
                parent = self.predicate_nodes[0][0]
        elif self.means_action != [] and node != self.means_action[0][0]:
            if self._can_connect(node,self.means_action[0][0],numbers,genders):
                parent = self.means_action[0][0]

        maxI = 0
        maxDelt = 1000

        for predicate in self.means_action:
            # if int(i-predicate[1])<maxDelt and int(i-predicate[1])!=0:
            if i > predicate[1] >= maxI:
                if self._can_connect(node, predicate[0], numbers, genders):
                    parent = predicate[0]
                    maxI = predicate[1]
                    maxDelt = i - predicate[1]
        if parent:
            parent.add_connection(node, link_type)
            return True
        return False

    def _can_connect(self, child, parent, numbers=None, genders=None):
        if numbers is None:
            numbers = []
        if genders is None:
            genders = []

        if parent.part_of_sentence in [PartOfSpeech.PREDICATE, PartOfSpeech.MAIN_PREDICATE]:
            if child.part_of_sentence in [PartOfSpeech.PREDICATE]:
                num_connect = (self.check_common_word(child.features.get("number"), parent.features.get("number"))
                               or child.features.get("number") + parent.features.get("number") == [])
                gender_connect = (self.check_common_word(child.features.get("gender"), parent.features.get("gender"))
                                  or child.features.get("gender") + parent.features.get("gender") == [])
                tense_connect = (self.check_common_word(child.features.get("tense"), parent.features.get("tense"))
                                 or child.features.get("tense") + parent.features.get("tense") == [])
                #type_connect = self.check_common_word(child.features.get("type"), parent.features.get("type"))
                # or child.features.get("type") + parent.features.get("type") == []
                return num_connect and gender_connect and tense_connect #and type_connect

            elif child.part_of_sentence in [PartOfSpeech.SUB_PREDICATE]:
                #child_intrans = self.check_common_word(child.features.get("trans"),["intrans"]) or True
                #parent_transe = self.check_common_word(parent.features.get("trans"), ["trans"])
                return  True#parent_transe #and child_intrans

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

        elif parent.part_of_sentence in [PartOfSpeech.NOMINAL_PREDICATE]:
            if child.part_of_sentence in [PartOfSpeech.SUBJECT]:
                return False
            return True

        elif parent.part_of_sentence in [PartOfSpeech.SUB_PREDICATE]:
            if child.part_of_sentence in [PartOfSpeech.PREDICATE,PartOfSpeech.SUBJECT,
                                          PartOfSpeech.SUB_PREDICATE,PartOfSpeech.DEFINITION]:
                return False
            return True

        elif parent.part_of_sentence in [PartOfSpeech.CIRCUMSTANCE]:
            if child.part_of_sentence in [PartOfSpeech.PREDICATE,PartOfSpeech.SUBJECT,
                                          PartOfSpeech.SUB_PREDICATE]:
                return False
            return True

        elif parent.part_of_sentence in [PartOfSpeech.DEFINITION]:
            if child.part_of_sentence in [PartOfSpeech.PREDICATE,PartOfSpeech.SUBJECT,
                                          PartOfSpeech.CIRCUMSTANCE] \
                    and not (child.type in ["PREP"]):
                return False
            return True





        else:
            if child.part_of_sentence in [PartOfSpeech.OBJECT]:
                return True
            return False

    def _connect_by_gender(self, parent, child):
        gender_connect = self.check_common_word(parent.features.get('gender'), child.features.get('gender'))
        gender_null = parent.features.get('gender') == [] or child.features.get('gender') == []
        return gender_connect or gender_null

    def _connect_by_num(self, parent, child):
        num_connect = self.check_common_word(parent.features.get('number'), child.features.get('number'))
        num_null = parent.features.get('number') == [] or child.features.get('number') == []
        return num_connect or num_null

    def _connect_by_case(self, parent, child):
        case_connect = self.check_common_word(parent.features.get('case'), child.features.get('case'))
        case_null = parent.features.get('case') == [] or child.features.get('case') == []
        return case_connect or case_null
    """------------------------------------------------"""


    """==========Методы предобработки========="""
    def _prep_process_node(self,node, i):
        self._collect_primary_predicate(node, i)
        self._collect_means_action(node, i)
        self._collect_subject_nodes(node, i)
        self._process_definition(node,i)
        self._process_definition_N_A(node,i)
        self._collect_nominal_predicate(node,i)
        self._process_preposition(node, i)
        self._process_particle(node,i)

    def _collect_primary_predicate(self, node, i):

        if (node.type == 'VERB'
                and node.features.get('tense') is not None
                and node.parent is None):

            if not ([node, i] in self.predicate_nodes):
                self.predicate_nodes.append([node, i])

            if self.predicate_node is None:
                node.change_part_of_sent(PartOfSpeech.PREDICATE)
                self.predicate_node = node

    def _collect_means_action(self, node, i):

        if node.type in ["VERB", "INFI", "ADVB_PARTICIPLE", "PARTICIPLE"]:
            if node.type is "ADVB_PARTICIPLE":
                node.change_part_of_sent(PartOfSpeech.DEFINITION)

            elif node.type is "ADVB_PARTICIPLE":
                node.change_part_of_sent(PartOfSpeech.CIRCUMSTANCE)

            elif node.type is "VERB":
                node.change_part_of_sent(PartOfSpeech.PREDICATE)

            elif node.type is "INFI":
                node.change_part_of_sent(PartOfSpeech.SUB_PREDICATE)

            if [node, i] not in self.means_action:
                self.means_action.append([node, i])

    def _collect_nominal_predicate(self, node, i):
        if (node!=self.subject_node and not self.predicate_node
                and not self.nominal_predicate_node and not node.parent)\
                and (self.is_indept or (self.is_hyphen and self.subject_node)) :

            if ((node.type in ["NOUN","NPRO"] and "nomn" in node.features.get('case'))
                    or node.type in ["ADJF_SHORT", "PARTICIPLE_SHORT", "PARTICIPLE", "ADJF"]):#,"ADVB"
                    self.nominal_predicate_node = node
                    node.change_part_of_sent(PartOfSpeech.NOMINAL_PREDICATE)

                    if [node, i] not in self.means_action:
                        self.means_action.append([node, i])

                    if [node, i] not in self.nominal_predicate_nodes:
                        self.nominal_predicate_nodes.append([node, i])

    def _collect_subject_nodes(self, node, i):

        if (node.type in ['NOUN', 'NPRO']
                and "nomn" in node.features.get('case')
                and node.parent is None):

            if not ([node, i] in self.subject_nodes):
                self.subject_nodes.append([node, i])

            if self.subject_node is None:
                node.change_part_of_sent(PartOfSpeech.SUBJECT)
                self.subject_node = node

    #частица
    def _process_particle(self, node, i):
        """Обработка частиц"""
        if node.type in ["PRCL", "PART"] and i + 1 < len(self.nodes) and node.parent is None:
            self.nodes[i + 1].add_connection(node, "participle")
    """------------------------------------------------"""


    """==========Основные методы построения связей========="""
    def _process_node(self, node, i):
        """Обработка отдельного узла"""
        self._process_infinitive(node, i)
        self._process_subject(node, i)
        self._process_participle(node, i)
        #self._process_definition(node, i)
        #self._process_definition_N_A(node, i)
        self._process_nominal_predicate(node, i)
        self._process_circumstance(node, i)
        self._process_verb(node, i)
        #self._process_particle(node, i)
        self._process_preposition(node, i)
        self._process_genitive(node, i)
        self._process_adverbial_participle(node, i)

    #подлежащее <- существительное местоимение
    def _process_subject(self, node, i):
        """Обработка подлежащего"""

        if (node.type in ['NOUN', 'NPRO']
                and "nomn" in node.features.get('case')
                and node.parent is None):

            numbers = []
            genders = []
            for var in node.features.get("variants"):
                if "nomn" in var:
                    numbers += [var[1]]
                    genders += [var[2]]

            node.change_part_of_sent(PartOfSpeech.SUBJECT)

            self.connect_to_predicate(i, node, 'subject',numbers,genders)

            if not ([node, i] in self.subject_nodes):
                self.subject_nodes.append([node, i])

            if self.subject_node is None:
                self.subject_node = node

    #определение <- прилагательное
    def _process_definition(self, node, i):
        """Обработка определений"""
        if (node.type == 'ADJF' and node.features.get('case') != []
                and node is not self.nominal_predicate_node and node.parent is None):
            node.change_part_of_sent(PartOfSpeech.DEFINITION)
            if not node.connections:
                closest_noun = next((n for n in self.nodes[i + 1:] if n.type in ['NOUN', 'NPRO'] and
                                     self.connect_adjf_to_n(node,n)), None)
                if closest_noun:
                    closest_noun.add_connection(node, 'attribute')
                elif self.flag_finish_mode:
                    self.connect_to_predicate(i, node, 'sub_predicate')

            if self.definition_node is None:
                self.definition_node = node

    #определение <- местоимение числительное
    def _process_definition_N_A(self, node, i):
        """Обработка определений"""
        if (node.type == 'NPRO_ADJF' or node.type == 'NOUN_ADJF') and node.parent is None:
            node.change_part_of_sent(PartOfSpeech.DEFINITION)
            if not node.connections:
                closest_noun = next((n for n in self.nodes[i + 1:] if n.type in ['NOUN', 'NPRO'] and
                                     (self.connect_adjf_to_n(node,n) or 1)), None)
                if closest_noun:
                    closest_noun.add_connection(node, 'attribute')
                #!!!!elif self.flag_finish_mode:
                #!!!!    self.connect_to_predicate(i, node, 'sub_predicate')

            if self.definition_node == None:
                self.definition_node = node

    #номинальное сказуемое <- сущ мест прич прил кр.прил кр.прич
    def _process_nominal_predicate(self, node, i):

        if (node!=self.subject_node and not self.predicate_node
                and not node.parent and not self.nominal_predicate_node)\
                and (self.is_indept or (self.is_hyphen and self.subject_node)) :


            if ((node.type in ["NOUN","NPRO"] and "nomn" in node.features.get('case'))
                    or node.type in ["ADJF_SHORT", "PARTICIPLE_SHORT", "PARTICIPLE", "ADJF", "ADVB"]):#
                    self.nominal_predicate_node = node
                    node.change_part_of_sent(PartOfSpeech.NOMINAL_PREDICATE)

                    if [node, i] not in self.means_action:
                        self.means_action.append([node, i])

                    if [node, i] not in self.nominal_predicate_nodes:
                        self.nominal_predicate_nodes.append([node, i])


        if self.nominal_predicate_node is node:
            if self.subject_node:
                node.change_part_of_sent(PartOfSpeech.NOMINAL_PREDICATE)
                self.subject_node.add_connection(self.nominal_predicate_node, "nominal_pred")




    #обстоятельство <- наречие кр.прил кр.прич
    def _process_circumstance(self, node, i):
        """Обработка обстоятельств"""
        if ((node.type in ['ADVB', "ADJF_SHORT","PARTICIPLE_SHORT"]
                or node.type == 'ADJF' and not node.features.get('case'))
                and node.parent is None and node is not self.nominal_predicate_node):

            if not node.part_of_sentence:
                node.change_part_of_sent(PartOfSpeech.CIRCUMSTANCE)

            if self.connect_to_predicate(i, node, 'adverbial'):
                node.change_part_of_sent(PartOfSpeech.CIRCUMSTANCE)

            if self.circumstance_node is None:
                self.circumstance_node = node

    #однородное сказуемое <- глагол
    def _process_verb(self, node, i):
        """Обработка глаголов и однородных сказуемых"""
        if node.type == 'VERB' and node != self.predicate_node:

            node.change_part_of_sent(PartOfSpeech.PREDICATE)
            self.connect_to_predicate(i, node,'homogeneous')

            if [node,i] not in self.predicate_nodes:
                self.predicate_nodes.append([node, i])

            if [node,i] not in self.means_action:
                self.means_action.append([node, i])

    #субпредикат <- инфинитив
    def _process_infinitive(self, node, i):
        """Обработка инфинитивов"""
        if node.type == 'INFI':

            node.change_part_of_sent(PartOfSpeech.SUB_PREDICATE)
            self.connect_to_predicate(i, node, 'sub_predicate')

            if [node,i] not in self.means_action:
                self.means_action.append([node, i])

    #определение\судпредикат <- причастие
    def _process_participle(self, node, i):
        """Обработка причастий"""
        if (node.type in ["PARTICIPLE"]
                and node is not self.nominal_predicate_node
                and node.parent is None):

            node.change_part_of_sent(PartOfSpeech.DEFINITION)
            if [node,i] not in self.means_action:
                self.means_action.append([node, i])

            closest_noun = None
            if self.predicate_nodes != [] and not self.flag_finish_mode:
                #обособление отсутствует
                closest_noun = next((n for n in self.nodes[i + 1:]
                                     if n.type in ['NOUN', 'NPRO']
                                     and self.connect_adjf_to_n(node, n)), None)

            if closest_noun is None:
                    closest_noun = next((n for n in reversed(self.nodes[:i])
                                         if n.type in ['NOUN', 'NPRO']
                                         and self.connect_adjf_to_n(node, n)),None)
                                    # next((n for n in reversed(self.nodes[i + 1:])
                                    #       if n.type in ['NOUN', 'NPRO']
                                    #       and self.connect_adjf_to_n(node, n)),None))
            if self.flag_finish_mode and closest_noun is None:
                closest_noun = next((n for n in self.nodes[i + 1:]
                                           if n.type in ['NOUN', 'NPRO']
                                           and self.connect_adjf_to_n(node, n)),None)


            noun = None
            if not node.connections and not self.flag_finish_mode:
                if "trans" in node.features.get("trans"):
                    if "passiv" in node.features.get("pledge"):
                        noun = next((n for n in self.nodes[i + 1:]
                                     if n.type in ['NOUN', 'NPRO']
                                     and (n is not closest_noun)
                                     and not (n.parent) and "ablt" in n.features.get("case")), None)
                        if noun:
                            noun.change_part_of_sent(PartOfSpeech.OBJECT)
                            node.add_connection(noun, 'active_object')

                    elif "activ" in node.features.get("pledge"):
                        noun = next((n for n in self.nodes[i + 1:]
                                     if n.type in ['NOUN', 'NPRO']
                                     and (n is not closest_noun)
                                     and not (n.parent) and "accs" in n.features.get("case")), None)

                        if noun:
                            noun.change_part_of_sent(PartOfSpeech.OBJECT)
                            node.add_connection(noun, 'passive_object')

            if closest_noun:  # and self.flag_finish_mode:#!!!!!
                closest_noun.add_connection(node, 'attribute')
            elif self.flag_finish_mode:
                self.connect_to_predicate(i, node, 'sub_predicate')


            if self.definition_node is None:
                self.definition_node = node

    #обстоятельство\дополнение <- существительное\местоимение с предлогом
    def _process_preposition(self, node, i):
        """Обработка предложных конструкций"""

        if node.type == 'PREP' and node.parent is None:
            if  all(not(connect[0].type in ['NOUN', 'NPRO']) for connect in node.connections):
                next_noun = next((
                    n for n in self.nodes[i + 1:]
                    if n.type in ['NOUN', 'NPRO']
                        and n.parent is None
                        and self.connect_pp_to_n(node, n)
                            ), None)

                # Связываем предлог с дополнением
                if (next_noun is not None
                        and next_noun.parent is None):
                    part_of_speech = self._choose_role_prep_noum(node,next_noun)
                    node.change_part_of_sent(part_of_speech)
                    next_noun.change_part_of_sent(part_of_speech)
                    node.add_connection(next_noun, 'object')

            # Связываем предлог с глаголом (сказуемым)
            if node.parent is None:
                self.connect_to_predicate(i, node, 'prepositional_object')

    #обстоятельство <- существительное\местоимение
    def _process_genitive(self, node, i):
        """Обработка родительного падежа"""
        if (node.type in ['NOUN', 'NPRO']
                and self.check_common_word(['gent', 'accs', "ablt"], node.features.get('case'))
                and not node.parent and node != self.nominal_predicate_node):
                                        #  and node != subject_node):#
            for n in reversed(self.nodes[:i]):
                if n.type in ['NOUN', 'NPRO', "VERB", "INFI"] and n.parent is not node:
                    #,"PARTICIPLE"
                    node.change_part_of_sent(PartOfSpeech.OBJECT)
                    n.add_connection(node, 'genitive')
                    if node == self.subject_node:
                        self.subject_node = None
                    break

    #обстоятельство <- деепричастие
    def _process_adverbial_participle(self, node, i):
        """Обработка деепричастий"""
        if node.type == "ADVB_PARTICIPLE":

            if "trans" in node.features.get("trans") and not node.connections:
                noun = next((n for n in self.nodes[i + 1:]
                             if n.type in ['NOUN', 'NPRO'] and not (n.parent)), None)
                if noun:
                    noun.change_part_of_sent(PartOfSpeech.OBJECT)
                    if node is self.subject_node:
                        self.subject_node = None
                    node.add_connection(noun, 'genitive')

            node.change_part_of_sent(PartOfSpeech.CIRCUMSTANCE)

            if [node, i] not in self.means_action:
                self.means_action.append([node, i])

            if self.circumstance_node:
                self.circumstance_node.add_connection(node, 'homogeneous')
            else:
                self.circumstance_node = node
                self.connect_to_predicate(i, node, 'circumstance')


    #определение главных корней
    def _determine_root_node(self):
        """Определение корневого узла"""
        if self.main:
            main_nodes = [data[0] for data in self.main]
            # if self.predicate_node and not self.predicate_node in main_nodes :
            #     main_nodes += [self.predicate_node]
            main_nodes += [pred[0]
                           for pred in self.predicate_nodes + self.nominal_predicate_nodes
                           if ((not pred[0] in main_nodes) and (pred[0].parent is None))]
            return main_nodes
        if self.predicate_node:
            return [self.predicate_node]
        if self.subject_node:
            #self.subject_node.change_part_of_sent(PartOfSpeech.SUBJECT)
            return [self.subject_node]
        if self.nominal_predicate_node:
            return [self.nominal_predicate_node]
        if self.circumstance_node:
            return [self.circumstance_node]
        if self.definition_node:
            return [self.definition_node]
        if len(self.nodes)>0:
            return [self.nodes[0]]
        return [None]


    @staticmethod
    def print_tree(root_node):
        """Визуализация синтаксического дерева."""

        text = []
        def _traverse(node,level=0,relation=''):
            text.append(' ' * level + f'└─ {relation} {node}')
            #print(' ' * level + f'└─ {relation} {node}')

            for child, rel in node.connections:
                _traverse(child, level + 1, rel)

        if root_node:
            _traverse(root_node)

        return "\n".join(text)
    """------------------------------------------------"""



    """=============Вспомогательные методы============="""

    def is_adjective_dependent_on_verb(self, verb, adj):
        # Списки лемм глаголов-связок и глаголов оценки
        linking_verbs = {"быть", "стать", "казаться", "являться", "считаться", "оставаться"}
        opinion_verbs = {"считать", "называть", "полагать", "признавать"}


        # Правило 1: Составное именное сказуемое
        if verb.lemma.lower() in linking_verbs:
            # Проверяем падеж прилагательного или краткую форму
            if (("ADJF_SHORT" in adj.type)
                    or (self.check_common_word(adj.features.get('case') ,["nomn", "ablt"]))):
                return True

        # Правило 2: Предикативное употребление (краткая форма или безличное -о)
        if ("ADJF" in adj.type
                and self.check_common_word(adj.features.get('case') ,["accs"])
                and adj.features.get('word').endswith("о")):
            return True

        # Правило 3: Глаголы оценки + творительный падеж
        if verb.lemma.lower() in opinion_verbs \
                and self.check_common_word(adj.features.get('case') ,["ablt"]):
            return True

        # Во всех остальных случаях — не зависит
        return False


    def connect_adjf_to_n(self,node,n):

        connect_case = self._connect_by_case(n,node)
        connect_number = self._connect_by_num(n,node)
        connect_gender = self._connect_by_gender(n,node)
        correct_position = True


        if n and node.type is "PARTICIPLE":
            if n.parent:
                num_parent = n.parent.features.get('num_in_text')
                num_noun = n.features.get('num_in_text')
                num_adjf = node.features.get('num_in_text')
                if num_adjf < num_parent < num_noun or num_adjf > num_parent > num_noun:
                    correct_position = False


        return (connect_case and connect_number and connect_gender and correct_position)

        # numbers = []
        # genders = []
        # for var in n.features.get("variants"):
        #     if self.check_common_word(node.features.get("case") ,var):
        #         numbers += [var[1]]
        #         genders += [var[2]]


        # return( self.check_common_word(node.features.get("case") ,n.features.get("case"))
        #         and (self.check_common_word(node.features.get("number"), numbers) or
        #         numbers == [] or
        #         node.features.get("number") == []) and
        #         (self.check_common_word(node.features.get("gender"), genders) or
        #         genders == [] or
        #         node.features.get("gender") == []))

        # print (n.lemma,[node.features.get("case")[0],
        #     node.features.get("number")[0],
        #     node.features.get("gender")[0]],
        #     n.features.get("variants"))
        #return ([node.features.get("case")[0],
        #     node.features.get("number")[0],
        #     node.features.get("gender")[0]] in
        #     n.features.get("variants"))

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

    def connect_pp_to_n(self, node_pp, node_n):
        return self.check_common_word(node_n.features.get('case'), node_pp.features.get("case"))

    @staticmethod
    def check_common_word(arr1, arr2):
        return len(set(arr1) & set(arr2)) > 0

    @staticmethod
    def collect_info_by_sent(separator, roots, sub_conj_sent):
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

    @staticmethod
    def collect_all_nodes(root_node):
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

    @staticmethod
    def is_link_pred_subj(root_node):
        for child, link_type in root_node.connections:
            if link_type == "subject":
                return True
        return False

    @staticmethod
    def is_link_homogeneous(root_node):
        def _traverse(node):
            link_types = []
            for child, link_type in node.connections:
                if link_type == "homogeneous" or link_type in link_types:
                    return True
                link_types += [link_type]

            for child, _ in node.connections:
                _traverse(child)

        if root_node:
            if _traverse(root_node):
                return True
        return False

    @staticmethod
    def is_link_common(root_node):
        def _traverse(node):
            for child, link_type in node.connections:
                if not(link_type in ["subject","homogeneous"]):
                    return True

            for child, _ in node.connections:
                _traverse(child)

        if root_node:
            if _traverse(root_node):
                return True
        return False

    @staticmethod
    def is_independent_clause(clause_nodes, root_node, correct_sep):
        has_subject = any(node.part_of_sentence == PartOfSpeech.SUBJECT
                          for node in clause_nodes)
        has_predicate = any(node.part_of_sentence in [PartOfSpeech.PREDICATE, PartOfSpeech.NOMINAL_PREDICATE]
                          for node in clause_nodes)

        root_is_predicate = (root_node.part_of_sentence in [PartOfSpeech.PREDICATE] )
        root_is_subject = (root_node.part_of_sentence in [PartOfSpeech.SUBJECT] )
        root_is_nominal_predicate = (root_node.part_of_sentence in [PartOfSpeech.NOMINAL_PREDICATE])

        part_sent_has_correct_sep =correct_sep

        return (((has_subject and has_predicate) or part_sent_has_correct_sep)
                and (root_is_predicate or root_is_subject or root_is_nominal_predicate))
    """------------------------------------------------"""





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

    num_in_text = 1
    for clause in clauses:
        morph_res_i_clause = []
        for token in clause.get("tokens"):
            word = token.get("word")
            descr = token.get("descriptors")
            morph_res_i_clause += [morph_analyzer.analyze_word(word, num_in_text, descr)]
            num_in_text+=1
        morph_res_for_clauses += [morph_res_i_clause]

    analyzer = SintaxisAnalyzer()
    root, nodes, info, tree = analyzer.analyze(clauses, morph_res_for_clauses)

    print("\nСинтаксический анализ:")
    print(analyzer.print_tree(root))