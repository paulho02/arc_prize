
from instruction_language.elements.base import Codeblock, Term
from instruction_language.elements.conditions import EqualTo, LessThan
from instruction_language.elements.control_statements import If, WhileLoop
from instruction_language.elements.instructions import Read_Pixel, Read_Var, Write_Pixel, Write_Var
from instruction_language.elements.operators import SUM
from instruction_language.interpreter import InstructionInterpreter


env_before = [[0, 1, 1], 
              [0, 1, 1]]





# todo introduce system variables (like envs size, etc ..)

# todo outsource output env in interpreter class
env_rs_2 = []
epoch_2_plan = Codeblock()
epoch_2_plan.execution_plan = [
    Write_Var("env_size_x", Term(2)),
    Write_Var("env_size_y", Term(3)),
    Write_Var("current_x", Term(0)),
    Write_Var("current_y", Term(0)),
    WhileLoop(
        LessThan(
            Term(Read_Var("current_x")),
            Term(Read_Var("env_size_x")),
        ),
        Codeblock(
            [
                WhileLoop(
                    LessThan(
                        Term(Read_Var("current_y")),
                        Term(Read_Var("env_size_y")),
                    ),
                    Codeblock(
                        [
                            If(
                                Codeblock(
                                    [
                                        Write_Pixel(
                                            env_rs_2,
                                            Term(Read_Var("current_x")),
                                            Term(Read_Var("current_y")),
                                            1,
                                        )
                                    ]
                                ),
                                (
                                    EqualTo(
                                        Term(
                                            Read_Pixel(
                                                env_before,
                                                Read_Var("current_x"),
                                                Read_Var("current_y"),
                                            )
                                        ),
                                        Term(1),
                                    ),
                                    Codeblock(
                                        [
                                            Write_Pixel(
                                                env_rs_2,
                                                Read_Var("current_x"),
                                                Read_Var("current_y"),
                                                0,
                                            )
                                        ]
                                    ),
                                ),
                            ),
                            Write_Var(
                                "current_y",
                                Term(
                                    SUM(Term(Read_Var("current_y")), Term(1))
                                ),
                            ),
                        ]
                    ),
                ),
                Write_Var(
                    "current_x",
                    Term(SUM(Term(Read_Var("current_x")), Term(1))),
                ),
                Write_Var("current_y", Term(0)),
            ]
        ),
    ),
]

interpreter = InstructionInterpreter(initial_env=env_before, output_env=env_rs_2, memory_manager_id='hello_word_mm_id')

interpreter.execute(epoch_2_plan)

interpreter.print_intitial_env()
interpreter.print_output_env()