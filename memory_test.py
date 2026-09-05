import gc
import os

from matplotlib import pyplot as plt
import psutil
from tqdm import tqdm
from instruction_language.elements.base import Codeblock, Constant, Term
from instruction_language.elements.conditions import GreaterThan
from instruction_language.elements.control_statements import WhileLoop
from instruction_language.elements.instructions import Read_Var, Write_Pixel, Write_Var
from instruction_language.elements.operators import SUM
from instruction_language.interpreter import InstructionInterpreter
from instruction_language.surroundings.environment import Environment, GEMService
from instruction_language.surroundings.interpreter_settings import GISManager
from tests.pytest_setup import invert_program

settings = GISManager.get("default")

initial_env = Environment.from_list([[0, 0, 0], [0, 1, 0]])


proc = psutil.Process(os.getpid())
memory_usage = []
memory_usage_total = []


codeblock = Codeblock([
    Write_Var("counter", Term(Constant(0))),
    WhileLoop(
        GreaterThan(
            Term(Constant(100)),
            Term(Read_Var("counter"))
        ),
        Codeblock([
            Write_Var("counter", Term(
                SUM(Term(Read_Var("counter")), Term(Constant(None)))))
        ])

    ),
    Write_Pixel("OUTPUT_ENV", Constant(0), Constant(0),
                Term(Read_Var("counter"))),
])

for i in tqdm(range(9000)):
    # gc.collect()
    GEMService.set("INITIAL_ENV", initial_env)
    GEMService.set("OUTPUT_ENV", Environment())

    try:
        interpreter = InstructionInterpreter("this_memory_test_id", settings)
        interpreter.execute(invert_program)
    except Exception as e:
        pass

    # GEMService.print_output_env()
    mem_list_size = memory_usage.__sizeof__() / 1024 / 1024  # size in MB
    mem_total = proc.memory_info().rss / 1024 / 1024
    memory_usage.append(mem_total - mem_list_size)
    memory_usage_total.append(mem_total)

plt.plot(memory_usage, marker='o', label='Memory Usage')
plt.plot(memory_usage_total, marker='x',
         color='red', label='Total Memory Usage')
plt.title("Memory Usage Over Iterations")
plt.xlabel("Iteration")
plt.ylabel("Memory Usage (MB)")
plt.grid(True)
plt.legend()
plt.show()
