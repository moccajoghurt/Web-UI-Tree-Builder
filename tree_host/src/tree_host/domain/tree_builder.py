import glob
import json
import os
import tempfile

from tree_host.domain import tree_converter, tree_visualizer
from tree_host.response.html import render_html


def build_tree_html() -> str:
    tree = tree_converter.build_tree("./data/**/*.jsonl")
    tree_html = tree_visualizer.visualize_tree(tree)
    full_page = render_html(tree_html)
    return full_page


def delete_tree_node(node_id: str) -> int:
    """
    Delete records from all JSONL files under ./data that match the given node id.

    Behavior:
    - Removes any record whose "id" equals node_id.
    - Also removes descendants (ids starting with f"{node_id}:") so group deletions
      clean the whole subtree.

    Returns the total number of deleted records across all files.
    """
    if not node_id:
        return 0

    total_deleted = 0
    for path in glob.glob("./data/**/*.jsonl", recursive=True):
        # Read all lines once
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = [ln.rstrip("\n") for ln in f]
        except FileNotFoundError:
            continue

        kept: list[str] = []
        deleted_here = 0
        for line in lines:
            if not line.strip():
                kept.append(line)
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                kept.append(line)
                continue
            oid = obj.get("id")
            if isinstance(oid, str) and (
                oid == node_id or oid.startswith(f"{node_id}:")
            ):
                deleted_here += 1
                continue
            kept.append(json.dumps(obj, ensure_ascii=False))

        if deleted_here > 0:
            dir_name = os.path.dirname(path) or "."
            with tempfile.NamedTemporaryFile(
                "w", encoding="utf-8", dir=dir_name, delete=False
            ) as tmp:
                tmp.write("\n".join(kept))
                if kept:
                    tmp.write("\n")
                tmp_path = tmp.name
            os.replace(tmp_path, path)
            total_deleted += deleted_here

    return total_deleted
