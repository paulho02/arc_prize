from instruction_language.elements.base import Executable, Term


class Operator(Executable):
    def __init__(self, term1:Term, term2:Term):
        pass

    def execute(self):
        pass


class SUM(Operator):
    def __init__(self, term1: Term, term2: Term):
        super().__init__(term1, term2)

        self.term1 = term1
        self.term2 = term2

    def execute(self):
        return self.term1.execute() + self.term2.execute()


# todo implement further operators