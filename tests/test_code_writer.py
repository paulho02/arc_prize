import pytest
from instruction_language.elements.base import Codeblock, Term
from instruction_language.interpreter import InstructionInterpreter
from instruction_language.surroundings.environment import Environment, GEMService
from tests.pytest_setup import sample_codeblock
import code_writer


# todo add more tests for each node type

def test_simple_new_node():
    """Code writer should create a program that writes a pixel at (0, 0) with value 1"""
    GEMService.set("INITIAL_ENV", Environment())

    codeblock = Codeblock()
    codeblock.execution_plan = []

    write_pixel = code_writer.new_node(
        parent=codeblock,
        node_type="write_pixel",
        order=0,
        carrying_value="OUTPUT_ENV"
    )

    code_writer.new_node(
        parent=write_pixel,
        node_type="term",
        order=0,
        carrying_value=1
    )

    code_writer.new_node(
        parent=write_pixel,
        node_type="term",
        order=1,
        carrying_value=0
    )

    code_writer.new_node(
        parent=write_pixel,
        node_type="term",
        order=2,
        carrying_value=0
    )

    interpreter = InstructionInterpreter(__file__)
    interpreter.execute(codeblock)

    output_env = GEMService.get_output_env()
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
    assert term.term is None

    child_term = code_writer.new_node(
        parent=term,
        node_type="term",
        order=0,
        carrying_value=2
    )

    assert isinstance(term.term, Term)
    assert term.term == child_term

    code_writer.delete_node(term, order=0)
    assert term.term is None
