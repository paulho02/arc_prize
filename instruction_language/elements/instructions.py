import os
from instruction_language.elements.base import Executable, Term
from instruction_language.surroundings.environment import GEMService
from instruction_language.surroundings.memory import GMMService
import networkx as nx


class Instruction(Executable):
    def __init__(self):
        pass

    def execute(self):
        pass

    def to_ast(self, ast=None, parent_suffix="", order=0, parent=None):
        pass


class Read_Pixel(Instruction):
    def __init__(self, env_key: str, x: Term, y: Term):
        super().__init__()
        self.env_key = env_key
        self.x = x
        self.y = y

    def execute(self):
        x = self.x.execute()
        y = self.y.execute()
        env = GEMService.get(self.env_key)
        return env.get(x, y)

    def to_ast(self, ast: nx.DiGraph = nx.DiGraph(), parent_suffix: str = "", order: int = 0, parent: str = None):
        """Converts the term to an AST representation."""
        suffix = f"{parent_suffix}.{order}"
        node_label = self.__class__.__name__ + suffix

        ast.add_node(self, label=node_label,
                     type="read_pixel", carrying_value=None)

        self.x.to_ast(ast, parent_suffix=suffix,
                      order=0, parent=self)
        self.y.to_ast(ast, parent_suffix=suffix,
                      order=1, parent=self)

        if parent is not None:
            ast.add_edge(parent, self, order=order)


class Write_Pixel(Instruction):
    def __init__(self, env_key: str, x: Term, y: Term, value: Term):
        super().__init__()
        self.env_key = env_key
        self.x = x
        self.y = y
        self.value = value

    # todo make initial_env write protected

    def execute(self):
        x = self.x.execute()
        y = self.y.execute()
        value = self.value.execute()
        env = GEMService.get(self.env_key)
        env.set(x, y, value)

    def to_ast(self, ast: nx.DiGraph = nx.DiGraph(), parent_suffix: str = "", order: int = 0, parent: str = None):
        """Converts the term to an AST representation."""
        suffix = f"{parent_suffix}.{order}"
        node_label = self.__class__.__name__ + suffix

        ast.add_node(self, label=node_label,
                     type="write_pixel", carrying_value=None)

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
        self.key = key

    def execute(self):
        namespace_id = os.environ.get("CURRENT_NAMESPACE_ID")
        return GMMService.get().get_var(namespace_id, self.key)

    def to_ast(self, ast: nx.DiGraph = nx.DiGraph(), parent_suffix: str = "", order: int = 0, parent: str = None):
        """Converts the term to an AST representation."""
        suffix = f"{parent_suffix}.{order}"
        node_label = self.__class__.__name__ + suffix

        ast.add_node(self, label=node_label, type="read_var",
                     carrying_value=self.key)

        if parent is not None:
            ast.add_edge(parent, self, order=order)


class Write_Var(Instruction):
    def __init__(self, key, value: Term):
        super().__init__()
        self.key = key
        self.value = value

    def execute(self):
        namespace_id = os.environ.get("CURRENT_NAMESPACE_ID")
        return GMMService.get().set_var(namespace_id, self.key, self.value.execute())

    def to_ast(self, ast: nx.DiGraph = nx.DiGraph(), parent_suffix: str = "", order: int = 0, parent: str = None):
        """Converts the term to an AST representation."""
        suffix = f"{parent_suffix}.{order}"
        node_label = self.__class__.__name__ + suffix

        self.value.to_ast(ast, parent_suffix=suffix,
                          order=0, parent=self)
        ast.add_node(self, label=node_label, type="write_var",
                     carrying_value=self.key)

        if parent is not None:
            ast.add_edge(parent, self, order=order)
