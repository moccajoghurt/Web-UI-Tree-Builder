import { loadStore } from "./storage";
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

  // Close panel
  ui.onClose(() => ui.teardown());

  // Install alt+click picker
  const removePicker = installPicker(ui.pathInput, ui.typeSelect);

  const teardown = () => {
    removePicker();
    ui.teardown();
  };

  window.__ATP__ = { panel: ui.panel, teardown };
}
