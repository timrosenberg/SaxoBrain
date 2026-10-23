# Body Components

Page-specific text belongs in the note body. These components use Obsidian callouts, so their titles, text, and links remain visible and editable in the note. Ordinary Markdown still works throughout descriptions.

## Resource Boxes

Put the resource's link in the callout title. Everything inside the block is its optional description or credit. It can contain multiple paragraphs and links. Italics and a particular prefix are optional.

```markdown
> [!resource] [Soprano Saxophone Altissimo Fingerings](/media/resources/altissimo/Soprano_Saxophone_Altissimo_Fingerings.pdf)
>
> via Eric Dannewitz

> [!resource] [Steve Lacy’s Soprano Altissimo Fingerings](/media/resources/altissimo/steve-lacys-soprano-altissimo-fingerings/Soprano_Altissimo_Fingerings.jpeg)
>
> via [Gilles Laheurte](http://www.gilleslaheurte.com/)

> [!resource] [[Albright Sonata Altissimo Fingerings]]
```

The same component provides PDF, image, and article buttons. Viewer controls and their shared labels remain in Site Text. Pages hosting PDFs use `pdf-viewer: true`; pages hosting images use `image-viewer: true`.

## Topic Cards

A `topics` callout groups `topic` callouts into the existing card grid. Each topic's linked title provides its destination. Descriptions can contain their own links.

```markdown
> [!topics]
>
> > [!topic] [Reeds](/resources/equipment/reeds/)
> >
> > Compare strengths, break in reeds, and troubleshoot.
>
> > [!topic] [Mouthpieces](/resources/equipment/mouthpieces/)
> >
> > Classical recommendations, specifications, and jazz artist setups.
```

## Article Cards

An `articles` callout groups `article` callouts into two columns, with one column on phones. Each article's linked title supplies its destination. The body holds the description and optional `byline` and `label` callouts. All copy stays readable and editable in Obsidian. Labels may link independently to a curriculum assignment or another context.

```markdown
## Practice

> [!articles]
>
> > [!article] [[Teaching Students How to Practice by Steven Mauk|Teaching Students How to Practice]]
> >
> > > [!byline] Steven Mauk
> >
> > Organize practice around clear goals and a consistent routine.
> >
> > > [!label] [First Year · Fall](/curriculum/first-year/#reading)
```

Keep topic headings outside the card group. A card without a linked title remains a readable blockquote. Use `list-children: false` on an index when these cards supply its complete reading selection.

The Reading library's curriculum labels mirror the assignments in the year notes. When Tim changes an assignment, update its label in the Reading note and the article note as well. These labels describe assigned readings, not repertoire difficulty.

## Product Cards

A `products` callout groups `product` callouts into two columns, with one column on mobile. Keep category headings outside the group so they span the full width. Each product's linked title supplies its destination. Its body holds an optional photo, comments, sizing options, and independent links.

```markdown
## Neck Straps

> [!products]
>
> > [!product] [Product name](https://example.org/product)
> >
> > ![Description of the product](/media/product-photo.jpg)
> >
> > Product notes and an optional [tall version](https://example.org/tall).
>
> > [!product] [Another product](https://example.org/another)
> >
> > Another product's notes.
```

Photos display whole within a consistent frame. A product without a linked title remains a readable blockquote.

## Introductions and Sections

Use `lead` for an introductory paragraph. Use `section` for a group with a heading. A linked heading can specify a stable fragment such as `#strengths`; changing the displayed words does not require changing that fragment.

```markdown
> [!lead]
>
> Choose a task to find charts, demonstrations, and reading.

> [!section] [Compare reed strengths](#strengths)
>
> ![[Reed Strength Charts]]
```

Keep existing fragments when editing headings because other pages may link to them.

## Shared Notes

Use a whole-note embed on its own paragraph:

```markdown
![[Breaking in and Storing Reeds]]
```

Obsidian displays the embedded note. The website renders that source note using its existing presentation. Edit the source note to change the shared content. Third-party notices remain attached to embedded sources. Private research sections remain excluded from public output. Circular or missing note embeds stop the build with an error.

Embeds support whole notes. Heading-specific and block-specific embeds are outside this component's supported syntax. Literal examples inside code remain literal examples.

## Figures and Link Groups

A `figure` callout keeps its caption, image, and alt text together. A `links` callout provides the compact quick-reference strip.

```markdown
> [!figure] Numbered adjustment areas
> ![Front and side views of a saxophone reed, with adjustment areas numbered 1 through 8.](/media/resources/equipment/reeds/quick-adjustments-guide/Saxophone_Reed_Adjustments.png)

> [!links] Quick reference
>
> [Reed strength charts](/resources/equipment/reeds/reed-strength-charts/)
> [Quick adjustments](/resources/equipment/reeds/quick-adjustments-guide/)
```

