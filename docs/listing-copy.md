# Canonical listing copy

Use this file as the source of truth when a directory does not refresh its card from
the official MCP Registry. Prices can change; the free `list_models` tool is the live
source for the current model catalogue and price matrix.

## Short description (90 characters)

Generate images, video & speech with Nano Banana, Veo, Omni and Gemini TTS. Pay as you go.

This is identical to the `description` in `server.json`.

## Medium description

BananaBanana is a hosted remote MCP server for image generation and editing, video
generation and video-to-video editing, and speech generation. It combines Nano Banana,
Veo, Omni Flash and Gemini TTS behind nine tools, with OAuth 2.1 sign-in, pay-as-you-go
pricing, cost confirmation before every video job, and automatic refunds on failure.

## Long description

BananaBanana is a hosted remote MCP server for creating images, video and speech from
an MCP client. Its nine live tools cover model and account discovery, image generation
and editing, video generation and video-to-video editing, synchronous speech generation,
job polling and generation history. It works with Claude Code, Claude Desktop, Cursor,
VS Code, Windsurf and other clients that support remote Streamable HTTP MCP servers.

Unlike a thin wrapper around a single Gemini API, BananaBanana does not require the
user to install a runtime or supply a Google API key. It provides one hosted endpoint
for the Nano Banana image family, the Veo 3.1 video family, Omni Flash video generation
and editing, and Gemini TTS. The service also owns the account balance, exact preflight
quotes, per-credential daily spend caps, generation history and automatic refunds when
an upstream job fails or is rejected by a content filter.

Authentication is OAuth 2.1 first: add
`https://bananabanana.pro/api/mcp`, sign in in the browser and approve the connection.
The server supports PKCE S256, dynamic client registration, protected-resource and
authorization-server discovery, refresh tokens and resource indicators. Bearer API
keys remain available for scripts, CI and clients without OAuth.

Pricing is pay as you go in USD. Images cost **$0.03–$0.20 each**. New Veo generations
cost **$0.10–$4.40 per 4-, 6- or 8-second clip**, depending on model, resolution and
audio; seven-second price entries apply to extension jobs. Omni Flash costs
**$0.10 per output second** for a user-selected 3–10 second clip, so a clip costs
**$0.30–$1.00**; video edits inherit the source length or use a shorter requested trim.
Gemini TTS costs **$0.01 per started 200 transcript characters**. The free
`list_models` tool returns the current complete matrix before anything is generated.

The balance is funded with cryptocurrency. Deposits of $50 or more receive 5% extra
balance, and deposits of $100 or more receive 10% extra balance. While a partner promo
code is active it adds another 10%; the promo and deposit bonus stack, so a $100 deposit
with an active code credits $120. These bonuses lower the effective out-of-pocket cost
of generations without changing their displayed balance charge.

## Current price summary

| Model | Current price |
|---|---:|
| `nano-banana-2-lite` | $0.03 at 1024 |
| `nano-banana-2` | $0.03 at 512; $0.06 at 1024; $0.09 at 2048; $0.13 at 4096 |
| `nano-banana-pro` | $0.11 at 1024 or 2048; $0.20 at 4096 |
| `veo-3.1-lite` | $0.10–$0.56 per 4/6/8-second clip |
| `veo-3.1-fast` | $0.35–$2.60 per 4/6/8-second clip |
| `veo-3.1` | $0.70–$4.40 per 4/6/8-second clip |
| `omni-flash` | $0.10 per output second; 3–10 seconds ($0.30–$1.00) |
| `gemini-3.1-flash-tts-preview` | $0.01 per started 200 transcript characters |

Veo prices vary by resolution and audio. Use `list_models` for every exact
model/resolution/audio combination.

## Tool list

- `list_models` — list the live model catalogue, USD prices, durations, resolutions and
  constraints; free.
