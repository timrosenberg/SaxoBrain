---
title: "SaxoBrain - Composer Research Record"
added: 2026-10-21
---

# SaxoBrain - Composer Research Record

## Audit Scope

The October 14, 2026 audit inspected 800 composer records. Its application log recorded 442 field additions across 338 records: 151 nationalities, 82 birth years, 30 death years and 179 composer or estate websites. These are historical application counts.

The full field-level evidence and later correction log are in the cleanup recovery archive. A blank death year does not establish that a composer is alive.

## Identity Precedents And Remaining Gaps


This dated audit contains subsequent corrections as well as unresolved cases. Check the current composer record before acting on an old gap.

- **Alan Oettinger:** Sources conflict over 1948 and 1950. Birth year remains blank. [Source 1](https://nyplorg-data-archives.s3.amazonaws.com/uploads/collection/generated_finding_aids/mus24605.pdf) [Source 2](https://www.copyrightencyclopedia.com/reflections-of-the-heart-and-soul-collection-reflections/)
- **Charles Ruggiero:** Corrected the birth year from 1971 to 1947 and cleared the drummer's Wikidata ID following Tim's identity confirmation. Added a composer biography and blocked the rejected Wikidata match from automatic reuse. [Michigan State University biography](https://music.msu.edu/faculty/charles-ruggiero/) [Recording liner notes](https://nwr-site-liner-notes.s3.amazonaws.com/nwcr876.pdf)
- **Walter Skolnik:** Corrected the Edward Skolnik credit to the existing Walter Skolnik record following Tim's confirmation. Renamed the Arioso and Dance file and updated its composer link. The former Edward page redirects to Walter's page. The original empty Edward record is preserved in the research archive. [Publisher listing](https://schottmusiclondon.com/arioso-danza-no440674.html)
- **Henri Eccles:** References give uncertain or conflicting birth dates. No exact birth year was added.
- **Jean Lemaire:** The film-composer biography could not be connected securely to Musiques legeres. Dates remain blank.
- **Jean-Luc Falchamps:** The listed Decalcomanie matches Jean-Luc Fafchamps. Added verified biography fields and retained the current filename and title. [Source 1](https://ressources.ircam.fr/fr/composer/jean-luc-fafchamps/biography) [Source 2](https://jeanlucfafchamps.eu/)
- **John Cooper:** Rejected the Skillet bassist. The saxophone composer is associated with C. Lynne Music. Birth year remains unknown. [Source 1](https://www.linkedin.com/in/john-cooper-1b73223a)
- **Joshua Reed:** Could not connect the listed Sonata to the trumpeter identified by the existing Wikidata record. No biography fields were added.
- **Michel Meriot:** Corrected the former Michael Meriot name following Tim's confirmation on October 14, 2026. Renamed the composer, both work files, and their review notes. Updated links and preserved permanent page URLs. [Publisher catalogue](https://johanvanderlinden.com/saxophone_catalogue_2010.pdf)
- **Noël Samyn:** Corrected nationality from French to Canadian following Tim's confirmation on October 14, 2026. His official biography confirms that he was born in Belgium. This subsequent correction is recorded separately from the 442 initial additions. [Biography](https://noelsamyn.com/biographie.htm)
- **Peter Nagy-Farkas:** Matched the composer name with Peter F. Wolf through his family obituary and the distinctive orchestral work Uprising. The Saxophone Sonatine was not independently located. [Source 1](https://www.funerals.coop/obituaries/peter-f-wolf)
- **Ramon Ricker:** Corrected the former Raymond Ricker name following Tim's confirmation on October 14, 2026. Renamed the composer and Jazz Sonata files, updated their links, and recorded Ray Ricker as his professional name. Permanent page URLs are unchanged. [Eastman biography](https://www.esm.rochester.edu/directory/ricker-ramon/)
- **Robert Waring:** The Labyrinth of Daedalus is attributed to Kate Waring in publisher and music-school repertoire sources. No Robert Waring biography was added. [Source 1](https://www.musikschulen.de/medien/doks/literatur/1-03/saxophon1-03.pdf) [Source 2](https://www.stretta-music.de/waring-kate-the-labyrinth-of-daedalus-nr-174104.html)
- **Robert Wilson:** Rejected the Gap Band bassist. The identity behind the listed saxophone works remains unresolved.
- **Scott Richards:** The composer identifies Scott Richards as a pseudonym of John Glenesk Mortimer. Added verified fields under the existing name. [Source 1](https://www.johngleneskmortimer.com/site/) [Source 2](https://schottmusiclondon.com/person/index/index/urlkey/john-mortimer)
- **Stephen Yates:** The listed Il Baco identifies the Australian composer born in 1957. The existing Wikidata record describes a British composer and guitarist. Preserved that existing ID for review. [Source 1](https://www.move.com.au/disc/muse) [Source 2](https://www.wikidata.org/wiki/Q131339965)
- **Willy van Dorsselaer:** Corrected birth year from 1916 to 1918 at Tim's request on October 14, 2026. Publisher and French national-library records support 1918. Death year remains 2017. [Publisher biography](https://www.hebu-music.com/en/musician/willy-van-dorsselaer.19832/?layout=line) [French national-library authority](https://data.bnf.fr/en/ark%3A/12148/cb14805446q.pdf)
- **Yuan-Chen Li:** Corrected the former Yuanzhen Li name at Tim's request on October 14, 2026. Renamed the composer and Spell files, updated the composer link, and preserved permanent page URLs. [Composer biography](https://yclimusic.com/bio/)


## Maintenance Safeguards

Keep `scripts/wikidata_composers.py` and `scripts/migration/wikidata-overrides.json` together. The overrides preserve rejected and confirmed matches. Common names can resolve to unrelated musicians. Review identity against the actual saxophone work before reusing a Wikidata biography.

`scripts/composer_photos.py` still uses `scripts/migration/photo-skip.json` and uses `notion-ids.json` for its historical Notion-photo mode. These data files remain with the reusable maintenance scripts.

The monthly living-composer workflow reports possible deaths for Tim to confirm. It does not edit composer records. See [[SaxoBrain - Review and Repair Record]] for archive recovery.
