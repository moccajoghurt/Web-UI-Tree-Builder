export interface ActionItem {
  id: string;
  parent: string | null;
  path: string[];
  title: string;
  route: string;
  type: string;
}

export interface Store {
  path?: string;
  actions: ActionItem[];
}

export interface ATPGlobal {
  panel: HTMLDivElement;
  teardown: () => void;
}
