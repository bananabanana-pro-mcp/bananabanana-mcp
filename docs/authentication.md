# Authentication

The BananaBanana MCP server authenticates every request with a **Bearer API key**.
There is no OAuth flow and no sign-in dialog — you create a key in your account and
put it in your MCP client's config.

- **Endpoint:** `https://bananabanana.pro/api/mcp`
- **Transport:** streamable HTTP (stateless JSON-RPC)
- **Header:** `Authorization: Bearer bb_live_…`

## Get an API key

1. Sign in at <https://bananabanana.pro> (or create an account — new accounts start
   with a small free balance).
2. Open your profile: <https://bananabanana.pro/profile>.
3. In the **API Keys** section, create a new key.
4. Copy the key immediately — it is shown **once** and cannot be retrieved later.

A key looks like:

```
bb_live_0123456789abcdef0123456789abcdef01234567
```

That is the `bb_live_` prefix followed by 40 hexadecimal characters.

## Use the key

Send it in the `Authorization` header on every request:

```
Authorization: Bearer bb_live_0123456789abcdef0123456789abcdef01234567
```

See the [`examples/`](../examples) directory for ready-to-paste client configs
(Claude Code, Claude Desktop, Cursor, VS Code, Windsurf).

Quick sanity check with `curl` (this calls `list_models`, which is free):

```bash
curl -s https://bananabanana.pro/api/mcp \
  -H "Authorization: Bearer bb_live_YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"list_models","arguments":{}}}'
```

A missing or malformed key returns HTTP `401` with a `WWW-Authenticate: Bearer`
header and a JSON-RPC error. See [troubleshooting.md](./troubleshooting.md).

## How keys work

- **Hashed at rest.** Only a SHA-256 hash of the key is stored. If you lose the key,
  you cannot recover it — create a new one and revoke the old.
- **Scoped to your account.** Every generation is billed to the balance of the
  account that owns the key, and appears in that account's generation history
  (shared with the website).
- **One account, many keys.** Give each client or project its own key so you can
  revoke or cap them independently.

## Spend caps and limits

- **Daily spend cap (optional).** Each key can carry a per-key daily USD cap. Once
  the key has spent that much in a UTC day, further paid calls return
  `DAILY_CAP_EXCEEDED` until the next UTC day. Set or change it in the profile.
- **Rate limit.** 20 tool calls per minute per key.
- **Usage log.** Every paid tool call is recorded per key (tool, model, cost, prompt
  preview) and visible in your profile.

See [pricing.md](./pricing.md) for the full cost and limits picture.

## Rotation & revocation

- **Revoke** a key from the profile at any time — it stops working immediately.
- **Rotate** by creating a new key, updating your client config, then revoking the
  old one. Because keys are independent, you can do this with zero downtime.
- If a key may have leaked, **revoke it first**, then investigate. A leaked key can
  spend your balance up to its daily cap.

## Keeping keys safe

- Treat a key like a password. Anyone with it can spend your balance.
- **Never commit keys.** This repo's `.gitignore` excludes `.env` and `*.pem`; keep
  real keys out of any config you check in — use placeholders like `bb_live_YOUR_KEY`.
- Prefer client features that store the key securely (e.g. VS Code's encrypted
  `promptString` input, shown in [`examples/vscode.json`](../examples/vscode.json)).
- Use separate keys per machine/project and set daily caps to bound the blast radius.
- Rotate periodically.
