from abc import abstractmethod
from instruction_language.elements.base import Executable, Term
import networkx as nx


class Operator(Executable):
    def __init__(self, term1: Term, term2: Term):
        pass

    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def to_ast(self, ast: nx.DiGraph = nx.DiGraph(), parent_suffix: str = "", order: int = 0, parent: str = None):
        pass


class SUM(Operator):
    def __init__(self, term1: Term, term2: Term):
        super().__init__(term1, term2)

        self.term1 = term1
        self.term2 = term2

    def execute(self):
        return self.term1.execute() + self.term2.execute()

    def to_ast(self, ast: nx.DiGraph = nx.DiGraph(), parent_suffix: str = "", order: int = 0, parent: str = None):
        """Converts the term to an AST representation."""
        suffix = f"{parent_suffix}.{order}"
        node_label = self.__class__.__name__ + suffix

        ast.add_node(self, label=node_label, type="sum", carrying_value=None)

        self.term1.to_ast(ast, parent_suffix=suffix,
                          order=0, parent=self)
        self.term2.to_ast(ast, parent_suffix=suffix,
                          order=1, parent=self)

        if parent is not None:
            ast.add_edge(parent, self, order=order)


# todo implement further operators
