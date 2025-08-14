from instruction_language.elements.base import Codeblock, Constant, Term
from instruction_language.elements.conditions import Condition, EqualTo
from instruction_language.elements.control_statements import WhileLoop
from instruction_language.elements.instructions import Read_Var, Write_Pixel, Write_Var
from instruction_language.elements.operators import SUM
from instruction_language.surroundings.environment import Environment, GEMService, evaluate
from instruction_language.interpreter import InstructionInterpreter

import pytest
from instruction_language.surroundings.interpreter_settings import GISManager
from tests.pytest_setup import sample_codeblock, sample_codeblock_1_1


def test_basic_execution(sample_codeblock):

    initial_env = Environment.from_list([[1, 1, 1],
                                        [0, 1, 1]])
    GEMService.set("INITIAL_ENV", initial_env)
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
    initial_env = Environment.from_list([[1, 1, 1],
                                        [0, 1, 1]])
    print(GEMService._envs)
    GEMService.set("INITIAL_ENV", initial_env)

    interpreter = InstructionInterpreter(memory_manager_id='hello_word_mm_id')
    interpreter.execute(sample_codeblock_1_1)

    expected_output_env = Environment.from_list([[0, 0, 0],
                                                 [1, 0, 0]])

    expected_output_env.plot()
    GEMService.print_output_env()

    equaltity_score = evaluate(GEMService.get(
        "OUTPUT_ENV"), expected_output_env)

    assert equaltity_score == 0


def test_interpreter_locking():
    # todo implement
    pass


def test_max_loop_iterations_setting():
    test_settings = GISManager.get("default")
    test_settings["max_loop_iterations"] = 5

    interpreter = InstructionInterpreter(
        memory_manager_id='test_mm_id', settings=test_settings)

    GEMService.add_env("test_max_loop_iterations_setting")

    codeblock = Codeblock(execution_plan=[
        Write_Var("counter", Constant(0)),
        WhileLoop(
            EqualTo(Term(Constant(1)), Term(Constant(1))),
            Codeblock([
                Write_Var(
                    "counter",
                    Term(SUM(
                        Term(Constant(1)),
                        Term(Read_Var("counter"))
                    )),
                ),
                Write_Pixel(
                    "test_max_loop_iterations_setting",
                    Constant(0),
                    Constant(0),
                    Term(Read_Var("counter"))
                )
            ])
        )
    ])

    try:
        interpreter.execute(codeblock)
    except RuntimeError as e:
        assert str(
            e) == "Max loop iterations reached: 5. Consider adjusting the 'max_loop_iterations' setting."

    assert test_settings["max_loop_iterations"] == GEMService.get(
        "test_max_loop_iterations_setting").get(0, 0)
