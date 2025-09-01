import os
import json
from tree_host.domain import tree_builder


async def load_index():
    return tree_builder.build_tree_html()


async def update_tree(action: dict):
    file_path = "./data/actions.jsonl"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(action) + "\n")
    return tree_builder.build_tree_html()
