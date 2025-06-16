from instruction_language.surroundings.environment import Environment, GEMService, evaluate
from instruction_language.interpreter import InstructionInterpreter

import pytest
from tests.pytest_setup import sample_codeblock


def test_basic_execution(sample_codeblock):

    intial_env = Environment.from_list([[1, 1, 1],
                                        [0, 1, 1]])
    GEMService.set("INITIAL_ENV", intial_env)

    interpreter = InstructionInterpreter(memory_manager_id='hello_word_mm_id')
    interpreter.execute(sample_codeblock)

    expected_output_env = Environment.from_list([[0, 0, 0],
                                                 [1, 0, 0]])

    expected_output_env.plot()
    GEMService.print_output_env()

    equaltity_score = evaluate(GEMService.get(
        "OUTPUT_ENV"), expected_output_env)

    assert equaltity_score == 0
