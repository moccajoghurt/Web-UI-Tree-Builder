// Ambient types for DOM if needed; extend as your project grows.
// You can add global declarations here.

import type { ATPGlobal } from "./bookmarklet/types";

declare global {
  interface Window {
    __ATP__?: ATPGlobal;
  }
}
