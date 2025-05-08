from abc import ABC, abstractmethod
import os

from instruction_language.surroundings.memory import GMMService

class Executable(ABC):
    @abstractmethod
    def execute(self):
        pass

class Term(Executable):
    def __init__(self, term):
        self.term = term

    def execute(self):
        try:
            return self.term.execute()
        except AttributeError as e:
            return self.term

class Codeblock(Executable):
    def __init__(self, execution_plan: list[Executable] = []):
        self.execution_plan: list[Executable] = execution_plan

    def execute(self):
        mm = GMMService.get()
        os.environ["CURRENT_NAMESPACE_ID"] = mm.new_namespace()

        for i, step in enumerate(self.execution_plan):
            try:
                step.execute()
            except Exception as e:
                print(f"Exception in step {i} (step type: {type(step)})")
                raise e
