import torch

from instruction_language.elements import types


def hierarchy_plot(G, root, width=1.0, horiz_gap=0.2, horiz_loc=0, ycenter=0.5, pos=None, parent=None):
    # Recursively assign positions to nodes for a left-to-right tree layout
    if pos is None:
        pos = {root: (horiz_loc, ycenter)}
    else:
        pos[root] = (horiz_loc, ycenter)
    children = list(G.successors(root))
    if len(children) != 0:
        # Sort children by edge 'order' attribute, higher order first (closer to top)
        children.sort(key=lambda c: -G.edges[root, c].get('order', 0))
        dy = width / len(children)
        nexty = ycenter - width / 2 - dy / 2
        for child in children:
            nexty += dy
            pos = hierarchy_plot(G, child, width=dy, horiz_gap=horiz_gap,
                                 horiz_loc=horiz_loc + horiz_gap, ycenter=nexty, pos=pos, parent=root)
    return pos


# todo write tests
# todo check and revise maybe
def encode_ast_nodes(ast):
    for node in ast.nodes:
        node_data = ast.nodes[node]

        # Get type as int vector (one-hot)
        type_idx = node_data.get("type", 0)
        type_onehot = torch.zeros(len(types.all_types))
        type_onehot[type_idx] = 1.0

        # Get carrying_value as float
        cv = node_data.get("carrying_value")
        carrying_value = torch.tensor([float(cv) if cv is not None else 0.0])

        # Combine them into one feature vector
        node_data["x"] = torch.cat([type_onehot, carrying_value])
