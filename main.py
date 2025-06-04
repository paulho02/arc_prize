
from matplotlib import pyplot as plt
import networkx as nx
from torch_geometric.utils import from_networkx
from instruction_language.ast_transformer import hierarchy_plot
from instruction_language.elements.base import Codeblock, Term
from instruction_language.elements.conditions import EqualTo, LessThan
from instruction_language.elements.control_statements import If, WhileLoop
from instruction_language.elements.instructions import Read_Pixel, Read_Var, Write_Pixel, Write_Var
from instruction_language.elements.operators import SUM
from instruction_language.interpreter import InstructionInterpreter
import json


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
                                            Term(1),
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

interpreter = InstructionInterpreter(
    initial_env=env_before, output_env=env_rs_2, memory_manager_id='hello_word_mm_id')

interpreter.execute(epoch_2_plan)

interpreter.print_intitial_env()
interpreter.print_output_env()

ast, root = epoch_2_plan.to_ast()

plot_blueprint = hierarchy_plot(ast, root)
labels = nx.get_node_attributes(ast, 'label')
nx.draw(ast, pos=plot_blueprint, labels=labels, with_labels=True, arrows=True)
plt.show()


# print nodes 'json'
#
# nodes_data = [
#     {"id": str(n), "label": d.get("label", ""), "type": d.get(
#         "type", ""), "carrying_value": d.get("carrying_value", None)}
#     for n, d in ast.nodes(data=True)
# ]
# print(json.dumps(nodes_data, indent=2))


# print nodes 'raw'
#
# nodes_data = [
#     {"id": n, **d}
#     for n, d in ast.nodes(data=True)
# ]
# print(nodes_data)

data = from_networkx(ast)
print(data)
