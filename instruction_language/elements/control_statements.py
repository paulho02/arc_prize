from instruction_language.elements.base import Codeblock, Executable
from  instruction_language.elements.conditions import Condition


class ControlFlowStatement(Executable):
    def __init__(self):
        pass

    def execute(self):
        pass

class If(ControlFlowStatement):
    def __init__(self, default: Codeblock, *args: tuple[Condition, Codeblock]):
        super().__init__()
        self.default = default
        self.condition_code_plan = list(args)

    def execute(self):
        for condition, codeblock in self.condition_code_plan:
            if condition.apply():
                codeblock.execute()
                return

        self.default.execute()
        return


class WhileLoop(ControlFlowStatement):
    def __init__(self, condition: Condition, codeblock: Codeblock):
        super().__init__()
        self.condition = condition
        self.codeblock = codeblock

    def execute(self):
        while self.condition.apply():
            self.codeblock.execute()