// Build script using esbuild to bundle and minify, then wrap as a bookmarklet URL.
import * as esbuild from "esbuild";
import fs from "node:fs/promises";
import path from "node:path";

const root = path.resolve(process.cwd());
const outDir = path.join(root, "dist");
const outFile = path.join(outDir, "bundle.js");
const bookmarkletFile = path.join(outDir, "bookmarklet.txt");
const htmlPreview = path.join(outDir, "preview.html");

/** Wrap JS code into a bookmarklet URL string. */
function toBookmarklet(code) {
  // Self-invoking wrapper to avoid leaking globals. Encode as URI component.
  const wrapped = `(()=>{${code}\n})();`;
  return "javascript:" + encodeURIComponent(wrapped);
}

async function ensureDir(dir) {
  await fs.mkdir(dir, { recursive: true });
}

async function writeFile(file, content) {
  await ensureDir(path.dirname(file));
  await fs.writeFile(file, content);
}

async function buildOnce() {
  await esbuild.build({
    entryPoints: ["src/index.ts"],
    outfile: outFile,
    bundle: true,
    minify: true,
    format: "iife",
    target: ["es2019"],
    platform: "browser",
    legalComments: "none",
    logLevel: "info",
    sourcemap: false,
  });

  const code = await fs.readFile(outFile, "utf8");
  const bookmarklet = toBookmarklet(code);

  await writeFile(bookmarkletFile, bookmarklet);
  await writeFile(
    htmlPreview,
    `<!doctype html>
<html>
  <meta charset="utf-8" />
  <title>Bookmarklet Preview</title>
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; padding: 24px; }
    a { display: inline-block; padding: 10px 14px; background: #111; color: #fff; border-radius: 6px; text-decoration: none; }
    code { user-select: all; }
  </style>
  <h1>Bookmarklet Preview</h1>
  <p><a href="${bookmarklet}">Drag this to your bookmarks bar</a></p>
  <p>Or copy the URL below:</p>
  <pre><code>${bookmarklet}</code></pre>
</html>`
  );
}
async function main() {
  const watch = process.argv.includes("--watch");
  if (!watch) {
    await buildOnce();
    return;
  }

  const ctx = await esbuild.context({
    entryPoints: ["src/index.ts"],
    outfile: outFile,
    bundle: true,
    minify: true,
    format: "iife",
    target: ["es2019"],
    platform: "browser",
    legalComments: "none",
    logLevel: "info",
    sourcemap: false,
  });

  await ctx.watch();
  console.log("Watching for changes...");

  // Initial post-processing and on each rebuild
  await buildOnce();

  const onRebuild = async () => {
    try {
      await buildOnce();
    } catch (e) {
      console.error("Post-build step failed:", e);
    }
  };

  // Hook into esbuild rebuild end by recreating context with a plugin
  await ctx.dispose();
  await esbuild.build({
    entryPoints: ["src/index.ts"],
    outfile: outFile,
    bundle: true,
    minify: true,
    format: "iife",
    target: ["es2019"],
    platform: "browser",
    legalComments: "none",
    logLevel: "info",
    sourcemap: false,
    watch: {
      onRebuild(error) {
        if (error) {
          console.error("Rebuild failed:", error);
        } else {
          onRebuild();
        }
      },
    },
  });
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