- `get_account` — show balance, credential identity, daily cap and spend today; free.
- `generate_image` — generate one to four images with the Nano Banana family; paid.
- `edit_image` — edit a completed image with a text instruction; paid.
- `generate_video` — generate a Veo or Omni Flash clip, optionally using image inputs;
  paid and always quoted before it starts.
- `edit_video` — edit an existing video with Omni Flash while retaining or trimming its
  duration; paid and always quoted before it starts.
- `generate_speech` — synchronously render one- or two-speaker Gemini TTS audio as mono
  24 kHz, 16-bit WAV; paid.
- `get_result` — poll an asynchronous image or video job and return its media URLs,
  cost and remaining balance; free.
- `list_generations` — list recent generation history for the account; free.

## Client configurations

The OAuth form comes first in every example. Do not add an `Authorization` header to
that form: the client discovers OAuth from the server at runtime and stores and
refreshes the resulting token itself.

### Claude Code

OAuth:

```bash
claude mcp add --transport http bananabanana https://bananabanana.pro/api/mcp
```

Run `/mcp` inside Claude Code and choose **Authenticate** when prompted.

Bearer API-key fallback for scripts or non-interactive environments:

```bash
claude mcp add --transport http bananabanana \
  https://bananabanana.pro/api/mcp \
  --header "Authorization: Bearer bb_live_YOUR_KEY"
```

### Claude Desktop

In a build with custom remote connectors, add the endpoint URL directly and complete
the browser sign-in. For the JSON configuration used by desktop builds that need the
`mcp-remote` bridge, OAuth is:

```json
{
  "mcpServers": {
    "bananabanana": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://bananabanana.pro/api/mcp"
      ]
    }
  }
}
```

Bearer API-key fallback:

```json
{
  "mcpServers": {
    "bananabanana": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://bananabanana.pro/api/mcp",
        "--header",
        "Authorization: Bearer bb_live_YOUR_KEY"
      ]
    }
  }
}
```

### Cursor

OAuth (`.cursor/mcp.json` or the user-level MCP configuration):

```json
{
  "mcpServers": {
    "bananabanana": {
      "url": "https://bananabanana.pro/api/mcp"
    }
  }
}
```

Bearer API-key fallback:

```json
{
  "mcpServers": {
    "bananabanana": {
      "url": "https://bananabanana.pro/api/mcp",
      "headers": {
        "Authorization": "Bearer bb_live_YOUR_KEY"
      }
    }
  }
}
```

### VS Code

OAuth (`.vscode/mcp.json` or the user MCP configuration):

```json
{
  "servers": {
    "bananabanana": {
      "type": "http",
      "url": "https://bananabanana.pro/api/mcp"
    }
  }
}
```

Bearer API-key fallback:

```json
{
  "inputs": [
    {
      "id": "bb-api-key",
      "type": "promptString",
      "description": "BananaBanana API key",
      "password": true
    }
  ],
  "servers": {
    "bananabanana": {
      "type": "http",
      "url": "https://bananabanana.pro/api/mcp",
      "headers": {
        "Authorization": "Bearer ${input:bb-api-key}"
      }
    }
  }
}
```

### Windsurf

OAuth (`~/.codeium/mcp_config.json`):

```json
{
  "mcpServers": {
    "bananabanana": {
      "serverUrl": "https://bananabanana.pro/api/mcp"
    }
  }
}
```

Bearer API-key fallback:

```json
{
  "mcpServers": {
    "bananabanana": {
      "serverUrl": "https://bananabanana.pro/api/mcp",
      "headers": {
        "Authorization": "Bearer bb_live_YOUR_KEY"
      }
    }
  }
}
```

## FAQ

### Do I need an API key?

Not in an OAuth-capable client. Add the remote endpoint, sign in and approve access.
Create a Bearer API key only for scripts, CI or a client without OAuth support.

### Do I need a subscription?

No. Generations are charged against a prepaid balance; there is no monthly subscription.

### How do I pay?

