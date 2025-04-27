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

class Instruction(Executable):
    def __init__(self):
        pass

    def execute(self):
        pass

class Condition:
    def __init__(self, term1, term2):
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
        for step in self.execution_plan:
            step.execute()

##################################################

# set of atomic instructions #####################
class Read_Pixel(Instruction):
    def __init__(self, env, x, y):
        super().__init__()
        self.env = env
        self.x = x
        self.y = y
    
    def execute(self):
        try:
            return self.env[self.x][self.y]
        except IndexError:
            return None
    
class Write_Pixel(Instruction):
    def __init__(self, env, x, y, value):
        super().__init__()
        self.env = env
        self.x = x
        self.y = y
        self.value = value
    
    def execute(self):
        while len(self.env) <= self.x:
            self.env.append([])

        while len(self.env[self.x]) <= self.y:
            self.env[self.x].append(0)

        # Write pixel value
        self.env[self.x][self.y] = self.value
        
    
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
    def __init__(self, storage, key, value):
        super().__init__()
        self.storage = storage
        self.key = key
        self.value = value

    def execute(self):
        self.storage[self.key] = self.value
        return 
    
##################################################
    
# set of atomic conditions #######################
class LessThan(Condition):
    def __init__(self, term1, term2):
        super().__init__(term1, term2)

    def apply(self):
        return self.term1 < self.term2
    
class EqualTo(Condition):
    def __init__(self, term1, term2):
        super().__init__(term1, term2)

    def apply(self):
        return self.term1 is self.term2 or self.term1 == self.term2
    
class GreaterThan(Condition):
    def __init__(self, term1, term2):
        super().__init__(term1, term2)

    def apply(self):
        return self.term1 > self.term2

##################################################

# set of atomic flow control statements ##########

class If(ControlFlowStatement):
    def __init__(self, default:Codeblock, *args: tuple[Condition, Codeblock]):
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
    def __init__(self, condition:Condition, codeblock:Codeblock):
        super().__init__()
        self.condition = condition
        self.codeblock = codeblock

    def execute(self):
        while self.condition.apply():
            self.codeblock.execute()

        



##################################################

def print_env(env: list[list[int]], env_name):
    print("------------------")
    print(f"'{env_name}':")
    for row in env:
        for col in row:
            print(f' {col} ', end='')
        print()
    print("------------------")
        

inital_env = {}
result_env = {}


# Ev1        Ev2

# 0 0  -->   1 1 
# 0 1        1 0 

# 1 1  -->   0 0
# 0 0        1 1

env_before = [
    [0, 1],
    [0, 0]
]

env_rs_1 = []
epoch_1_plan = Codeblock()
epoch_1_plan.execution_plan = [
    Write_Pixel(env_rs_1,0,0,1),
    Write_Pixel(env_rs_1,0,1,1),
    Write_Pixel(env_rs_1,1,0,1),
    Write_Pixel(env_rs_1,1,1,0),
]
epoch_1_plan.execute()
print_env(env_rs_1, "env_rs_1")


# todo introduce system variables (like envs size, etc ..)
env_rs_2 = []
vars_rs_2 = []
epoch_2_plan = Codeblock()
epoch_2_plan.execution_plan = [
    Write_Var(vars_rs_2, "env_size_x", 2),
    Write_Var(vars_rs_2, "env_size_y", 2),

    Write_Var(vars_rs_2, "current_x", 0),
    Write_Var(vars_rs_2, "current_y", 0),

    
    WhileLoop(LessThan(Read_Var(vars_rs_2, "current_x"), Read_Var(vars_rs_2, "env_size_x")),
              Codeblock([
                  If(
                      Codeblock([
                          Write_Pixel(env_rs_2, Read_Var(vars_rs_2, "current_x"), Read_Var(vars_rs_2, "current_y"), 1)
                      ],
                      [
                          (
                            Condition(Read_Pixel(vars_rs_2, Read_Var(vars_rs_2, "current_x"), Read_Var(vars_rs_2, "current_y")), 1),
                            Codeblock([
                                Write_Pixel(env_rs_2, Read_Var(vars_rs_2, "current_x"), Read_Var(vars_rs_2, "current_y"), 1)
                            ])
                          )
                      ]
                      )
                  )
              ])          
    )
]


