// Entry point for the bookmarklet. You can import other modules from here.
import { init } from "./bookmarklet/init";

(async () => {
  try {
    await init();
  } catch (err) {
    // Avoid noisy alerts in production bookmarklets; log to console instead.
    console.error("[Bookmarklet] init failed:", err);
  }
})();