Fund the balance with cryptocurrency. Deposit-size bonuses and an active partner promo
code can add extra balance as described above.

### How much does generation cost?

Images cost $0.03–$0.20 each. Veo costs $0.10–$4.40 per new 4/6/8-second clip.
Omni Flash costs $0.10 per output second for 3–10 seconds, and speech costs $0.01 per
started 200 transcript characters. Run the free `list_models` tool for the complete
current matrix.

### Who selects the duration?

The user selects 4, 6 or 8 seconds for a new Veo generation and any whole duration from
3 through 10 seconds for Omni Flash. A seven-second Veo price applies to extension jobs,
not to a new generation. Video edits inherit the source duration unless the user asks
to trim it shorter.

### What happens if generation fails?

Upstream failures and content-filter rejections are refunded automatically.

### Can an agent spend without confirmation?

Every video generation or edit returns an exact cost quote and charges nothing until
the same request is repeated with that `confirm_cost`. Multi-image generation also uses
cost confirmation. A per-credential daily spend cap can impose an additional limit.

### Is this a wrapper around my Gemini API key?

No. It is a hosted remote service with its own balance, job history, quotes and refunds.
Users do not provide a Google API key or run a local Gemini wrapper.

### Which URL should I configure?

Use `https://bananabanana.pro/api/mcp`. The shorter
`https://bananabanana.pro/mcp` URL is the human documentation page.

### What are the rate limits?

Each credential is limited to 20 tool calls per minute. A paid call can also be blocked
by insufficient balance or an optional daily spend cap.

## Manual marketplace checklist

### Smithery

- Open the existing `support-dbuq/bananabanana` card and confirm the account can edit it.
- Replace the short and long description with the canonical copy above; include image,
  video, video-to-video and speech generation.
- Set the remote endpoint to `https://bananabanana.pro/api/mcp` and make OAuth discovery
  the primary authentication path. Do not require an API-key configuration field;
  mention Bearer keys only as the fallback.
- Refresh or rescan the tool catalogue and verify that all nine tools appear, especially
  `edit_video` and `generate_speech`.
- Replace flat or model-selected Omni wording with $0.10 per user-selected output second
  for 3–10 seconds; keep Veo at 4/6/8 seconds for new clips and note seven seconds only
  for extension jobs.
- Replace the payment, bonus and promo text with the canonical copy; remove every
  reference to Telegram Stars.
- Verify the repository, website, docs, icon and Apache-2.0 license links.

### mcp.so

- Click **Claim** on the existing `bananabanana-mcp` card before editing it.
- Update **About**, **Overview**, **Config**, **Tools** and **FAQ** from this file.
- Make the headerless OAuth config the first config and keep the Bearer config second.
- Change the visible tool count from seven to nine and add `edit_video` and
  `generate_speech`; paid tools total five and free tools total four.
- Remove the stale statements that Omni is a flat $1.00, that its duration is chosen by
  the model, and that payment supports Telegram Stars.
- Add speech to the title/description and add relevant speech and video-editing tags if
  the form exposes tags.
- Verify the repository, homepage, documentation, icon, category and Apache-2.0 license.

### LobeHub

- Search for the exact official BananaBanana card and distinguish it from unrelated
  local "Nano Banana MCP" wrappers. If the official card is absent, use **Submit MCP**
  with this repository and the official Registry identity
  `pro.bananabanana/image-video`; do not edit another project's card.
- Use the canonical short and long description, nine-tool list, pricing, payment and FAQ.
- Mark it as a hosted remote Streamable HTTP server, not a local npm/Python server, and
  use `https://bananabanana.pro/api/mcp` as the endpoint.
- Put the headerless OAuth config first and the Bearer API-key fallback second.
- Set the category to media generation, license to Apache-2.0, and verify the repository,
  website, documentation and icon links.
- After publication, verify that the card shows video-to-video and speech rather than
  describing a single-model Gemini image wrapper.
