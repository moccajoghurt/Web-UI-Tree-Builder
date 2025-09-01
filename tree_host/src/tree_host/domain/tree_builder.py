from tree_host.domain import tree_converter, tree_visualizer


def build_tree_html() -> str:

    tree = tree_converter.build_tree("./data/**/*.jsonl")
    return tree_visualizer.visualize_tree(tree)
