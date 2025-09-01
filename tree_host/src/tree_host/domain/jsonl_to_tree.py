import json
import glob


def _load_lines(file_paths):
    for p in file_paths:
        with open(p, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                yield json.loads(line)


def _build_tree(actions):
    return {"actions": list(actions)}


def build_tree(files: str) -> dict:
    input_paths = glob.glob(files, recursive=True)
    all_actions = list(_load_lines(input_paths))
    tree = _build_tree(all_actions)
    return tree
