# Troubleshooting

Two layers can return errors:

- **Transport / auth errors** — HTTP status + a JSON-RPC `error` object (e.g. bad key,
  global rate limit, malformed request).
- **Tool errors** — a normal JSON-RPC result whose payload has `isError: true` and a
  structured body: `error_code`, `message`, `next_step`.

## Connection & auth

### 401 Unauthorized

```json
{ "jsonrpc": "2.0", "id": null, "error": { "code": -32001, "message": "..." } }
```

The response also carries `WWW-Authenticate: Bearer …, resource_metadata="…"` — an
OAuth-capable client uses that pointer to start the sign-in flow. Causes:

- **No `Authorization` header** or it doesn't start with `Bearer `.
- **Malformed key.** Keys are `bb_live_` + 40 hex chars. Check for stray spaces,
  quotes or a truncated copy-paste.
- **Unknown or revoked key.** Create a fresh key at
  <https://bananabanana.pro/profile> and update your client config.
- **Expired OAuth access token.** Tokens live one hour; refresh with the refresh
  token (clients do this automatically). If the refresh fails with `invalid_grant`,
  reconnect the app.
- **Disconnected OAuth app.** Disconnecting it in the profile revokes its tokens —
  connect again.
- **Account blocked.** Contact support@bananabanana.pro.

Note that `initialize`, `ping` and `tools/list` answer *without* credentials, so a
successful `tools/list` does not prove your credential works — test with a tool call
such as `list_models` (free).

Verify quickly:

```bash
curl -s https://bananabanana.pro/api/mcp \
  -H "Authorization: Bearer bb_live_YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"list_models","arguments":{}}}'
```

### I get HTML back / the endpoint "doesn't speak MCP"

Make sure you are pointing at **`https://bananabanana.pro/api/mcp`** (the MCP endpoint),
not `https://bananabanana.pro/mcp` (the human docs page). The transport is
**streamable HTTP** — configure your client as an HTTP/remote server, not stdio.

### 405 on GET or DELETE

Expected. The server is stateless: it only accepts `POST` JSON-RPC. There are no
sessions to open (GET) or terminate (DELETE).

### 400 Parse error

The request body must be valid JSON-RPC 2.0 (`{"jsonrpc":"2.0", ...}`). Usually a
client misconfiguration.

## Rate limiting

### 429 — too many requests (per key)

```json
{ "jsonrpc": "2.0", "id": null, "error": { "code": -32002, "message": "Rate limit exceeded. Wait a minute and retry." } }
```

Sent with `Retry-After: 60`. There is also a tool-level limit — a `tools/call` may
return `error_code: "RATE_LIMITED"` when the **20 tool calls/min per key** ceiling is
hit. Back off ~1 minute, or spread work across keys. Video has a tighter internal
burst limit than images.

## Tool error codes

Returned inside a tool result (`isError: true`) with a `next_step` you can act on:

| `error_code` | Meaning | What to do |
|---|---|---|
| `INVALID_PARAMS` | Bad/again incompatible arguments (e.g. 512 on a model that has no 512). | Fix params; check `list_models` for valid combinations. |
| `NOT_FOUND` | No such `job_id` / `source_generation_id` for this account. | Verify the id with `list_generations`. |
| `INSUFFICIENT_BALANCE` | Balance too low for this generation. | Top up at the profile, then retry. |
| `DAILY_CAP_EXCEEDED` | This key hit its daily USD cap (UTC). | Wait for the next UTC day, use another key, or raise the cap. |
| `RATE_LIMITED` | Too many tool calls this minute. | Wait ~1 minute and retry. |
| `SAFETY_FILTERED` | Google's content filter rejected the prompt **or** the finished file (auto-refunded). The payload carries `upstream_reason` with the exact upstream verdict and `relaxed_filter` with the flag used. | Read `upstream_reason` first: `SAFETY_BLOCK` (rejected before generation) is what `relaxed_filter: true` is for on images and Veo video; `IMAGE_SAFETY` came from the non-configurable output classifier, where the flag changes nothing and only a different prompt helps. On `omni-flash`, which has no such switch and filters video hardest, retry on `veo-3.1-fast`. `RECITATION` is unaffected by the flag — describe the subject generically instead of naming a work, character or brand. See below. |
| `UPSTREAM_FAILED` | Upstream overloaded, out of quota, timed out, or an expired edit source (auto-refunded). | Retry in a minute or two; for edits, generate a fresh video; try a lower resolution or another model. |
| `ACCOUNT_BLOCKED` | Account is blocked. | Contact support@bananabanana.pro. |
| `MAINTENANCE` | Service under maintenance. | Retry in a few minutes. |
| `INTERNAL_ERROR` | Unexpected server error. | Retry; if it persists, contact support@bananabanana.pro. |

