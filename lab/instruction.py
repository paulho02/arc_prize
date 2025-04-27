from abc import ABC, abstractmethod
from typing import Callable

# TODO
# TODO aktuell gobales variable system!!
# ggf aendern, sodass codeblock den "pointer" aktuellen var store managed


# abstract elements ############################


class Executable(ABC):
    @abstractmethod
    def execute(self):
        pass


# todo revise term (maybe replace with CONSTANT instruction, etc)
class Term(Executable):
    def __init__(self, term):
        self.term = term

    def execute(self):
        try:
            return self.term.execute()
        except AttributeError as e:
            return self.term


class Instruction(Executable):
    def __init__(self):
        pass

    def execute(self):
        pass


class Operator(Executable):
    def __init__(self, term1, term2):
        # todo add Var class, etc..
        # if type(term1) != type(term2):
        #     raise TypeError("Operator terms must be of same type.")
        pass

    def execute(self):
        pass


class Condition:
    def __init__(self, term1: Term, term2: Term):
        self.term1 = term1
        self.term2 = term2

    def apply(self) -> bool:
        pass


class ControlFlowStatement(Executable):
    def __init__(self):
        pass

    def execute(self):
        pass


class Function:
    pass


class Codeblock(Executable):
    def __init__(self, execution_plan: list[Executable] = []):
        self.execution_plan: list[Executable] = execution_plan

    def execute(self):
        for i, step in enumerate(self.execution_plan):
            try:
                step.execute()
            except Exception as e:
                print(f"Exception in step {i} (step type: {type(step)})")
                raise e


##################################################


# set of atomic instructions #####################
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
    def __init__(self, storage, key):
        super().__init__()
        self.storage = storage
        self.key = key

    def execute(self):
        if self.key not in self.storage:
            return None

        return self.storage[self.key]


class Write_Var(Instruction):
    def __init__(self, storage, key, value:Term):
        super().__init__()
        self.storage = storage
        self.key = key
        self.value = value

    def execute(self):
        self.storage[self.key] = self.value.execute()
        return


##################################################


# set of atomic operators ########################


class SUM(Operator):
    def __init__(self, term1: Term, term2: Term):
        super().__init__(term1, term2)

        self.term1 = term1
        self.term2 = term2

    def execute(self):
        return self.term1.execute() + self.term2.execute()


# todo implement further operators


##################################################


# set of atomic conditions #######################
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


##################################################

# set of atomic flow control statements ##########


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


##################################################


def print_env(env: list[list[int]], env_name):
    print("------------------")
    print(f"Env '{env_name}':")
    for row in env:
        for col in row:
            print(f" {col} ", end="")
        print()
    print("------------------")


def print_var_storage(vars: dict):
    print("------------------")
    print("Var storage:")
    for key, var in vars.items():
        print(f"{key} = {var}")
    print("------------------")


inital_env = {}
result_env = {}


# Ev1        Ev2

# 0 0  -->   1 1
# 0 1        1 0

# 1 1  -->   0 0
# 0 0        1 1

env_before = [[0, 1, 1], 
              [0, 0, 1]]
print_env(env_before, "env_before")

env_rs_1 = []
epoch_1_plan = Codeblock()
epoch_1_plan.execution_plan = [
    Write_Pixel(env_rs_1, Term(0), Term(0), 1),
    Write_Pixel(env_rs_1, Term(0), Term(1), 0),
    Write_Pixel(env_rs_1, Term(1), Term(0), 1),
    Write_Pixel(env_rs_1, Term(1), Term(1), 1)
]
epoch_1_plan.execute()
print_env(env_rs_1, "env_rs_1")


# todo introduce system variables (like envs size, etc ..)

env_rs_2 = []
vars_rs_2 = {}
epoch_2_plan = Codeblock()
epoch_2_plan.execution_plan = [
    Write_Var(vars_rs_2, "env_size_x", Term(2)),
    Write_Var(vars_rs_2, "env_size_y", Term(3)),
    Write_Var(vars_rs_2, "current_x", Term(0)),
    Write_Var(vars_rs_2, "current_y", Term(0)),
    WhileLoop(
        LessThan(
            Term(Read_Var(vars_rs_2, "current_x")),
            Term(Read_Var(vars_rs_2, "env_size_x")),
        ),
        Codeblock(
            [
                WhileLoop(
                    LessThan(
                        Term(Read_Var(vars_rs_2, "current_y")),
                        Term(Read_Var(vars_rs_2, "env_size_y")),
                    ),
                    Codeblock(
                        [
                            If(
                                Codeblock(
                                    [
                                        Write_Pixel(
                                            env_rs_2,
                                            Term(Read_Var(vars_rs_2, "current_x")),
                                            Term(Read_Var(vars_rs_2, "current_y")),
                                            1,
                                        )
                                    ]
                                ),
                                (
                                    EqualTo(
                                        Term(
                                            Read_Pixel(
                                                env_before,
                                                Read_Var(vars_rs_2, "current_x"),
                                                Read_Var(vars_rs_2, "current_y"),
                                            )
                                        ),
                                        Term(1),
                                    ),
                                    Codeblock(
                                        [
                                            Write_Pixel(
                                                env_rs_2,
                                                Read_Var(vars_rs_2, "current_x"),
                                                Read_Var(vars_rs_2, "current_y"),
                                                0,
                                            )
                                        ]
                                    ),
                                ),
                            ),
                            Write_Var(
                                vars_rs_2,
                                "current_y",
                                Term(
                                    SUM(Term(Read_Var(vars_rs_2, "current_y")), Term(1))
                                ),
                            ),
                        ]
                    ),
                ),
                Write_Var(
                    vars_rs_2,
                    "current_x",
                    Term(SUM(Term(Read_Var(vars_rs_2, "current_x")), Term(1))),
                ),
                Write_Var(vars_rs_2, "current_y", Term(0)),
            ]
        ),
    ),
]

epoch_2_plan.execute()
print_env(env_rs_2, "env_rs_2")
# todo output fehler
