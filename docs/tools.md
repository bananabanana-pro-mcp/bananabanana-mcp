# Tools

The server exposes **10 tools**. Read-only and account-access tools (`list_models`,
`get_account`, `top_up`, `get_result`, `list_generations`) are free. Generation tools
charge your balance.

Image and video generation/editing is **asynchronous**: the tool charges (or quotes)
and returns a `job_id` with `status: "processing"`; you then poll `get_result` for the
finished media URLs. `generate_speech` is synchronous: it returns a hosted WAV URL
directly and does not create an image/video Generation record.

**Cost confirmation is mandatory** for `generate_video` and `edit_video` (always) and for
`generate_image` with `number_of_images > 1`. The first such call returns
`status: "confirmation_required"` with a `quoted_cost_usd` and charges nothing — repeat
the exact same call adding `confirm_cost` set to that quoted number to actually start.

All prices are USD and come from the same source as the website. Call `list_models`
for the live numbers rather than hard-coding them.

---

## Common concepts

- **`job_id`** — id of a generation, returned by `generate_image` / `edit_image` /
  `generate_video` / `edit_video`. Pass it to `get_result`, or as
  `source_generation_id` / `edit_from_generation_id`.
- **`confirm_cost`** — the quoted USD number you accept. Omit to get a quote first.
- **`idempotency_key`** — optional unique string (≤64 chars). Retries with the same key
  never double-charge; a repeat returns the original job.
- **Media URLs** — signed and valid for **24 hours**. The media itself is kept — call
  `get_result` again for fresh links.
- **Refunds** — failed and content-filtered generations are refunded automatically.
- **Secure OAuth top-up** — `top_up` returns a one-time, 30-minute browser link for an
  OAuth connection. It opens a deposit-only session with a two-hour sliding idle
  timeout; it cannot expose profile data, API keys, generation history or promo codes.

---

## `list_models`  — free

List every image, video and speech model with live per-unit USD prices, resolutions,
durations and constraints. Call this before quoting a cost or choosing a model.

**Parameters:** none.

**Example call**

```json
{ "name": "list_models", "arguments": {} }
```

**Example response (abridged)**

```json
{
  "currency": "USD",
  "image_models": [
    { "id": "nano-banana-2-lite", "type": "image", "vendor": "google", "prices_per_image_usd": { "1024": 0.03 }, "resolutions": ["1024"], "max_reference_images": 14, "supports": { "seed": true, "negative_prompt": true, "relaxed_filter": true, "edit_image": true } },
    { "id": "nano-banana-2", "type": "image", "vendor": "google", "prices_per_image_usd": { "512": 0.03, "1024": 0.06, "2048": 0.09, "4096": 0.13 } },
    { "id": "nano-banana-pro", "type": "image", "vendor": "google", "prices_per_image_usd": { "1024": 0.11, "2048": 0.11, "4096": 0.20 } },
    { "id": "gpt-image-2.5-flare", "type": "image", "vendor": "openai", "prices_per_image_usd": { "1024": 0.02, "2048": 0.08, "4096": 0.13 }, "supports": { "seed": false, "negative_prompt": false, "relaxed_filter": false, "edit_image": false } },
    { "id": "gpt-image-2.5-sunburst", "type": "image", "vendor": "openai", "prices_per_image_usd": { "1024": 0.02, "2048": 0.08, "4096": 0.13 } },
    { "id": "qwen-image-3.0-pro", "type": "image", "vendor": "alibaba", "prices_per_image_usd": { "1024": 0.04, "2048": 0.08 }, "max_reference_images": 3 }
  ],
  "video_models": [
    { "id": "veo-3.1", "type": "video", "prices_usd": { "silent": { "720p": { "4": 0.70, "6": 1.05, "8": 1.40 } }, "with_audio": { "720p": { "4": 1.50, "6": 2.25, "8": 3.00 } } }, "durations_seconds": [4, 6, 8] },
    { "id": "wan-3.0", "type": "video", "prices_usd_per_second_by_resolution": { "480p": 0.05, "720p": 0.10, "1080p": 0.20 }, "durations_seconds": [4, 6, 8, 10, 15, 20, 30], "video_inputs": { "max_clips": 5, "max_input_seconds": 15, "max_input_plus_output_seconds": 30 } },
    { "id": "grok-imagine-video-1.5", "type": "video", "prices_usd_per_second_by_resolution": { "480p": 0.08, "720p": 0.14, "1080p": 0.25 }, "durations_seconds": [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "aspect_ratios": ["16:9", "9:16", "1:1", "3:2", "2:3"], "max_input_images": 7, "max_input_images_by_resolution": { "1080p": 1 } },
    { "id": "omni-flash", "name": "Gemini Omni 1.1 Flash", "type": "video", "prices_usd_per_second_by_resolution": { "360p": 0.03, "720p": 0.10, "1080p": 0.15, "4k": 0.30 }, "durations_seconds": [3, 4, 5, 6, 7, 8, 9, 10], "max_total_seconds_after_extension": 40 },
    { "id": "omni-flash-1.0", "type": "video", "prices_usd_per_second_by_resolution": { "720p": 0.10, "1080p": 0.12 }, "durations_seconds": [4, 6, 8, 10] }
  ],
  "speech_models": [
    { "id": "gemini-3.1-flash-tts-preview", "type": "speech", "price_usd_per_started_200_characters": 0.01 }
  ],
  "top_up_url": "https://bananabanana.pro/profile",
  "docs_url": "https://bananabanana.pro/mcp"
}
```

