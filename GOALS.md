# Next goals — HTTP Request → Image Filter (multi-URL)

## Done

- [x] `HttpRequestPiece`: `urls: List[str]` → `base64_bytes_data: List[str]`
- [x] `ImageFilterPiece`: `input_images: List[str]` → list outputs + indexed file names
- [x] Tests for single and multiple URLs/images
- [x] README workflow section

---

## Bug fixes (fix broken or fragile behavior)

| Priority | Goal | Why |
|----------|------|-----|
| **P0** | Validate HTTP responses are images before Image Filter | Non-image bodies (HTML/JSON/404) crash PIL with an opaque error |
| **P0** | Error on empty `urls` / `input_images` | Empty lists silently return nothing — easy to misconfigure |
| **P1** | Partial failure for multi-URL fetch | One bad URL currently aborts the entire batch |
| **P1** | Partial failure for multi-image filter | One bad entry currently aborts the entire batch |
| **P2** | Downstream wiring after Image Filter | `SaveImagePiece` still expects single `base64_data: str`; list outputs don't connect |
| **P2** | Confirm Domino edge mapping in UI | `base64_bytes_data` → `input_images` may need manual field selection |

---

## Features (nice to have, not strictly broken)

| Priority | Goal | Why |
|----------|------|-----|
| **P1** | Attach source URL to each output | `modified_image_0.png` has no metadata — hard to debug which URL failed |
| **P2** | Multi-image canvas preview | `display_result` only shows the first filtered image |
| **P2** | Optional content-type / URL check in HttpRequest | Skip or flag URLs that don't return `image/*` |
| **P3** | Parallel HTTP requests | Sequential fetch is slow for many URLs |
| **P3** | Backward-compat shim (`url` + `urls`) | Old saved workflows break without reconfigure — only if we care |
| **P3** | Per-URL HTTP settings | Same method/body for all URLs — limit if URLs need different configs |

---

## Suggested order

1. **Validate image responses** (P0) — biggest real-world failure mode for Image Filter workflow
2. **Reject empty inputs** (P0) — cheap, clear error messages
3. **Partial failure + URL in output** (P1) — makes multi-URL runs usable in practice
4. **SaveImage / downstream** (P2) — only if the workflow continues past Image Filter
5. **Preview + perf** (P2–P3) — polish once core path is stable

---

## Out of scope (for now)

- PageScrapper multi-URL (separate piece / goal)
- Workflow-level foreach instead of in-piece batching
- New combined "batch fetch + filter" piece
