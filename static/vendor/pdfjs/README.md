# PDF.js

Version: 6.4.299, pinned from the official `pdfjs-dist` npm package.
Source: https://registry.npmjs.org/pdfjs-dist/-/pdfjs-dist-6.4.299.tgz
Project: https://mozilla.github.io/pdf.js/
License: Apache-2.0, included in `6.4.299/LICENSE`.

The core, worker and viewer components/styles come from the package's `legacy/` compatibility build for Safari support. Images, character maps, standard fonts, color profile and WebAssembly resources come from the package root. All files are served locally. Source maps, editing/scripting bundles, examples and types are omitted. Preserve upstream license notices when updating. Update the version paths in `layouts/baseof.html` and `static/js/pdf-overlay.js` together, and verify the archive against npm's published integrity hash before copying a new release.