---

## `get_account`  — free

Return the current account balance, this key's name, its optional daily spend cap and
how much of it is used today (UTC).

**Parameters:** none.

**Example response**

```json
{
  "balance_usd": 12.40,
  "api_key": { "name": "claude-desktop", "daily_cap_usd": 5, "spent_today_usd": 0.62 },
  "top_up_url": "https://bananabanana.pro/profile",
  "docs_url": "https://bananabanana.pro/mcp"
}
```

---

## `top_up`  — free

Return a link for adding funds to the account balance — by crypto (from $1) or by card,
PayPal or SEPA (from $20). The response depends on how the MCP connection
authenticated:

- **OAuth:** a one-time URL valid for 30 minutes. Opening it creates a restricted
  deposit-only browser session with a two-hour sliding idle timeout. The page can show
  the balance, create or display a crypto deposit address and wait for a transfer, or
  take a card payment; it cannot expose the full profile, API keys, generation history
  or promo-code controls.
- **Bearer API key:** the normal profile URL. Sign in there if the browser does not
  already have a web session.

Link creation is limited to three per minute for each credential. If a link is used,
expired or opened in another browser, ask the agent to call `top_up` again.

**Parameters:** none.

**OAuth response**

```json
{
  "balance_usd": 0.01,
  "top_up_url": "https://bananabanana.pro/mcp/top-up?token=bb_tu_…",
  "expires_at": "2026-08-20T13:30:00.000Z",
  "single_use": true,
  "access": "deposit_only",
  "next_step": "Open top_up_url in a browser. It grants deposit-only access and does not sign in to the full profile."
}
```

The raw token is never stored in the database or written to nginx access logs. After
redemption the browser is redirected to the clean `/mcp/top-up` URL.

---

## `generate_image`  — paid ($0.02–$0.20 per image)

Start a text-to-image generation with the Google Nano Banana family, OpenAI GPT Image
2.5 or Alibaba Qwen Image 3.0 Pro. Charges immediately for a single image and returns a
`job_id`. Typical completion 10–60 s. `number_of_images > 1` is a batch and requires
`confirm_cost`.

