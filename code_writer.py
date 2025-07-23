from typing import Literal, Union
from instruction_language.elements.base import Codeblock, Constant, Executable, NoneType, Term
from instruction_language.elements.conditions import Condition, EqualTo, GreaterThan, LessThan
from instruction_language.elements.instructions import Read_Pixel, Read_Var, Write_Pixel, Write_Var
from instruction_language.elements.operators import SUM, Operator
from instruction_language.elements.control_statements import If, WhileLoop
from instruction_language.interpreter import InstructionInterpreter
from instruction_language.surroundings.environment import Environment, GEMService
from instruction_language.surroundings.environment import evaluate as env_evaluate
import instruction_language.elements.types as types  # import n_types, all_types


def get_action_space(codeblock: Codeblock) -> list[tuple]:
    ast, root = codeblock.to_ast()

    action_space = []

    # Helper to get children from the networkx graph
    def get_children(graph, node):
        return list(graph.successors(node))

    def traverse(graph, node, order=None):

        if isinstance(node, Codeblock):
            order = len(node.execution_plan)
            for n_type in types.not_none_types:
                action_space.append((node, n_type, order))
        elif isinstance(node, Term):
            for n_type in types.not_none_types:
                action_space.append((node, n_type, 0))
        elif isinstance(node, NoneType):
            # NoneType nodes cannot have children
            pass
        elif isinstance(node, Constant):
            # Constant nodes cannot have children
            pass
        elif isinstance(node, Read_Var):
            # Read_Var cannot have children
            pass
        elif isinstance(node, Write_Var):
            action_space.append((node, "term", 0))
        elif isinstance(node, Read_Pixel):
            action_space.append((node, "term", 0))
            action_space.append((node, "term", 1))
        elif isinstance(node, Write_Pixel):
            action_space.append((node, "term", 0))
            action_space.append((node, "term", 1))
            action_space.append((node, "term", 2))
        elif isinstance(node, (Condition, Operator)):
            action_space.append((node, "term", 0))
            action_space.append((node, "term", 1))
        elif isinstance(node, If):
            action_space.append((node, "codeblock", 0))
            for i in range(len(node.condition_code_plan) + 1):
                for n_type in types.condition_types:
                    action_space.append((node, n_type, i))
                action_space.append((node, "codeblock", i + 1))
        elif isinstance(node, WhileLoop):
            action_space.append((node, "codeblock", 0))
            for n_type in types.condition_types:
                action_space.append((node, n_type, 0))
        else:
            raise TypeError(
                f"Unsupported node type: {type(node)}.")

        children = get_children(graph, node)
        for idx, child in enumerate(children):
            traverse(graph, child, idx)

    traverse(ast, root)
    return action_space

# todo the ai may not be able to handle string types well for 'carrying_value', so maybe i need to implement storage addresses or string to int mapping


def new_node(parent: Executable, node_type: types.n_types, order: int, carrying_value: Union[str, int, None] = None) -> Executable:
    """Creates a new node in the code block."""

    if node_type == "none_type":
        raise ValueError("Creation of 'none_type' nodes is not allowed.")
    elif node_type == "term":
        if not isinstance(carrying_value, Union[int, None]):
            raise TypeError(
                f"carrying_value must be an int for node type 'term', got {type(carrying_value)}")
        new_node = Term(NoneType())

    elif node_type == "constant":
        if not isinstance(carrying_value, Union[int, str, None]):
            raise TypeError(
                f"carrying_value must be an int or str for node type 'constant', got {type(carrying_value)}")
        new_node = Constant(carrying_value)

    elif node_type == "codeblock":
        new_node = Codeblock([])

    elif node_type == "read_var":
        # todo make carrying_value of type int
        if not isinstance(carrying_value, Union[str, None]):
            raise TypeError(
                f"carrying_value must be an str for node type 'read_var', got {type(carrying_value)}")
        new_node = Read_Var(carrying_value)

    elif node_type == "write_var":
        if not isinstance(carrying_value, Union[str, None]):
            raise TypeError(
                f"carrying_value must be an str for node type 'write_var', got {type(carrying_value)}")
        new_node = Write_Var(carrying_value, NoneType())

    elif node_type == "read_pixel":
        if not isinstance(carrying_value, Union[str, None]):
            raise TypeError(
                f"carrying_value must be an str for node type 'read_pixel', got {type(carrying_value)}")
        new_node = Read_Pixel(carrying_value, NoneType(), NoneType())

    elif node_type == "write_pixel":
        if not isinstance(carrying_value, Union[str, None]):
            raise TypeError(
                f"carrying_value must be an str for node type 'write_pixel', got {type(carrying_value)}")
        new_node = Write_Pixel(
            carrying_value, NoneType(), NoneType(), NoneType())

    elif node_type == "equal_to":
        new_node = EqualTo(NoneType(), NoneType())

    elif node_type == "greater_than":
        new_node = GreaterThan(NoneType(), NoneType())

    elif node_type == "less_than":
        new_node = LessThan(NoneType(), NoneType())

    elif node_type == "sum":
        new_node = SUM(NoneType(), NoneType())

    elif node_type == "if":
        new_node = If(Codeblock([]))

    elif node_type == "while":
        new_node = WhileLoop(NoneType(), Codeblock([]))

    else:
        raise ValueError(
            f"Unknown node type: {node_type}. Type must be one of {n_types}.")

    parent.add_child(new_node, order)
    return new_node


def delete_node(parent: Executable, order: int) -> None:
    parent.delete_child(order)


def determine_incomplete_nodes(root: Codeblock) -> list[Executable]:
    # todo maybe implement later, when learning is too difficult/slow

    raise NotImplementedError(
        "This function is not implemented yet.")
    pass


def evaluate(codeblock: Codeblock) -> float:
    # todo make function more generic
    """Evaluates the code block and returns a reward based on the output environment."""
    interpreter = InstructionInterpreter("code_writer_memory_manager_id")

    intial_env = Environment.from_list([[1, 1],
                                        [0, 1]])
    GEMService.set(0, intial_env)
    output_env = Environment()
    GEMService.set(1, output_env)

    try:
        interpreter.execute(codeblock)
        deviation = env_evaluate(GEMService.get(
            1), GEMService.get("EXP_OUTPUT_ENV"))
        # Sqaured deviation to penalize larger deviations more heavily and guarantee non-negative values
        deviation = deviation ^ 2

        deviation_score = 100 - deviation  # Higher is better, so we subtract from 100
        deviation_score = max(0, deviation_score)  # Ensure non-negative
        reward = deviation_score / 100  # Normalize to [0, 1]
        return float(reward)

    except Exception as e:
        print(
            f"[code_writer] Error during execution: {e} || -> return min reward")
        return 0.0
