import pytest
from instruction_language.interpreter import InstructionInterpreter
from instruction_language.surroundings.interpreter_settings import GISManager
from instruction_language.surroundings.memory import MemoryManager
from tests.pytest_setup import sample_codeblock


def test_memory_manager_reset():
    assert MemoryManager.current_namespace_id == None
    assert MemoryManager.namespace_register == {}
    assert MemoryManager.namespace_stack == []

    # test single namespace
    MemoryManager.new_namespace()
    MemoryManager.set_var("test_key", "test_value")
    MemoryManager.reset()

    assert MemoryManager.current_namespace_id == None
    assert MemoryManager.namespace_register == {}
    assert MemoryManager.namespace_stack == []

    # test multiple namespaces
    MemoryManager.new_namespace()
    MemoryManager.set_var("test_key", "test_value")
    MemoryManager.new_namespace()
    MemoryManager.set_var("test_key_2", "test_value_2")
    MemoryManager.reset()

    assert MemoryManager.current_namespace_id == None
    assert MemoryManager.namespace_register == {}
    assert MemoryManager.namespace_stack == []


def test_memory_manager_rest_with_interpreter(sample_codeblock):
    assert MemoryManager.current_namespace_id == None
    assert MemoryManager.namespace_register == {}
    assert MemoryManager.namespace_stack == []

    interpreter = InstructionInterpreter()
    interpreter.execute(sample_codeblock)

    assert MemoryManager.current_namespace_id == None
    assert MemoryManager.namespace_register == {}
    assert MemoryManager.namespace_stack == []
