# Mod thumbnail

The user supplied the square Mandate & Ministry illustration on 2026-10-30 and requested it as the mod image. After the user reported upload-size and missing-preview issues, `thumbnail.png` was optimized to 512 × 512 (631,735 bytes). The original 1254 × 1254 PNG is preserved byte-for-byte as `thumbnail-original.png`. No artwork was regenerated or cropped. Both the packaged descriptor and local launcher registration still use `picture="thumbnail.png"`; the published item ID `3830313941` is retained. Local changes do not publish or update Steam's stored preview.

SHA-256: `b52fe002fc92d7344b187ab93a904d234d9eaf15a5080977394028730a630cba`.

The staged builder copies and tracks both root assets. Completion-safety verification checks the original hash, the optimized preview's dimensions/size and the descriptor reference. Do not restore the oversized original as the active preview. Preserve both when regenerating runtime files. Launcher display/cache behavior still needs visual confirmation.

### Confirmed upload failure and correction

The local launcher publisher log `launcher-2026-10-30.log` at `2026-10-30T18:33:58.748Z` explicitly says this mod's `thumbnail.png` is too large and is being skipped. Its original size was 2,807,787 bytes. Steam documents a primary preview limit below 1 MB: https://partner.steamgames.com/doc/api/ISteamUGC#SubmitItemUpdateResult_t . The 512-square replacement is below 1,000,000 bytes and retains the same descriptor filename.

The read-only open-beta launcher database record identifies this mod as `source=local`, with both thumbnail URL and path null. That establishes its missing registered thumbnail, not a confirmed database defect. No database, playset, subscription or cache was changed. Reopen the launcher and update the existing published item to upload the corrected preview. An actual upload and rendered local/Steam tile remain unverified.

## Workshop description artwork

The user explicitly requested separate generated graphics and dividers on 2026-10-30, with no use of the main mod image inside the description. The `workshop/` description kit contains an original desk-and-ledger banner and three matching dark teal/gold section dividers, generated with the built-in image tool without an image-reference input. Do not substitute `thumbnail.png` into this page.

See `workshop/README.md` for placement, `workshop/generation-prompts.json` for the full final prompts, and `workshop/assets-manifest.json` for original byte hashes and dimensions. Following the user's size complaint, `tools/optimize_workshop_images.ps1` exports the four description graphics as 1280-pixel-wide JPEGs at quality 90; the PNG originals remain for future editing. `workshop/optimized-assets-manifest.json` records the exported hashes, dimensions and file sizes. All upload images are below 1 MB. The updated ZIP contains the optimized JPEGs plus the small main preview separately; it excludes the large source PNGs.

The BBCode description now has verified direct image URLs, with a text-only fallback; Steam rendering after saving is not verified and nothing was uploaded by the agent. Visual text review, dimensions, BBCode tag balance and preserved original hashes were checked. No gameplay or build-version change was made. Native Windows image encoding is used for the explicitly requested file-size reduction; no image-generation call is used for compression.

### Description image URL repair

The user's four uploaded artwork IDs are `3830332780`, `3830332650`, `3830332342` and `3830332063`. Their artwork-page links had been placed inside `[img]`, preventing image rendering. On 2026-10-30 the direct image URLs were recovered through Steam's public metadata and the last artwork page's `image_src`. All four unauthenticated image requests returned JPEG data exactly matching the local optimized exports. `workshop/description.bbcode.txt` now uses those direct URLs, and `workshop/steam-image-links.json` records verification. The text-only fallback remains. No remote description was edited; actual description rendering after the user saves it remains unverified.

The main mod page is reachable anonymously but still advertised Steam's default Workshop image during this check. This is separate from the description's four repaired URLs and does not establish that the optimized thumbnail has been uploaded. No main-image upload or listing recreation was performed.

### Transparent description revision

On 2026-10-30 the user requested the banner and dividers without backgrounds. `workshop/transparent/` now contains separate PNG replacements with real alpha transparency. The title retains gold lettering and central ornamental rules only; the dividers retain their lettering, rules, cloud/scroll/brush/seal details. Background extraction used the built-in image tool with `transparent_background=true`, followed by native ARGB/PNG export for transparent margins and upload sizes. A targeted second edit removes a stray accent from the final S in Current Features.

Full-resolution edited masters and the full prompt set are retained; the transparent ZIP includes the four upload PNGs, a placeholder BBCode draft and their README/manifest/prompts. All exports are at most 1280 pixels wide and under 1 MB. Zero-alpha background, partial antialiasing, opaque foreground, transparent corners, hashes, dimensions and text/compositing were checked. The existing hosted-image description remains unchanged until new transparent artwork links are supplied. The main mod thumbnail, gameplay and build version are unchanged; no Steam upload/rendering claim is made.
