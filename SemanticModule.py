class SemanticAnalyzer:
    def __init__(self):
        self.groups = []

    def getWord(self, node):
        #return node.features.get("word")
        return node#.features.get("word")
        
    def _find_connections(self, node, current_group, mainNowI = 0):
        # Собираем связанные элементы для действия
        nextMainNowI = mainNowI

        if (node.type == "PARTICIPLE" and "activ" in node.features.get("pledge") and node.parent and node.parent.type in ["NOUN", "NPRO"]):
                current_group["subjects"].append(self.getWord(node.parent))

        elif (node.type == "PARTICIPLE" and "passiv" in node.features.get("pledge") and node.parent and node.parent.type in ["NOUN", "NPRO"]):
                current_group["objects"].append(self.getWord(node.parent))
        
        if (node.type == "VERB" and node.link_to_parent == "homogeneous" and node.parent):
            for child, relation in node.parent.connections:
                if relation == "subject":
                    current_group["subjects"].append(self.getWord(child))

        if (node.type == "ADVB_PARTICIPLE" and node.link_to_parent == "circumstance" and node.parent):
            parent = node.parent
            linkToParent = node.link_to_parent
            flag = True

            while parent and flag and linkToParent!="part":
                
                if parent.parent:
                    parent = parent.parent
                    linkToParent = parent.link_to_parent
                else:
                    flag = False
                    break
                
            for child, relation in parent.connections:
                if relation == "subject":
                    current_group["subjects"].append(self.getWord(child))



        for child, relation in node.connections:
            finish = 0
            if relation == "subject":
                current_group["subjects"].append(self.getWord(child))

            elif relation in ["genitive"]:
                current_group["objects"].append(self.getWord(child))

            elif relation == "adverbial":
                current_group["circumstances"].append(self.getWord(child))

            elif relation == "sub_predicate":
                current_group["actions"] += [current_group["actions"][0], self.getWord(child)]
                current_group["actions"].pop(0)

            elif relation == "participle":
                current_group["actions"] += [self.getWord(child), current_group["actions"][0]]
                current_group["actions"].pop(0)

            elif relation in ["passive_object"]:
                current_group["objects"].append(self.getWord(child))

            elif relation in ["active_object"] :
                current_group["subjects"].append(self.getWord(child))

            elif relation in ["prepositional_object"]:
                if len(child.connections)>0:
                    obj =next(self.getWord(subChild) for subChild,_ in child.connections if subChild)
                    if obj:
                        current_group["objects"]+= [self.getWord(child), obj]
            elif relation in ["object"]:
                pass
            else: 
                finish+=1
            
            if finish < 1:
                self._find_connections(child, current_group, nextMainNowI)


    def round(self, root):
        """Группировка элементов по логическим связям"""
        self.groups = []
        
        def _traverse(node):
            if node.type in ["VERB", "PARTICIPLE", "ADVB_PARTICIPLE"]:
                group = {
                    "subjects": [],
                    "actions": [self.getWord(node)],
                    "objects": [],
                    "tools": [],
                    "locations": [],
                    "time": [],
                    "circumstances": []
                }
                
                # Поиск связанных элементов
                self._find_connections(node, group)
                
                # Добавление группы, если есть хотя бы действие
                if group["actions"]:
                    self.groups.append(group)
                    
            for child, _ in node.connections:
                _traverse(child)
                
        if root:
            _traverse(root)
            
        return self._format_groups()
    
    def _format_groups(self):
        # Преобразование в нужный формат
        formatted = []
        for group in self.groups:
            formatted.append([
                (group["subjects"]) ,
                (group["actions"]),
                (group["objects"]) ,
                (group["tools"]),
                (group["locations"]) ,
                (group["time"]),
                (group["circumstances"])
            ])
        return formatted

