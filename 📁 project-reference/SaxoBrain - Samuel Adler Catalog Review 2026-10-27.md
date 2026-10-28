# Samuel Adler Catalog Review

Checked 2026-10-27 for the request to add five works, locate score editions and streaming recordings, and suggest difficulty ratings.

## Catalog Scope

The existing catalog contained Soundings. Added Canto IV, Contrasting Inventions, Line Drawings, Music of Yearning, and Pensive Soliloquy. The existing Samuel Adler composer note already has the automatic Composer Works Base view. No composer change was needed.

## Editions

Public publisher pages were fetched directly with Python because the web reader could not retrieve several pages. All five product pages returned HTTP 200 and identified the expected work. HTML snapshots remain in `/private/tmp/adler-research-20261027/`.

| Work | Current edition | Findings |
| --- | --- | --- |
| Canto IV | [Dorn DORN1010](https://www.grothmusic.com/p-140132.aspx) | Groth lists alto saxophone unaccompanied and in-stock print materials. Dorn’s [April 2025 catalog](https://www.grothmusic.com/images/DP%20Catalog%20April%202025.pdf), page 1, confirms order 1010. The composer’s Ludwig attribution conflicts with this current edition. |
| Contrasting Inventions | [Carl Fischer CY2984](https://www.carlfischer.com/cy2984-contrasting-inventions.html) | Publisher page confirms alto and tenor parts, dedication to Lawrence Gwozdz, and score-and-parts options. It says the materials come from the composer’s original edition. [Presto’s listing](https://www.prestomusic.com/sheet-music/products/8762225--adler-s-contrasting-inventions) independently confirms the publisher and number. Presser is the attribution in the composer’s catalog and the older dissertation. |
| Line Drawings | [Dorn DORN0771](https://www.grothmusic.com/p-149658.aspx) | Groth confirms SATB quartet and in-stock materials. Dorn’s April 2025 catalog lists order 771 under SATB quartets. |
| Music of Yearning | [Theodore Presser 114-42247](https://www.presser.com/114-42247-music-of-yearning.html) | Publisher confirms solo alto saxophone, four-minute duration, dedication to Sampen, and student suitability. [Presto](https://www.prestomusic.com/sheet-music/products/9317797--adler-s-music-of-yearning) confirms the edition and ISBN 9781491134917. |
| Pensive Soliloquy | [Theodore Presser 114-40914](https://www.presser.com/114-40914-pensive-soliloquy.html) | Publisher confirms score and parts, seven minutes, and dedication to Sampen and Shrude. [Sheet Music Plus](https://www.sheetmusicplus.com/en/product/pensive-soliloquy-1789999.html) confirms instrumentation, 1997 composition, and the edition. |

Stock descriptions are observations from this check and may change. No prices were copied into the public notes.

## Difficulty Estimates

Every rating is provisional. These are editorial mappings to SaxoBrain’s college-year categories. No complete score or recording was examined.

- **Canto IV: Advanced.** Wei-Lun Chien’s 2015 University of North Texas dissertation, [Music for the Saxophone Duet Genre](https://digital.library.unt.edu/ark:/67531/metadc804908/), contrasts this solo’s flutter tonguing, multiphonics, and quarter tones with the duet’s conventional techniques. This supports advanced preparation. Moderate confidence in the broad category.
- **Contrasting Inventions: Advanced.** Chien, pages 13 to 17, documents alto altissimo A, tenor altissimo G, wide leaps, rapid register connections, polyrhythm, and changing meters. Moderate confidence. The dissertation PDF was downloaded and its relevant text read directly.
- **Line Drawings: Advanced.** Rhett Lyle Bender’s 2000 University of Georgia dissertation, [Annotated Bibliography of Published Saxophone Quartets](https://getd.libs.uga.edu/pdfs/bender_rhett_l_200012_dma.pdf), pages 15 to 17, recommends an advanced ensemble and specifies alto altissimo G-sharp and A. Its discussion also covers upper-register intervals and changing meters. Moderate confidence.
- **Music of Yearning: Second Year.** The publisher explicitly describes conventional range and student suitability. The precise year placement is a low-confidence inference. Publisher gallery retrieval showed cover images only, so no claim about inspected notation is made.
- **Pensive Soliloquy: Third Year.** Presser specifies a slow expressive opening. [Grand Rapids Community College’s Applied Music Rubrics](https://www.grcc.edu/sites/default/files/docs/music/music_appliedMusicRubics_1415-38580_01-2015.pdf) include the piece among saxophone repertoire suggestions. This supports college use without assigning a year. Third Year is a low-confidence candidate pending score review. Preview attempts yielded the cover only.

## Recording Checks

Spotify’s connected catalog returned exact matches for Canto IV, Line Drawings, and Pensive Soliloquy. The selected tracks reported PLAYABLE. The two successful Canto and Line searches returned complete movement sets, reordered into musical sequence in the notes. This is metadata verification, not an audition or a guarantee of availability in every region.

- **Canto IV:** Ronald L. Caravan, Single Reed Expressions, Vol. 7. All three movements are linked individually.
- **Contrasting Inventions:** Michael Duke and Michael Lichnovsky, Duo Sax, Saxophone Classics CC4006. The connected search failed to return the work. Spotify’s [public album track listing](https://open.spotify.com/track/6lJwQDXrIqIdqhSLIeJGUS) contained both exact Adler titles, performer credits, and track destinations. Those two destinations were used. [Duke’s store](https://michael-duke.com/store) confirms the recording project. Local HTML preserves the source track list. Individual playback was not tested.
- **Line Drawings:** Vision Saxophone Quartet, Conicality. Both movements are linked. This is an alternative to the Rascher recording listed by the composer.
- **Music of Yearning:** no matching streaming recording located after targeted web, YouTube-index, and Spotify searches. Unrelated results were excluded. [BGSU’s February 27, 2022 listing](https://events.bgsu.edu/calendar/day/2022/2/27) names Sampen as performer but does not establish a recording.
- **Pensive Soliloquy:** John Sampen and Marilyn Shrude, Visions in Metaphor. [The album’s liner notes](https://www.dramonline.org/albums/visions-in-metaphor/notes) independently confirm the performers and postcard project.

## Chronology and Duration Caveats

The [composer’s chamber-music catalog](https://samuelhadler.com/works-samuel-adler/chamber-music/) supplies the requested composition dates, premiere credits, and nominal durations. Dates are preserved with the following qualifications.

- **Canto IV:** retained 1975 from the supplied information and composer catalog. [Eastman’s archive](https://www.esm.rochester.edu/sibley/specialcollections/findingaids/adler-99-18/ser1/) describes a published Dorn score dated 1973. Chien uses 1971. The public note explicitly identifies the discrepancy. No definitive composition year was established.
- **Line Drawings:** the composer estimates eight minutes. Bender times it at 5:40. The public duration is attributed to the composer.
- **Music of Yearning:** the website misspells the premiere performer’s first name as Jahn. [John Sampen’s own commissions and premieres list](https://www.johnwsampen.com/commissions-premieres) confirms the work and his identity.
- **Pensive Soliloquy:** public duration is five to seven minutes, reflecting composer and publisher estimates. The website’s Valencia premiere date of August 1998 conflicts with the 1997 congress. The [North American Saxophone Alliance’s honorary-member history](https://saxophonealliance.org/about/honorary-life-members/) confirms Valencia in 1997. Album liner notes place the remaining postcard premieres there in 1997. The exact premiere date is omitted pending score documentation.

## Verification

Verification results are reported in the accompanying chat after the final build and rendered-content checks. These notes and the private sections of the work files are excluded from public output by the existing site conventions. No commit or push is part of this request.

## YouTube Follow-Up

Checked 2026-10-27 after Tim specified YouTube as his preferred listening service. Direct YouTube search pages found recordings omitted by the general web index. The YouTube recordings are now first in the streaming properties. Spotify links remain as alternatives.

- **Canto IV:** Ronald L. Caravan on Single Reed Expressions, Vol. 7. Verified [movement I](https://www.youtube.com/watch?v=MB9QlekTDk0), [movement II](https://www.youtube.com/watch?v=0Js80xyDLhc), and [movement III](https://www.youtube.com/watch?v=VGAlmZdX-fY). The uploader’s descriptions credit Caravan, Adler, and NAXOS of America. One player queues all three movements in order.
- **Contrasting Inventions:** Michael Duke’s Duo Sax recording. Verified [movement I](https://www.youtube.com/watch?v=PeEQD4q5IxI) and [movement II](https://www.youtube.com/watch?v=tXNDgvDEwUI). The descriptions identify the album and Clarinet & Saxophone Classics. Lichnovsky’s credit follows the independently verified Spotify track list and album documentation above. One player queues both movements in order.
- **Line Drawings:** Vision Saxophone Quartet on Conicality. Verified [Light Drawing](https://www.youtube.com/watch?v=iz5_CXzY2RU) and [Dark Drawing](https://www.youtube.com/watch?v=oFR4k_-0V5c). Both descriptions name Adler and the quartet. One player queues both movements in order.
- **Pensive Soliloquy:** [John Sampen and Marilyn Shrude](https://www.youtube.com/watch?v=Wlpx2WvlKW0) on Visions in Metaphor. The description names both performers, Adler, and Albany Records.
- **Music of Yearning:** no matching video found after direct YouTube searches using the exact title, composer, instrument, Sampen’s name, and the BGSU birthday-concert date. This establishes only that these searches did not locate a recording.

Each selected video’s player metadata reported status OK and playableInEmbed true. Titles, artist descriptions, and durations were checked. Audio was not auditioned. Search and player metadata snapshots are in `/private/tmp/adler-youtube-20261027/`. Canto IV’s existing public-body removal was preserved.
