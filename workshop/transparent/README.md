# Transparent description graphics

Use the four PNG files in this folder as replacements for the earlier opaque description graphics. All have real alpha transparency: the lettering and ornaments remain, with no teal/black panel or scene behind them. The main title keeps only its gold text and central ornamental rules. The main mod cover/thumbnail is not included or changed.

| File | Size | Purpose |
|---|---:|---|
| `workshop-banner-transparent.png` | 855,476 bytes | Main description title |
| `divider-current-features-transparent.png` | 331,552 bytes | Current Features section |
| `divider-planned-features-transparent.png` | 357,352 bytes | Planned Features section |
| `divider-alpha-feedback-transparent.png` | 312,824 bytes | Early Alpha & Feedback section |

## Upload and use

Upload these PNGs as artwork accessible to visitors. Keep PNG format; JPEG cannot retain their transparency. Obtain the direct image address for each new upload, then replace the matching image tag in your description. Artwork page links (`steamcommunity.com/sharedfiles/filedetails/?id=...`) are not direct image addresses. Send the artwork links here if you want the direct URLs resolved again.

`description-transparent.bbcode.txt` is the current description with four clearly named placeholders for the new transparent uploads. The existing `../description.bbcode.txt` still points to the verified older images so it is not silently broken before replacement uploads exist. Nothing was uploaded or published by the agent.

## Source and checks

Background extraction was performed using the built-in image editor with transparency enabled. Full prompts, including the small final-letter correction, are in `generation-prompts.json`. Edited full-resolution masters are retained under `source/` on disk but excluded from the download ZIP. Windows ARGB/PNG encoding trimmed empty alpha margins and resized exports to at most 1280 pixels wide with transparent padding; it did not paint a replacement background.

`manifest.json` records dimensions, byte sizes, hashes, transparent/partial/opaque pixel counts and original edited-master hashes. All files contain zero-alpha background pixels and nonzero-alpha foreground detail. Corners are fully transparent; all uploads are below 1,000,000 bytes. Text and compositing over a dark inspection background were reviewed. The inspection background is not part of the PNGs. Steam rendering of these new assets is still untested.
