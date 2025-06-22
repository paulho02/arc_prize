from abc import abstractmethod
from typing import Union
from instruction_language.elements.base import Executable, Term
import networkx as nx


class Operator(Executable):
    def __init__(self, term1: Union[Term, None], term2: Union[Term, None]):
        pass

    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def add_child(self, child, order=0):
        pass

    @abstractmethod
    def delete_child(self, order: int):
        pass

    @abstractmethod
    def to_ast(self, ast: nx.DiGraph = nx.DiGraph(), parent_suffix: str = "", order: int = 0, parent: str = None):
        pass


class SUM(Operator):
    def __init__(self, term1: Union[Term, None], term2: Union[Term, None]):
        super().__init__(term1, term2)

        self.term1: Union[Term, None] = term1
        self.term2: Union[Term, None] = term2

    def execute(self):
        return self.term1.execute() + self.term2.execute()

    def add_child(self, child, order=0):
        if not isinstance(child, Term):
            raise TypeError("Child must be an instance of Term.")

        if order <= 0:
            self.term1 = child
        elif order >= 1:
            self.term2 = child

    def delete_child(self, order: int):
        if order <= 0:
            self.term1 = None
        elif order >= 1:
            self.term2 = None

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
