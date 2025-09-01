import json
import glob
import re
import sys
from collections import defaultdict


def read_inputs(paths):
    files = []
    for p in paths:
        files.extend(glob.glob(p))
    if not files:
        raise SystemExit("No input files matched. Use --input with JSON/JSONL paths.")

    items = []
    for fp in files:
        with open(fp, "r", encoding="utf-8") as f:
            txt = f.read().strip()
            if not txt:
                continue
            if fp.endswith(".jsonl"):
                for line in txt.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        items.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        print(
                            f"Warning: skipping bad JSONL line in {fp}: {e}",
                            file=sys.stderr,
                        )
            elif fp.endswith(".json"):
                try:
                    obj = json.loads(txt)
                except json.JSONDecodeError as e:
                    raise SystemExit(f"Invalid JSON in {fp}: {e}") from e
                items.append(obj)
            else:

                try:
                    obj = json.loads(txt)
                    items.append(obj)
                except json.JSONDecodeError:
                    print(f"Skipping non-JSON file: {fp}", file=sys.stderr)
    return items


def slug_id(parts):
    s = ":".join(parts)
    s = s.lower()
    s = re.sub(r"[^a-z0-9:.\-]+", "-", s).strip("-")
    return s


def normalize_tree(tree):
    groups = {g["id"]: g for g in tree.get("groups", [])}
    actions = tree.get("actions", [])

    for node in list(groups.values()):
        pid = node.get("parent")
        if pid and pid not in groups:
            parts = node["id"].split(":")
            title = parts[-2] if len(parts) >= 2 else node.get("title", "Group")
            groups[pid] = {
                "id": pid,
                "title": title,
                "parent": slug_id(parts[:-2]) if len(parts) > 2 else None,
                "isGroup": True,
            }

    edges = []
    nodes = {}

    for g in groups.values():
        nodes[g["id"]] = {
            "id": g["id"],
            "title": g.get("title", "Group"),
            "kind": "group",
        }
        if g.get("parent"):
            edges.append((g["parent"], g["id"]))

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


