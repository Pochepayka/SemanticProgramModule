class SemanticAnalyzer:
    def __init__(self):
        self.root = None
        self.nodes = None

    def who_do(self):
        person = None

    def what_do(self):
        action = None

    def over_whom_do(self):
        object = None

    def raund(self,root):
        data = []
        def _traverse(node, link = None):
            if link and not(node.type in ["ROOT","SENT","PART_SENT"]):
                if link == "subject":
                    data.append(node.features.get("word"))

            for child, relation in node.connections:
                _traverse(child,relation)

        if root:
            _traverse(root)

        return data