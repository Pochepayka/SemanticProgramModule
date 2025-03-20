from MorphModuleOLD import FromJSON

class TreeNode:
    def __init__(self, value):
        self.value = value
        self.children = []

    def add_child(self, child):
        self.children.append(child)
    def __repr__(self):
        return f"{self.value} -> {self.children}"


def ParseSentence(tokens):
    root = TreeNode('S')

    # 1. Разбор подлежащего (NP) с зависимыми определениями
    np = parse_np(tokens)
    print (np)
    if np:
        root.add_child(np)

    # 2. Разбор сказуемого (VP) с обстоятельствами и дополнениями
    vp = parse_vp(tokens)
    if vp:
        root.add_child(vp)

        # Привязка предлогов к VP
        attach_pp_to_vp(vp, tokens)

    return root


def parse_np(tokens):

    np_node = TreeNode('NP')
    """Поиск именной группы с главным словом в именительном падеже"""
    for i, token in enumerate(tokens):
        if token['pos'] in ['N', 'P'] and 'nom' in token['morph']:

            subject = TreeNode(token["word"])

            #tokens.pop(i)

            # Прикрепление определений
            for j, token in enumerate(tokens):
                if token['pos'] in ['A']:
                    # while tokens and tokens[0]['pos'] == 'A':
                    # adj = tokens.pop(0)
                    # np_node.add_child(TreeNode(adj['word']))
                    subject.add_child(TreeNode(token['word']))
                    #tokens.pop(j)

            np_node.add_child(subject)






            #return TreeNode('NP').add_child(np_node)
    return np_node#TreeNode('NP').add_child(np_node)


def parse_vp(tokens):
    vp_node = TreeNode('VP')
    """Поиск глагольной группы с зависимыми обстоятельствами"""
    for i, token in enumerate(tokens):
        if token['pos'] == 'V':
            predicate = TreeNode(token['word'])
            #tokens.pop(i)

            # Прикрепление наречий напрямую к глаголу
            for j, token in enumerate(tokens):
                if token['pos'] in ['ADV', "INFINITIVE"]:
                    predicate.add_child(TreeNode(token['word']))
                    #tokens.pop(j)

            vp_node.add_child(predicate)

    return vp_node


def attach_pp_to_vp(vp_node, tokens):
    PREPOSITION_CASES = FromJSON("PREPOSITION_CASES_ru.json")
    #print(PREPOSITION_CASES)
    """Привязка предлогов с дополнениями к сказуемому"""
    for i, token in enumerate(tokens):
        if token['pos'] == 'PREP':
            prep = token
            pp_node = TreeNode(token['word'])
            #tokens.pop(i)

            for j in range(i,len(tokens)):
                if tokens[j]['pos'] == 'N' and tokens[j]['morph'].intersection(PREPOSITION_CASES[prep['word'].lower()]):  # Проверяем соответствие падежа
                    noun = TreeNode(tokens[j]["word"])
                    #tokens.pop(j)
                    pp_node.add_child(TreeNode(noun))
                    break

            vp_node.add_child(pp_node)


def CreateTokens(words, morph_data):
    tokens = []

    for i, word_pos in enumerate(words):
        word, pos = word_pos.split(' : ')  # Разделяем слово и часть речи
        morph_str = morph_data[i][0].split(' : ')[1]  # Извлекаем строку с морфологией
        morph = eval(morph_str)  # Преобразуем строку в множество

        tokens.append({'word': word, 'pos': pos, 'morph': morph})

    return tokens

