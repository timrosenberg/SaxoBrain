---
title: "Site Text"
build:
  render: never
  list: never
cascade:
  build:
    render: never
    list: local
---

Shared navigation, buttons, filters, accessibility labels, and system messages live in this folder. Each note has a table with two columns: **Setting** identifies the wording, and **Text** is what appears on the site.

Edit the **Text** column in Obsidian. The site uses it on the next build. Keep the **Setting** column unchanged. Values are plain text. Preserve placeholders such as `{title}` and `{count}`, which the site fills in automatically. In Markdown source, write a literal pipe as `\|` so it stays inside its table cell.

These settings live in tables so they do not appear in Obsidian's property suggestions. The properties on this folder note control publishing and should stay unchanged.

Page introductions, headings, descriptions, captions, credits, and editorial links live in the corresponding note bodies. See [[SaxoBrain - Body Components]] for editing examples.
