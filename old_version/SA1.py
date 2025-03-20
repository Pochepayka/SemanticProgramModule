from pylem import MorphanHolder, MorphLanguage
import re
from typing import List, Dict, Set


class MorphAnalyzer:
    def __init__(self):
        self.morphan = MorphanHolder(MorphLanguage.Russian)
        self.pos_map = {
            'N': 'NOUN', 'V': 'VERB', 'A': 'ADJ',
            'NUM': 'NUM', 'ADV': 'ADV', 'PREP': 'PREP',
            'CONJ': 'CONJ', 'PRCL': 'PART', 'INTJ': 'INTJ'
        }
        self.feature_map = {
            'nom': 'nomn', 'gen': 'gent', 'dat': 'datv',
            'acc': 'accs', 'ins': 'ablt', 'prp': 'loct',
            'sg': 'sing', 'pl': 'plur', 'masc': 'masc',
            'fem': 'femn', 'neut': 'neut', 'anim': 'anim',
            'inanim': 'inan', 'pres': 'pres', 'past': 'past',
            'futr': 'futr'
        }

    def parse_morph_features(self, raw_features: Set[str]) -> Dict:
        features = {'case': None, 'number': None,
                    'gender': None, 'animacy': None, 'tense': None}

        for f in raw_features:
            if f in {'nom', 'gen', 'dat', 'acc', 'ins', 'prp'}:
                features['case'] = self.feature_map.get(f)
            elif f in {'sg', 'pl'}:
                features['number'] = self.feature_map.get(f)
            elif f in {'masc', 'fem', 'neut'}:
                features['gender'] = self.feature_map.get(f)
            elif f in {'anim', 'inanim'}:
                features['animacy'] = self.feature_map.get(f)
            elif f in {'pres', 'past', 'futr'}:
                features['tense'] = self.feature_map.get(f)

        return features

    def analyze(self, word: str) -> List[Dict]:
        analyses = []
        for lemma_info in self.morphan.lemmatize(word):
            pos = self.pos_map.get(lemma_info.part_of_speech,
                                   lemma_info.part_of_speech)
            features = self.parse_morph_features(lemma_info.morph_features)

            analyses.append({
                'word': word,
                'lemma': lemma_info.lemma,
                'pos': pos,
                'features': features,
                'morph_features': lemma_info.morph_features

            })
        return analyses


class SyntaxNode:
    def __init__(self, word: str, lemma: str, pos: str, features: Dict):
        self.word = word
        self.lemma = lemma
        self.pos = pos
        self.features = features
        self.children = []
        self.parent = None
        self.relations = {}

    def add_child(self, node, relation_type: str):
        node.parent = self
        self.children.append((node, relation_type))
        self.relations[relation_type] = self.relations.get(relation_type, []) + [node]

    def __repr__(self):
        return f"{self.pos}('{self.lemma}', {self.features})"


class SyntaxParser:
    def __init__(self):
        self.morph = MorphAnalyzer()
        self.rules = {
            'nomn': self.process_nominative,
            #'gent': self.process_genitive,
            #'adj_noun': self.process_adj_noun,
            #'prep_phrase': self.process_prep_phrase
        }

    def create_nodes(self, sentence: str) -> List[SyntaxNode]:
        tokens = re.findall(r'\b[\w-]+\b', sentence.lower())
        return [self._create_node(token) for token in tokens]

    def _create_node(self, token: str) -> SyntaxNode:
        analysis = self.morph.analyze(token)[0]  # Берем первый анализ
        return SyntaxNode(
            word=token,
            lemma=analysis['lemma'],
            pos=analysis['pos'],
            features=analysis['features']
        )

    def process_nominative(self, nodes: List[SyntaxNode]) -> SyntaxNode:
        for i, node in enumerate(nodes):
            if node.features.get('case') == 'nomn':
                return self._build_nominative_phrase(nodes, i)
        return nodes[0]

    def _build_nominative_phrase(self, nodes: List[SyntaxNode], head_idx: int):
        head = nodes[head_idx]
        # Собираем согласованные определения слева
        for left in reversed(nodes[:head_idx]):
            if self._check_agreement(left, head):
                head.add_child(left, 'attribute')
        return head

    def _check_agreement(self, node1: SyntaxNode, node2: SyntaxNode) -> bool:
        keys = ['case', 'number', 'gender']
        return all(node1.features.get(k) == node2.features.get(k)
                   for k in keys if node1.features.get(k))

    def build_tree(self, sentence: str) -> SyntaxNode:
        nodes = self.create_nodes(sentence)
        print(nodes)
        # Применение правил в приоритетном порядке
        for rule in ['nomn', 'gent', 'adj_noun', 'prep_phrase']:
            if handler := self.rules.get(rule):
                handler(nodes)

        # Поиск сказуемого
        predicate = next((n for n in nodes if n.pos == 'VERB'), nodes[0])

        # Связывание компонентов
        for node in nodes:
            if node != predicate:
                if self._should_attach(node, predicate):
                    predicate.add_child(node, 'object' if
                    node.features.get('case') == 'accs'
                    else 'modifier')

        return predicate

    def _should_attach(self, node: SyntaxNode, head: SyntaxNode) -> bool:
        if node.parent:  # Уже привязан к другому узлу
            return False
        return True  # Упрощенная логика для примера


# Пример использования
parser = SyntaxParser()
sentence = "Две старые кошки поймали трёх мелких мышей в саду"
root = parser.build_tree(sentence)


def print_tree(node: SyntaxNode, level: int = 0):
    indent = "  " * level
    print(f"{indent}{node}")
    for child, rel in node.children:
        print(f"{indent}-> {rel}:")
        print_tree(child, level + 1)


print("Синтаксическое дерево:")
print_tree(root)