"""#     def _extract_semantic_groups(self, node, link, parent):
#         #Определение семантических групп на основе типа узла и связи.

#         # 8.1. Агент (subject)
#         if (
#             link in ["subject","active_object"]
#         ):
#             self.subjects.append(node.features.get("word"))

#         # # 8.2. Действие (predicate) node.change_part_of_sent(PartOfSpeech.PREDICATE)
#         if (
#             node.type in ["VERB","INFI", "PARTICIPLE", "ADVB_PARTICIPLE"] 
#         ):
#             self.actions.append(node.features.get("word"))

#         # # 8.3. Пациент ()
#         if (
#             link in ["passive_object", "genitive", "object"] 
#         ):
#             self.objects.append(node.features.get("word"))

#         # # 8.4. Инструмент (творительный падеж с предлогом"с" или без)
#         # if (
#         #     node.type in ["NOUN", "NPRO"] 
#         #     # and "ablt" in node.features.get("case", [])
#         #     and (parent and parent.type == "PREP" and parent.features.get("word").lower() in ["с", "без"])
#         # ):
#         #     self.tool.append(node.features.get("word"))

#         # # 8.5. Локация (предложный/местный падеж с предлогами места)
#         # if (
#         #     node.type in ["NOUN", "NPRO"] 
#         #     # and "loct" in node.features.get("case", [])
#         #     and ((parent and parent.type == "PREP" and parent.features.get("word").lower() in ["в", "на", "под","до"]))
#         # ):
#         #     self.locate.append(node.features.get("word"))

#         # # 8.6. Время (предлоги времени + падежи)
#         # if (
#         #     node.type in ["NOUN", "NPRO"] 
#         #     # and "gent" in node.features.get("case", [])
#         #     and ((parent and parent.type == "PREP" and parent.features.get("word").lower() in ["в", "после", "до"]))
#         # ):
#         #     self.time.append(node.features.get("word"))

#         # # 8.7. Обстоятельство (наречия или конструкции с предлогом)
#         if (
#             link in ["adverbial"] 
#         ):
#             self.circumstance.append(node.features.get("word"))"""

#     def action_VERB(self, node, link, parent):

#         subject = []
#         action = []
#         object = []

#         if node.type == "VERB":
#             for child, child_link in node.connections:
#                 if child_link == "subject":
#                     if child not in subject:
#                         subject += [child]
#                         self.subjects.append(child.features.get("word"))
#                     if node not in action:
#                         action += [node]
#                         self.actions.append(node.features.get("word"))

#                 if child_link == "sub_predicate":
#                     if node not in action:
#                         action += [node]
#                         self.actions.append(node.features.get("word"))
#                     if child not in action:
#                         action += [child]
#                         self.actions.append(child.features.get("word"))

#                 if child_link == "homogeneous":
#                     if node not in action:
#                         action += [node]
#                         self.actions.append(node.features.get("word"))
#                     if child not in action:
#                         action += [child]
#                         self.actions.append(child.features.get("word"))



#                 if child_link == "genitive":
#                     if child not in object:
#                         object += [child]
#                         self.objects.append(child.features.get("word"))
#                     if node not in action:
#                         action += [node]
#                         self.actions.append(node.features.get("word"))
#         if action != [] or subject != [] or object != []:
#             self.predicate_argument_structure += [[action, subject,object]]

#     def action_PARTICIPLE(self, node, link, parent):
#         subject = []
#         action = []
#         object = []


#         if node.type == "PARTICIPLE":
#             if node not in action:
#                 action += [node]
#                 self.actions.append(node.features.get("word"))
#             if link == "attribute" and parent.type in ["NOUN","NPRO"]:
#                 if "activ" in  node.features.get("pledge"):
#                     if parent not in subject:
#                         subject += [parent]
#                         self.subjects.append(parent.features.get("word"))
#                     for child, child_link in node.connections:
#                         if child_link == "genitive":
#                             if child not in object:
#                                 object += [child]
#                                 self.objects.append(child.features.get("word"))
#                 elif "passiv" in node.features.get("pledge"):
#                     if parent not in object:
#                         object += [parent]
#                         self.objects.append(parent.features.get("word"))
#                     for child, child_link in node.connections:
#                         if child_link == "genitive":
#                             if child not in subject:
#                                 subject += [child]
#                                 self.subjects.append(child.features.get("word"))
#         if action != [] or subject != [] or object != []:
#             self.predicate_argument_structure += [[action, subject, object]]

#     def action_ADVB_PARTICIPLE(self, node, link, parent):
#         subject = []
#         action = []
#         object = []


#         if node.type == "ADVB_PARTICIPLE":
#             if parent.parent is not None and parent.parent not in subject:
#                 subject += [parent.parent]
#                 self.subjects.append(parent.parent.features.get("word"))

#             if link == "attribute" and parent.type in ["NOUN","NPRO"]:
#                 if node.features.get("pledge") =="activ":
#                     if parent not in subject:
#                         subject += [parent]
#                         self.subjects.append(parent.features.get("word"))
#                     for child, child_link in node.connections:
#                         if child_link == "genitive":
#                             if child not in object:
#                                 object += [child]
#                                 self.objects.append(child.features.get("word"))
#                 else:
#                     if node not in action:
#                         action += [node]
#                         self.actions.append(node.features.get("word"))
#                     for child, child_link in node.connections:
#                         if child_link == "genitive":
#                             if child not in subject:
#                                 subject += [child]
#                                 self.subjects.append(child.features.get("word"))
#         if action!= [] or subject!=[]or object!=[]:
#             self.predicate_argument_structure += [[action, subject, object]]

