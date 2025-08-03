from abc import ABC, abstractmethod
import logging
import os
from typing import Union
import networkx as nx

from instruction_language.logging_setup import setup_logger
from instruction_language.surroundings.memory import GMMService
from instruction_language.elements import types
from typing import Sequence


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
    def to_ast(self, ast: nx.DiGraph = nx.DiGraph(), parent_suffix: str = "", order: int = 0, parent=None):
        pass


class NoneType(Executable):
    def __init__(self):
        self.logger = setup_logger("NoneType", level=logging.ERROR)

    def execute(self):
        self.logger.warning("Executed NoneType node.")
        return None

    def add_child(self, child: 'Executable', order: int = 0):
        raise NotImplementedError("NoneType cannot have children.")

    def delete_child(self, order: int):
        raise NotImplementedError("NoneType cannot have children.")

    def to_ast(self, ast: nx.DiGraph = nx.DiGraph(), parent_suffix: str = "", order: int = 0, parent=None):
        """Converts the NoneType to an AST representation."""
        suffix = f"{parent_suffix}.{order}"
        node_label = self.__class__.__name__ + suffix
        ast.add_node(self, label=node_label,
                     type=types.t2int["none_type"], carrying_value=None)
        if parent is not None:
            ast.add_edge(parent, self, order=order)


class Constant(Executable):
    def __init__(self, value: Union[int, str, None] = None):
        self.logger = setup_logger("Constant", level=logging.INFO)

        self.value = value

    def execute(self) -> Union[int, str, None]:
        return self.value

    def add_child(self, child: 'Executable', order: int = 0):
        raise NotImplementedError("Constant nodes cannot have children.")

    def delete_child(self, order: int):
        raise NotImplementedError("Constant nodes cannot have children.")

    def to_ast(self, ast: nx.DiGraph = nx.DiGraph(), parent_suffix: str = "", order: int = 0, parent=None):
        """Converts the constant to an AST representation."""
        suffix = f"{parent_suffix}.{order}"
        node_label = self.__class__.__name__ + suffix
        ast.add_node(self, label=node_label,
                     type=types.t2int["constant"], carrying_value=self.value)
        if parent is not None:
            ast.add_edge(parent, self, order=order)


class Term(Executable):
    def __init__(self, term: Union[Executable, None]):
        self.logger = setup_logger("Term", level=logging.INFO)

        self.child: Union[Executable, None] = term

    def execute(self) -> int:
        if isinstance(self.child, Executable):
            return self.child.execute()
        else:
            raise TypeError(
                f"Unsupported term type: {type(self.child)}. Expected Executable.")

    def add_child(self, child: 'Executable', order: int = 0):
        self.child = child

    def delete_child(self, order: int):
        self.child = NoneType()

    def to_ast(self, ast: nx.DiGraph = nx.DiGraph(), parent_suffix: str = "", order: int = 0, parent=None):
        """Converts the term to an AST representation."""
        suffix = f"{parent_suffix}.{order}"
        node_label = self.__class__.__name__ + suffix

        ast.add_node(self, label=node_label, type=types.t2int["term"],
                     carrying_value=None)

        if isinstance(self.child, Executable):
            self.child.to_ast(ast, parent_suffix=suffix,
                              order=0, parent=self)
        else:
            raise TypeError(
                f"Unsupported term type: {type(self.child)}. Expected Executable.")

        if parent is not None:
            ast.add_edge(parent, self, order=order)


class Codeblock(Executable):
    def __init__(self, execution_plan: Sequence[Executable] = ()):
        self.logger = setup_logger("Codeblock", level=logging.CRITICAL)

        self.execution_plan: list[Executable] = list(execution_plan)

    def execute(self):
        mm = GMMService.get()
        os.environ["CURRENT_NAMESPACE_ID"] = mm.new_namespace()

        for i, step in enumerate(self.execution_plan):
            try:
                step.execute()
            except Exception as e:
                self.logger.error(
                    f"Exception in step {i} (step type: {type(step)})")
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

    def to_ast(self, ast: Union[nx.DiGraph, None] = None, parent_suffix: str = "", order: int = 0, parent: str = None):
        """Converts the codeblock to an AST representation."""

        if ast is None:
            ast = nx.DiGraph()

        suffix = f"{parent_suffix}.{order}"
        node_label = self.__class__.__name__ + suffix

        ast.add_node(self, label=node_label,
                     type=types.t2int["codeblock"], carrying_value=None)

        # call to_ast for each child
        for i, step in enumerate(self.execution_plan):
            if step is not None:
                step.to_ast(ast, parent_suffix=suffix, order=i, parent=self)

        if parent is not None:
            ast.add_edge(parent, self, order=order)

        return ast, self
