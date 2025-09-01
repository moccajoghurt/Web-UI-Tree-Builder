import { ActionItem } from "./types";
import { addAction } from "./storage";
import { visible, getLabel, makeId, route, splitPath } from "./utils";

export function currentPath(inputEl: HTMLInputElement) {
  return splitPath(inputEl.value || "");
}

export function highlight(el: Element, ms = 800) {
  const x = document.createElement("div");
  const r = (el as HTMLElement).getBoundingClientRect();
  Object.assign(x.style, {
    position: "fixed",
    left: r.left + "px",
    top: r.top + "px",
    width: r.width + "px",
    height: r.height + "px",
    border: "2px solid #4ade80",
    borderRadius: "6px",
    pointerEvents: "none",
    zIndex: 2147483646 as any,
  } as CSSStyleDeclaration);
  document.body.appendChild(x);
  setTimeout(() => x.remove(), ms);
}

export function installPicker(
  pathInput: HTMLInputElement,
  typeSelect?: HTMLSelectElement
) {
  // Cycle the Type dropdown on mouse wheel: down = next, up = previous
  const wheelHandler = (e: WheelEvent) => {
    if (!typeSelect) return;
    const opts = typeSelect.options;
    const len = opts.length;
    if (!len) return;
    const cur = typeSelect.selectedIndex >= 0 ? typeSelect.selectedIndex : 0;
    const dir = e.deltaY > 0 ? 1 : e.deltaY < 0 ? -1 : 0;
    if (dir === 0) return;
    const next = (cur + dir + len) % len;
    typeSelect.selectedIndex = next;
    // Optional: fire change event if anything listens to it later
    typeSelect.dispatchEvent(new Event("change", { bubbles: true }));
  };

  window.addEventListener("wheel", wheelHandler, { passive: true });
  const clickHandler = (e: MouseEvent) => {
    if (!e.altKey && !e.ctrlKey) return;
    const target = e.target as Element | null;
    const el = target?.closest("*");
    if (!el || !visible(el)) return;
    if (e.ctrlKey) {
      _setPath(el, e.shiftKey);
    }
    if (e.altKey) {
      _addPickedElement(el);
    }

    e.preventDefault();
    e.stopImmediatePropagation();
    e.stopPropagation();
  };

  const _addPickedElement = (el: Element) => {
    let title = getLabel(el as any) || "(unlabeled)";
    const path = currentPath(pathInput);
    const type = (typeSelect?.value || "click") as ActionItem["type"];
    title = type === "list-item-click" ? "list-item-click" : title;
    title =
      type === "list-item-double-click" ? "list-item-double-click" : title;
    const obj: ActionItem = {
      id: makeId(path, title),
      parent: path.length
        ? makeId(path.slice(0, -1), path.slice(-1)[0] || "")
        : null,
      path: path.concat([title]),
      title,
      route: route(),
      type,
    };
    addAction(obj);
    highlight(el);
  };

  const _setPath = (el: Element, remove = false) => {
    const path = currentPath(pathInput);
    if (remove) {
      path.pop();
      pathInput.value = path.join(" > ");
    } else {
      const type = (typeSelect?.value || "click") as ActionItem["type"];
      let title = getLabel(el as any) || "(unlabeled)";
      title = type === "list-item-click" ? "list-item-click" : title;
      title =
        type === "list-item-double-click" ? "list-item-double-click" : title;
      const newPath = path.concat([title]).join(" > ");
      pathInput.value = newPath;
    }

    // Notify listeners so the UI/store stay in sync
    pathInput.dispatchEvent(new Event("input", { bubbles: true }));
  };

  window.addEventListener("click", clickHandler, true);
  return () => {
    window.removeEventListener("click", clickHandler, true);
    window.removeEventListener("wheel", wheelHandler as any);
  };
}
