from abc import abstractmethod
from instruction_language.elements.base import Executable, Term
import networkx as nx


class Condition(Executable):
    def __init__(self, term1: Term, term2: Term):
        self.term1 = term1
        self.term2 = term2

    @abstractmethod
    def execute(self) -> bool:
        pass

    def add_child(self, child: 'Executable', order: int):
        if order <= 0:
            self.term1 = child
        elif order >= 1:
            self.term2 = child

    def delete_child(self, order: int):
        if order <= 0:
            self.term1 = None
        elif order >= 1:
            self.term2 = None

    def to_ast(self, ast: nx.DiGraph = nx.DiGraph(), parent_suffix: str = "", order: int = 0, parent: str = None, type: str = "condition"):
        """Converts the term to an AST representation."""
        suffix = f"{parent_suffix}.{order}"
        node_label = self.__class__.__name__ + suffix

        ast.add_node(self, label=node_label,
                     type="less_than", carrying_value=None)

        self.term1.to_ast(ast, parent_suffix=suffix,
                          order=0, parent=self)
        self.term2.to_ast(ast, parent_suffix=suffix,
                          order=1, parent=self)

        if parent is not None:
            ast.add_edge(parent, self, order=order)


class LessThan(Condition):
    def __init__(self, term1: Term, term2: Term):
        super().__init__(term1, term2)

    def execute(self):
        return self.term1.execute() < self.term2.execute()

    def to_ast(self, ast: nx.DiGraph = nx.DiGraph(), parent_suffix: str = "", order: int = 0, parent: str = None):
        """Converts the term to an AST representation."""
        super().to_ast(ast, parent_suffix, order, parent, type="less_than")


class EqualTo(Condition):
    def __init__(self, term1: Term, term2: Term):
        super().__init__(term1, term2)

    def execute(self):
        return (
            self.term1.execute() is self.term2.execute()
            or self.term1.execute() == self.term2.execute()
        )

    def to_ast(self, ast: nx.DiGraph = nx.DiGraph(), parent_suffix: str = "", order: int = 0, parent: str = None):
        """Converts the term to an AST representation."""
        super().to_ast(ast, parent_suffix, order, parent, type="equal_to")


class GreaterThan(Condition):
    def __init__(self, term1: Term, term2: Term):
        super().__init__(term1, term2)

    def execute(self):
        return self.term1.execute() > self.term2.execute()

    def to_ast(self, ast: nx.DiGraph = nx.DiGraph(), parent_suffix: str = "", order: int = 0, parent: str = None):
        """Converts the term to an AST representation."""
        super().to_ast(ast, parent_suffix, order, parent, type="greater_than")
