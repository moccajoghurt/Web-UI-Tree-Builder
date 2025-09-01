import { Store, ActionItem } from "./types";

const SKEY = "__action_picker_store__";

export function loadStore(): Store {
  try {
    const raw = localStorage.getItem(SKEY) || "{}";
    const parsed = JSON.parse(raw) as Partial<Store>;
    return { path: parsed.path || "" };
  } catch {
    return { path: "" };
  }
}

export function saveStore(store: Store) {
  localStorage.setItem(SKEY, JSON.stringify({ path: store.path || "" }));
}

export async function addAction(item: ActionItem) {
  try {
    await fetch("http://localhost/update-tree", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(item),
    });
  } catch (err) {
    console.error("Failed to POST action to /update-tree", err);
  }
}

export function setPath(store: Store, value: string) {
  store.path = value || "";
  saveStore(store);
}
