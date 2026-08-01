# Changelog

All notable changes to the BananaBanana MCP server and this documentation are
recorded here. The format is based on [Keep a Changelog](https://keepachangelog.com/),
and the server follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

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

## [1.0.2] — 2026-07-12

### Changed

- Reworded the server `description` in `server.json` to a clearer pay-as-you-go summary:
  "Generate images & video (Nano Banana, Veo, Omni) pay-as-you-go. No subscription, crypto
  payments." (kept within the registry's 100-character `description` limit). Republished to
  the MCP Registry as 1.0.2 (now the latest version); 1.0.1 remains available but is no
  longer latest.

## [1.0.1] — 2026-07-12

### Fixed

- Corrected the remote endpoint URL in `server.json` to
  `https://bananabanana.pro/api/mcp` (1.0.0 pointed at `https://bananabanana.pro/mcp`,
  which is the human docs page, not the MCP endpoint). Republished to the MCP Registry
  as a new version; 1.0.0 superseded.

## [1.0.0] — 2026-07-12

Initial public release of the BananaBanana remote MCP server.

### Server

- Remote MCP server at `https://bananabanana.pro/api/mcp` over streamable HTTP
  (stateless JSON-RPC — one request per POST, no session id).
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
