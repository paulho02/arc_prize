from enum import Enum
from typing import Callable, Union
import random
import string


def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

   
class Atom:
    def __init__(self, x, y, value=0):
        self.x = x
        self.y = y
        self.value = value

    # @property
    # def value(self):
    #     return self._value

    # @value.setter
    # def value(self, value):
    #     if value not in self.environment.values:
    #         raise ValueError(f"Only the following values assignable: {self.environment.values}")
    #     self._value = value


class Environment():
    def __init__(self, values):
        self.values = values
        # todo make atoms unique maybe
        self.atoms: list[Atom] = []

    def add_atom(self, atom):
        self.atoms.append(atom)


env = Environment(
    values = [1,0]
)
atom = Atom(
    x = 2,
    y = 2,
    value=1
)

env.add_atom(atom)


# Example usage:
rule_register = {}


class Rule():
    def __init__(self):
        self.conditions: list[Union["Rule",str,Callable]] = []
        self.name: str = generate_random_string(5)

        if self.name not in rule_register:
            rule_register[self.name] = self
        else:
            raise KeyError(f"Duplicate key: Rule register already contains rule '{self.name}'")

    def add_condition(self, condition: list[Union["Rule",str,Callable]]):
        self.conditions.append(condition)


# test example: line

line = Rule()
line.name = "line"
line.add_condition("two_pixels")

two_pixels = Rule()
two_pixels.name = "two_pixels"
# two_pixels.add_condition()

pixel = Rule()
pixel.name = "pixel"
def is_pixel():
    for atom in env.atoms:
        if atom.value == 1:
            return True
    return False
pixel.add_condition(is_pixel)

print(is_pixel())