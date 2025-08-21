
from concurrent.futures import ThreadPoolExecutor
import os
from typing import Any, Union
from instruction_language.elements.base import Codeblock
from instruction_language.surroundings.environment import GEMService
from instruction_language.surroundings.interpreter_settings import GISManager
from instruction_language.surroundings.memory import MemoryManager


class InstructionInterpreter():
    def __init__(self, settings: Union[dict[str, Any], None] = None):
        settings = settings if settings is not None else GISManager.get(
            "default")
        GISManager.set(self, settings)

    def execute(self, code: Codeblock, reset_vars: bool = True):
        GISManager.interpreter_lock(self)

        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(code.execute)
                timeout = GISManager.get_setting("max_run_time_seconds")
                future.result(timeout=timeout)
        finally:
            # post execution clean
            # GEMService.reset_all_envs()
            # todo reset env logic required
            MemoryManager.reset()
            GISManager.release_interpreter_lock(self)

    def _print_var_storage(self, vars: dict):
        print("------------------")
        print("Var storage:")
        for key, var in vars.items():
            print(f"{key} = {var}")
        print("------------------")
