# BananaBanana MCP Server

An MCP server for **image generation** and **video generation** — Google **Nano Banana**, **Veo**, and **Omni** models — that lets any MCP client (Claude Code, Claude Desktop, Cursor, and more) create media **pay-as-you-go** with **crypto payments** and **no subscription**.

- **Endpoint:** `https://bananabanana.pro/api/mcp` (streamable HTTP)
- **Auth:** `Authorization: Bearer bb_live_…` — [create a key](https://bananabanana.pro/profile)
- **Website:** <https://bananabanana.pro> · **Docs & live example:** <https://bananabanana.pro/mcp>

Generate images from $0.03 and videos from $0.10, billed per generation from an account
balance you top up with crypto or Telegram Stars. Cost quotes before every expensive
call, automatic refunds on failure, and one shared history with the website.

## Quick Start

First, create an API key in your profile: <https://bananabanana.pro/profile>
(API Keys section). Then add the server to your client.

### Claude Code

```bash
claude mcp add --transport http bananabanana https://bananabanana.pro/api/mcp \
  --header "Authorization: Bearer bb_live_YOUR_KEY"
```

### Claude Desktop

Add this to `claude_desktop_config.json` (Settings → Developer → Edit Config). Requires
[Node.js](https://nodejs.org) for the `mcp-remote` bridge:

```json
{
  "mcpServers": {
    "bananabanana": {
      "command": "npx",
      "args": [
        "-y", "mcp-remote", "https://bananabanana.pro/api/mcp",
        "--header", "Authorization: Bearer bb_live_YOUR_KEY"
      ]
    }
  }
}
```

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
to run `list_models` (free) — it returns the live model list and prices.

## Tools

Seven tools; the read-only ones are free. Full reference in [`docs/tools.md`](./docs/tools.md).

| Tool | What it does | Key parameters |
|---|---|---|
| `list_models` | List models with live USD prices, resolutions, durations, constraints. Free. | — |
| `get_account` | Balance, key name, daily cap, spend today. Free. | — |
| `generate_image` | Text-to-image (Nano Banana 2 Lite / 2 / Pro), up to 4K, 1–4 variants. Returns a `job_id`. | `prompt`, `model`, `aspect_ratio`, `resolution`, `number_of_images`, `confirm_cost` |
| `edit_image` | Multi-turn edit of a finished image by text instruction. | `source_generation_id`, `prompt`, `model`, `resolution` |
| `generate_video` | Video (Veo 3.1 family or Omni Flash). Always quotes first. Returns a `job_id`. | `prompt`, `model`, `duration`, `resolution`, `with_audio`, `confirm_cost` |
| `get_result` | Poll a job; returns hosted media URLs (24 h) + cost/balance. Free. | `job_id`, `wait_seconds` |
| `list_generations` | Recent account history (shared with the website). Free. | `limit`, `type`, `status` |

Generation is async: a `generate_*` call returns a `job_id`; poll `get_result` for the
media. `generate_video` and multi-image `generate_image` **quote first and charge
nothing** until you repeat the call with `confirm_cost`.

## Pricing

Pay-as-you-go, per generated item (USD). Live numbers come from `list_models`; full
tables in [`docs/pricing.md`](./docs/pricing.md).

| Model | Type | Price |
|---|---|---|
| `nano-banana-2-lite` | Image (1024) | $0.03 |
| `nano-banana-2` | Image (512→4096) | $0.03 – $0.13 |
| `nano-banana-pro` | Image (1024→4096) | $0.11 – $0.20 |
| `veo-3.1-lite` | Video (720p/1080p, 4–8 s) | $0.10 – $0.56 |
| `veo-3.1-fast` | Video (up to 4K, 4–8 s) | $0.35 – $2.60 |
| `veo-3.1` | Video (up to 4K, 4–8 s) | $0.70 – $4.40 |
| `omni-flash` | Video (720p, sound, 3–10 s) | $1.00 flat |

Images **$0.03–$0.20**, video **$0.10–$4.40** per clip. Free reads: `list_models`,
`get_account`, `get_result`, `list_generations`. Failed and content-filtered
generations are refunded automatically.

## Why this instead of a subscription service

- **You pay for what you generate — nothing else.** No monthly fee, no seats, no credits
  that expire. A quiet month costs $0; the balance you top up is the only spend.
- **The agent sees the price before it spends.** `list_models` returns live prices, and
  video / batch calls return a quote and charge nothing until confirmed — so an agent
  can't run up a surprise bill.
- **Failures don't cost you.** Upstream errors and content-filter rejections are
  refunded automatically; optional per-key daily caps and `idempotency_key` bound the
  downside further.
- **Crypto or Telegram Stars, no card required.** Top up anonymously; one balance and
  one history are shared between the API and the website.

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
