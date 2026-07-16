#!/usr/bin/env node
// Generate an image on BananaBanana without an MCP client — plain JSON-RPC over HTTPS.
//
// Usage (Node 18+, no dependencies):
//   BB_API_KEY=bb_live_... node generate.mjs "a watercolor lighthouse at dawn"
//
// Docs: https://bananabanana.pro/mcp#code · ./no-sdk.md

const MCP = "https://bananabanana.pro/api/mcp";
const API_KEY = process.env.BB_API_KEY;

async function call(tool, args) {
  const res = await fetch(MCP, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      jsonrpc: "2.0", id: 1, method: "tools/call",
      params: { name: tool, arguments: args },
    }),
  });
  const body = await res.json();
  if (body.error) throw new Error(`${body.error.message} (${body.error.code})`);
  return body.result.structuredContent;
}

if (!API_KEY) {
  console.error("Set BB_API_KEY (create one at https://bananabanana.pro/profile)");
  process.exit(1);
}
const prompt = process.argv[2] ?? "isometric 3D render of a tiny greenhouse at golden hour";

const job = await call("generate_image", { prompt });
console.log(`job ${job.job_id} started, charged $${job.cost_charged_usd}`);

let out = await call("get_result", { job_id: job.job_id, wait_seconds: 30 });
while (out.status === "processing") {
  out = await call("get_result", { job_id: job.job_id, wait_seconds: 30 });
}

if (out.status !== "completed") {
  console.error(`generation ${out.status}: ${out.message ?? ""} (auto-refunded)`);
  process.exit(1);
}
console.log(out.files[0].url);
console.log(`cost: $${out.cost_charged_usd}, balance left: $${out.balance_remaining_usd}`);
