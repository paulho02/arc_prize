import pytest
from torch_geometric.utils import from_networkx
from instruction_language.elements.base import Codeblock
from tests.pytest_setup import sample_codeblock


def test_to_ast(sample_codeblock):
    """Test the conversion of a Codeblock to an AST and translation to torch_geometric format."""
    ast, root = sample_codeblock.to_ast()
    data = from_networkx(ast)
    assert data is not None


def test_to_ast_with_empty_codeblock():
    """Test the conversion of an empty Codeblock to an AST."""
    empty_codeblock = Codeblock()
    ast, root = empty_codeblock.to_ast()

    data = from_networkx(ast)
    assert data is not None
