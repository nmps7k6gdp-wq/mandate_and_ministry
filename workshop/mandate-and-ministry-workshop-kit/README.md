# Steam Workshop description kit

Created 2026-10-30 with the built-in image-generation tool. These are separate description assets. The main mod image (`thumbnail.png`) is deliberately excluded and remains unchanged.

## Files and placement

| Description placeholder | Asset |
|---|---|
| `BANNER_IMAGE_URL` | `assets/workshop-banner.jpg` |
| `CURRENT_FEATURES_IMAGE_URL` | `assets/divider-current-features.jpg` |
| `PLANNED_FEATURES_IMAGE_URL` | `assets/divider-planned-features.jpg` |
| `ALPHA_FEEDBACK_IMAGE_URL` | `assets/divider-alpha-feedback.jpg` |

`description.bbcode.txt` contains the finished description layout. Upload the four optimized JPGs to an image host accepted by Steam's Workshop description editor, obtain the direct image URLs, and replace the four placeholders inside their `[img]...[/img]` tags. Local Windows paths do not embed an image in a public Workshop description. A Steam artwork/detail-page URL is not the same as its direct image URL. Check the actual Workshop preview before saving.

Paste the BBCode file's contents into the description editor. No upload or publication was performed by the agent. Plain paragraphs are retained for accessible, easy-to-update feature information; only the banner and section headings are images. The informational content separates implemented features, future plans and alpha caveats.

`description-text-only.bbcode.txt` provides the same description with native BBCode headings if image hosting is not ready or the editor rejects an image link. The updated ZIP includes both versions, the four small JPGs, the full prompts and manifests. Large original PNGs remain on disk for future editing and are deliberately excluded from the ZIP.

## Main thumbnail fix and upload sizes

The launcher publisher log on 2026-10-30 at 18:33:58 UTC explicitly reported that this mod's original 2,807,787-byte thumbnail was too large and skipped it. The optimized main `thumbnail.png` is now 512 × 512 and 631,735 bytes. The same file is included as `mod-thumbnail.png` in this kit for convenience. It belongs to the Workshop item's main preview and is NOT used inside the description. Both descriptors still reference `thumbnail.png`; the published item ID is preserved.

Steam's primary Workshop preview limit is less than 1 MB, per https://partner.steamgames.com/doc/api/ISteamUGC#SubmitItemUpdateResult_t . The description banner is 246,239 bytes; the three dividers are 92,756, 76,706 and 81,532 bytes. Use the JPG versions for uploads. The original main cover is preserved byte-for-byte as root `thumbnail-original.png`.

Close and reopen the Paradox launcher, then update the existing Steam item `3830313941` through its mod upload/update action; do not create a new listing. Merely changing a local file does not update Steam's stored preview. The local launcher database currently identifies this as a local mod and has no thumbnail path/URL registered. A refreshed local tile is not yet verified; do not rewrite the launcher database or delete playsets/cache to force one. The corrected preview upload still needs user execution/confirmation.

Valve's formatting help: https://steamcommunity.com/comment/WorkshopItem/formattinghelp

## Artwork and reproduction

The original dark teal/antique gold illustrations were generated without supplying the main mod image as an image reference. Full prompts are in `generation-prompts.json`; original source/copy hashes are in `assets-manifest.json`, while `optimized-assets-manifest.json` records upload exports. Optimization uses Windows image resizing and PNG/JPEG encoding without regenerating the artwork. The banner uses a distinct desk-and-ledger composition; the dividers use scroll, brush and seal motifs. No game screenshot, official Paradox branding or third-party artwork is embedded.

Visual review: title and all three section labels checked; all files use opaque backgrounds. Steam's actual hosted-image rendering remains untested. The later optimization changes the main thumbnail's dimensions/encoding only; no gameplay, saved identity, descriptor reference or build-version change is involved.
