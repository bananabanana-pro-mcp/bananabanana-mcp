# Pricing

BananaBanana is **pay-as-you-go**: you top up a balance and each generation is charged
to it. No subscription, no monthly fee, no credit-card hold. Top up with **crypto** or
**Telegram Stars** at <https://bananabanana.pro/profile>.

> These tables are current at the time of writing. Prices are always available live
> from the [`list_models`](./tools.md#list_models--free) tool — treat that as the
> source of truth and let your agent read it before quoting a cost.

All prices are **USD, per generated item** (per image, per video clip).

## Images (per image)

| Model | 512 | 1024 | 2048 | 4096 |
|---|---|---|---|---|
| `nano-banana-2-lite` | — | $0.03 | — | — |
| `nano-banana-2` | $0.03 | $0.06 | $0.09 | $0.13 |
| `nano-banana-pro` | — | $0.11 | $0.11 | $0.20 |

`nano-banana-2-lite` supports 1024 only. `nano-banana-pro` has no 512.
**Editing** (`edit_image`) costs the same as generating one image of the chosen
model and resolution.

## Video (per clip)

Veo clips are priced by model × resolution × duration, and separately for silent vs.
native audio. Durations available via the API: **4, 6, 8 seconds**.

### Silent

| Model | Resolution | 4 s | 6 s | 8 s |
|---|---|---|---|---|
| `veo-3.1` | 720p / 1080p | $0.70 | $1.05 | $1.40 |
| `veo-3.1` | 4K | $1.50 | $2.25 | $3.00 |
| `veo-3.1-fast` | 720p / 1080p | $0.35 | $0.52 | $0.70 |
| `veo-3.1-fast` | 4K | $1.10 | $1.65 | $2.20 |
| `veo-3.1-lite` | 720p | $0.10 | $0.15 | $0.20 |
| `veo-3.1-lite` | 1080p | $0.17 | $0.25 | $0.34 |

### With native audio (`with_audio: true`)

| Model | Resolution | 4 s | 6 s | 8 s |
|---|---|---|---|---|
| `veo-3.1` | 720p / 1080p | $1.50 | $2.25 | $3.00 |
| `veo-3.1` | 4K | $2.20 | $3.30 | $4.40 |
| `veo-3.1-fast` | 720p / 1080p | $0.50 | $0.75 | $1.00 |
| `veo-3.1-fast` | 4K | $1.30 | $1.95 | $2.60 |
| `veo-3.1-lite` | 720p | $0.18 | $0.27 | $0.36 |
| `veo-3.1-lite` | 1080p | $0.28 | $0.42 | $0.56 |

`veo-3.1-lite` has no 4K. 4K is available on `veo-3.1` and `veo-3.1-fast` only.

### Omni Flash

| Model | Price | Notes |
|---|---|---|
| `omni-flash` | **$1.00 flat** | Always includes sound. 720p only. The model picks the clip duration (3–10 s) itself. Conversational editing of a finished clip costs the same flat price. |

**Overall ranges:** images **$0.03–$0.20**, video **$0.10–$4.40** per clip.

## Cost transparency

The server is built so an agent never spends by surprise:

- **Quote-before-charge.** `generate_video` (always) and `generate_image` with
  `number_of_images > 1` return a `quoted_cost_usd` on the first call and charge
  nothing. You only start by repeating the call with `confirm_cost` set to that quote.
- **Every result reports money.** Successful generations return `cost_charged_usd` and
  `balance_remaining_usd`.
- **Automatic refunds.** If a generation fails upstream or is rejected by the content
  filter, the charge is refunded automatically (`refunded: true` in `get_result`).
- **Free reads.** `list_models`, `get_account`, `get_result` and `list_generations`
  never cost anything.

## Spend caps & limits

- **Per-key daily spend cap (optional).** Set a USD cap on any key. When exceeded, paid
  calls return `DAILY_CAP_EXCEEDED` until the next UTC day. Manage it in the profile.
- **Rate limit.** 20 tool calls per minute per key.
- **Per-key usage log.** Tool, model, cost and a prompt preview are recorded per key
  and visible in your profile.

## Billing model

- Charges go through the **same code path as the web app** — MCP and website share one
  balance and one generation history.
- A single image is charged on start (and refunded if it fails). Videos and multi-image
  batches are charged only after you confirm the quote.
- `idempotency_key` makes retries safe: the same key never double-charges.
