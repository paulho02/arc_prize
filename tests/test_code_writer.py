from typing import Literal
import pytest
from instruction_language.elements.base import Codeblock, NoneType, Term
from instruction_language.interpreter import InstructionInterpreter
from instruction_language.surroundings.environment import Environment, GEMService
from tests.pytest_setup import sample_codeblock
import code_writer


# todo add more tests for each node type

def test_simple_new_node():
    """Code writer should create a program that writes a pixel at (0, 0) with value 1"""

    # env '0' represents INPUT_ENV
    # env '1' represents OUTPUT_ENV
    GEMService.add_env(0)
    GEMService.add_env(1)

    GEMService.set(0, Environment())

    codeblock = Codeblock()
    codeblock.execution_plan = []

    write_pixel = code_writer.new_node(
        parent=codeblock,
        node_type="write_pixel_output",
        order=0,
    )

    code_writer.new_node(
        parent=write_pixel,
        node_type="constant",
        order=0,
        carrying_value=1
    )

    code_writer.new_node(
        parent=write_pixel,
        node_type="constant",
        order=1,
        carrying_value=0
    )

    code_writer.new_node(
        parent=write_pixel,
        node_type="constant",
        order=2,
        carrying_value=0
    )

    interpreter = InstructionInterpreter()
    interpreter.execute(codeblock)

    output_env = GEMService.get("OUTPUT_ENV")
    assert output_env.get(0, 0) == 1


def test_simple_node_deletion():
    """Code writer should delete a child node """
    GEMService.set("INITIAL_ENV", Environment())

    codeblock = Codeblock()
    codeblock.execution_plan = []

    term = code_writer.new_node(
        parent=codeblock,
        node_type="term",
        order=0
    )

    assert isinstance(term, Term)
    assert isinstance(term.child, NoneType)

    child_term = code_writer.new_node(
        parent=term,
        node_type="term",
        order=0,
        carrying_value=2
    )

    assert isinstance(term.child, Term)
    assert term.child == child_term

    code_writer.delete_node(term, order=0)
    assert isinstance(term.child, NoneType)


def test_get_action_space(sample_codeblock):
    """Code writer should return the correct action space for a given code block"""
    action_space = code_writer.get_action_space(sample_codeblock)

    assert len(action_space) > 0
    assert all(isinstance(action, tuple) and len(
        action) == 3 for action in action_space)

    # test first level of action space (note: this covers not the entire action space!)
    assert (
        (sample_codeblock, "term", len(sample_codeblock.execution_plan)) in action_space and
        (sample_codeblock, "codeblock", len(sample_codeblock.execution_plan)) in action_space and
        (sample_codeblock, "read_var", len(sample_codeblock.execution_plan)) in action_space and
        (sample_codeblock, "write_var", len(sample_codeblock.execution_plan)) in action_space and
        (sample_codeblock, "read_pixel_input", len(sample_codeblock.execution_plan)) in action_space and
        (sample_codeblock, "read_pixel_output", len(sample_codeblock.execution_plan)) in action_space and
        (sample_codeblock, "write_pixel_output", len(sample_codeblock.execution_plan)) in action_space and
        (sample_codeblock, "equal_to", len(sample_codeblock.execution_plan)) in action_space and
        (sample_codeblock, "greater_than", len(sample_codeblock.execution_plan)) in action_space and
        (sample_codeblock, "less_than", len(sample_codeblock.execution_plan)) in action_space and
        (sample_codeblock, "sum", len(sample_codeblock.execution_plan)) in action_space and
        (sample_codeblock, "if", len(sample_codeblock.execution_plan)) in action_space and
        (sample_codeblock, "while", len(
            sample_codeblock.execution_plan)) in action_space
    )

    print(action_space)
    print(len(action_space))