Unsupported callout types remain readable blockquotes. A resource or topic without a linked title also remains readable instead of losing its text.

## Metadata and Shared Controls

Keep titles, slugs, aliases, authorship, instruments, and other genuine metadata in properties. `equipment-format` selects an existing reusable leaf-page presentation, such as instruments, products, or methods. Its headings and content remain in the note body.

`list-children: false` turns off an index's automatic child list when its body explicitly provides those links. This prevents a second copy of the Albright link on Altissimo.

Shared interface wording remains in `content/Site Text`, including viewer buttons, instrument-picker labels, filter controls, and return navigation. Page introductions, card copy, credits, headings, and captions belong in the corresponding note bodies.


## Home Entry Cards

The home note `content/_index.md` holds its entry heading, category labels, card titles, descriptions, and destinations. A `starts` group contains `start` blocks. Each linked callout title supplies the category and destination. The level-three heading supplies the card title.

```markdown
> [!starts] Start here
>
> > [!start] [Curriculum](/curriculum/)
> > ### Follow the curriculum
> > Suggested études, repertoire, and listening for each level of university student.
```

Descriptions support ordinary Markdown and independent links. The existing mobile layout hides descriptions while keeping the card titles available.

## Explanatory Columns

Use `columns` with nested `column` blocks for the explanatory cards below the Curriculum matrix. Their headings and paragraphs remain in the overview note.

```markdown
> [!columns]
> > [!column] Beyond these lists
> > Every year links to the full catalog, filtered to that year of study.
```

## Curriculum Sections, Focus, and Catalog Invitations

The overview note contains a `strands` block listing the matrix's row labels. Keep the fragment names because they select the existing matrix rows.

```markdown
> [!strands]
> - [Technique](#technique)
> - [Études](#etudes)
> - [Solo repertoire](#repertoire)
> - [Reading](#reading)
> - [Listening](#listening)
```

Each year note uses linked headings such as `## [Reading](#reading)`. Edit the words inside the square brackets. Preserve the fragment in parentheses. The other section fragments are `#technique`, `#etudes`, `#repertoire`, and `#listening`. The website uses these headings for its section titles and navigation. Existing level-three categories, terms, groups, and list items retain their normal Markdown structure.

A `focus` block supplies the label and reading focus. The overview also shows a text summary of the focus. Emphasis is optional.

```markdown
> [!focus] This year’s focus:
> How to practice
```

A `catalog` block keeps the invitation and links together. Its title is the actual catalog level used to calculate `{count}`. `{advanced-count}` counts Advanced works. These two placeholders update when the catalog changes. All surrounding wording is editable.

```markdown
> [!catalog] First Year
> Looking for something else? The catalog lists **{count}** first-year pieces.
>
> [See them all →](/?lvl=First%20Year)
```

## Composer Photo Captions

The composer note's `caption` block supplies the complete photo caption and source link. It appears beneath the portrait. Edit it directly, including the `Photo:` label. Image paths and provenance remain in the `photo` and `photo-source` properties. Empty legacy `photo-credit` properties are unused. The photo-maintenance script preserves existing body captions.

```markdown
> [!caption]
> Photo: [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Example.jpg)
```

## Album Player Captions

An album note can use a `caption` callout for text displayed above its embedded player. Keep labels such as "Album excerpts" in this block so they remain editable in Obsidian.

```markdown
> [!caption]
> Album excerpts
```

## Album Track Credits

The album's `tracks` property can give a verified composer name as plain text when the composer has no catalog page. The name appears in the player's existing composer-credit style. This creates no composer page.

```yaml
tracks:
  - "Obsidian Butterfly · 9:59 · John Leszczyński"
  - "Bleu, Rouge, Brun, Violet · 5:28 · Claudio Gabriele"
```

Use `[[Work File]]` when the work is in the catalog. Use `[[Composer File]]` when only the composer has a page. Those links supply the composer credit from the catalog. After adding a composer page, you can replace the plain name with its composer wikilink. Movements with a shared title prefix and composer credit show that credit once in their group heading.

## Inline PDFs

Use `pdf` for an inline PDF frame with an ordinary fallback link. It works alongside other paragraphs and does not depend on the note containing only one link. Use `resource` for the existing overlay viewer and download buttons.

```markdown
> [!pdf] [Quality Practice PDF](/media/reading/quality-practice/example.pdf)
```
