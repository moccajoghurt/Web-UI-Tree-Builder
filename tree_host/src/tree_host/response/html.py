import os

TEMPLATE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "static", "template.html"
)
PLACEHOLDER = "<!-- TREE_HTML_PLACEHOLDER -->"


def render_html(tree_html: str) -> str:
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        tpl = f.read()
    return tpl.replace(PLACEHOLDER, tree_html)
