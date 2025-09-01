import { Store } from "./types";
import { setPath } from "./storage";

export interface UIPanel {
  panel: HTMLDivElement;
  pathInput: HTMLInputElement;
  typeSelect: HTMLSelectElement;
  teardown: () => void;
  onClose: (fn: () => void) => void;
}

export function createPanel(store: Store): UIPanel {
  const panel = document.createElement("div");
  panel.style.cssText =
    "position:fixed;top:12px;right:12px;z-index:2147483647;background:#111;color:#fff;padding:8px 10px;border-radius:8px;font:12px system-ui;box-shadow:0 6px 20px rgba(0,0,0,.4)";
  panel.innerHTML = `
    <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
      <strong>Action Picker</strong>
      <label>Path <input id="ap_path" placeholder="e.g. Personal > Hinzufügen" style="width:240px;margin-left:4px"></label>
      <label>Type
        <select id="ap_type" style="margin-left:4px">
          <option value="click" selected>click</option>
          <option value="form-fill">form-fill</option>
          <option value="list-item-double-click">list-item-double-click</option>
          <option value="list-item-click">list-item-click</option>
        </select>
  </label>
      <button id="ap_close">×</button>
    </div>
    <div style="margin-top:6px;opacity:.9">
      Alt+Click = Add Action | Ctrl+Click = Add to Path | Ctrl+Shift+Click = Remove from Path
    </div>`;
  document.body.appendChild(panel);

  const pathInput = panel.querySelector("#ap_path") as HTMLInputElement;
  pathInput.value = store.path || "";
  // Ensure the rightmost part is visible on init
  try {
    const len = pathInput.value.length;
    pathInput.setSelectionRange(len, len);
  } catch {}
  pathInput.scrollLeft = pathInput.scrollWidth;

  // Keep view anchored to the rightmost part while editing
  pathInput.addEventListener("input", (e: Event) => {
    const input = e.target as HTMLInputElement;
    setPath(store, input.value);
    const len = input.value.length;
    try {
      input.setSelectionRange(len, len);
    } catch {}
    input.scrollLeft = input.scrollWidth;
  });

  const typeSelect = panel.querySelector("#ap_type") as HTMLSelectElement;
  if (!typeSelect.value) typeSelect.value = "click";

  const teardown = () => panel.remove();

  const on = (selector: string, fn: () => void) => {
    const el = panel.querySelector(selector) as HTMLButtonElement | null;
    if (el) el.onclick = fn;
  };

  let closeCb: () => void = () => {};

  on("#ap_close", () => closeCb());

  return {
    panel,
    pathInput,
    typeSelect,
    teardown,
    onClose: (fn) => (closeCb = fn),
  };
}
