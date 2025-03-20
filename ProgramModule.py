from GraphematicModule import GraphematicAnalyzer
from MorphModule import MorphAnalyzer
from ClauseSpliter import ClauseSplitter
from SintaxisModule import SintaxisAnalyzer
from VisualizeTree import visualize_tree
from TextSyntaxisLinks import visualize_syntax_links


class ProgramModule:
    def __init__(self,main_text):
        self.TEXT = main_text
        
        self.graphematic_analyzer = GraphematicAnalyzer()
        self.morph_analyzer = MorphAnalyzer()
        self.clause_spliter = ClauseSplitter()
        self.sintaxis_analyzer = SintaxisAnalyzer()

        self.graphems_res = self.graphematic_analyzer.analyze(self.TEXT)

        self.clauses_res = self.clause_spliter.split_into_clauses(self.graphems_res)
        self.words_res = self.clause_spliter.split_into_words(self.graphems_res)
        self.tokens_res = self.clause_spliter.split_into_tokens(self.graphems_res)

        self.morph_res_for_clauses = []
        self.morph_res = []

        for clause in self.clauses_res:
            morph_res_i_clause = []
            for word in clause.get("tokens"):
                morph_res_i_clause += [self.morph_analyzer.analyze_word(word)]
                self.morph_res += [self.morph_analyzer.analyze_word(word)]
            self.morph_res_for_clauses += [morph_res_i_clause]

        self.sintaxis_root, self.sintaxis_nodes, self.sintaxis_text_info, self.sintaxis_tree_in_txt = \
            self.sintaxis_analyzer.analyze(self.clauses_res, self.morph_res_for_clauses)


        # self.graphems_res = None
        # self.clauses_res = None
        # self.words_res = None
        # self.tokens_res = None
        # self.morph_res = None
        # self.morph_res_for_clauses = None
        # self.text_info = None
        
    def print_graphem_res(self):
        # self.graphems_res = self.graphematic_analyzer.analyze(self.TEXT)

        print("\nГрафематический анализ:")
        for graphem in self.graphems_res:
            print(f"{graphem[0]}\t{graphem[1]}")

        #return self.graphems_res

    def print_spliter_res(self):
        # self.clauses_res = self.clause_spliter.split_into_clauses(self.graphems_res)
        # self.words_res = self.clause_spliter.split_into_words(self.graphems_res)
        # self.tokens_res = self.clause_spliter.split_into_tokens(self.graphems_res)

        print("\nРазделение на кляузы:")
        for clause in self.clauses_res:
            print(clause)
        print("\nРазделение на слова:")
        for word in self.words_res:
            print(word)
        print("\nРазделение на токены:")
        for token in self.tokens_res:
            print(token)

        #return self.clauses_res, self.words_res, self.tokens_res

    def print_morph_res(self):
        # self.morph_res_for_clauses = []
        # self.morph_res = []
        #
        # for clause in self.clauses_res:
        #     morph_res_i_clause = []
        #     for word in clause.get("tokens"):
        #         morph_res_i_clause += [self.morph_analyzer.analyze_word(word)]
        #         self.morph_res += [self.morph_analyzer.analyze_word(word)]
        #     self.morph_res_for_clauses += [morph_res_i_clause]

        print("\nМорфологический анализ:")
        for morph in self.morph_res:
            print(morph)

        #return self.morph_res_for_clauses, self.morph_res

    def print_sintaxis_res(self):
        # self.sintaxis_root, self.sintaxis_nodes, self.sintaxis_text_info, self.sintaxis_tree_in_txt =\
        #     self.sintaxis_analyzer.analyze(self.clauses_res,self.morph_res_for_clauses)

        print("\nСинтаксический анализ:")
        print(self.sintaxis_tree_in_txt)
        self.print_text_info()
        visualize_tree(self.sintaxis_root)
        visualize_syntax_links(self.sintaxis_nodes, self.tokens_res)

        #return self.sintaxis_root, self.sintaxis_nodes,self.sintaxis_text_info,self.sintaxis_tree_in_txt


    def print_text_info(self):

        info_count_sent, info_count_part_sent, info_two_part, info_purpose_statement, info_intonation, \
            info_complexity, info_common, info_homogeneous = self.sintaxis_text_info

        text_info = f"Количество предложений: {info_count_sent}\n"

        for i in range(info_count_sent):

            two_part = ""
            if info_two_part[i]:
                two_part = "двусоставное"
            else:
                two_part = "односоставное"

            intonation = ""
            if info_intonation[i]:
                intonation = "восклицательное"
            else:
                intonation = "невосклицательное"

            complexity = ""
            if info_complexity[i] == 0:
                complexity = "СПП"
            elif info_complexity[i] == 1:
                complexity = "ССП"
            else:
                complexity = "простое"

            purpose_statement = ""
            if info_purpose_statement[i] == 0:
                purpose_statement = "повествовательное"
            elif info_purpose_statement[i] == 1:
                purpose_statement = "побудительное"
            else:
                purpose_statement = "вопросительное"

            text_info +=f"""Предложение{i + 1}:
            \tПо цели высказывания: {purpose_statement}
            \tПо интонации: {intonation}
            \tПо сложности: {complexity}
            \tКоличество частей: {info_count_part_sent[i]}
            \tПо наличию главных членов: {two_part}
            \tПо наличию второстепенных членов: {info_homogeneous[i]}
            \tПо наличию однородных членов: {info_common[i]}\n"""


        print(f"\nИнформация о тексте:\n{text_info}")



# Пример использования
if __name__ == "__main__":
    text = """Две старые кошки, мурлыча и грациозно двигаясь, поймали трёх мелких мышей в саду, но потом убежали в тёмный лес, где всегда тихо."""
    module = ProgramModule(text)
    module.print_graphem_res()
    module.print_spliter_res()
    module.print_morph_res()
    module.print_sintaxis_res()






