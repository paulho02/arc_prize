
from matplotlib import pyplot as plt
import networkx as nx
from instruction_language.ast_transformer import hierarchy_plot
from tests.pytest_setup import invert_program


# todo move this somewhere else
ast, root = invert_program.to_ast()
plot_blueprint = hierarchy_plot(ast, root)
labels = nx.get_node_attributes(ast, 'label')
nx.draw(ast, pos=plot_blueprint, labels=labels, with_labels=True, arrows=True)
plt.show()


# print nodes 'json'
#
# nodes_data = [
#     {"id": str(n), "label": d.get("label", ""), "type": d.get(
#         "type", ""), "carrying_value": d.get("carrying_value", None)}
#     for n, d in ast.nodes(data=True)
# ]
# print(json.dumps(nodes_data, indent=2))


# print nodes 'raw'
#
# nodes_data = [
#     {"id": n, **d}
#     for n, d in ast.nodes(data=True)
# ]
# print(nodes_data)
