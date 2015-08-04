try:
    from graph_tool import Graph
    from .board_graph_graphtool import BoardGraph
except ImportError:
    from .board_graph_networkx import BoardGraph
