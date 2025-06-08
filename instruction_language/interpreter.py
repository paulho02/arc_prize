
import os
from instruction_language.elements.base import Codeblock
from instruction_language.surroundings.environment import GEMService
from instruction_language.surroundings.memory import GMMService


class InstructionInterpreter():
    def __init__(self, memory_manager_id):
        self.memory_manager_id = memory_manager_id

    def execute(self, code: Codeblock, reset_vars: bool = True):
        os.environ["MEMORY_MANAGER_ID"] = self.memory_manager_id

        code.execute()

        # post execution clean
        # GEMService.reset_all_envs()
        # todo reset env logic required
        GMMService.delete()
        del os.environ["MEMORY_MANAGER_ID"]
        del os.environ["CURRENT_NAMESPACE_ID"]

    def _print_var_storage(self, vars: dict):
        print("------------------")
        print("Var storage:")
        for key, var in vars.items():
            print(f"{key} = {var}")
        print("------------------")
