# Bookmarklet Project

Modular TypeScript project for building a production-ready bookmarklet.

## What you get

- Source in `src/` split into modules
- Single-file bundled + minified output via esbuild
- Automatic bookmarklet URL wrapping
- `dist/preview.html` you can open and drag the link to your bookmarks

## Scripts

- `npm run build` – bundle, minify, and emit bookmarklet files into `dist/`
- `npm run watch` – rebuild on changes

## Project structure

- `src/index.ts` – entry point; import your modules here
- `src/lib/*` – organize your code here
- `scripts/build.mjs` – esbuild-based bundler and bookmarklet wrapper

## Using your existing bookmarklet

Paste or split your current logic into modules under `src/lib/` and call from `src/index.ts`.

## Output files

- `dist/bundle.js` – minified bundle
- `dist/bookmarklet.txt` – bookmarklet URL
- `dist/preview.html` – page with a drag-to-bookmarks link
