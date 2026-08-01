# Tools

The server exposes **7 tools**. Read-only tools (`list_models`, `get_account`,
`get_result`, `list_generations`) are free. Generation tools charge your balance.

Generation is **asynchronous**: a `generate_*` / `edit_image` call charges (or quotes)
and returns a `job_id` with `status: "processing"`; you then poll `get_result` for the
finished media URLs.

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

---

## `list_models`  — free

List every image and video model with live per-unit USD prices, resolutions,
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
    { "id": "nano-banana-2-lite", "type": "image", "prices_per_image_usd": { "1024": 0.03 }, "resolutions": ["1024"] },
    { "id": "nano-banana-2", "type": "image", "prices_per_image_usd": { "512": 0.03, "1024": 0.06, "2048": 0.09, "4096": 0.13 } },
    { "id": "nano-banana-pro", "type": "image", "prices_per_image_usd": { "1024": 0.11, "2048": 0.11, "4096": 0.20 } }
  ],
  "video_models": [
    { "id": "veo-3.1", "type": "video", "prices_usd": { "silent": { "720p": { "4": 0.70, "6": 1.05, "8": 1.40 } }, "with_audio": { "720p": { "4": 1.50, "6": 2.25, "8": 3.00 } } } },
    { "id": "omni-flash", "type": "video", "price_usd_flat": 1.00, "resolutions": ["720p"] }
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

## `generate_image`  — paid ($0.03–$0.20 per image)

Start a text-to-image generation with the Google Nano Banana family. Charges
immediately for a single image and returns a `job_id`. Typical completion 10–60 s.
`number_of_images > 1` is a batch and requires `confirm_cost`.

| Parameter | Type | Default | Notes |
|---|---|---|---|
| `prompt` | string, ≤2000 | — | **Required.** English works best. |
| `model` | enum | `nano-banana-2` | `nano-banana-2-lite` (cheapest, 1024 only) · `nano-banana-2` · `nano-banana-pro` (top quality, up to 4K, no 512). |
| `aspect_ratio` | enum | `1:1` | `1:1`, `3:2`, `2:3`, `4:3`, `3:4`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`. |
| `resolution` | enum | `1024` | `512`, `1024`, `2048`, `4096`. 512 only on `nano-banana-2`; lite is 1024 only; `nano-banana-pro` has no 512. |
| `number_of_images` | integer 1–4 | `1` | `>1` requires `confirm_cost`. |
| `negative_prompt` | string, ≤1000 | — | What to avoid. |
| `output_format` | enum | `jpeg` | `jpeg`, `png`, `webp`. |
| `seed` | integer 0–2147483647 | — | For reproducible results. |
| `confirm_cost` | number | — | Required for batches: the quoted total USD you accept. |
| `idempotency_key` | string, ≤64 | — | Safe-retry key. |

**Example call**

```json
{
  "name": "generate_image",
  "arguments": {
    "prompt": "studio photo of a ceramic mug on linen, soft daylight",
    "model": "nano-banana-2",
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
  "cost_charged_usd": 0.06,
  "balance_remaining_usd": 12.34,
  "next_step": "Call get_result with job_id \"cmxyz123...\". Images usually finish in 10–60 seconds."
}
```

**Batch (quote first)** — with `number_of_images: 3` and no `confirm_cost`:

```json
{
  "status": "confirmation_required",
  "quoted_cost_usd": 0.18,
  "balance_usd": 12.40,
  "message": "Generating 3 images costs $0.18. Nothing has been charged.",
  "next_step": "Call generate_image again with the same arguments plus confirm_cost: 0.18."
}
```

---

## `edit_image`  — paid (price of one image of the chosen model/resolution)

Refine a previously generated image with a text instruction (multi-turn editing:
change colors, remove objects, restyle, etc.). Charged like a single image;
auto-refund on failure.

| Parameter | Type | Default | Notes |
|---|---|---|---|
| `source_generation_id` | string | — | **Required.** `job_id` of a **completed** image generation owned by this account. |
| `prompt` | string, ≤2000 | — | **Required.** The edit instruction. |
| `model` | enum | `nano-banana-2` | Same set as `generate_image`. |
| `aspect_ratio` | enum | `1:1` | Same set as `generate_image`. |
| `resolution` | enum | `1024` | `512`, `1024`, `2048`, `4096` (model constraints apply). |
| `output_format` | enum | `jpeg` | `jpeg`, `png`, `webp`. |
| `seed` | integer 0–2147483647 | — | For reproducible results. |
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

## `generate_video`  — paid ($0.10–$4.40 per clip). Cost confirmation always required.

Start a video generation with the Google Veo 3.1 family or Gemini Omni Flash. The
**first call always returns a quote and charges nothing** — repeat with `confirm_cost`
to start. Returns a `job_id`; videos take **1–10+ minutes**.

| Parameter | Type | Default | Notes |
|---|---|---|---|
| `prompt` | string, ≤2000 | — | **Required.** |
| `model` | enum | `veo-3.1-fast` | `veo-3.1` (best Veo quality) · `veo-3.1-fast` (best value) · `veo-3.1-lite` (cheapest, no 4K) · `omni-flash` (always has sound, conversational editing). |
| `duration` | enum `4`,`6`,`8` (Veo) · `3`–`10` (omni-flash) | `8` | Seconds. `omni-flash` accepts any value from 3 to 10 and is billed $0.10/s. Ignored together with `edit_from_generation_id` — a conversational edit always keeps the source clip's length. |
| `resolution` | enum | `720p` | `720p`, `1080p`, `4k`. 4K only on `veo-3.1` / `veo-3.1-fast`; `omni-flash` is 720p only. |
| `aspect_ratio` | enum | `16:9` | `16:9`, `9:16`. |
| `with_audio` | boolean | `false` | Native audio for Veo (costs more). `omni-flash` always has audio. |
| `audio_prompt` | string, ≤500 | — | Describe the desired sound (used when audio is on). |
| `negative_prompt` | string, ≤1000 | — | Veo. |
| `seed` | integer 0–2147483647 | — | Veo only. |
| `first_frame` | string | — | Animate a still image: the `job_id` of a completed image generation on this account, **or** a public http(s) image URL (a signed `get_result` URL works — that is how you pick one variant of a multi-image job). On `omni-flash` it combines with `reference_images`; on Veo it is either/or. |
| `reference_images` | string[], ≤10 | — | Reference images that keep a subject, character or style consistent — they are **not** used as literal frames. Same forms as `first_frame` (`job_id` or public URL). `omni-flash`: up to 10 images in total together with `first_frame`. Veo: at most 3, only with `duration: 8` and without `first_frame`. |
| `edit_from_generation_id` | string | — | **`omni-flash` only:** `job_id` of a completed omni video to refine conversationally; `prompt` describes the changes. Duration, aspect ratio and scene context are inherited from that clip. |
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

Images are fetched server-side and downscaled before they reach the model; private
and internal addresses are rejected. The quote echoes `input_images` so you can see
how many were accepted. Editing modes (`edit_from_generation_id`, `edit_video`) take
their context from the source clip and ignore image inputs.

---

## `edit_video`  — paid ($0.10 per second of output). Cost confirmation always required.

Edit an **existing** video with Gemini Omni Flash (video-to-video): restyle it, replace
or add objects, relight the scene, change the mood — the motion and composition of the
source clip are preserved. The **first call always returns a quote and charges
nothing** — repeat with `confirm_cost` to start. Returns a `job_id`; edits usually take
1–3 minutes.

The source is normalised server-side to MP4 720p and the **first 10 seconds** (model
limit); the output is 720p with sound and keeps the aspect ratio of the source.

**The edited clip is always exactly as long as the source** — the model cannot stretch
or shorten a video. `duration` therefore works only downwards: it trims the source to
its first N seconds and you pay for those N seconds only. Omit it to edit the whole
clip; the quote reports the resolved `duration_seconds` and `source_duration_seconds`.
Clips shorter than 3 seconds are rejected.

| Parameter | Type | Default | Notes |
|---|---|---|---|
| `prompt` | string, ≤2000 | — | **Required.** What to change in the video. |
| `source_generation_id` | string | — | `job_id` of a completed video on this account (see `list_generations`). Use this **or** `video_url`. |
| `video_url` | string | — | Public http(s) link to the source clip (mp4/mov/webm/mkv, ≤200 MB). Private and internal addresses are rejected. |
| `source_ref` | string | — | Returned by the quote when `video_url` was used. Pass it back with `confirm_cost` to reuse the already downloaded clip instead of downloading it again. |
| `duration` | integer 3–10 | source length | Trim the source to its first N seconds and edit only that part ($0.10/s). Values above the source length are ignored — a clip cannot be made longer. |
| `audio_prompt` | string, ≤500 | — | Describe the desired sound — Omni Flash always generates audio. |
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

> `edit_video` rebuilds the clip from its pixels, so it works on any video you own or
> can link to. For refining an **omni-flash** clip you generated moments ago, the
> conversational `generate_video` + `edit_from_generation_id` path keeps the original
> scene context and is usually the better choice.

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
