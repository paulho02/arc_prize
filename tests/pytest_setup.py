import pytest
from instruction_language.elements.operators import SUM
from instruction_language.elements.instructions import Read_Pixel, Read_Var, Write_Pixel, Write_Var
from instruction_language.elements.control_statements import If, WhileLoop
from instruction_language.elements.conditions import EqualTo, LessThan
from instruction_language.elements.base import Codeblock, Term
from instruction_language.ast_transformer import hierarchy_plot
from torch_geometric.utils import from_networkx


# todo introduce system variables (like envs size, etc ..)
invert_program = Codeblock()
invert_program.execution_plan = [
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
                                            "OUTPUT_ENV",
                                            Term(Read_Var("current_x")),
                                            Term(Read_Var("current_y")),
                                            Term(1),
                                        )
                                    ]
                                ),
                                (
                                    EqualTo(
                                        Term(
                                            Read_Pixel(
                                                "INITIAL_ENV",
                                                Read_Var("current_x"),
                                                Read_Var("current_y"),
                                            )
                                        ),
                                        Term(1),
                                    ),
                                    Codeblock(
                                        [
                                            Write_Pixel(
                                                "OUTPUT_ENV",
                                                Read_Var("current_x"),
                                                Read_Var("current_y"),
                                                Term(0),
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


@pytest.fixture(scope="session")
def sample_codeblock() -> Codeblock:
    """a small program that should invert every pixel from the initial environment and write it to the output environment """

    return invert_program


invert_program_1_1 = Codeblock()
# Environment map:
# 0 = INITIAL_ENV
# 1 = OUTPUT_ENV

# Memory map:
# 0 = current_x
# 1 = current_y
# 2 = env_size_x
# 3 = env_size_y
invert_program_1_1.execution_plan = [
    Write_Var(3, Term(2)),
    Write_Var(4, Term(3)),
    Write_Var(0, Term(0)),
    Write_Var(1, Term(0)),
    WhileLoop(
        LessThan(
            Term(Read_Var(0)),
            Term(Read_Var(3)),
        ),
        Codeblock(
            [
                WhileLoop(
                    LessThan(
                        Term(Read_Var(1)),
                        Term(Read_Var(4)),
                    ),
                    Codeblock(
                        [
                            If(
                                Codeblock(
                                    [
                                        Write_Pixel(
                                            1,
                                            Term(Read_Var(0)),
                                            Term(Read_Var(1)),
                                            Term(1),
                                        )
                                    ]
                                ),
                                (
                                    EqualTo(
                                        Term(
                                            Read_Pixel(
                                                1,
                                                Read_Var(0),
                                                Read_Var(1),
                                            )
                                        ),
                                        Term(1),
                                    ),
                                    Codeblock(
                                        [
                                            Write_Pixel(
                                                1,
                                                Read_Var(0),
                                                Read_Var(1),
                                                Term(0),
                                            )
                                        ]
                                    ),
                                ),
                            ),
                            Write_Var(
                                1,
                                Term(
                                    SUM(Term(Read_Var(1)), Term(1))
                                ),
                            ),
                        ]
                    ),
                ),
                Write_Var(
                    0,
                    Term(SUM(Term(Read_Var(0)), Term(1))),
                ),
                Write_Var(1, Term(0)),
            ]
        ),
    ),
]


@pytest.fixture(scope="session")
def sample_codeblock_1_1() -> Codeblock:
    ''' same as sample_codeblock but with storage adresses instead of string keys '''
    return invert_program_1_1
