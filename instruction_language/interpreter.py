
import os
from typing import Any, Union
from instruction_language.elements.base import Codeblock
from instruction_language.surroundings.environment import GEMService
from instruction_language.surroundings.interpreter_settings import GISManager
from instruction_language.surroundings.memory import GMMService


class InstructionInterpreter():
    def __init__(self, memory_manager_id, settings: Union[dict[str, Any], None] = None):
        self.memory_manager_id = memory_manager_id
        settings = settings if settings is not None else GISManager.get(
            "default")
        GISManager.set(self, settings)

    def execute(self, code: Codeblock, reset_vars: bool = True):
        GISManager.interpreter_lock(self)
        os.environ["MEMORY_MANAGER_ID"] = self.memory_manager_id

        try:
            code.execute()
        finally:
            # post execution clean
            # GEMService.reset_all_envs()
            # todo reset env logic required
            GMMService.delete()
            del os.environ["MEMORY_MANAGER_ID"]
            del os.environ["CURRENT_NAMESPACE_ID"]
            GISManager.release_interpreter_lock(self)

    def _print_var_storage(self, vars: dict):
        print("------------------")
        print("Var storage:")
        for key, var in vars.items():
            print(f"{key} = {var}")
        print("------------------")
