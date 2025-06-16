from typing import Literal, Union
from instruction_language.elements.base import Codeblock, Executable, Term
from instruction_language.elements.conditions import EqualTo, GreaterThan, LessThan
from instruction_language.elements.instructions import Read_Pixel, Read_Var, Write_Pixel, Write_Var
from instruction_language.elements.operators import SUM
from instruction_language.elements.control_statements import If, WhileLoop

n_types = Literal["term", "codeblock",
                  "read_var", "write_var", "read_pixel", "write_pixel",
                  "egual_to", "greater_than", "less_than",
                  "sum"
                  "if", "while"]


class CodeWriter:
    def __init__(self, codeblock: Codeblock = Codeblock()):
        self.codeblock = codeblock

    # todo the ai may not be able to handle string types well for 'carrying_value', so maybe i need to implement storage addresses or string to int mapping
    def new_node(self, parent: Executable, node_type: n_types, order: int, carrying_value: Union[any, None] = None) -> Executable:
        """Creates a new node in the code block."""

        if node_type == "term":
            new_node = Term(carrying_value)
        elif node_type == "codeblock":
            new_node = Codeblock([])
        elif node_type == "read_var":
            new_node = Read_Var(carrying_value)
        elif node_type == "write_var":
            new_node = Write_Var(carrying_value, None)
        elif node_type == "read_pixel":
            new_node = Read_Pixel(carrying_value, None, None)
        elif node_type == "write_pixel":
            new_node = Write_Pixel(carrying_value, None, None, None)
        elif node_type == "egual_to":
            new_node = EqualTo(None, None)
        elif node_type == "greater_than":
            new_node = GreaterThan(None, None)
        elif node_type == "less_than":
            new_node = LessThan(None, None)
        elif node_type == "sum":
            new_node = SUM(None, None)
        elif node_type == "if":
            new_node = If(None)
        elif node_type == "while":
            new_node = WhileLoop(None, None)
        else:
            raise ValueError(
                f"Unknown node type: {node_type}. Type must be one of {n_types}.")

        # parent.add_child