def to_cytoscape_html(nodes, edges, title="Action Tree"):

    cy_nodes = []
    for n in nodes.values():
        data = {
            "id": n["id"],
            "label": n.get("title", ""),
            "kind": n.get("kind", "node"),
            "role": n.get("role"),
            "route": n.get("route"),
            "type": n.get("type"),
            "path": " / ".join(n.get("path", [])) if n.get("path") else "",
        }
        cy_nodes.append({"data": data})
    cy_edges = [
        {"data": {"id": f"{u}->{v}", "source": u, "target": v}} for (u, v) in edges
    ]

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{title}</title>
<style>
  html, body {{ height: 100%; margin: 0; }}
  #app {{ display: grid; grid-template-columns: 1fr 320px; height: 100%; }}
  #cy {{ width: 100%; height: 100%; }}
  #side {{ border-left: 1px solid #ddd; padding: 12px; font: 14px/1.4 system-ui, -apple-system, Segoe UI, Roboto, Arial; overflow: auto; }}
  .row {{ display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin-bottom: 8px; }}
  input[type="text"] {{ flex: 1 1 auto; padding: 6px 8px; }}
  button {{ padding: 6px 10px; }}
  .muted {{ color: #666; }}
  .badge {{ display:inline-block; padding:2px 6px; border:1px solid #ccc; border-radius: 10px; margin-right:6px; font-size:12px; }}
</style>
</head>
<body>
<div id="app">
  <div id="cy"></div>
  <div id="side">
    <div class="row">
      <input id="q" placeholder="Filter by title (regex ok)" />
      <button id="fit">Fit</button>
    </div>
    <div class="row">
      <label class="muted"><input type="checkbox" id="toggleGroups" checked/> Show groups</label>
      <label class="muted"><input type="checkbox" id="toggleActions" checked/> Show actions</label>
    </div>
    <div id="info" class="muted">Click a node to see details…</div>
  </div>
</div>
<script src="https://unpkg.com/cytoscape@3.26.0/dist/cytoscape.min.js"></script>
<script>
  const elements = {{
    nodes: {json.dumps(cy_nodes, ensure_ascii=False)},
    edges: {json.dumps(cy_edges, ensure_ascii=False)}
  }};

  const cy = cytoscape({{
    container: document.getElementById('cy'),
    elements: elements,
    layout: {{ name: 'breadthfirst', directed: true, spacingFactor: 1.1, padding: 20 }},
    style: [
      {{
        selector: 'node[kind = "group"]',
        style: {{
          'shape': 'round-rectangle',
          'background-opacity': 0.1,
          'border-width': 1,
          'border-color': '#999',
          'label': 'data(label)',
          'text-wrap': 'wrap',
          'text-max-width': 200,
          'font-size': 12
        }}
      }},
      {{
        selector: 'node[kind = "action"]',
        style: {{
          'shape': 'ellipse',
          'background-opacity': 0.5,
          'label': 'data(label)',
          'text-wrap': 'wrap',
          'text-max-width': 220,
          'font-size': 12
        }}
      }},
      {{
        selector: 'edge',
        style: {{
          'width': 1.5,
          'curve-style': 'bezier',
          'target-arrow-shape': 'triangle',
          'target-arrow-color': '#999',
          'line-color': '#bbb'
        }}
      }}
    ]
  }});

  function updateInfo(n) {{
    const box = document.getElementById('info');
    if (!n) {{ box.textContent = 'Click a node to see details…'; box.className='muted'; return; }}
    const d = n.data();
    const esc = (s) => (s||'').toString().replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    box.className='';
    box.innerHTML = `
      <div><strong>${{esc(d.label)}}</strong></div>
    <div class="muted">${{ [d.kind, d.type, d.role].filter(Boolean).map(x=>esc(x)).join(' • ') }}</div>
    ${{ d.path ? `<div><span class="muted">Path:</span> ${{esc(d.path)}}</div>` : '' }}
    ${{ d.route ? `<div><span class="muted">Route:</span> ${{esc(d.route)}}</div>` : '' }}
      <div class="muted" style="margin-top:8px">ID: ${{esc(d.id)}}</div>
    `;
  }}

  cy.on('tap', 'node', (evt) => {{ updateInfo(evt.target); }});

  document.getElementById('fit').onclick = () => cy.fit(null, 30);

  // Filtering by title
  const q = document.getElementById('q');
  const toggleGroups = document.getElementById('toggleGroups');
  const toggleActions = document.getElementById('toggleActions');

  function applyFilters() {{
    const re = q.value ? new RegExp(q.value, 'i') : null;
    cy.nodes().forEach(n => {{
      const isGroup = n.data('kind') === 'group';
      const isAction = n.data('kind') === 'action';
      let vis = true;
      if (re && !re.test(n.data('label'))) vis = false;
      if (isGroup && !toggleGroups.checked) vis = false;
      if (isAction && !toggleActions.checked) vis = false;
      n.style('display', vis ? 'element' : 'none');
    }});
    // hide edges whose endpoints hidden
    cy.edges().forEach(e=> {{
      const src = e.source().style('display') !== 'none';
      const tgt = e.target().style('display') !== 'none';
      e.style('display', (src && tgt) ? 'element' : 'none');
    }});
  }}

  q.addEventListener('input', applyFilters);
  toggleGroups.addEventListener('change', applyFilters);
  toggleActions.addEventListener('change', applyFilters);

  // initial fit
  setTimeout(() => cy.fit(null, 30), 100);
</script>
</body>
</html>
"""
    return html


def visualize_tree(tree: dict) -> str:

    nodes, edges = normalize_tree(tree)
    out = to_cytoscape_html(nodes, edges, title="Action Tree")

    return out
