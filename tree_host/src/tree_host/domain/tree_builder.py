from tree_host.domain import tree_converter, tree_visualizer
from tree_host.response.html import render_html


def build_tree_html() -> str:
    tree = tree_converter.build_tree("./data/**/*.jsonl")
    tree_html = tree_visualizer.visualize_tree(tree)
    full_page = render_html(tree_html)
    return full_page
