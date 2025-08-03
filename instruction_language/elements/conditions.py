from abc import abstractmethod
import logging
from typing import Union
from instruction_language.elements.base import Executable, NoneType, Term
from instruction_language.elements import types
import networkx as nx

from instruction_language.logging_setup import setup_logger


class Condition(Executable):
    def __init__(self, term1: Union[Term, NoneType], term2: Union[Term, NoneType]):
        self.logger = setup_logger("Condition", level=logging.INFO)

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
            self.term1 = NoneType()
        elif order >= 1:
            self.term2 = NoneType()

    def to_ast(self, ast: nx.DiGraph = nx.DiGraph(), parent_suffix: str = "", order: int = 0, parent: str = None, type: str = "condition"):
        """Converts the term to an AST representation."""
        suffix = f"{parent_suffix}.{order}"
        node_label = self.__class__.__name__ + suffix

        ast.add_node(self, label=node_label,
                     type=types.t2int[type], carrying_value=None)

        self.term1.to_ast(ast, parent_suffix=suffix,
                          order=0, parent=self)
        self.term2.to_ast(ast, parent_suffix=suffix,
                          order=1, parent=self)

        if parent is not None:
            ast.add_edge(parent, self, order=order)


class LessThan(Condition):
    def __init__(self, term1: Union[Term, NoneType], term2: Union[Term, NoneType]):
        super().__init__(term1, term2)
        self.logger = setup_logger("LessThan", level=logging.INFO)

    def execute(self):
        return self.term1.execute() < self.term2.execute()

    def to_ast(self, ast: nx.DiGraph = nx.DiGraph(), parent_suffix: str = "", order: int = 0, parent: str = None):
        """Converts the term to an AST representation."""
        super().to_ast(ast, parent_suffix, order, parent, type="less_than")


class EqualTo(Condition):
    def __init__(self, term1: Union[Term, NoneType], term2: Union[Term, NoneType]):
        super().__init__(term1, term2)
        self.logger = setup_logger("EqualTo", level=logging.INFO)

    def execute(self):
        return (
            self.term1.execute() is self.term2.execute()
            or self.term1.execute() == self.term2.execute()
        )

    def to_ast(self, ast: nx.DiGraph = nx.DiGraph(), parent_suffix: str = "", order: int = 0, parent: str = None):
        """Converts the term to an AST representation."""
        super().to_ast(ast, parent_suffix, order, parent, type="equal_to")


class GreaterThan(Condition):
    def __init__(self, term1: Union[Term, NoneType], term2: Union[Term, NoneType]):
        super().__init__(term1, term2)
        self.logger = setup_logger("GreaterThan", level=logging.INFO)

    def execute(self):
        return self.term1.execute() > self.term2.execute()

    def to_ast(self, ast: nx.DiGraph = nx.DiGraph(), parent_suffix: str = "", order: int = 0, parent: str = None):
        """Converts the term to an AST representation."""
        super().to_ast(ast, parent_suffix, order, parent, type="greater_than")
