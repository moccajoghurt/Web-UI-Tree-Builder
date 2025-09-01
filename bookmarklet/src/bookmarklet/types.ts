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
}

export interface ATPGlobal {
  panel: HTMLDivElement;
  teardown: () => void;
}
