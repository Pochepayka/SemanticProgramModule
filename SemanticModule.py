class SemanticAnalyzer:
    def __init__(self):
        self.root = None
        self.nodes = None

        self.subjects = []
        self.actions = []
        self.objects = []

        self.predicate_argument_structure = []

    def action_VERB(self, node, link, parent):

        subject = []
        action = []
        object = []

        if node.type == "VERB":
            for child, child_link in node.connections:
                if child_link == "subject":
                    if child not in subject:
                        subject += [child]
                        self.subjects.append(child.features.get("word"))
                    if node not in action:
                        action += [node]
                        self.actions.append(node.features.get("word"))

                if child_link == "sub_predicate":
                    if node not in action:
                        action += [node]
                        self.actions.append(node.features.get("word"))
                    if child not in action:
                        action += [child]
                        self.actions.append(child.features.get("word"))

                if child_link == "homogeneous":
                    if node not in action:
                        action += [node]
                        self.actions.append(node.features.get("word"))
                    if child not in action:
                        action += [child]
                        self.actions.append(child.features.get("word"))



                if child_link == "genitive":
                    if child not in object:
                        object += [child]
                        self.objects.append(child.features.get("word"))
                    if node not in action:
                        action += [node]
                        self.actions.append(node.features.get("word"))
        if action != [] or subject != [] or object != []:
            self.predicate_argument_structure += [[action, subject,object]]


    def action_PARTICIPLE(self, node, link, parent):
        subject = []
        action = []
        object = []


        if node.type == "PARTICIPLE":
            if node not in action:
                action += [node]
                self.actions.append(node.features.get("word"))
            if link == "attribute" and parent.type in ["NOUN","NPRO"]:
                if "activ" in  node.features.get("pledge"):
                    if parent not in subject:
                        subject += [parent]
                        self.subjects.append(parent.features.get("word"))
                    for child, child_link in node.connections:
                        if child_link == "genitive":
                            if child not in object:
                                object += [child]
                                self.objects.append(child.features.get("word"))
                elif "passiv" in node.features.get("pledge"):
                    if parent not in object:
                        object += [parent]
                        self.objects.append(parent.features.get("word"))
                    for child, child_link in node.connections:
                        if child_link == "genitive":
                            if child not in subject:
                                subject += [child]
                                self.subjects.append(child.features.get("word"))
        if action != [] or subject != [] or object != []:
            self.predicate_argument_structure += [[action, subject, object]]

    def action_ADVB_PARTICIPLE(self, node, link, parent):
        subject = []
        action = []
        object = []


        if node.type == "ADVB_PARTICIPLE":
            if parent.parent is not None and parent.parent not in subject:
                subject += [parent.parent]
                self.subjects.append(parent.parent.features.get("word"))

            if link == "attribute" and parent.type in ["NOUN","NPRO"]:
                if node.features.get("pledge") =="activ":
                    if parent not in subject:
                        subject += [parent]
                        self.subjects.append(parent.features.get("word"))
                    for child, child_link in node.connections:
                        if child_link == "genitive":
                            if child not in object:
                                object += [child]
                                self.objects.append(child.features.get("word"))
                else:
                    if node not in action:
                        action += [node]
                        self.actions.append(node.features.get("word"))
                    for child, child_link in node.connections:
                        if child_link == "genitive":
                            if child not in subject:
                                subject += [child]
                                self.subjects.append(child.features.get("word"))
        if action!= [] or subject!=[]or object!=[]:
            self.predicate_argument_structure += [[action, subject, object]]



    def round(self,root):

        self.subjects = []
        self.actions = []
        self.objects = []

        def _traverse(node, link = None, parent = None):
            if link and not(node.type in ["ROOT","SENT","PART_SENT"]):

                self.action_VERB(node, link, parent)
                self.action_PARTICIPLE(node, link, parent)


            for child, relation in node.connections:
                _traverse(child,relation,node)

        if root:
            _traverse(root)

        return self.subjects, self.actions, self.objects, self.predicate_argument_structure


