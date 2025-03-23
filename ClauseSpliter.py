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
            if "PUN" in descriptors or "SUB_CONJ" in descriptors or "COORD_CONJ" in descriptors:
                clause_separator = (clause_separator + " " + graphem).strip()
                clause_descriptors = (clause_descriptors + " " + descriptors).strip()
                if clause != []:
                    try:
                        if not("PUN" in graphems[i+1][1] or "SUB_CONJ" in graphems[i+2][1] or "COORD_CONJ" in graphems[i+2][1]):
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
                else:

                    clause_separator = ""
                    clause_descriptors = ""

            if not("DEL" in descriptors or "PUN" in descriptors): #URL EA DC RLE
                if "SUB_CONJ" in descriptors:
                    clause_sub_conjunction += [graphem.lower()]
                if "COORD_CONJ" in descriptors:
                    clause_coord_conjunction += [graphem.lower()]
                clause += [graphem]

        return clauses


# Пример использования
if __name__ == "__main__":

    from GraphematicModule import GraphematicAnalyzer

    text = """
    Когда солнце взошло, мы отправились в путь, и дорога оказалась удивительно красивой и светлой.
    Я знал, что он придёт, но всё равно волновался.
    Она улыбнулась мне, потому что была рада встрече, и я почувствовал тепло её взгляда.
    """
    graphems = GraphematicAnalyzer().analyze(text)

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
