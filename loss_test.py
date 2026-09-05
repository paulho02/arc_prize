import code_writer
from instruction_language.interpreter import InstructionInterpreter
from instruction_language.surroundings.environment import Environment, GEMService
from instruction_language.surroundings.interpreter_settings import GISManager
import torch.nn as nn
from tests.pytest_setup import invert_program

loss_fn = nn.MSELoss()

settings = GISManager.get("default")
GEMService.set("INITIAL_ENV", Environment.from_list([[0, 0, 0],
                                                     [1, 1, 1]]))

GEMService.add_env("EXP_OUTPUT_ENV")
expected_output_env = Environment.from_list([[1, 1, 1],
                                            [0, 0, 0]])
GEMService.set("EXP_OUTPUT_ENV", expected_output_env)


GEMService.print_output_env()

# interpreter = InstructionInterpreter(settings)
# interpreter.execute(invert_program)

reward, _ = code_writer.evaluate(invert_program, [])

loss = loss_fn(pred_score, reward)
print("------------------------")
print()
print()
print("--- program executed ---")
print()
print()
print("------------------------")

print(f"reward: {reward}")
GEMService.print_output_env()
