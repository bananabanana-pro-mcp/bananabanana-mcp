#!/usr/bin/env python3
"""Generate an image on BananaBanana without an MCP client — plain JSON-RPC over HTTPS.

Usage:
    pip install requests
    BB_API_KEY=bb_live_... python generate.py "a watercolor lighthouse at dawn"

Docs: https://bananabanana.pro/mcp#code · ./no-sdk.md
"""

import os
import sys

import requests

MCP = "https://bananabanana.pro/api/mcp"
API_KEY = os.environ.get("BB_API_KEY")


def call(tool: str, **args):
    r = requests.post(
        MCP,
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": tool, "arguments": args},
        },
        timeout=60,
    )
    r.raise_for_status()
    body = r.json()
    if "error" in body:
        raise RuntimeError(f"{body['error'].get('message')} ({body['error'].get('code')})")
    return body["result"]["structuredContent"]


def main() -> None:
    if not API_KEY:
        sys.exit("Set BB_API_KEY (create one at https://bananabanana.pro/profile)")
    prompt = sys.argv[1] if len(sys.argv) > 1 else "watercolor painting of a lighthouse at dawn"

    job = call("generate_image", prompt=prompt)
    print(f"job {job['job_id']} started, charged ${job['cost_charged_usd']}")

    result = call("get_result", job_id=job["job_id"], wait_seconds=30)
    while result["status"] == "processing":
        result = call("get_result", job_id=job["job_id"], wait_seconds=30)

    if result["status"] != "completed":
        sys.exit(f"generation {result['status']}: {result.get('message', '')} (auto-refunded)")

    print(result["files"][0]["url"])
    print(f"cost: ${result['cost_charged_usd']}, balance left: ${result['balance_remaining_usd']}")


if __name__ == "__main__":
    main()
