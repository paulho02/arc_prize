from instruction_language.elements.base import Term


class Condition:
    def __init__(self, term1: Term, term2: Term):
        self.term1 = term1
        self.term2 = term2

    def apply(self) -> bool:
        pass


class LessThan(Condition):
    def __init__(self, term1: Term, term2: Term):
        super().__init__(term1, term2)

    def apply(self):
        return self.term1.execute() < self.term2.execute()


class EqualTo(Condition):
    def __init__(self, term1: Term, term2: Term):
        super().__init__(term1, term2)

    def apply(self):
        return (
            self.term1.execute() is self.term2.execute()
            or self.term1.execute() == self.term2.execute()
        )


class GreaterThan(Condition):
    def __init__(self, term1: Term, term2: Term):
        super().__init__(term1, term2)

    def apply(self):
        return self.term1.execute() > self.term2.execute()