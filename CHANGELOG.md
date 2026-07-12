# Changelog

All notable changes to the BananaBanana MCP server and this documentation are
recorded here. The format is based on [Keep a Changelog](https://keepachangelog.com/),
and the server follows [Semantic Versioning](https://semver.org/).

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
