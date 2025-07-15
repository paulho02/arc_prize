from abc import abstractmethod
import os
from typing import Union
from instruction_language.elements import types
from instruction_language.elements.base import Executable, Term
from instruction_language.surroundings.environment import GEMService
from instruction_language.surroundings.memory import GMMService
import networkx as nx


class Instruction(Executable):
    def __init__(self):
        pass

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
    def to_ast(self, ast=None, parent_suffix="", order=0, parent=None):
        pass


class Read_Pixel(Instruction):
    def __init__(self, env_key: Union[str, None], x: Term, y: Term):
        super().__init__()
        if env_key == types.carrying_value_none_encoding:
            raise ValueError(
                f"env_key cannot be set to the carrying_value_none_encoding (which is {types.carrying_value_none_encoding}).")
        self.env_key: Union[str, None] = env_key
        self.x: Union[Term, None] = x
        self.y: Union[Term, None] = y

    def execute(self):
        x = self.x.execute()
        y = self.y.execute()
        env = GEMService.get(self.env_key)
        return env.get(x, y)

    def add_child(self, child: 'Executable', order: int = 0):
        if not isinstance(child, Term):
            raise TypeError("Child must be an instance of Term.")

        if order <= 0:
            self.x = child
        elif order >= 1:
            self.y = child

    def delete_child(self, order: int):
        if order <= 0:
            self.x = None
        elif order >= 1:
            self.y = None

    def to_ast(self, ast: nx.DiGraph = nx.DiGraph(), parent_suffix: str = "", order: int = 0, parent: str = None):
        """Converts the term to an AST representation."""
        suffix = f"{parent_suffix}.{order}"
        node_label = self.__class__.__name__ + suffix

        ast.add_node(self, label=node_label,
                     type=types.t2int["read_pixel"], carrying_value=None)

        self.x.to_ast(ast, parent_suffix=suffix,
                      order=0, parent=self)
        self.y.to_ast(ast, parent_suffix=suffix,
                      order=1, parent=self)

        if parent is not None:
            ast.add_edge(parent, self, order=order)


class Write_Pixel(Instruction):
    def __init__(self, env_key: Union[str, None], x: Union[Term, None], y: Union[Term, None], value: Union[Term, None]):
        super().__init__()
        if env_key == types.carrying_value_none_encoding:
            raise ValueError(
                f"env_key cannot be set to the carrying_value_none_encoding (which is {types.carrying_value_none_encoding}).")
        self.env_key: Union[str, None] = env_key
        self.x: Union[Term, None] = x
        self.y: Union[Term, None] = y
        self.value: Union[Term, None] = value

    # todo make initial_env write protected

    def execute(self):
        x = self.x.execute()
        y = self.y.execute()
        value = self.value.execute()
        env = GEMService.get(self.env_key)
        env.set(x, y, value)

    def add_child(self, child: 'Executable', order: int = 0):
        if not isinstance(child, Term):
            raise TypeError("Child must be an instance of Term.")

        if order <= 0:
            self.value = child
        elif order == 1:
            self.x = child
        elif order >= 2:
            self.y = child

    def delete_child(self, order: int):
        if order <= 0:
            self.value = None
        elif order == 1:
            self.x = None
        elif order >= 2:
            self.y = None

    def to_ast(self, ast: nx.DiGraph = nx.DiGraph(), parent_suffix: str = "", order: int = 0, parent: str = None):
        """Converts the term to an AST representation."""
        suffix = f"{parent_suffix}.{order}"
        node_label = self.__class__.__name__ + suffix

        ast.add_node(self, label=node_label,
                     type=types.t2int["write_pixel"], carrying_value=None)

        self.value.to_ast(ast, parent_suffix=suffix,
                          order=0, parent=self)
        self.x.to_ast(ast, parent_suffix=suffix,
                      order=1, parent=self)
        self.y.to_ast(ast, parent_suffix=suffix,
                      order=2, parent=self)

        if parent is not None:
            ast.add_edge(parent, self, order=order)


# todo maybe replace direct key access with Term, etc..
class Read_Var(Instruction):
    def __init__(self, key):
        super().__init__()
        if key == types.carrying_value_none_encoding:
            raise ValueError(
                f"key cannot be set to the carrying_value_none_encoding (which is {types.carrying_value_none_encoding}).")
        self.key = key

    def execute(self):
        namespace_id = os.environ.get("CURRENT_NAMESPACE_ID")
        return GMMService.get().get_var(namespace_id, self.key)

    def add_child(self, child: 'Executable', order: int = 0):
        # A Read_Var cannot have children, so this method does nothing.
        pass

    def delete_child(self, order: int):
        # A Read_Var cannot have children, so this method does nothing.
        pass

    def to_ast(self, ast: nx.DiGraph = nx.DiGraph(), parent_suffix: str = "", order: int = 0, parent: str = None):
        """Converts the term to an AST representation."""
        suffix = f"{parent_suffix}.{order}"
        node_label = self.__class__.__name__ + suffix

        ast.add_node(self, label=node_label, type=types.t2int["read_var"],
                     carrying_value=self.key)

        if parent is not None:
            ast.add_edge(parent, self, order=order)


class Write_Var(Instruction):
    def __init__(self, key, value: Union[Term, None]):
        super().__init__()
        if key == types.carrying_value_none_encoding:
            raise ValueError(
                f"key cannot be set to the carrying_value_none_encoding (which is {types.carrying_value_none_encoding}).")
        self.key = key
        self.value: Union[Term, None] = value

    def execute(self):
        namespace_id = os.environ.get("CURRENT_NAMESPACE_ID")
        return GMMService.get().set_var(namespace_id, self.key, self.value.execute())

    def add_child(self, child: 'Executable', order: int = 0):
        if not isinstance(child, Term):
            raise TypeError("Child must be an instance of Term.")

        self.value = child

    def delete_child(self, order: int):
        self.value = None

    def to_ast(self, ast: nx.DiGraph = nx.DiGraph(), parent_suffix: str = "", order: int = 0, parent: str = None):
        """Converts the term to an AST representation."""
        suffix = f"{parent_suffix}.{order}"
        node_label = self.__class__.__name__ + suffix

        self.value.to_ast(ast, parent_suffix=suffix,
                          order=0, parent=self)
        ast.add_node(self, label=node_label, type=types.t2int["write_var"],
                     carrying_value=self.key)

        if parent is not None:
            ast.add_edge(parent, self, order=order)
