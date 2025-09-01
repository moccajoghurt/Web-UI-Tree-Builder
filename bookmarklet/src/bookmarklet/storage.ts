import { Store, ActionItem } from "./types";

const SKEY = "__action_picker_store__";

export function loadStore(): Store {
  try {
    const raw = localStorage.getItem(SKEY) || '{"actions":[]}';
    const parsed = JSON.parse(raw) as Store;
    if (!Array.isArray(parsed.actions)) parsed.actions = [];
    return parsed;
  } catch {
    return { actions: [] };
  }
}

export function saveStore(store: Store) {
  localStorage.setItem(SKEY, JSON.stringify(store));
}

export function addAction(store: Store, item: ActionItem) {
  store.actions.push(item);
  saveStore(store);
}

export function clearActions(store: Store) {
  store.actions = [];
  saveStore(store);
}

export function setPath(store: Store, value: string) {
  store.path = value || "";
  saveStore(store);
}