Charges for `SAFETY_FILTERED` and `UPSTREAM_FAILED` failures are **refunded
automatically** — the `get_result` payload shows `refunded: true` and the restored
`balance_usd`.

## Two filter stages, and what `relaxed_filter` actually does

Google applies **two independent filters** to every generation, and only the first
one is configurable:

| Stage | When it runs | Typical `upstream_reason` | Configurable? |
|---|---|---|---|
| **1. Request filter** | Before anything is rendered — screens the prompt and any input images. | `SAFETY_BLOCK` (images), prompt-level RAI rejection (Veo) | **Yes** — this is the stage `relaxed_filter: true` loosens (safety thresholds → OFF, `personGeneration` → adults allowed). |
| **2. Output filter** | After the media exists — a classifier inspects the finished image/clip and decides whether to release it. | `IMAGE_SAFETY` (images), `rai_media_filtered_reasons` (Veo) | **No** — no API parameter disables it; it runs identically with `relaxed_filter: true`. |

Practical consequences:

- `relaxed_filter` is the right retry when the request never made it to the model —
  legitimate prompts about real-looking people, medical or anatomical subjects, mild
  fictional violence, edgy artwork.
- Retrying an `IMAGE_SAFETY` failure with `relaxed_filter: true` will fail the same
  way. The image was already produced and rejected on its own merits; only changing
  the prompt (less person-centric, less anatomically explicit, less likeness-specific)
  changes the outcome.
- Neither stage can be bought around: sexual content, minors, real public figures and
  extreme gore stay blocked upstream regardless of the flag.
- Both stages surface as `error_code: "SAFETY_FILTERED"` and both are fully refunded —
  `upstream_reason` is what tells them apart.

## Video jobs

Videos are the slowest and most failure-prone path — plan for polling.

- **Expect 1–10+ minutes.** `generate_video` returns a `job_id` immediately; the clip
  is not ready yet.
- **Poll `get_result`** roughly every **10–15 seconds**, using `wait_seconds` (up to
  30) so each call long-polls instead of returning instantly.
- **`status: "processing"` is normal** for a while. If the payload includes a
  `note` about "high load — automatic retry N of 4", the upstream is busy and the
  server is already retrying for you; keep polling.
- **A video that fails is auto-refunded.** You'll see `status: "failed"`,
  `refunded: true` and an `error_code` (usually `UPSTREAM_FAILED` or
  `SAFETY_FILTERED`).
- **"It's taking too long."** Keep polling — long clips, 4K and audio take longer. If a
  single job runs well beyond ~25 minutes without completing, it will end as `failed`
  and be refunded; start a new job, optionally at a lower resolution or with
  `veo-3.1-fast`.
- **Editing an old omni clip returns `UPSTREAM_FAILED` / expired.** The source
  interaction expired upstream — generate a fresh video instead of editing.

## Results & media URLs

- **Media URLs are signed and valid for 24 hours.** They expire, the media does not —
  call `get_result` again with the same `job_id` for fresh links anytime.
- **Lost a `job_id`?** Use `list_generations` to find recent jobs (shared with your
  website history), then `get_result`.

## Still stuck?

- Docs & live example: <https://bananabanana.pro/mcp>
- Account, keys, balance: <https://bananabanana.pro/profile>
- Support: support@bananabanana.pro
