from abc import ABC, abstractmethod
import os
from typing import Union
import networkx as nx

from instruction_language.surroundings.memory import GMMService


class Executable(ABC):
    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def to_ast(self, ast: nx.DiGraph = nx.DiGraph(), parent_suffix: str = "", order: int = 0, parent: str = None):
        pass


class Term(Executable):
    def __init__(self, term: Union[int, Executable]):
        self.term = term

    def execute(self):
        if isinstance(self.term, int):
            return self.term
        elif isinstance(self.term, Executable):
            return self.term.execute()
        else:
            raise TypeError(
                f"Unsupported term type: {type(self.term)}. Expected int or Executable.")

    def to_ast(self, ast: nx.DiGraph = nx.DiGraph(), parent_suffix: str = "", order: int = 0, parent: str = None):
        """Converts the term to an AST representation."""
        suffix = f"{parent_suffix}.{order}"
        node_label = self.__class__.__name__ + suffix

        if isinstance(self.term, int):
            ast.add_node(self, type="term", label=node_label,
                         carrying_value=self.term)
        elif isinstance(self.term, Executable):
            ast.add_node(self, label=node_label, type="term",
                         carrying_value=None)
            self.term.to_ast(ast, parent_suffix=suffix,
                             order=0, parent=self)
        else:
            raise TypeError(
                f"Unsupported term type: {type(self.term)}. Expected int or Executable.")

        if parent is not None:
            ast.add_edge(parent, self, order=order)


class Codeblock(Executable):
    def __init__(self, execution_plan: list[Executable] = []):
        self.execution_plan: list[Executable] = execution_plan

    def execute(self):
        mm = GMMService.get()
        os.environ["CURRENT_NAMESPACE_ID"] = mm.new_namespace()

        for i, step in enumerate(self.execution_plan):
            try:
                step.execute()
            except Exception as e:
                print(f"Exception in step {i} (step type: {type(step)})")
                raise e

    def to_ast(self, ast: nx.DiGraph = nx.DiGraph(), parent_suffix: str = "", order: int = 0, parent: str = None):
        """Converts the codeblock to an AST representation."""

        suffix = f"{parent_suffix}.{order}"
        node_label = self.__class__.__name__ + suffix

        ast.add_node(self, label=node_label,
                     type="codeblock", carrying_value=None)

        # call to_ast for each child
        for i, step in enumerate(self.execution_plan):
            step.to_ast(ast, parent_suffix=suffix, order=i, parent=self)

        if parent is not None:
            ast.add_edge(parent, self, order=order)

        return ast, self
