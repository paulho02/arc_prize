
import os
from instruction_language.elements.base import Codeblock
from instruction_language.surroundings.memory import GMMService


class InstructionInterpreter():
    def __init__(self, initial_env:list[list], output_env:list, memory_manager_id):
        self.initial_env = initial_env
        self._output_env = output_env
        self.memory_manager_id = memory_manager_id

    def execute(self, code: Codeblock, reset_vars:bool = True):
        os.environ["MEMORY_MANAGER_ID"] = self.memory_manager_id
        
        code.execute()

        # post execution clean
        GMMService.delete()
        del os.environ["MEMORY_MANAGER_ID"]
        del os.environ["CURRENT_NAMESPACE_ID"]



    def print_intitial_env(self):
        self._print_env(self.initial_env, "initial_env")

    def print_output_env(self):
        self._print_env(self._output_env, "output_env")
    
    def _print_env(self, env: list[list[int]], env_name):
        print("------------------")
        print(f"Env '{env_name}':")
        for row in env:
            for col in row:
                print(f" {col} ", end="")
            print()
        print("------------------")


    def _print_var_storage(self, vars: dict):
        print("------------------")
        print("Var storage:")
        for key, var in vars.items():
            print(f"{key} = {var}")
        print("------------------")