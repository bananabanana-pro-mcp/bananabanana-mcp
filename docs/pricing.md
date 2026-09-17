# Pricing

BananaBanana is **pay-as-you-go**: you top up a balance and each generation is charged
to it. No subscription, no monthly fee, no saved card, no auto-renewal. Top up with
**crypto** (from $1) or by **card, PayPal or SEPA** (from $20) at
<https://bananabanana.pro/profile>, or ask the agent for a link with the free `top_up`
tool.

> These tables are current at the time of writing. Prices are always available live
> from the [`list_models`](./tools.md#list_models--free) tool — treat that as the
> source of truth and let your agent read it before quoting a cost.

All prices are in **USD**. Images are billed per image, Veo per clip, Omni Flash,
Wan 3.0 and Grok Imagine Video per second of output, and speech per started block of
transcript characters.

## Payment methods

| Method | Minimum | Notes |
|---|---|---|
| Crypto | $1 (USDC on ERC-20: $2) | USDT, USDC, DAI, BTC, ETH, SOL, BNB, LTC, TRX, TON, XRP, DOGE and more, on most major networks. A permanent deposit address per coin; the balance is credited after blockchain confirmation. Fees of a few cents on networks such as TON or Solana. |
| Card, PayPal or SEPA (EU) | $20 (up to $2,000 per payment) | Visa and Mastercard, a PayPal balance or a SEPA transfer, handled inside PayPal's checkout — card details never reach BananaBanana. Credited as soon as the payment clears. |

Both are one-off top-ups: the balance does not expire and nothing renews. Crypto is the
lighter path (lower minimum, no bank in the loop); card is there for anyone who does not
hold crypto.

## Top-up bonuses and effective cost

- Deposits of **$50+** receive **5% extra balance**.
- Deposits of **$100+** receive **10% extra balance**.
- An active partner promo code adds another **10%** to each deposit while it is active.
- The volume bonus and promo-code bonus stack: a $100 deposit with an active code
  credits $120 to the account balance. Bonuses apply to crypto and card deposits alike.

Promo-code controls require the fully authenticated profile. The restricted page
opened by an OAuth `top_up` link intentionally supports deposits only (crypto address
or card payment); an already active promo still affects the account according to the
rules above.

The model tables below show the nominal amount deducted from the BananaBanana balance.
Because bonuses add balance without increasing the deposit by the same amount, the
effective out-of-pocket price can be lower.

## Images (per image)

| Model | Vendor | 512 | 1024 | 2048 | 4096 |
|---|---|---|---|---|---|
| `nano-banana-2-lite` | Google | — | $0.03 | — | — |
| `nano-banana-2` | Google | $0.03 | $0.06 | $0.09 | $0.13 |
| `nano-banana-pro` | Google | — | $0.11 | $0.11 | $0.20 |
| `gpt-image-2.5-flare` | OpenAI | — | $0.02 | $0.08 | $0.13 |
| `gpt-image-2.5-sunburst` | OpenAI | — | $0.02 | $0.08 | $0.13 |
| `qwen-image-3.0-pro` | Alibaba | — | $0.04 | $0.08 | — |

`nano-banana-2-lite` supports 1024 only. `nano-banana-pro` and the GPT Image models
have no 512; `qwen-image-3.0-pro` accepts 1024 or 2048 only. GPT Image renders 1024 at
about 1.5 MP and 2048 / 4096 at the exact requested size (4K = 3840 on the long side,
8.3 MP cap). `generate_image` defaults to `nano-banana-2-lite`; choose `nano-banana-2`
explicitly for 512, 2048 or 4096 output. Every image model accepts `reference_images`
(up to 14; Qwen up to 3).

**Editing** (`edit_image`) runs on the Nano Banana models only and costs the same as
generating one image of the chosen model and resolution. GPT Image and Qwen do not
accept `edit_image` — pass the picture to `generate_image` through `reference_images`
instead.

## Video

### Veo 3.1 (per clip)

Veo clips are priced by model × resolution × duration, and separately for silent vs.
native audio. Durations available via the API: **4, 6, 8 seconds**.

The 7-second entries returned inside Veo price maps by `list_models` apply to extension
jobs. A new MCP `generate_video` call accepts only 4, 6 or 8 seconds for Veo; 7 seconds
is not a selectable generation duration.

#### Silent

| Model | Resolution | 4 s | 6 s | 8 s |
|---|---|---|---|---|
| `veo-3.1` | 720p / 1080p | $0.70 | $1.05 | $1.40 |
| `veo-3.1` | 4K | $1.50 | $2.25 | $3.00 |
| `veo-3.1-fast` | 720p / 1080p | $0.35 | $0.52 | $0.70 |
| `veo-3.1-fast` | 4K | $1.10 | $1.65 | $2.20 |
| `veo-3.1-lite` | 720p | $0.10 | $0.15 | $0.20 |
| `veo-3.1-lite` | 1080p | $0.17 | $0.25 | $0.34 |

#### With native audio (`with_audio: true`)

| Model | Resolution | 4 s | 6 s | 8 s |
|---|---|---|---|---|
| `veo-3.1` | 720p / 1080p | $1.50 | $2.25 | $3.00 |
| `veo-3.1` | 4K | $2.20 | $3.30 | $4.40 |
| `veo-3.1-fast` | 720p / 1080p | $0.50 | $0.75 | $1.00 |
| `veo-3.1-fast` | 4K | $1.30 | $1.95 | $2.60 |
| `veo-3.1-lite` | 720p | $0.18 | $0.27 | $0.36 |
| `veo-3.1-lite` | 1080p | $0.28 | $0.42 | $0.56 |

`veo-3.1-lite` has no 4K. 4K is available on `veo-3.1` and `veo-3.1-fast` only.

### Per-second models

| Model | Price per second of output | Durations | Per clip | Notes |
|---|---|---|---|---|
| `omni-flash` (Gemini Omni 1.1 Flash) | **$0.03** at 360p · **$0.10** at 720p · **$0.15** at 1080p · **$0.30** at 4K | any whole 3–10 s | $0.09 – $3.00 | Always includes sound. 360p is a draft tier (a third of the price, up to 60% faster); 720p is the native render; 1080p and 4K are upscaled. Accepts a first and last frame plus reference images. Scene extension via `edit_video` `mode: "extend"` appends 3–10 s to an existing clip, up to 40 s in total, billed on the full resulting length. Video-to-video edits keep the source length (see `edit_video`). |
| `omni-flash-1.0` (previous Omni generation) | **$0.10** at 720p · **$0.12** at 1080p (upscaled) | 4, 6, 8, 10 s (1080p: 6, 8, 10) | $0.40 – $1.20 | Always includes sound. Kept as an option; no last frame, extension or video references. |
| `wan-3.0` (Alibaba) | **$0.05** at 480p · **$0.10** at 720p · **$0.20** at 1080p | 4, 6, 8, 10, 15, 20, 30 s | $0.20 – $6.00 | Audio on by default and free to switch off. First and last frame, up to 10 reference images, seed. Reads up to 5 reference videos (15 s in total); **input seconds are billed like output seconds**, and input + output must fit in 30 s. Alibaba's own list price. |
| `grok-imagine-video-1.5` (xAI) | **$0.14** at 720p · **$0.25** at 1080p | any whole 4–15 s | $0.56 – $3.75 | Native sound always on. Five aspect ratios (16:9, 9:16, 1:1, 3:2, 2:3). A first frame reproduced exactly plus up to 7 reference images (one image in total at 1080p). Input images are free (xAI's own API adds $0.01 each). xAI's own per-second list price for these tiers; xAI's 480p tier is not offered. |

## Speech

| Model | Price | Notes |
|---|---|---|
| `gemini-3.1-flash-tts-preview` | **$0.01 per started 200 transcript characters** | One voice or exactly two named dialogue speakers. Returns mono 24 kHz, 16-bit WAV audio synchronously. |

**Overall ranges:** images **$0.02–$0.20** each; video **$0.10–$6.00** per clip (Veo per
clip; Omni Flash $0.03–$0.30/s, Wan 3.0 $0.05–$0.20/s, Grok Imagine Video $0.14–$0.25/s);
speech **$0.01 per started 200 transcript characters**.

## Cost transparency

The server is built so an agent never spends by surprise:

- **Quote-before-charge.** `generate_video` and `edit_video` (always) and `generate_image` with
  `number_of_images > 1` return a `quoted_cost_usd` on the first call and charge
  nothing. You only start by repeating the call with `confirm_cost` set to that quote.
- **Every result reports money.** Successful generations return `cost_charged_usd` and
  `balance_remaining_usd`.
- **Automatic refunds.** If a generation fails upstream or is rejected by the content
  filter, the charge is refunded automatically (`refunded: true` in `get_result`).
- **Speech charges after valid audio.** `generate_speech` charges only after the
  upstream model has returned valid audio.
- **Free reads.** `list_models`, `get_account`, `top_up`, `get_result` and
  `list_generations` never cost anything.

## Spend caps & limits

- **Per-key daily spend cap (optional).** Set a USD cap on any key. When exceeded, paid
  calls return `DAILY_CAP_EXCEEDED` until the next UTC day. Manage it in the profile.
- **Rate limits.** A request may return HTTP `429` or tool error `RATE_LIMITED`.
  Respect `Retry-After` when present and retry with backoff.
- **Per-key usage log.** Tool, model, cost and a prompt preview are recorded per key
  and visible in your profile.

## Billing model

- Charges go through the **same code path as the web app** — MCP and website share one
  balance and one generation history.
- A single image is charged on start (and refunded if it fails). Videos and multi-image
  batches are charged only after you confirm the quote.
- Speech is synchronous and charged only after valid audio has been returned; it does
  not create an image/video Generation record.
- `idempotency_key` makes retries safe: the same key never double-charges.
