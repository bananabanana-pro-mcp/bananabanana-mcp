# Changelog

All notable changes to the BananaBanana MCP server and this documentation are
recorded here. The format is based on [Keep a Changelog](https://keepachangelog.com/),
and the server follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Added `glama.json` so the Glama catalogue can verify repository ownership
  (maintainer `bananabanana-pro`).
- Added a Cursor Plugin manifest — `.cursor-plugin/plugin.json` with a
  `BANANABANANA_API_KEY` variable, plus the plugin-root `mcp.json` that points at the
  streamable-HTTP endpoint and reads the key from that variable. No key is stored in
  the repository.

### Changed

- Pointed the Cursor plugin `logo` at the hosted absolute icon URL
  (`https://bananabanana.pro/mcp-icon-512.png`, the same asset `server.json` uses) so
  catalogue scanners that render the card outside the repository resolve it.

### Fixed

- Listed `top_up` among the free tools in the "Cost transparency" section of
  `docs/pricing.md`; the tool reference and README already counted it as free.

## [1.0.8] — 2026-08-20

### Added

- Added the free `top_up` tool, bringing the live catalogue to ten tools. OAuth
  connections receive a one-time, account-bound deposit-only link valid for 30
  minutes; API-key users receive the normal profile URL.
- Added restricted OAuth top-up sessions with a two-hour sliding idle timeout. URL
  and cookie secrets are stored only as SHA-256 hashes, raw URL tokens are excluded
  from nginx access logs, and the restricted page cannot expose API keys, profile
  data, generation history or promo-code controls.
- Added a top-up link to insufficient-balance errors. Completed `get_result` responses
  now include the remaining balance and add the same link when it is below the
  cheapest image price derived from the application price table.

### Changed

- Changed the `generate_image` default from `nano-banana-2` to the $0.03,
  1024-only `nano-banana-2-lite` model. Callers can choose `nano-banana-2` explicitly
  for 512, 2048 or 4096 output; `edit_image` keeps its existing default.
- Limited OAuth top-up-link issuance to three per minute for each credential. Used,
  expired or cross-browser links return actionable guidance to call `top_up` again.

## [1.0.7] — 2026-08-20

### Added

- Documented all nine live tools, including `edit_video` video-to-video editing and
  synchronous `generate_speech`.
- Added OAuth-first setup instructions and the complete OAuth 2.1 flow, while keeping
  Bearer API keys as the documented option for scripts and CI.
- Added the live speech price, all current image and video prices, top-up bonuses and
  partner promo-code bonuses.
- Added troubleshooting guidance for `DAILY_CAP_EXCEEDED`, insufficient balance,
  rate limits, and the `/mcp` documentation page versus the `/api/mcp` endpoint.

### Changed

- Corrected Omni Flash pricing to $0.10 per output second for a user-selected duration
  of 3–10 seconds; video edits inherit or trim the source duration.
- Clarified that Veo generation accepts 4, 6 or 8 seconds, while the seven-second
  price entries apply to extension jobs.
- Removed the optional `Authorization` header declaration from `server.json` so
  OAuth-capable clients use runtime discovery. Existing Bearer API-key requests remain
  supported by the server.
- Updated the Registry title and description to include speech generation.

Registry history: `1.0.6` was deprecated with status message
“Superseded by 1.0.7 (documentation synced to nine live tools and current pricing;
OAuth discovery is primary).”

## [1.0.6] — 2026-08-16

### Changed

- Clarified that image `relaxed_filter` selects Google's documented Vertex AI
  presets (`safetySettings` thresholds off and adult person generation allowed); it
  does not bypass the independent classifier that inspects finished media.
- Clarified that retrying a legitimate output-stage rejection can still succeed
  because each attempt renders different media, while video `relaxed_filter` is
  near-inert because Google exposes no configurable Veo safety settings.

Registry history: `1.0.5` was deprecated with status message
“Superseded by 1.0.6 (relaxed_filter wording clarified as Google Vertex AI presets)”.

## [1.0.5] — 2026-08-16

### Changed

- **`relaxed_filter` is now documented for what it actually does.** Google applies two
  independent filters: a configurable check on the request *before* generation, and a
  non-configurable classifier that inspects the finished image or clip. `relaxed_filter`
  only loosens the first one. Tool descriptions, the `list_models` content-filter note
  and the `get_result` failure guidance now state this explicitly and report which stage
  fired via `upstream_reason` (`SAFETY_BLOCK` = request stage, `IMAGE_SAFETY` /
  `rai_media_filtered_reasons` = output stage). New reference section:
  [Two filter stages](./docs/troubleshooting.md#two-filter-stages-and-what-relaxed_filter-actually-does).

Registry history: `1.0.4` was deprecated with status message
“Superseded by 1.0.5 (relaxed_filter semantics documented per Google's two filter
stages).”

## [1.0.4] — 2026-08-01

### Added

- **OAuth 2.1 sign-in** alongside API keys. The server is now a full OAuth
  authorization server for its own MCP endpoint: PKCE (S256), dynamic client
  registration (RFC 7591), protected resource metadata (RFC 9728), authorization
  server metadata (RFC 8414) and resource indicators (RFC 8707). Connector-style
  clients — claude.ai, Claude Desktop, Claude mobile, Claude Code, MCP Inspector —
  connect by pasting `https://bananabanana.pro/api/mcp` and signing in; there is no
  key to copy. Access tokens live one hour, refresh tokens rotate on every use, and
  connected apps can be disconnected from the profile at any time.
  Documented in [`docs/authentication.md`](./docs/authentication.md).
- **Lazy authentication.** `initialize`, `ping` and `tools/list` answer without
  credentials so a client can inspect the tool catalogue before signing in; a
  `tools/call` without a valid token returns `401` with
  `WWW-Authenticate: Bearer …, resource_metadata="…"`, which is what starts the
  OAuth flow.
- New tool **`edit_video`** — video-to-video editing on Gemini Omni Flash: restyle,
  replace objects or relight an existing clip while keeping its motion and
  composition. The source is either a completed video on the account
  (`source_generation_id`) or a public link (`video_url`); it is normalised to MP4
  720p and the first 10 seconds (model limit). Billed per second of output with the
  usual quote-then-`confirm_cost` flow and automatic refunds on failure.
  Documented in [`docs/tools.md`](./docs/tools.md).
- **Image inputs for `generate_video`** — `first_frame` animates a still picture and
  `reference_images` (up to 10) keep a subject, character or style consistent. Each is
  either the `job_id` of a completed image generation on the account or a public image
  URL, so nothing has to be uploaded as base64. On `omni-flash` a start frame and
  references combine (10 images per request in total); on Veo they are mutually
  exclusive, with at most 3 references and `duration: 8`.

### Changed

- **`omni-flash` is now billed per second — $0.10/s ($0.30 for 3 s … $1.00 for 10 s)**
  instead of a flat $1.00, and `generate_video` accepts an exact `duration` of 3–10 s
  for it (previously the model chose the length itself).
- **Editing keeps the source length.** The model cannot stretch or shorten a clip, so
  the output of `edit_video` and of a conversational `edit_from_generation_id` edit is
  always exactly as long as its source. `edit_video` therefore accepts `duration` only
  as a *trim*: it cuts the source to its first N seconds and charges for those. The
  quote resolves the source first and reports `duration_seconds`,
  `source_duration_seconds` and — for `video_url` sources — a `source_ref` you can pass
  back with `confirm_cost` to avoid downloading the clip twice.

Registry history: `1.0.3` was deprecated with status message
“Superseded by 1.0.4 (OAuth 2.1 sign-in; Authorization header no longer required)”.

## [1.0.3] — 2026-07-16

### Added

- Server icon (512×512, [`assets/icon-512.png`](./assets/icon-512.png), hosted at
  <https://bananabanana.pro/mcp-icon-512.png>) declared via the `icons` field of
  `server.json`, so MCP directories and clients can display a logo. Republished to
  the MCP Registry as 1.0.3 (latest); 1.0.2 deprecated, endpoint unchanged.
- Docs: no-SDK usage guide [`examples/no-sdk.md`](./examples/no-sdk.md) — calling the
  server as plain JSON-RPC over HTTPS from curl, Python and TypeScript, mirroring
  <https://bananabanana.pro/mcp#code> — plus runnable scripts
  [`examples/generate.py`](./examples/generate.py) and
  [`examples/generate.mjs`](./examples/generate.mjs).

Registry history: `1.0.2` was deprecated with status message
“Superseded by 1.0.3 (added server icon). Endpoint unchanged:
https://bananabanana.pro/api/mcp”.

## [1.0.2] — 2026-07-12

### Changed

- Reworded the server `description` in `server.json` to a clearer pay-as-you-go summary:
  "Generate images & video (Nano Banana, Veo, Omni) pay-as-you-go. No subscription, crypto
  payments." (kept within the registry's 100-character `description` limit). Republished to
  the MCP Registry as 1.0.2 (now the latest version); 1.0.1 remains available but is no
  longer latest.

Registry history: `1.0.1` was deprecated with status message
“Superseded by 1.0.2 (reworded description). Endpoint unchanged:
https://bananabanana.pro/api/mcp”.

## [1.0.1] — 2026-07-12

### Fixed

- Corrected the remote endpoint URL in `server.json` to
  `https://bananabanana.pro/api/mcp` (1.0.0 pointed at `https://bananabanana.pro/mcp`,
  which is the human docs page, not the MCP endpoint). Republished to the MCP Registry
  as a new version; 1.0.0 superseded.

Registry history: `1.0.0` was deprecated with status message
“Wrong endpoint URL (docs page). Use 1.0.1:
https://bananabanana.pro/api/mcp”.

## [1.0.0] — 2026-07-12

Initial public release of the BananaBanana remote MCP server.

The published Registry descriptor mistakenly used the human documentation page
`https://bananabanana.pro/mcp` as its remote endpoint. Version 1.0.1 corrected it to
`https://bananabanana.pro/api/mcp`.

### Server

- Remote MCP server over streamable HTTP (stateless JSON-RPC — one request per POST,
  no session id). The intended production endpoint was
  `https://bananabanana.pro/api/mcp`; the Registry URL was corrected in 1.0.1.
- Bearer API-key authentication (`bb_live_…`), keys hashed at rest and shown once.
- Seven tools: `list_models`, `get_account`, `generate_image`, `edit_image`,
  `generate_video`, `get_result`, `list_generations`.
- Image models: Nano Banana 2 Lite, Nano Banana 2, Nano Banana Pro (up to 4K).
- Video models: Veo 3.1, Veo 3.1 Fast, Veo 3.1 Lite (4–8 s, up to 4K, optional
  native audio) and Gemini Omni Flash (always with sound, conversational editing).
- Mandatory cost confirmation (`confirm_cost`) for video and multi-image batches:
  the first call returns a quote and charges nothing.
- Automatic refunds on upstream failure and content-filter rejection.
- Optional `idempotency_key` so retries never double-charge.
- Per-key rate limit (20 tool calls/min) and optional per-key daily spend cap.
- Signed media URLs valid for 24 hours.
- Published in the official MCP Registry as `pro.bananabanana/image-video`.

### Docs

- Authentication, tools, pricing and troubleshooting guides.
- Client setup examples for Claude Code, Claude Desktop, Cursor, VS Code, Windsurf.
