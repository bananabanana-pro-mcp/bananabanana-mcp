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
- **Malformed key.** Keys start with `bb_live_`. Check for stray spaces, quotes or a
  truncated copy-paste.
- **Unknown or revoked key.** Create a fresh key at
  <https://bananabanana.pro/profile> and update your client config.
- **Expired OAuth access token.** OAuth-capable clients refresh tokens automatically.
  If refresh fails with `invalid_grant`, reconnect the app.
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

Follow `Retry-After` when the response provides it. A `tools/call` may instead return
`error_code: "RATE_LIMITED"`. Stop polling or submitting new jobs, wait for the
indicated interval, then retry with backoff. Do not immediately fan retries out across
multiple credentials.

## Balance and spend caps

### `INSUFFICIENT_BALANCE`

The quote or generation costs more than the available account balance. The error
includes a top-up link: OAuth connections receive a one-time deposit-only URL, while
Bearer API-key users receive <https://bananabanana.pro/profile>. Open it, add funds,
then repeat the original call. If the tool requires cost confirmation, request a fresh
quote before sending `confirm_cost` again.

You can also call the free `top_up` tool at any time. OAuth links expire after 30
minutes and can be redeemed once. If the browser shows `410 Gone`, the link is invalid,
expired, already used in another browser or its restricted session ended; ask the agent
to call `top_up` again. Link issuance is limited to three per minute per credential.

A completed `get_result` always reports `balance_remaining_usd`. When that balance is
below the cheapest image price in the live application price table, it also includes a
top-up link (or a retry delay if link issuance is temporarily limited).

### `DAILY_CAP_EXCEEDED`

The credential has reached its optional daily USD spend cap. The account can still
use free read tools. Wait for the next UTC day or change the cap in the profile before
retrying a paid tool; adding balance does not reset the cap.

## Tool error codes

Returned inside a tool result (`isError: true`) with a `next_step` you can act on:

| `error_code` | Meaning | What to do |
|---|---|---|
| `INVALID_PARAMS` | Bad or incompatible arguments (e.g. 512 on a model that has no 512). | Fix params; check `list_models` for valid combinations. |
| `NOT_FOUND` | No such `job_id` / `source_generation_id` for this account. | Verify the id with `list_generations`. |
| `INSUFFICIENT_BALANCE` | Balance too low for this generation. | Open the returned `top_up_url`, or call `top_up`, then retry. |
| `DAILY_CAP_EXCEEDED` | This key hit its daily USD cap (UTC). | Wait for the next UTC day, use another key, or raise the cap. |
| `RATE_LIMITED` | Too many tool calls. | Respect `Retry-After` when present and retry with backoff. |
| `SAFETY_FILTERED` | The vendor's content filter (Google, OpenAI, Alibaba or xAI, depending on the model) rejected the request or output (auto-refunded). `get_result` includes `upstream_reason` and the `relaxed_filter` value used; for Google it includes `safety` categories, support codes and input/output stage when known. | Read those details before retrying. Google images already default to `relaxed_filter: true` when a project key is available; if it was false after a `SAFETY_BLOCK`, retry with explicit `true`. `IMAGE_SAFETY` is an output check unaffected by the flag; a plain retry can help for a borderline subject. `SAFETY_INPUT_IMAGE` means replace the input image. Celebrity support codes `15236754` / `29310472` require a different source or support review, not a flag change. On `omni-flash`, try `veo-3.1-fast`. See below. |
| `SERVICE_UNAVAILABLE` | An explicit `relaxed_filter: true` for a Google image could not run because no project Vertex key was free. Nothing was charged. | Retry in about a minute or pass `relaxed_filter: false` to use the standard filter now. |
| `UPSTREAM_FAILED` | Upstream overloaded, out of quota, timed out, or an expired edit source (auto-refunded). | Retry in a minute or two; for edits, generate a fresh video; try a lower resolution or another model. |
| `ACCOUNT_BLOCKED` | Account is blocked. | Contact support@bananabanana.pro. |
| `MAINTENANCE` | Service under maintenance. | Retry in a few minutes. |
| `INTERNAL_ERROR` | Unexpected server error. | Retry; if it persists, contact support@bananabanana.pro. |

Charges for `SAFETY_FILTERED` and `UPSTREAM_FAILED` failures are **refunded
automatically** — the `get_result` payload shows `refunded: true` and the restored
`balance_usd`.

<a id="two-filter-stages-and-what-relaxed_filter-actually-does"></a>

## Content filtering and `relaxed_filter`

