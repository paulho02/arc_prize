# rule: invert pixels

from instruction_language.elements.base import Codeblock
from instruction_language.elements.control_statements import If
from instruction_language.interpreter import InstructionInterpreter

from eval import evaluate


while_loops = 2
if_statements = 1

riddle_env = [
    [0, 1, 1],
    [0, 1, 1],
]

expexted_solution_env = [
    [1, 0, 0],
    [1, 0, 0],
]

actual_solution_env = []


deviation_score = evaluate(env1, env2)
print(deviation_score)

plan = Codeblock()

def write_code():
    before_deviation_score = evaluate(env_before, env_rs_2)


code = Codeblock()
code.execution_plan = [
    If(),
    
]