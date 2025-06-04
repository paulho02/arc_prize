from instruction_language.elements.base import Codeblock, Executable
from instruction_language.elements.conditions import Condition
import networkx as nx


class ControlFlowStatement(Executable):
    def __init__(self):
        pass

    def execute(self):
        pass

    def to_ast(self, ast: nx.DiGraph = nx.DiGraph(), parent_suffix: str = "", order: int = 0, parent: str = None):
        pass


class If(ControlFlowStatement):
    # todo maybe outsource the condition_code_plan to a separate class
    def __init__(self, default: Codeblock, *args: tuple[Condition, Codeblock]):
        super().__init__()
        self.default = default
        self.condition_code_plan = list(args)

    def execute(self):
        for condition, codeblock in self.condition_code_plan:
            if condition.apply():
                codeblock.execute()
                return

        self.default.execute()
        return

    def to_ast(self, ast: nx.DiGraph = nx.DiGraph(), parent_suffix: str = "", order: int = 0, parent: str = None):
        """Converts the term to an AST representation."""
        suffix = f"{parent_suffix}.{order}"
        node_label = self.__class__.__name__ + suffix

        ast.add_node(self, label=node_label, type="if", carrying_value=None)

        self.default.to_ast(ast, parent_suffix=suffix,
                            order=0, parent=self)

        for i, (condition, codeblock) in enumerate(self.condition_code_plan):
            condition.to_ast(ast, parent_suffix=suffix,
                             order=i + 1, parent=self)
            codeblock.to_ast(ast, parent_suffix=suffix,
                             order=i + 1, parent=self)

        if parent is not None:
            ast.add_edge(parent, self, order=order)


class WhileLoop(ControlFlowStatement):
    def __init__(self, condition: Condition, codeblock: Codeblock):
        super().__init__()
        self.condition = condition
        self.codeblock = codeblock

    def execute(self):
        while self.condition.apply():
            self.codeblock.execute()

    def to_ast(self, ast: nx.DiGraph = nx.DiGraph(), parent_suffix: str = "", order: int = 0, parent: str = None):
        """Converts the term to an AST representation."""
        suffix = f"{parent_suffix}.{order}"
        node_label = self.__class__.__name__ + suffix

        ast.add_node(self, label=node_label, type="while", carrying_value=None)

        self.condition.to_ast(ast, parent_suffix=suffix,
                              order=0, parent=self)
        self.codeblock.to_ast(ast, parent_suffix=suffix,
                              order=0, parent=self)

        if parent is not None:
            ast.add_edge(parent, self, order=order)
