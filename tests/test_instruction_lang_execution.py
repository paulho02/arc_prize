from instruction_language.surroundings.environment import Environment, GEMService, evaluate
from instruction_language.interpreter import InstructionInterpreter

import pytest
from tests.pytest_setup import sample_codeblock, sample_codeblock_1_1


def test_basic_execution(sample_codeblock):

    intial_env = Environment.from_list([[1, 1, 1],
                                        [0, 1, 1]])
    GEMService.set("INITIAL_ENV", intial_env)
    GEMService.set("OUTPUT_ENV", Environment())

    interpreter = InstructionInterpreter(memory_manager_id='hello_word_mm_id')
    interpreter.execute(sample_codeblock)

    expected_output_env = Environment.from_list([[0, 0, 0],
                                                 [1, 0, 0]])

    expected_output_env.plot()
    GEMService.print_output_env()

    equaltity_score = evaluate(GEMService.get(
        "OUTPUT_ENV"), expected_output_env)

    assert equaltity_score == 0


def test_basic_execution_1_1(sample_codeblock_1_1):
    GEMService.add_env(0)
    intial_env = Environment.from_list([[1, 1, 1],
                                        [0, 1, 1]])
    print(GEMService._envs)
    GEMService.set(0, intial_env)

    GEMService.add_env(1)

    interpreter = InstructionInterpreter(memory_manager_id='hello_word_mm_id')
    interpreter.execute(sample_codeblock_1_1)

    expected_output_env = Environment.from_list([[0, 0, 0],
                                                 [1, 0, 0]])

    expected_output_env.plot()
    GEMService.print_output_env()

    equaltity_score = evaluate(GEMService.get(
        "OUTPUT_ENV"), expected_output_env)

    assert equaltity_score == 0
