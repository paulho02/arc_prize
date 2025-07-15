from abc import ABC, abstractmethod
import os
from typing import Union
import networkx as nx

from instruction_language.surroundings.memory import GMMService
from instruction_language.elements import types


class Executable(ABC):
    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def add_child(self, child: 'Executable', order: int = 0):
        pass

    @abstractmethod
    def delete_child(self, order: int):
        pass

    @abstractmethod
    def to_ast(self, ast: nx.DiGraph = nx.DiGraph(), parent_suffix: str = "", order: int = 0, parent: str = None):
        pass


class Term(Executable):
    def __init__(self, term: Union[int, Executable, None]):
        self.term: Union[int, Executable, None] = term

    def execute(self) -> int:
        if isinstance(self.term, int):
            return self.term
        elif isinstance(self.term, Executable):
            return self.term.execute()
        else:
            raise TypeError(
                f"Unsupported term type: {type(self.term)}. Expected int or Executable.")

    def add_child(self, child: 'Executable', order: int = 0):
        self.term = child

    def delete_child(self, order: int):
        self.term = None

    def to_ast(self, ast: nx.DiGraph = nx.DiGraph(), parent_suffix: str = "", order: int = 0, parent: str = None):
        """Converts the term to an AST representation."""
        suffix = f"{parent_suffix}.{order}"
        node_label = self.__class__.__name__ + suffix

        if isinstance(self.term, int):
            ast.add_node(self, type=types.t2int["term"], label=node_label,
                         carrying_value=self.term)
        elif isinstance(self.term, Executable):
            ast.add_node(self, label=node_label, type=types.t2int["term"],
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

    def add_child(self, child: Executable, order: int = 0):
        # if order ist out of range, set it to max or minimum
        if order < 0:
            order = 0
        elif order > len(self.execution_plan):
            order = len(self.execution_plan)

        self.execution_plan.insert(order, child)

    def delete_child(self, order: int):
        """Deletes a child at the specified order."""
        if 0 <= order < len(self.execution_plan):
            del self.execution_plan[order]
        else:
            raise IndexError("Order out of range for execution plan.")

    def to_ast(self, ast: nx.DiGraph = nx.DiGraph(), parent_suffix: str = "", order: int = 0, parent: str = None):
        """Converts the codeblock to an AST representation."""

        suffix = f"{parent_suffix}.{order}"
        node_label = self.__class__.__name__ + suffix

        ast.add_node(self, label=node_label,
                     type=types.t2int["codeblock"], carrying_value=None)

        # call to_ast for each child
        for i, step in enumerate(self.execution_plan):
            step.to_ast(ast, parent_suffix=suffix, order=i, parent=self)

        if parent is not None:
            ast.add_edge(parent, self, order=order)

        return ast, self
