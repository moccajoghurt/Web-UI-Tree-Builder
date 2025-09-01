import json
import glob


def _normalize_tree(actions):
    edges = []
    nodes = {}

    for a in actions:
        nid = a["id"]
        nodes[nid] = {
            "id": nid,
            "title": a.get("title", "(action)"),
            "kind": "action",
            "role": a.get("role"),
            "route": a.get("route"),
            "type": a.get("type"),
            "path": a.get("path", []),
        }
        if a.get("parent"):
            edges.append((a["parent"], nid))

    return nodes, edges


def _load_lines(file_paths):
    for p in file_paths:
        with open(p, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                yield json.loads(line)


def build_tree(files: str) -> dict:
    input_paths = glob.glob(files, recursive=True)
    all_actions = list(_load_lines(input_paths))
    nodes, edges = _normalize_tree(all_actions)
    return {"nodes": nodes, "edges": edges}
