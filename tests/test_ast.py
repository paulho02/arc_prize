import pytest
from torch_geometric.utils import from_networkx
from tests.pytest_setup import sample_codeblock


def test_to_ast(sample_codeblock):
    """Test the conversion of a Codeblock to an AST and translation to torch_geometric format."""
    ast, root = sample_codeblock.to_ast()
    data = from_networkx(ast)
