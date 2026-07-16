# Calling the server without an MCP client (curl / Python / TypeScript)

The server is plain **JSON-RPC 2.0 over HTTPS** (MCP streamable HTTP, stateless).
You don't need an MCP SDK or client — any language that can send a POST request
can generate media. Live version of these snippets: <https://bananabanana.pro/mcp#code>.

Every request is:

```http
POST https://bananabanana.pro/api/mcp
Authorization: Bearer bb_live_YOUR_KEY
Content-Type: application/json
Accept: application/json, text/event-stream

{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"<tool>","arguments":{...}}}
```

Responses are a single JSON body; the useful payload is
`result.structuredContent`. No session handshake is required — `initialize` is
optional, and each call is independent.

## curl

```bash
# start an image generation (charges one image, $0.06 on the default model)
curl -s https://bananabanana.pro/api/mcp \
  -H "Authorization: Bearer bb_live_YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{
        "name":"generate_image",
        "arguments":{"prompt":"studio photo of a ceramic mug on linen, soft daylight"}}}'

# → result.structuredContent.job_id = "cmxy…"

# fetch the result (long-polls server-side up to 30 s; free)
curl -s https://bananabanana.pro/api/mcp \
  -H "Authorization: Bearer bb_live_YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{
        "name":"get_result",
        "arguments":{"job_id":"cmxy…","wait_seconds":30}}}'
```

## Python

Runnable version: [`generate.py`](./generate.py) (needs `pip install requests`).

```python
import requests

MCP = "https://bananabanana.pro/api/mcp"
HEADERS = {"Authorization": "Bearer bb_live_YOUR_KEY"}

def call(tool, **args):
    r = requests.post(MCP, headers=HEADERS, json={
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": tool, "arguments": args},
    })
    r.raise_for_status()
    return r.json()["result"]["structuredContent"]

job = call("generate_image", prompt="watercolor painting of a lighthouse at dawn")

result = call("get_result", job_id=job["job_id"], wait_seconds=30)
while result["status"] == "processing":
    result = call("get_result", job_id=job["job_id"], wait_seconds=30)

print(result["files"][0]["url"], "cost:", result["cost_charged_usd"])
```

## TypeScript / JavaScript

Runnable version: [`generate.mjs`](./generate.mjs) (Node 18+, no dependencies).

```ts
const MCP = "https://bananabanana.pro/api/mcp";

async function call(tool: string, args: Record<string, unknown>) {
  const res = await fetch(MCP, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${process.env.BB_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      jsonrpc: "2.0", id: 1, method: "tools/call",
      params: { name: tool, arguments: args },
    }),
  });
  const { result } = await res.json();
  return result.structuredContent;
}

const job = await call("generate_image", {
  prompt: "isometric 3D render of a tiny greenhouse at golden hour",
});

let out = await call("get_result", { job_id: job.job_id, wait_seconds: 30 });
while (out.status === "processing") {
  out = await call("get_result", { job_id: job.job_id, wait_seconds: 30 });
}
console.log(out.files[0].url, "cost:", out.cost_charged_usd);
```

## Notes

- **Async jobs.** `generate_image` / `generate_video` return a `job_id` immediately;
  poll `get_result` (free, long-polls up to 30 s per call) until `status` is
  `completed` or `failed`. Failed jobs are refunded automatically.
- **Cost confirmation.** `generate_video` and multi-image `generate_image` return
  `status: "confirmation_required"` with a `quoted_cost_usd` and charge nothing —
  repeat the call with `confirm_cost: <quoted value>` to run it. See
  [`../docs/tools.md`](../docs/tools.md).
- **Idempotency.** Pass an `idempotency_key` argument to any `generate_*` call to
  make retries safe — a repeated key never charges twice.
- **Errors.** JSON-RPC errors carry a machine-readable code (`INSUFFICIENT_BALANCE`,
  `SAFETY_FILTERED`, `RATE_LIMITED`, …) — see
  [`../docs/troubleshooting.md`](../docs/troubleshooting.md).
- **Limits.** 20 tool calls/min per key. Media URLs are signed and valid for 24 h —
  download what you want to keep.
