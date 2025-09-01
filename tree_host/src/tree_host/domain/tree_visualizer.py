import json


def to_cytoscape_fragment(nodes, edges):
    """Return only the JS needed to render the tree in an existing template.

    The template must provide:
      - A <div id="cy"></div> container
      - Controls with ids: q, fit, toggleActions, and an #info box
      - The Cytoscape script included on the page
    """

    cy_nodes = []
    for n in nodes.values():
        data = {
            "id": n["id"],
            "label": n.get("title", ""),
            "kind": n.get("kind", "node"),
            "role": n.get("role"),
            "route": n.get("route"),
            "type": n.get("type"),
            "path": " > ".join(n.get("path", [])) if n.get("path") else "",
        }
        cy_nodes.append({"data": data})

    cy_edges = [
        {"data": {"id": f"{u}->{v}", "source": u, "target": v}} for (u, v) in edges
    ]

    # Only return the script that sets up the graph using the provided DOM
    script = f"""
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

  let selected = null;

  function updateInfo(n) {{
    const box = document.getElementById('info');
    if (!n) {{ box.textContent = 'Click a node to see details…'; box.className='muted'; return; }}
    const d = n.data();
    const esc = (s) => (s||'').toString().replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    box.className='';
    box.innerHTML = `
      <div><strong>${{esc(d.label)}}</strong></div>
    <div class=\"muted\">${{ [d.kind, d.type, d.role].filter(Boolean).map(x=>esc(x)).join(' • ') }}</div>
    ${{ d.path ? `<div><span class=\"muted\">Path:</span> ${{esc(d.path)}}</div>` : '' }}
    ${{ d.route ? `<div><span class=\"muted\">Route:</span> ${{esc(d.route)}}</div>` : '' }}
      <div class=\"muted\" style=\"margin-top:8px\">ID: ${{esc(d.id)}}</div>
    `;
  }}

  cy.on('tap', 'node', (evt) => {{ selected = evt.target; updateInfo(evt.target); }});
  cy.on('tap', (evt) => {{ if (evt.target === cy) {{ selected = null; updateInfo(null); }} }});

  document.getElementById('fit').onclick = () => cy.fit(null, 30);

  // Filtering by title
  const q = document.getElementById('q');
  const toggleActions = document.getElementById('toggleActions');

  function applyFilters() {{
    const re = q.value ? new RegExp(q.value, 'i') : null;
    cy.nodes().forEach(n => {{
      const isAction = n.data('kind') === 'action';
      let vis = true;
      if (re && !re.test(n.data('label'))) vis = false;
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
  toggleActions.addEventListener('change', applyFilters);

  // initial fit
  setTimeout(() => cy.fit(null, 30), 100);

  // Delete selected node with Delete key
  function isFormElement(el) {{
    return el && (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' || el.isContentEditable);
  }}
  document.addEventListener('keydown', async (e) => {{
    if (e.key !== 'Delete') return;
    if (isFormElement(document.activeElement)) return;
    if (!selected) return;
    const id = selected.id();
    try {{
      await fetch('/delete', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
  body: JSON.stringify({{ id }})
      }});
      // Page will auto-reload via WebSocket broadcast
    }} catch (err) {{
      console.error('Delete failed', err);
    }}
  }});
</script>
"""
    return script


def visualize_tree(tree: dict) -> str:
    """Return only the tree fragment (script) to be embedded into a template."""
    nodes = tree.get("nodes", {})
    edges = tree.get("edges", [])
    out = to_cytoscape_fragment(nodes, edges)
    return out
