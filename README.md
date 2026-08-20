# BananaBanana MCP Server

An MCP server for **image, video, and speech generation** — Google **Nano Banana**, **Veo**, **Omni**, and **Gemini TTS** models — that lets any MCP client (Claude Code, Claude Desktop, Cursor, and more) create media **pay-as-you-go** with **crypto payments** and **no subscription**.

- **Endpoint:** `https://bananabanana.pro/api/mcp` (streamable HTTP)
- **Auth:** OAuth 2.1 (sign in — nothing to copy) or `Authorization: Bearer bb_live_…` — [create a key](https://bananabanana.pro/profile)
- **Website:** <https://bananabanana.pro> · **Docs & live example:** <https://bananabanana.pro/mcp>

Generate images from $0.03, videos from $0.10, and speech for $0.01 per started 200
transcript characters, billed from an account balance you top up with crypto. Cost
quotes before every expensive call, automatic refunds on failure, and one shared
image/video history with the website.

## Quick Start

OAuth is the primary connection path. API keys remain available for clients without
OAuth and for scripts or CI:

- **OAuth 2.1** (claude.ai, Claude Desktop, Claude mobile, Claude Code, MCP Inspector):
  add a custom connector with the URL above, press Connect and approve access. No key
  to copy. See [docs/authentication.md](./docs/authentication.md).
- **API key** (Cursor, VS Code, Windsurf, Codex, scripts, CI): create a key in your
  profile — <https://bananabanana.pro/profile>, API Keys section — and put it in the
  client config as shown below.

### claude.ai / Claude Desktop / mobile (OAuth)

```
Settings → Connectors → Add custom connector
URL: https://bananabanana.pro/api/mcp
→ Add → Connect → approve access on bananabanana.pro
```

### Claude Code

```bash
# OAuth — no key; run /mcp inside Claude Code and choose "Authenticate"
claude mcp add --transport http bananabanana https://bananabanana.pro/api/mcp

# API-key fallback for non-interactive use
claude mcp add --transport http bananabanana https://bananabanana.pro/api/mcp \
  --header "Authorization: Bearer bb_live_YOUR_KEY"
```

### Claude Desktop

Use **Settings → Connectors → Add custom connector** and enter
`https://bananabanana.pro/api/mcp`, then press **Connect** and approve access. If your
Desktop build uses `claude_desktop_config.json`, the OAuth-capable `mcp-remote` bridge
requires [Node.js](https://nodejs.org):

```json
{
  "mcpServers": {
    "bananabanana": {
      "command": "npx",
      "args": [
        "-y", "mcp-remote", "https://bananabanana.pro/api/mcp"
      ]
    }
  }
}
```

The bridge opens the OAuth sign-in flow on first use. See
[`docs/authentication.md`](./docs/authentication.md) for the API-key fallback.

<details>
<summary><b>Other clients (Cursor, VS Code, Windsurf)</b></summary>

**Cursor** — `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (project):

```json
{
  "mcpServers": {
    "bananabanana": {
      "url": "https://bananabanana.pro/api/mcp",
      "headers": { "Authorization": "Bearer bb_live_YOUR_KEY" }
    }
  }
}
```

**VS Code** — `.vscode/mcp.json` (stores the key as an encrypted prompt):

```json
{
  "servers": {
    "bananabanana": {
      "type": "http",
      "url": "https://bananabanana.pro/api/mcp",
      "headers": { "Authorization": "Bearer ${input:bb-api-key}" }
    }
  },
  "inputs": [
    { "type": "promptString", "id": "bb-api-key", "description": "BananaBanana API key (bb_live_…)", "password": true }
  ]
}
```

**Windsurf** — `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "bananabanana": {
      "serverUrl": "https://bananabanana.pro/api/mcp",
      "headers": { "Authorization": "Bearer bb_live_YOUR_KEY" }
    }
  }
}
```

</details>

Ready-to-copy configs live in [`examples/`](./examples). Once connected, ask your agent
to run `list_models` (free) — it returns the live model list and prices. An OAuth user
can also ask the agent to call `top_up`; the returned browser link grants deposit-only
access without exposing the full profile.

**No MCP client?** The server is plain JSON-RPC over HTTPS — call it from curl, Python
or TypeScript with no SDK: [`examples/no-sdk.md`](./examples/no-sdk.md) (runnable
scripts: [`generate.py`](./examples/generate.py), [`generate.mjs`](./examples/generate.mjs)).

## Tools

Ten tools; the read-only and account-access tools are free. Full reference in
[`docs/tools.md`](./docs/tools.md).

| Tool | What it does | Key parameters |
|---|---|---|
| `list_models` | List models with live USD prices, resolutions, durations, constraints. Free. | — |
| `get_account` | Balance, key name, daily cap, spend today. Free. | — |
| `top_up` | Return a balance top-up link. OAuth gets a one-time deposit-only link; API-key users get the profile URL. Free. | — |
| `generate_image` | Text-to-image (Nano Banana 2 Lite / 2 / Pro), up to 4K, 1–4 variants. Lite is the default; choose Nano Banana 2 for resolutions above 1024. Returns a `job_id`. | `prompt`, `model`, `aspect_ratio`, `resolution`, `number_of_images`, `confirm_cost` |
| `edit_image` | Multi-turn edit of a finished image by text instruction. | `source_generation_id`, `prompt`, `model`, `resolution` |
| `generate_video` | Video (Veo 3.1 family or Omni Flash), optionally from a start frame and reference images. Always quotes first. Returns a `job_id`. | `prompt`, `model`, `duration`, `resolution`, `with_audio`, `first_frame`, `reference_images`, `confirm_cost` |
| `edit_video` | Video-to-video editing on Omni Flash: restyle, replace objects, relight an existing clip. Always quotes first. | `prompt`, `source_generation_id` or `video_url`, `duration`, `audio_prompt`, `confirm_cost` |
| `generate_speech` | Gemini 3.1 Flash TTS speech: one speaker or a two-speaker dialogue. Returns a hosted WAV URL synchronously. | `text`, `voice`, `language_code`, `style`, `speakers` |
| `get_result` | Poll a job; returns hosted media URLs (24 h) + cost/balance. Free. | `job_id`, `wait_seconds` |
| `list_generations` | Recent account history (shared with the website). Free. | `limit`, `type`, `status` |

Image and video generation is async: generation/editing calls return a `job_id`; poll
`get_result` for the media. `generate_speech` is synchronous and returns its WAV URL
directly. `generate_video`, `edit_video` and multi-image `generate_image` **quote first
and charge nothing** until you repeat the call with `confirm_cost`.

## Pricing

Pay-as-you-go in USD: per image, per Veo clip, per second for Omni Flash, and per
started 200 transcript characters for speech. Live numbers come from `list_models`;
full tables in [`docs/pricing.md`](./docs/pricing.md).

| Model | Type | Price |
|---|---|---|
| `nano-banana-2-lite` | Image (1024) | $0.03 |
| `nano-banana-2` | Image (512→4096) | $0.03 – $0.13 |
| `nano-banana-pro` | Image (1024→4096) | $0.11 – $0.20 |
| `veo-3.1-lite` | Video (720p/1080p; 4, 6 or 8 s) | $0.10 – $0.56 |
| `veo-3.1-fast` | Video (up to 4K; 4, 6 or 8 s) | $0.35 – $2.60 |
| `veo-3.1` | Video (up to 4K; 4, 6 or 8 s) | $0.70 – $4.40 |
| `omni-flash` | Video (720p, sound, 3–10 s) | $0.10 / s ($0.30 – $1.00) |
| `gemini-3.1-flash-tts-preview` | Speech (WAV) | $0.01 / started 200 transcript characters |

Images cost **$0.03–$0.20** each; video costs **$0.10–$4.40** per clip, with Omni
Flash billed at **$0.10/s**. Veo generation accepts 4, 6 or 8 seconds; the 7-second
prices returned by `list_models` are for extension jobs, not a selectable
`generate_video` duration. Free tools: `list_models`, `get_account`, `top_up`,
`get_result`, `list_generations`. Failed and content-filtered generations are refunded
automatically.

Top-up bonuses can lower the effective cost: deposits of $50+ receive 5% extra
balance, deposits of $100+ receive 10%, and an active partner promo code adds another
10%. Bonuses stack. The table shows nominal generation charges; effective
out-of-pocket cost depends on the top-up bonus. Promo codes require a normal signed-in
profile and are intentionally unavailable in an OAuth deposit-only session.

## Why this instead of a subscription service

- **You pay for what you generate — nothing else.** No monthly fee, no seats, no credits
  that expire. A quiet month costs $0; the balance you top up is the only spend.
- **The agent sees the price before it spends.** `list_models` returns live prices, and
  video / batch calls return a quote and charge nothing until confirmed — so an agent
  can't run up a surprise bill.
- **Failures don't cost you.** Upstream errors and content-filter rejections are
  refunded automatically; optional per-key daily caps and `idempotency_key` bound the
  downside further.
- **Crypto top-ups, no card required.** Deposits of $50+ / $100+ receive 5% / 10%
  extra balance, and an active partner promo code adds another 10%. One balance and
  one image/video history are shared between MCP and the website.

## Registry

Published in the official [MCP Registry](https://github.com/modelcontextprotocol/registry)
as **`pro.bananabanana/image-video`**. The canonical descriptor is
[`server.json`](./server.json). Look it up:

```bash
curl -s "https://registry.modelcontextprotocol.io/v0/servers?search=pro.bananabanana/image-video"
```

## Links

- **Website:** <https://bananabanana.pro>
- **MCP docs & live example:** <https://bananabanana.pro/mcp>
- **Create an API key:** <https://bananabanana.pro/profile>
- **Authentication** · [`docs/authentication.md`](./docs/authentication.md)
- **Tools reference** · [`docs/tools.md`](./docs/tools.md)
- **Pricing & limits** · [`docs/pricing.md`](./docs/pricing.md)
- **Troubleshooting** · [`docs/troubleshooting.md`](./docs/troubleshooting.md)
- **Support:** support@bananabanana.pro

## License

[Apache-2.0](./LICENSE) © BananaBanana. This repository is public documentation only —
it contains no server source code, keys, or secrets.
