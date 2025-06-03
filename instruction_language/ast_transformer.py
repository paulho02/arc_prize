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
