import os
from instruction_language.elements.base import Executable, Term
from instruction_language.surroundings.memory import GMMService


class Instruction(Executable):
    def __init__(self):
        pass

    def execute(self):
        pass


class Read_Pixel(Instruction):
    def __init__(self, env, x: Term, y: Term):
        super().__init__()
        self.env = env
        self.x = x
        self.y = y

    def execute(self):
        x = self.x.execute()
        y = self.y.execute()

        try:
            return self.env[x][y]
        except IndexError:
            return None


class Write_Pixel(Instruction):
    def __init__(self, env, x: Term, y: Term, value):
        super().__init__()
        self.env = env
        self.x = x
        self.y = y
        self.value = value

    def execute(self):
        x = self.x.execute()
        y = self.y.execute()

        while len(self.env) <= x:
            self.env.append([])

        while len(self.env[x]) <= y:
            self.env[x].append(0)

        # Write pixel value
        self.env[x][y] = self.value


class Read_Var(Instruction):
    def __init__(self, key):
        super().__init__()
        self.key = key

    def execute(self):
        namespace_id = os.environ.get("CURRENT_NAMESPACE_ID")
        return GMMService.get().get_var(namespace_id, self.key)


class Write_Var(Instruction):
    def __init__(self, key, value:Term):
        super().__init__()
        self.key = key
        self.value = value

    def execute(self):
        namespace_id = os.environ.get("CURRENT_NAMESPACE_ID")
        return GMMService.get().set_var(namespace_id, self.key, self.value.execute())

