import re
from GraphematicModule import GraphematicAnalyzer

class ClauseSplitter:
    def __init__(self):
       
        # Список подчинительных союзов
        self.conjunctions_subordinating = [
            "что",
            "чтобы",
            "как",
            "когда",
            "если",
            "хотя",
            "потому что",
            "так как",
            "несмотря на то что",
            "в то время как",
            "пока",
            "лишь",
            "будто",
            "чем",
            "дабы",
            "словно",
            "едва",
            "как будто",
            "ибо",
            "оттого что",
            "для того чтобы",
            "тогда как",
            "затем что",
            "по мере того как",
            "с тех пор как"
        ]

        # Список сочинительных союзов
        self.conjunctions_coordinating= [
            "и",
            "а",
            "но",
            "да",
            "или",
            "либо",
            "тоже",
            "также",
            "не только..., но и",
            "как...так и",
            "то ли...то ли",
            "или...или",
            "да и",
            "однако",
            "зато",
            "притом",
            "причем"
        ]

        self.graphematic_analyzer = GraphematicAnalyzer()

    @staticmethod
    def split_into_tokens(graphems):#(self, sentence ):
        #graphems = self.graphematic_analyzer.analyze(sentence)
        tokens = [graphem[0] for graphem in graphems if not("DEL" in graphem[1])]
        return tokens

    @staticmethod
    def split_into_words(graphems):#(self, sentence):
        #graphems = self.graphematic_analyzer.analyze(sentence)

        tokens = []
        for i, token in enumerate(graphems):
            graphem = token[0]
            descriptors = token[1]
            if not ("DEL" in descriptors or "PUN" in descriptors):  # URL EA DC RLE
                tokens += [graphem]

        return tokens

    @staticmethod
    def split_into_clauses(graphems):#(self, sentence):
        #graphems = self.graphematic_analyzer.analyze(sentence)

        clauses = []
        clause = []
        clause_sub_conjunction = []
        clause_coord_conjunction = []
        clause_separator = ""
        clause_descriptors = ""

        for i, token in enumerate(graphems):
            graphem = token[0]
            descriptors = token[1]
            if "PUN" in descriptors:
                clause_separator = (clause_separator + " " + graphem).strip()
                clause_descriptors = (clause_descriptors + " " + descriptors).strip()
                if clause != []:
                    try:
                        if not("PUN" in graphems[i+1][1]):
                            clauses.append({
                                'tokens': clause,
                                'separator': clause_separator,
                                'descriptor': clause_descriptors,
                                'sub_conjunctions': clause_sub_conjunction,
                                'coord_conjunctions': clause_coord_conjunction,
                            })
                            clause = []
                            clause_separator = ""
                            clause_descriptors = ""
                            clause_sub_conjunction = []
                            clause_coord_conjunction = []

                    except:
                        clauses.append({
                            'tokens': clause,
                            'separator': clause_separator,
                            'descriptor': clause_descriptors,
                            'sub_conjunctions': clause_sub_conjunction,
                            'coord_conjunctions': clause_coord_conjunction,
                        })
                        clause = []
                        clause_separator = ""
                        clause_descriptors = ""
                        clause_sub_conjunction = []
                        clause_coord_conjunction = []

            elif not("DEL" in descriptors): #URL EA DC RLE
                if "SUB_CONJ" in descriptors:
                    clause_sub_conjunction += [graphem.lower()]
                if "COORD_CONJ" in descriptors:
                    clause_coord_conjunction += [graphem.lower()]
                clause += [graphem]

        return clauses


# Пример использования
if __name__ == "__main__":


    text = """
    Когда солнце взошло, мы отправились в путь, и дорога оказалась удивительно красивой.
    Я знал, что он придёт, но всё равно волновался.
    Она улыбнулась мне, потому что была рада встрече, и я почувствовал тепло её взгляда.
    """
    graphems = [('↵␣␣␣␣', 'DEL EOLN BEG'), ('Когда', 'SUB_CONJ'), ('␣', 'DEL SPC'), ('солнце', 'RLE aa'), \
                ('␣', 'DEL SPC'), ('взошло', 'RLE aa'), (',', 'PUN'), ('␣', 'DEL SPC'), ('мы', 'RLE aa'), \
                ('␣', 'DEL SPC'), ('отправились', 'RLE aa'), ('␣', 'DEL SPC'), ('в', 'RLE aa'), ('␣', 'DEL SPC'), \
                ('путь', 'RLE aa'), (',', 'PUN'), ('␣', 'DEL SPC'), ('и', 'COORD_CONJ'), ('␣', 'DEL SPC'), \
                ('дорога', 'RLE aa'), ('␣', 'DEL SPC'), ('оказалась', 'RLE aa'), ('␣', 'DEL SPC'), \
                ('удивительно', 'RLE aa'), ('␣', 'DEL SPC'), ('красивой', 'RLE aa'), ('.', 'PUN SENT_END'), \
                ('␣↵␣␣␣␣', 'DEL EOLN'), ('Я', 'RLE AA'), ('␣', 'DEL SPC'), ('знал', 'RLE aa'), (',', 'PUN'), \
                ('␣', 'DEL SPC'), ('что', 'SUB_CONJ'), ('␣', 'DEL SPC'), ('он', 'RLE aa'), ('␣', 'DEL SPC'), \
                ('придёт', 'RLE aa'), (',', 'PUN'), ('␣', 'DEL SPC'), ('но', 'COORD_CONJ'), ('␣', 'DEL SPC'), \
                ('всё', 'RLE aa'), ('␣', 'DEL SPC'), ('равно', 'RLE aa'), ('␣', 'DEL SPC'), ('волновался', 'RLE aa'), \
                ('.', 'PUN SENT_END'), ('␣↵␣␣␣␣', 'DEL EOLN'), ('Она', 'RLE Aa NAM?'), ('␣', 'DEL SPC'), \
                ('улыбнулась', 'RLE aa'), ('␣', 'DEL SPC'), ('мне', 'RLE aa'), (',', 'PUN'), ('␣', 'DEL SPC'), \
                ('потому␣что', 'SUB_CONJ'), ('␣', 'DEL SPC'), ('была', 'RLE aa'), ('␣', 'DEL SPC'), ('рада', 'RLE aa'), \
                ('␣', 'DEL SPC'), ('встрече', 'RLE aa'), (',', 'PUN'), ('␣', 'DEL SPC'), ('и', 'COORD_CONJ'), \
                ('␣', 'DEL SPC'), ('я', 'RLE aa'), ('␣', 'DEL SPC'), ('почувствовал', 'RLE aa'), ('␣', 'DEL SPC'),\
                ('тепло', 'RLE aa'), ('␣', 'DEL SPC'), ('её', 'RLE aa'), ('␣', 'DEL SPC'), ('взгляда', 'RLE aa'), \
                ('.', 'PUN SENT_END'), ('↵␣␣␣␣', 'DEL EOLN')]

    clause_spliter = ClauseSplitter()

    print("\nРазделение на кляузы:")
    clauses_res = clause_spliter.split_into_clauses(graphems)
    for clause in clauses_res:
        print(clause)

    print("\nРазделение на токены:")
    tokens_res = clause_spliter.split_into_tokens(graphems)
    for token in tokens_res:
        print(token)

    print("\nРазделение на слова:")
    words_res = clause_spliter.split_into_words(graphems)
    for word in words_res:
        print(word)