| Parameter | Type | Default | Notes |
|---|---|---|---|
| `prompt` | string, ≤32000 | — | **Required.** English works best. `list_models` reports `max_prompt_chars` per model (Qwen: 20000). |
| `model` | enum | `nano-banana-2-lite` | `nano-banana-2-lite` (cheapest Google default, 1024 only) · `nano-banana-2` (choose for 512, 2048 or 4096) · `nano-banana-pro` (top Google quality, up to 4K, no 512) · `gpt-image-2.5-flare` / `gpt-image-2.5-sunburst` (OpenAI — strongest at readable in-image text and long literal briefs; 1024, 2048 or 4096; Flare is the fast tier, Sunburst the precision tier; they ignore `seed` and `relaxed_filter`) · `qwen-image-3.0-pro` (Alibaba — crisp small text and dense layouts; 1024 or 2048 only, up to 3 references, `seed` and `negative_prompt`). Cheapest per image: `gpt-image-2.5-flare` at $0.02. |
| `aspect_ratio` | enum | `1:1` | `1:1`, `3:2`, `2:3`, `4:3`, `3:4`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`. |
| `resolution` | enum | `1024` | `512`, `1024`, `2048`, `4096`. 512 only on `nano-banana-2`; lite is 1024 only; `nano-banana-pro` and GPT Image have no 512; Qwen accepts 1024 or 2048. GPT Image renders 4096 at 3840 on the long side (8.3 MP cap). |
| `number_of_images` | integer 1–4 | `1` | `>1` requires `confirm_cost`. |
| `negative_prompt` | string, ≤1000 | — | What to avoid (Nano Banana and Qwen). |
| `output_format` | enum | `jpeg` | `jpeg`, `png`, `webp`. |
| `seed` | integer 0–2147483647 | — | For reproducible results (Nano Banana and Qwen; GPT Image ignores it). |
| `reference_images` | string[], ≤14 | — | Visual references supplied as a completed image `job_id`, a public http(s) image URL, or an inline `data:image/png|jpeg|webp;base64,...` URL (≤10 MB each). A remote server cannot read a bare local filesystem path; encode a local file as a data URL. Qwen takes up to 3. This is also how GPT Image and Qwen edit a picture, since `edit_image` does not accept them. |
| `relaxed_filter` | boolean | `false` | Nano Banana only. Loosens the **configurable** stage of Google's content filter for this call (safety thresholds off, adult person generation allowed). It relaxes the check applied to the request *before* generation — the standard retry after a `SAFETY_FILTERED` failure with `upstream_reason: "SAFETY_BLOCK"`. The classifier that inspects the finished image (`upstream_reason: "IMAGE_SAFETY"`) is not configurable and stays active; it judges each rendered image separately, so borderline subjects often pass on a retry, but not *because* of this flag. See [Two filter stages](troubleshooting.md#two-filter-stages-and-what-relaxed_filter-actually-does). |
| `confirm_cost` | number | — | Required for batches: the quoted total USD you accept. |
| `idempotency_key` | string, ≤64 | — | Safe-retry key. |

**Example call**

```json
{
  "name": "generate_image",
  "arguments": {
    "prompt": "studio photo of a ceramic mug on linen, soft daylight",
    "model": "nano-banana-2-lite",
    "aspect_ratio": "4:5",
    "resolution": "1024"
  }
}
```

**Example response**

```json
{
  "job_id": "cmxyz123...",
  "status": "processing",
  "cost_charged_usd": 0.03,
  "balance_remaining_usd": 12.37,
  "next_step": "Call get_result with job_id \"cmxyz123...\". Images usually finish in 10–60 seconds."
}
```

**Batch (quote first)** — with `number_of_images: 3` and no `confirm_cost`:

```json
{
  "status": "confirmation_required",
  "quoted_cost_usd": 0.09,
  "balance_usd": 12.40,
  "message": "Generating 3 images costs $0.09. Nothing has been charged.",
  "next_step": "Call generate_image again with the same arguments plus confirm_cost: 0.09."
}
```

---

## `edit_image`  — paid (price of one image of the chosen model/resolution)

Refine a previously generated image with a text instruction (multi-turn editing:
change colors, remove objects, restyle, etc.) on the Nano Banana models. Charged like
a single image; auto-refund on failure. GPT Image and Qwen do not take this tool — pass
the picture to `generate_image` as a reference instead.

| Parameter | Type | Default | Notes |
|---|---|---|---|
| `source_generation_id` | string | — | **Required.** `job_id` of a **completed** image generation owned by this account. |
| `prompt` | string, ≤32000 | — | **Required.** The edit instruction. |
| `model` | enum | `nano-banana-2` | `nano-banana-2-lite`, `nano-banana-2`, `nano-banana-pro`. |
| `aspect_ratio` | enum | `1:1` | Same set as `generate_image`. |
| `resolution` | enum | `1024` | `512`, `1024`, `2048`, `4096` (model constraints apply). |
| `output_format` | enum | `jpeg` | `jpeg`, `png`, `webp`. |
| `seed` | integer 0–2147483647 | — | For reproducible results. |
| `relaxed_filter` | boolean | `false` | Same two-stage image-filter behavior as `generate_image`; it only relaxes Google's configurable request-stage presets. |
| `idempotency_key` | string, ≤64 | — | Safe-retry key. |

**Example call**

```json
{
  "name": "edit_image",
  "arguments": {
    "source_generation_id": "cmxyz123...",
    "prompt": "make the background pure white and add a soft shadow"
  }
}
```

Response is the same shape as `generate_image` (a new `job_id` you poll with
`get_result`).

---

## `generate_video`  — paid ($0.10–$6.00 per clip). Cost confirmation always required.

Start a video generation with the Google Veo 3.1 family, Gemini Omni Flash (1.1 or
1.0), Alibaba Wan 3.0 or xAI Grok Imagine Video 1.5. The **first call always returns a
quote and charges nothing** — repeat with `confirm_cost` to start. Returns a `job_id`;
videos take **1–10+ minutes**.

| Parameter | Type | Default | Notes |
|---|---|---|---|
| `prompt` | string | — | **Required.** Limit per model: 2000 characters on Veo, 20000 on `omni-flash` and `wan-3.0`, 2048 on `grok-imagine-video-1.5` (`max_prompt_chars` in `list_models`). |
| `model` | enum | `veo-3.1-fast` | `veo-3.1` (best Veo quality) · `veo-3.1-fast` (best value) · `veo-3.1-lite` (cheapest, no 4K) · `omni-flash` (Gemini Omni 1.1 Flash: always has sound, 360p–4K priced per second, last frame, conversational editing, scene extension) · `omni-flash-1.0` (previous Omni generation, 720p/1080p) · `wan-3.0` (Alibaba: up to 30 s, 480p–1080p, optional free audio, first/last frame, seed, reference videos) · `grok-imagine-video-1.5` (xAI: 4–15 s at any whole second, 480p–1080p, sound always on, five aspect ratios, exact first frame). |
| `duration` | integer | `8` | Seconds. Veo: 4, 6 or 8. `omni-flash`: any whole 3–10. `omni-flash-1.0`: 4, 6, 8, 10 (1080p: 6, 8, 10). `wan-3.0`: 4, 6, 8, 10, 15, 20, 30. `grok-imagine-video-1.5`: any whole 4–15. Ignored together with `edit_from_generation_id` — a conversational edit always keeps the source clip's length. |
| `resolution` | enum | `720p` | Veo: `720p`, `1080p`, plus `4k` on `veo-3.1` / `veo-3.1-fast`. `omni-flash`: `360p` (draft, a third of the price), `720p` (native), `1080p` and `4k` (upscaled). `omni-flash-1.0`: `720p`, or `1080p` upscaled. `wan-3.0` and `grok-imagine-video-1.5`: `480p`, `720p`, `1080p`. |
| `aspect_ratio` | enum | `16:9` | `16:9`, `9:16` on Veo, Omni and Wan; `grok-imagine-video-1.5` adds `1:1`, `3:2`, `2:3`. |
| `with_audio` | boolean | `false` | Native audio for Veo (costs more). `omni-flash` and `grok-imagine-video-1.5` always have audio. On `wan-3.0` audio is on by default and free — pass `false` for a silent clip. |
| `audio_prompt` | string, ≤500 | — | Describe the desired sound (used when audio is on). |
| `negative_prompt` | string, ≤1000 | — | Native negative field on Veo. Omni Flash has no separate field, so the server appends it to the prompt as plain text. |
| `seed` | integer 0–2147483647 | — | Veo and `wan-3.0` only. |
| `first_frame` | string | — | Animate a still image: a completed image `job_id`, a public http(s) image URL, or an inline base64 image data URL. A signed `get_result` URL selects one variant of a multi-image job. On `omni-flash` and `grok-imagine-video-1.5` it combines with `reference_images`; on Veo and `wan-3.0` it is either/or. Grok reproduces it as the literal opening frame. |
| `last_frame` | string | — | Closing frame for Veo, `omni-flash` (1.1) and `wan-3.0`: the model interpolates from `first_frame` to this image. Requires `first_frame`; same accepted forms. Not on `omni-flash-1.0` or Grok. |
| `reference_images` | string[], ≤10 | — | Subject/style references, not literal frames. Each uses the same three forms as `first_frame`; encode local files as inline data URLs rather than passing filesystem paths. `omni-flash`: up to 10 images total with the frames. Veo 3.1 / Fast: at most 3, only with `duration: 8` and without frames; Veo Lite: unsupported. `wan-3.0`: up to 10, not together with frames. `grok-imagine-video-1.5`: up to 7 together with `first_frame`, and exactly one image in total at 1080p. |
| `reference_videos` | string[], ≤5 | — | **`wan-3.0` only.** Clips the model reads before generating: rework a scene, continue its story, or carry its characters and setting into a new clip — the prompt says what to do with "Video 1", "Video 2" (job_ids are numbered first, then URLs). Each item is a completed video `job_id`, a public http(s) video URL, or a `reference_video_refs` value returned by the quote. Up to 5 clips and 15 s in total; each clip is normalised to MP4 720p and whole seconds. **Input seconds are billed like output seconds**, and input + output must fit in 30 s. Cannot be combined with frames. |
| `relaxed_filter` | boolean | `false` | **Veo only** (`omni-flash` ignores it), and close to a no-op: Google exposes no configurable safety settings for Veo, so the flag can only pin `personGeneration=allow_adult` — already the default for Veo 3.1. Video is filtered before generation and again on the finished clip (`rai_media_filtered_reasons`), and neither check can be switched off. After a rejection, retry (refused clips are refunded), reword, or switch model. See [Two filter stages](troubleshooting.md#two-filter-stages-and-what-relaxed_filter-actually-does). |
| `edit_from_generation_id` | string | — | **`omni-flash` / `omni-flash-1.0` only:** `job_id` of a completed omni video to refine conversationally; `prompt` describes the changes. Duration, aspect ratio, the scene and the Omni generation that shot the clip are inherited from it. |
| `confirm_cost` | number | — | The quoted USD you accept. Omit on the first call to get the quote. |
| `idempotency_key` | string, ≤64 | — | Safe-retry key. |

**First call (quote)**

```json
{
  "name": "generate_video",
  "arguments": {
    "prompt": "drone shot over a misty pine forest at sunrise",
    "model": "veo-3.1-fast",
    "duration": 8,
    "resolution": "720p"
  }
}
```

```json
{
  "status": "confirmation_required",
  "quoted_cost_usd": 0.70,
  "model": "veo-3.1-fast",
  "resolution": "720p",
  "duration_seconds": 8,
  "audio": false,
  "balance_usd": 12.40,
  "message": "This video costs $0.70. Nothing has been charged.",
  "next_step": "Call generate_video again with the same arguments plus confirm_cost: 0.70."
}
```

**Second call (start)** — same arguments plus `"confirm_cost": 0.70` → returns a
`job_id` with `status: "processing"`.

**Image inputs** — animate a picture you already generated and keep a character
consistent, without uploading base64 anywhere:

```json
{
  "name": "generate_video",
  "arguments": {
    "prompt": "the mascot walks toward camera through falling snow, single unbroken shot",
    "model": "omni-flash",
    "duration": 6,
    "first_frame": "cmx_image_job_id",
    "reference_images": ["cmx_other_image_job_id", "https://example.com/mascot-side.png"],
    "confirm_cost": 0.60
  }
}
```

URL images are fetched server-side and downscaled before they reach the model; private
and internal addresses are rejected. Local files must be passed as inline base64 data
URLs. The quote echoes `input_images` so you can see how many were accepted. Editing
modes (`edit_from_generation_id`, `edit_video` mode `edit`) take their context from the
source clip and ignore image inputs.

**Video inputs (Wan 3.0)** — continue a clip's story with the same characters and
setting:

```json
{
  "name": "generate_video",
  "arguments": {
    "prompt": "Extend Video 1 forward: the barista hands over the cup and the customer walks out into the rain",
    "model": "wan-3.0",
    "duration": 6,
    "resolution": "720p",
    "reference_videos": ["cmx_video_job_id"]
  }
}
```

The quote reports the input seconds it counted; with a 6-second source and a 6-second
output at 720p the price is 12 × $0.10 = $1.20.

**Grok first frame** — an exact opening frame with a spoken line:

```json
{
  "name": "generate_video",
  "arguments": {
    "prompt": "The woman looks at the camera, smiles and says: this took ten seconds. Natural handheld motion.",
    "model": "grok-imagine-video-1.5",
    "duration": 5,
    "resolution": "480p",
    "first_frame": "cmx_image_job_id"
  }
}
```

Quoted at 5 × $0.08 = $0.40; the same take at 1080p is $1.25.

---

## `edit_video`  — paid (per second of output). Cost confirmation always required.

Edit an **existing** video (video-to-video). The default model is Gemini Omni Flash:
restyle the clip, replace or add objects, relight the scene, change the mood — the
motion and composition of the source are preserved — or **extend** an Omni clip with a
3–10 s continuation. With `model: "wan-3.0"` the source is read as a reference and Wan
renders a new clip of the length you choose (edit or continue, driven by the prompt).
The **first call always returns a quote and charges nothing** — repeat with
`confirm_cost` to start. Returns a `job_id`; edits usually take 1–5 minutes.

On Omni the source is normalised server-side to MP4 720p and, for mode `edit`, the
**first 10 seconds** (model limit); the output is 720p with sound and keeps the aspect
ratio of the source. Billing is $0.10 per output second.

**An Omni edit is always exactly as long as the source** — the model cannot stretch or
shorten a video. `duration` therefore works only downwards: it trims the source to its
first N seconds and you pay for those N seconds only. Omit it to edit the whole clip;
the quote reports the resolved `duration_seconds` and `source_duration_seconds`. Clips
shorter than 3 seconds are rejected. Mode `extend` instead appends a continuation to the
end: `duration` is then the length of the appended part (3–10 s), the whole source is
read (up to 37 s) so extensions chain, the total is capped at 40 s, and the job is
billed on the full resulting length.

On Wan 3.0 the source counts as a reference video: **source seconds are billed together
with the output**, source + output must fit in 30 s, and the output length, resolution
and audio are yours to choose.

| Parameter | Type | Default | Notes |
|---|---|---|---|
| `prompt` | string, ≤20000 | — | **Required.** What to change in the video, or what happens next. |
| `model` | enum | `omni-flash` | `omni-flash` (Gemini Omni 1.1: keeps motion and length, can extend) · `omni-flash-1.0` (previous generation, edit only) · `wan-3.0` (reads the source as a reference, renders a new clip of the chosen duration). |
| `source_generation_id` | string | — | `job_id` of a completed video on this account (see `list_generations`). Use this **or** `video_url`. |
| `video_url` | string | — | Public http(s) link to the source clip (mp4/mov/webm/mkv/avi/wmv/flv/3gpp, ≤200 MB). Private and internal addresses are rejected. |
| `source_ref` | string | — | Returned by the quote when `video_url` was used. Pass it back with `confirm_cost` to reuse the already downloaded clip instead of downloading it again. |
| `mode` | enum | `edit` | `edit` rewrites the clip; `extend` continues it. Omni: `edit` keeps the length, `extend` appends 3–10 s (40 s total cap). Wan: `edit` rebuilds the scene at the chosen duration, `extend` shoots the next scene. |
| `duration` | integer | source length | Omni `edit`: trim the source to its first N seconds (3–10). Omni `extend`: length of the appended part (3–10). Wan: length of the **output** — 4, 6, 8, 10, 15, 20 or 30 s (default 8). |
| `resolution` | enum | `720p` | `wan-3.0` only: `480p`, `720p`, `1080p`. Omni edits are always 720p. |
| `with_audio` | boolean | `true` | `wan-3.0` only: sound is on by default and free — pass `false` for a silent clip. Omni always generates audio. |
| `audio_prompt` | string, ≤500 | — | Describe the desired sound — Omni Flash always generates audio. |
| `reference_images` | string[], ≤10 | — | Omni `extend` only: subjects, products or characters the continuation should bring into the scene (job_id, public URL or base64 data URL). Refer to them in the prompt. Ignored by `edit` and by Wan. |
| `confirm_cost` | number | — | The quoted USD you accept. Omit on the first call to get the quote. |
| `idempotency_key` | string, ≤64 | — | Safe-retry key. |

**First call (quote)**

```json
{
  "name": "edit_video",
  "arguments": {
    "prompt": "make the whole scene look like a pencil sketch, keep the motion identical",
    "source_generation_id": "cmxyz123..."
  }
}
```

```json
{
  "status": "confirmation_required",
  "quoted_cost_usd": 0.80,
  "model": "omni-flash",
  "duration_seconds": 8,
  "source_duration_seconds": 8,
  "resolution": "720p",
  "audio": true,
  "balance_usd": 12.40,
  "message": "This video edit costs $0.80. Nothing has been charged.",
  "next_step": "Call edit_video again with the same arguments plus confirm_cost: 0.8."
}
```

**Second call (start)** — same arguments plus `"confirm_cost": 0.8` → returns a `job_id`
with `status: "processing"`.

**Extend an Omni clip** — append 6 seconds to an 8-second clip (billed on the resulting
14 s at $0.10/s):

```json
{
  "name": "edit_video",
  "arguments": {
    "prompt": "the camera keeps pulling back until the whole coastline is in frame",
    "source_generation_id": "cmxyz123...",
    "mode": "extend",
    "duration": 6,
    "confirm_cost": 1.4
  }
}
```

> `edit_video` rebuilds the clip from its pixels, so it works on any video you own or
> can link to. For refining an **omni-flash** clip you generated moments ago, the
> conversational `generate_video` + `edit_from_generation_id` path keeps the original
> scene context and is usually the better choice.

---

## `generate_speech` — paid ($0.01 per started 200 transcript characters)

Generate natural speech with Gemini 3.1 Flash TTS Preview. Unlike image and video
tools, this call is **synchronous**: it returns a hosted WAV URL directly, requires no
`get_result` polling and does not create an image/video Generation record. The account
is charged only after the upstream model has returned valid audio.

| Parameter | Type | Default | Notes |
|---|---|---|---|
| `text` | string, ≤6000 | — | **Required.** Exact transcript. In dialogue mode, prefix each turn with the matching speaker name. |
| `style` | string, ≤1500 | — | Overall persona, scene, emotion, accent, pace, pronunciation and delivery direction. |
| `voice` | enum | `Kore` | Single-speaker voice. Ignored when `speakers` is provided. |
| `language_code` | string | automatic | Optional BCP-47 language/locale such as `en-US`, `ru-RU`, `ja-JP` or `es-MX`. |
| `speakers` | object[2] | — | Exactly two dialogue speakers. Each object requires a `name` (1–40 chars) and `voice`; those names must prefix turns in `text`. |
| `idempotency_key` | string, ≤64 | — | Safe-retry key. |

Available voices:

`Achernar`, `Achird`, `Algenib`, `Algieba`, `Alnilam`, `Aoede`, `Autonoe`,
`Callirrhoe`, `Charon`, `Despina`, `Enceladus`, `Erinome`, `Fenrir`, `Gacrux`,
`Iapetus`, `Kore`, `Laomedeia`, `Leda`, `Orus`, `Pulcherrima`, `Puck`,
`Rasalgethi`, `Sadachbia`, `Sadaltager`, `Schedar`, `Sulafat`, `Umbriel`,
`Vindemiatrix`, `Zephyr`, `Zubenelgenubi`.

The generated file is mono, 24 kHz, 16-bit WAV. `style` and `text` together must fit
within 8,000 UTF-8 bytes; split longer scripts to keep voice quality stable. Inline
performance tags include `[whispers]`, `[laughs]`, `[sighs]`, `[shouting]`,
`[very fast]` and `[very slow]`.

**Single-speaker example**

```json
{
  "name": "generate_speech",
  "arguments": {
    "text": "[cheerfully] Welcome to BananaBanana!",
    "voice": "Kore",
    "style": "Warm product announcement, medium pace."
  }
}
```

**Two-speaker example**

```json
{
  "name": "generate_speech",
  "arguments": {
    "text": "Sam: Did the render finish?\nMira: Yes, it is ready to review.",
    "speakers": [
      { "name": "Sam", "voice": "Charon" },
      { "name": "Mira", "voice": "Aoede" }
    ]
  }
}
```

---

## `get_result`  — free

Get the status and result of a job. Waits up to `wait_seconds` for completion before
returning (long-poll). Poll roughly every 10–15 s for videos, every few seconds for
images.

| Parameter | Type | Default | Notes |
|---|---|---|---|
| `job_id` | string | — | **Required.** |
| `wait_seconds` | integer 0–30 | `15` | How long the server waits before answering. |

**Completed image response**

```json
{
  "job_id": "cmxyz123...",
  "type": "image",
  "model": "nano-banana-2",
  "status": "completed",
  "completed_at": "2026-07-12T10:00:12.000Z",
  "files": [
    { "url": "https://bananabanana.pro/api/files/...?sig=...", "thumbnail_url": "https://bananabanana.pro/api/files/...?thumb=1&sig=..." }
  ],
  "files_note": "URLs are valid for 24 hours. The media itself is kept — call get_result again for fresh links.",
  "cost_charged_usd": 0.06,
  "balance_remaining_usd": 12.34
}
```

Image responses also include a small inline `image` preview block alongside the JSON.
Every completed result includes `balance_remaining_usd`. When that balance is below
the cheapest current image price (derived from the application's price table), the
response also includes `cheapest_image_price_usd`, `can_afford_cheapest_image: false`,
a `balance_notice`, and either a `top_up_url` or the number of seconds before another
link can be requested.

**Still processing**

```json
{
  "job_id": "cmxyz123...",
  "type": "video",
  "model": "veo-3.1-fast",
  "status": "processing",
  "next_step": "Still processing. Call get_result again in 10–15 seconds."
}
```

**Failed (auto-refunded)**

```json
{
  "error_code": "SAFETY_FILTERED",
  "message": "The upstream content filter (Google) rejected this prompt or its output. The charge was automatically refunded.",
  "next_step": "Rephrase the prompt to avoid people-likeness, violence or other sensitive content and try again.",
  "job_id": "cmxyz123...",
  "status": "failed",
  "refunded": true,
  "balance_usd": 12.40
}
```

---

## `list_generations`  — free

List this account's recent generations (both MCP and website) — `job_id`, type, model,
status, cost and prompt preview. Use it to find a `job_id` to re-download or to pick a
source for `edit_image`.

| Parameter | Type | Default | Notes |
|---|---|---|---|
| `limit` | integer 1–50 | `10` | |
| `type` | enum | — | `image` or `video`. |
| `status` | enum | — | `processing`, `completed` or `failed`. |

**Example response**

```json
{
  "generations": [
    {
      "job_id": "cmxyz123...",
      "type": "image",
      "model": "nano-banana-2",
      "status": "completed",
      "cost_usd": 0.06,
      "prompt_preview": "studio photo of a ceramic mug on linen, soft daylight",
      "created_at": "2026-07-12T10:00:00.000Z"
    }
  ],
  "next_step": "Call get_result with a job_id to fetch media URLs."
}
```
