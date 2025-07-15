from typing import Literal

# todo maybe outsource the types to the language module or so
# -> so that if the types change, the code does not need to be adjusted here as well
'''
This file defines and manifests possible (node) types for the instruction language and all related components.

Warning!!
Only adjust the following fields dynamically with care, as this may lead to unexpected behavior in the code generation and execution.
(e.g. the mappings will not be updated)
'''

n_types = Literal["term", "codeblock",
                  "read_var", "write_var", "read_pixel", "write_pixel",
                  "equal_to", "greater_than", "less_than",
                  "sum",
                  "if", "while"]

# encoding to tell pytorch when a carrying value is not set
carrying_value_none_encoding: int = 99


# shortcut to get all types
all_types = list(n_types.__args__)

# shortcut for all instruction types
instruction_types = [t for t in ["read_var", "write_var",
                                 "read_pixel", "write_pixel"] if t in n_types.__args__]
# shortcut for all condition types
condition_types = [t for t in ["equal_to",
                               "greater_than", "less_than"] if t in n_types.__args__]

# shortcut for all control types
control_types = [t for t in ["if", "while"] if t in n_types.__args__]

# shortcut for all operator types
operator_types = [t for t in ["sum"] if t in n_types.__args__]


# type mappping (string to int)
t2int: dict[str, int] = {t: i for i, t in enumerate(all_types)}
# reverse type mapping (int to string)
int2t: dict[int, str] = {i: t for t, i in t2int.items()}
