export const norm = (s: any) => (s ?? "").toString().trim();

export const splitPath = (s: string) =>
  norm(s)
    .split(">")
    .map((x: string) => x.trim())
    .filter(Boolean);

const labelById = (id: string | null) => {
  if (!id) return "";
  const n = document.getElementById(id);
  return n?.textContent?.trim() ?? "";
};

export const getLabel = (el: Element & (HTMLElement | SVGElement)) =>
  norm(el.getAttribute("aria-label")) ||
  norm(
    el.getAttribute("aria-labelledby") &&
      labelById(el.getAttribute("aria-labelledby"))
  ) ||
  norm((el as HTMLElement).innerText) ||
  norm(el.textContent) ||
  norm(el.getAttribute("title")) ||
  // value may exist on inputs
  norm((el as HTMLInputElement).value as any);

export const visible = (el: Element) => {
  const r = (el as HTMLElement).getBoundingClientRect();
  const cs = getComputedStyle(el as HTMLElement);
  return (
    r.width > 5 &&
    r.height > 5 &&
    cs.display !== "none" &&
    cs.visibility !== "hidden" &&
    cs.opacity !== "0"
  );
};

export const makeId = (path: string[], title: string) =>
  path
    .concat([title])
    .join(":")
    .toLowerCase()
    .replace(/\s+/g, "-")
    .replace(/[^a-z0-9:.-]/g, "");

export const route = () => location.pathname + location.hash;
