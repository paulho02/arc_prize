import pytest
from instruction_language.elements import types


def test_type_mappings():
    assert len(types.t2int.items()) == len(types.n_types.__args__)

    assert types.t2int["term"] == 0
    assert types.t2int["while"] == 11

    assert types.t2int["if"] == types.t2int[types.int2t[types.t2int["if"]]]
