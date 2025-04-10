from GraphematicModule import GraphematicAnalyzer
from MorphModule import MorphAnalyzer
from ClauseSpliter import ClauseSplitter
from SintaxisModule import SintaxisAnalyzer
from VisualizeTree import VisualResult
from SemanticModule import SemanticAnalyzer

class ProgramModule:
    def __init__(self,main_text):
        self.TEXT = main_text
        
        self.graphematic_analyzer = GraphematicAnalyzer()
        self.morph_analyzer = MorphAnalyzer()
        self.clause_spliter = ClauseSplitter()
        self.sintaxis_analyzer = SintaxisAnalyzer()
        self.visual_result = VisualResult()
        self.semantic_analyzer = SemanticAnalyzer()




        # self.graphems_res = self.graphematic_analyzer.analyze(self.TEXT)
        #
        # self.clauses_res = self.clause_spliter.split_into_clauses(self.graphems_res)
        # self.words_res = self.clause_spliter.split_into_words(self.graphems_res)
        # self.tokens_res = self.clause_spliter.split_into_tokens(self.graphems_res)
        #
        # self.morph_res_for_clauses = []
        # self.morph_res = []
        # num_in_text = 1
        # for clause in self.clauses_res:
        #     morph_res_i_clause = []
        #     for token in clause.get("tokens"):
        #         word = token.get("word")
        #         descr = token.get("descriptors")
        #         morph_res_i_clause += [self.morph_analyzer.analyze_word(word, num_in_text, descr)]
        #         self.morph_res += [self.morph_analyzer.analyze_word(word,num_in_text)]
        #         num_in_text+=1
        #     self.morph_res_for_clauses += [morph_res_i_clause]
        #
        # self.sintaxis_root, self.sintaxis_nodes, self.sintaxis_text_info, self.sintaxis_tree_in_txt = \
        #     self.sintaxis_analyzer.analyze(self.clauses_res, self.morph_res_for_clauses)
        #
        #
        # # self.graphems_res = None
        # # self.clauses_res = None
        # # self.words_res = None
        # # self.tokens_res = None
        # # self.morph_res = None
        # # self.morph_res_for_clauses = None
        # # self.text_info = None

    def main(self,num_test):

        graphems_res = self.graphem_res()

        print("\nГрафематический анализ:")
        for graphem in graphems_res:
            print(f"{graphem[0]}\t{graphem[1]}")




        clauses_res, words_res, tokens_res = self.spliter_res(graphems_res)

        print("\nРазделение на кляузы:")
        for clause in clauses_res:
            print(clause)

        print("\nРазделение на слова:")
        for word in words_res:
            print(word)

        print("\nРазделение на токены:")
        for token in tokens_res:
            print(token)



        morph_res_for_clauses, morph_res = self.morph_res(clauses_res)

        print("\nМорфологический анализ:")
        for morph in morph_res:
            print(morph)




        sintaxis_root, sintaxis_nodes, sintaxis_text_info, sintaxis_tree_in_txt =\
            self.sintaxis_res(clauses_res, morph_res_for_clauses)

        print("\nСинтаксический анализ:")
        print(sintaxis_tree_in_txt)

        text_info = self.print_text_info(sintaxis_text_info)
        path_info = self.visual_result.save_txt(text_info, f"test_{num_test}_info")
        #text_info = self.visual_result.load_txt(path_info)

        graph = self.visual_result.create_graph(sintaxis_root)
        path_graph = self.visual_result.save_graph(graph, f"test_{num_test}_graph")
        #graph = self.visual_result.load_graph(path_graph)

        plt_graph = self.visual_result.visualize_graph(graph)
        #path_graph_plt = self.visual_result.save_plt_png(plt_graph,f"test{num_test}_treeA")

        plt_text = self.visual_result.visualize_syntax_links(sintaxis_nodes,tokens_res)
        #path_text_plt = self.visual_result.save_plt_png(plt_text, f"test{num_test}_textA")



        print("\nСемантический анализ:")
        subjects, actions, objects, datas = self.semantic_analyzer.round(sintaxis_root)
        print(subjects)
        print(actions)
        print(objects)
        for data in datas:
            print("[",end = "")
            for type in data:
                print("[",end = "")
                for item in type:
                    #print(item)
                    if not(item is None):
                        print(item.features.get("word"),end = " ")

                print("]",end = "")
            print("]\n")

    def graphem_res(self):
        graphems_res = self.graphematic_analyzer.analyze(self.TEXT)
        return graphems_res

    def spliter_res(self, graphems_res):
        clauses_res = self.clause_spliter.split_into_clauses(graphems_res)
        words_res = self.clause_spliter.split_into_words(graphems_res)
        tokens_res = self.clause_spliter.split_into_tokens(graphems_res)
        return clauses_res, words_res, tokens_res

    def morph_res(self,clauses_res):
        morph_res_for_clauses=[]
        morph_res=[]
        num_in_text = 1
        for clause in clauses_res:
            morph_res_i_clause = []
            for token in clause.get("tokens"):
                word = token.get("word")
                descr = token.get("descriptors")
                morph_res_i_clause += [self.morph_analyzer.analyze_word(word, num_in_text, descr)]
                morph_res += [self.morph_analyzer.analyze_word(word, num_in_text)]
                num_in_text += 1
            morph_res_for_clauses += [morph_res_i_clause]

        return morph_res_for_clauses, morph_res

    def sintaxis_res(self,clauses_res, morph_res_for_clauses):
        sintaxis_root, sintaxis_nodes, sintaxis_text_info, sintaxis_tree_in_txt =\
             self.sintaxis_analyzer.analyze(clauses_res,morph_res_for_clauses)

        return sintaxis_root, sintaxis_nodes, sintaxis_text_info, sintaxis_tree_in_txt


    @staticmethod
    def print_text_info(sintaxis_text_info):

        info_count_sent, info_count_part_sent, info_two_part, info_purpose_statement, info_intonation, \
            info_complexity, info_common, info_homogeneous = sintaxis_text_info

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

        return f"\nИнформация о тексте:\n{text_info}"



# Пример использования
if __name__ == "__main__":
    text = """Две старые кошки, мурлыча и грациозно двигаясь, поймали трёх мелких мышей в саду, но потом убежали в тёмный лес, где всегда тихо."""
    module = ProgramModule(text)
    module.main()