Google image generation has a configurable request filter plus independent checks on
input media and generated output. `relaxed_filter` defaults to `true` for Google images
when a project Vertex key is free; pass `false` to opt out. With no free project key,
an explicit `true` returns `SERVICE_UNAVAILABLE` before charging, while the omitted
default falls back to the standard filter. `get_result` reports the flag actually used.
GPT Image, Qwen, Wan and Grok use their own filters, without this switch.

| Stage | When it runs | Typical `upstream_reason` | Configurable? |
|---|---|---|---|
| **Request filter** | Before a Google image is rendered. | `SAFETY_BLOCK` | **Yes**, on Google images: `relaxed_filter: true` selects Vertex safety thresholds OFF and adult person generation. |
| **Input media check** | Checks the supplied first frame or reference image. | `SAFETY_INPUT_IMAGE`; `safety.stage: "input"` when Google supplies support codes | **No**. Replace the input image; repeating the same file is unlikely to help. |
| **Output filter** | Inspects the generated image or video. | `IMAGE_SAFETY`; `safety.stage: "output"` when known | **No**. It scores each rendered file independently, so a plain retry can help for borderline subjects. |

Practical consequences:

- For Google images, inspect the `relaxed_filter` value in the failed result. If it is
  already true, changing the flag will not help; rephrase the prompt. If it is false
  after `SAFETY_BLOCK`, an explicit `true` may help a legitimate request when a
  project key is available.
- **After an `IMAGE_SAFETY` failure, retry anyway — just not because of the flag.**
  Stage 2 scores the pixels it was handed, and every attempt renders a different
  image, so borderline-but-legitimate subjects frequently pass on the second or third
  try. Failed generations are fully refunded, so an attempt costs time, not money.
  What the flag does *not* do is bypass that stage, so don't treat toggling it on as
  the fix.
- **Nudging the wording helps more than the flag** at stage 2: same idea, less
  ambiguous framing (more coverage, less close-up anatomy, no specific real person).
- **On video the flag has no effect.** Veo already defaults to adult person generation
  and exposes no configurable safety thresholds. There the working options are a
  retry, revised wording, or another model; `omni-flash` filters video hardest and
  `veo-3.1-fast` is often more permissive with real-looking scenes.
- **Celebrity refusals stay blocked.** Support codes `15236754` and `29310472` may
  mean a possible prominent-person likeness or missing project approval; they do not
  prove the subject's identity. The flag does not disable this check. For a false
  positive, use another source image or contact support with the `job_id`.
- `MODEL_DECLINED` and `IMAGE_TEXT_ONLY` mean the model returned text instead of an
  image. They surface as `UPSTREAM_FAILED`, not a proven policy refusal: make the
  image task explicit and retry.
- Safety refusals surface as `error_code: "SAFETY_FILTERED"` and are fully refunded;
  read `upstream_reason` and any `safety` details to identify the check.

## Video jobs

Videos are the slowest and most failure-prone path — plan for polling.

- **Expect 1–10+ minutes.** `generate_video` returns a `job_id` after cost
  confirmation; the clip is not ready yet.
- **Poll `get_result`** roughly every **10–15 seconds**, using `wait_seconds` (up to
  30) so each call long-polls instead of returning instantly.
- **`status: "processing"` is normal** for a while. If the payload includes a
  `note` about "high load — automatic retry N of 4", the upstream is busy and the
  server is already retrying for you; keep polling.
- **A video that fails is auto-refunded.** You'll see `status: "failed"`,
  `refunded: true` and an `error_code` (usually `UPSTREAM_FAILED` or
  `SAFETY_FILTERED`).
- **"It's taking too long."** Keep polling — long clips, 4K and audio take longer. If
  the job eventually fails, it is refunded; start a new job, optionally at a lower
  resolution or with `veo-3.1-fast`.
- **Editing an old omni clip returns `UPSTREAM_FAILED` / expired.** The source
  interaction expired upstream — generate a fresh video instead of editing.

## Results & media URLs

- **Media URLs are signed and valid for 24 hours.** Generated files are retained
  for 30 days from creation. Within that period, call `get_result` again with the
  same image/video `job_id` for fresh links. After cleanup, it returns `NOT_FOUND`.
  Speech is absent from `get_result` and account history; download its WAV directly
  from the synchronous response before that link expires.
- **Lost a `job_id`?** Use `list_generations` to find recent jobs (shared with your
  website history), then `get_result`.

## Still stuck?

- Docs & live example: <https://bananabanana.pro/mcp>
- Account, keys, balance: <https://bananabanana.pro/profile>
- Support: support@bananabanana.pro
