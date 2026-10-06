# SaxoBrain

Repertoire, curriculum and reading for saxophonists, built and maintained by Timothy Rosenberg.

## How it works

The `content/` folder holds everything on the site, one Markdown file per page. Open `content/` in Obsidian as its own vault. Every change you send to GitHub rebuilds the site on GitHub Pages within a couple of minutes.

| Folder | What's in it |
|---|---|
| `content/works/` | One file per piece |
| `content/composers/` | One file per composer |
| `content/curriculum/` | The four-year curriculum |
| `content/reading/` | Preserved articles |
| `content/resources/` | Scale Series, Ferling Project, altissimo charts, equipment |
| `content/lists/` | Competition lists, college lists, recital programs |
| `content/recordings/` | Recordings |
| `content/Catalog.base` | Table views of the whole catalog |

Everything outside `content/` builds the site. You never need to open it.

## Editing

- **Quick fixes:** open `Catalog.base` in Obsidian and type into the cells.
- **Longer edits:** open the piece's file. Notes about the piece go below the fields.
- **New piece:** copy an existing piece file, rename it `Composer Name - Title`, and change the fields.
- **Composer:** type `[[Composer Name]]` in the composer field. The name must match a file in `composers/` exactly. If it doesn't, the site won't publish, and the error names the file to fix.

## Three rules

1. **Never change a `slug:`.** It's the page's permanent web address. Rename files and fix titles freely; the address stays the same.
2. **To move an address,** put the old one in the `aliases:` list of the page it should point to, for example `aliases: ["/works/old-address/"]`. Visitors following the old link land on the right page.
3. **If a publish stops,** GitHub shows which page broke which rule. Fix that file and send the changes again.

## License

Timothy Rosenberg's own material is licensed CC BY-SA 4.0. Articles by other authors remain theirs and are preserved here with credit to their sources.
