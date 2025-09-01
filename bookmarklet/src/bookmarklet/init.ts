import { loadStore, saveStore, clearActions } from "./storage";
import { createPanel } from "./ui";
import { installPicker } from "./picker";
import type { ATPGlobal } from "./types";

declare global {
  interface Window {
    __ATP__?: ATPGlobal;
  }
}

export async function init() {
  // Remove prior panel if exists
  if (window.__ATP__) {
    try {
      window.__ATP__!.teardown();
    } catch {}
  }

  const store = loadStore();
  const ui = createPanel(store);

  // Download action list as .jsonl
  ui.onDownload(() => {
    const lines = store.actions.map((o) => JSON.stringify(o));
    const blob = new Blob([lines.join("\n")], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    const ts = new Date().toISOString().replace(/[:.]/g, "-");
    a.download = `actions_${ts}.jsonl`;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
      URL.revokeObjectURL(a.href);
      a.remove();
    }, 0);
  });

  // Clear current recording
  ui.onClear(() => {
    if (confirm("Clear current recording?")) {
      clearActions(store);
      alert("Cleared.");
    }
  });

  // Close panel
  ui.onClose(() => ui.teardown());

  // Install alt+click picker
  const removePicker = installPicker(store, ui.pathInput, ui.typeSelect);

  const teardown = () => {
    removePicker();
    ui.teardown();
  };

  window.__ATP__ = { panel: ui.panel, teardown };
}
