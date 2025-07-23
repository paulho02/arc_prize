from abc import abstractmethod
from typing import Union
from instruction_language.elements import types
from instruction_language.elements.base import Codeblock, Executable, NoneType
from instruction_language.elements.conditions import Condition
import networkx as nx


class ControlFlowStatement(Executable):
    def __init__(self):
        pass

    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def add_child(self, child: Executable, order: int = 0):
        pass

    @abstractmethod
    def delete_child(self, order: int):
        pass

    @abstractmethod
    def to_ast(self, ast: nx.DiGraph = nx.DiGraph(), parent_suffix: str = "", order: int = 0, parent: str = None):
        pass


class If(ControlFlowStatement):
    # todo maybe outsource the condition_code_plan to a separate class
    def __init__(self, default: Codeblock, *args: tuple[Condition, Codeblock]):
        super().__init__()
        self.default = default
        # typing says condition_code_plan can take infinite tuples of (Condition, Codeblock), but can be None (which is necessary during the code_writing process)
        self.condition_code_plan: list[tuple[Union[Condition, None], Union[Condition, None]]] = list(
            args)

    def execute(self):
        for condition, codeblock in self.condition_code_plan:
            if condition.execute():
                codeblock.execute()
                return

        self.default.execute()
        return

    def add_child(self, child: Executable, order: int = 0):
        if order <= 0:
            if not isinstance(child, Codeblock):
                raise TypeError("Default child must be a Codeblock.")
            self.default.add_child(child)
        elif order >= 1:
            index = order - 1
            code_condition_tuple = self.condition_code_plan.get(
                index, (None, None))

            # assign the child to according pos in the tuple (and leave the other one as it is)
            if isinstance(child, Condition):
                code_condition_tuple = (
                    child, code_condition_tuple[1])
            elif isinstance(child, Codeblock):
                code_condition_tuple = (
                    code_condition_tuple[0], child)
            else:
                raise TypeError(
                    "Child must be either a Condition or a Codeblock.")

            self.condition_code_plan.insert(index, code_condition_tuple)

    def delete_child(self, order: int):
        if order <= 0:
            self.default = Codeblock([])
        elif order >= 1:
            index = order - 1
            if index < len(self.condition_code_plan):
                del self.condition_code_plan[index]
            else:
                raise IndexError(
                    f"No condition_code_plan at index {index}. Current length: {len(self.condition_code_plan)}.")

    def to_ast(self, ast: nx.DiGraph = nx.DiGraph(), parent_suffix: str = "", order: int = 0, parent: str = None):
        """Converts the term to an AST representation."""
        suffix = f"{parent_suffix}.{order}"
        node_label = self.__class__.__name__ + suffix

        ast.add_node(self, label=node_label,
                     type=types.t2int["if"], carrying_value=None)

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
    def __init__(self, condition: Union[Condition, NoneType], codeblock: Codeblock):
        super().__init__()
        self.condition = condition
        self.codeblock = codeblock

    def execute(self):
        while self.condition.execute():
            self.codeblock.execute()

    def add_child(self, child: Executable, order: int = 0):
        if isinstance(child, Condition):
            self.condition = child
        elif isinstance(child, Codeblock):
            self.codeblock = child
        else:
            raise TypeError("Child must be either a Condition or a Codeblock.")

    def delete_child(self, order: int):
        self.condition = NoneType()
        self.codeblock = Codeblock([])

    def to_ast(self, ast: nx.DiGraph = nx.DiGraph(), parent_suffix: str = "", order: int = 0, parent: str = None):
        """Converts the term to an AST representation."""
        suffix = f"{parent_suffix}.{order}"
        node_label = self.__class__.__name__ + suffix

        ast.add_node(self, label=node_label,
                     type=types.t2int["while"], carrying_value=None)

        self.condition.to_ast(ast, parent_suffix=suffix,
                              order=0, parent=self)
        self.codeblock.to_ast(ast, parent_suffix=suffix,
                              order=0, parent=self)

        if parent is not None:
            ast.add_edge(parent, self, order=order)
