import json
import glob
import re


def _slug(s):
    s = re.sub(r"[^a-z0-9:.\-]+", "", s.lower())
    return s


def _load_lines(file_paths):
    for p in file_paths:
        with open(p, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                yield json.loads(line)


def _build_tree(actions):
    nodes = {}

    def nid(path):
        return _slug(":".join(path)) if path else None

    for a in actions:
        p = a.get("path") or []
        # ensure group nodes (categories) exist
        for i in range(1, len(p)):
            pid = nid(p[:i])
            if pid not in nodes:
                nodes[pid] = {
                    "id": pid,
                    "title": p[i - 1],
                    "parent": nid(p[: i - 1]),
                    "isGroup": True,
                }
    # leaf actions
    out = []
    for a in actions:
        out.append(a)
    result = {"groups": list(nodes.values()), "actions": out}
    return result


def build_tree(files: str) -> dict:
    input_paths = glob.glob(files, recursive=True)
    all_actions = list(_load_lines(input_paths))
    tree = _build_tree(all_actions)
    return tree
