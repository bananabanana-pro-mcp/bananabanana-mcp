# Authentication

The BananaBanana MCP server accepts two kinds of credentials, both sent as a Bearer
token on every request:

| Method | Best for | What you do |
|--------|----------|-------------|
| **OAuth 2.1** | claude.ai, Claude Desktop, Claude mobile, Claude Code, MCP Inspector and other OAuth-capable clients | paste the server URL, sign in, approve access — nothing to copy |
| **API key** (`bb_live_…`) | Cursor, VS Code, Windsurf, Codex CLI, scripts, CI | create a key in your profile and put it in the client config |

- **Endpoint:** `https://bananabanana.pro/api/mcp`
- **Transport:** streamable HTTP (stateless JSON-RPC)
- **Header:** `Authorization: Bearer <token>`

Both paths end up at the same account: the same balance, the same generation history,
the same usage log and spend cap.

## OAuth 2.1 (nothing to copy)

The server implements the [MCP authorization spec](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization):
OAuth 2.1 with PKCE (S256), dynamic client registration (RFC 7591), protected resource
metadata (RFC 9728) and resource indicators (RFC 8707).

In an OAuth-capable client the flow is:

1. Add a custom connector with the URL `https://bananabanana.pro/api/mcp`.
2. The first protected tool call receives HTTP `401` with a `WWW-Authenticate`
   pointer to the protected-resource metadata.
3. The client discovers the authorization server and its endpoints. Clients using
   dynamic registration register themselves at `/api/oauth/register`.
4. The client creates an S256 PKCE challenge and opens the BananaBanana authorization
   page in a browser.
5. Sign in (or create an account) and approve access.
6. The client exchanges the returned authorization code, together with its PKCE
   verifier and the MCP `resource`, for an access token.
7. The client sends that token as `Authorization: Bearer <access-token>` on protected
   MCP requests and uses the refresh-token grant when a refresh token was issued.

From then on generations are billed to the account you signed in with. Connected apps
are listed in <https://bananabanana.pro/profile> and can be disconnected there at any
time — that invalidates their tokens immediately.

### Discovery endpoints

| Document | URL |
|----------|-----|
| Protected resource metadata at the domain root (RFC 9728) | `https://bananabanana.pro/.well-known/oauth-protected-resource` |
| Protected resource metadata (RFC 9728) | `https://bananabanana.pro/.well-known/oauth-protected-resource/api/mcp` |
| Authorization server metadata (RFC 8414) | `https://bananabanana.pro/.well-known/oauth-authorization-server` |
| Dynamic client registration (RFC 7591) | `POST https://bananabanana.pro/api/oauth/register` |
| Authorization endpoint | `https://bananabanana.pro/oauth/authorize` |
| Token endpoint | `POST https://bananabanana.pro/api/oauth/token` |
| Revocation endpoint (RFC 7009) | `POST https://bananabanana.pro/api/oauth/revoke` |

Details that matter when you implement a client:

- **Scope:** `mcp` (full tool access on behalf of the signed-in user). Request
  `offline_access` as well if you want a refresh token.
- **PKCE:** required, `S256` only — `plain` is rejected.
- **`resource` parameter:** send `https://bananabanana.pro/api/mcp` on both the
  authorization and the token request. Tokens are audience-bound to this server.
- **Grants:** `authorization_code` and `refresh_token`. `client_credentials` is *not*
  supported — every connection needs a user's consent.
- **Token endpoint body:** `application/x-www-form-urlencoded`. The registration
  endpoint takes `application/json`.

Discovery is also advertised on `401`: an unauthenticated `tools/call` returns

```
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer realm="bananabanana", resource_metadata="https://bananabanana.pro/.well-known/oauth-protected-resource/api/mcp", scope="mcp"
```

`initialize`, `ping` and `tools/list` answer without credentials, so a client can
inspect the tool catalogue before signing in (lazy authentication).

The Registry descriptor intentionally declares only the remote URL — it does not
declare a manual `Authorization` header. OAuth discovery happens at runtime through
the standard `401` challenge and well-known documents above. This does not change
existing API-key configurations: a manually configured `Authorization: Bearer
bb_live_…` header continues to work.

### Adding balance from an OAuth session

An OAuth user does not need to open or authenticate the full website profile just to
add funds. Call the free `top_up` tool:

```json
{ "name": "top_up", "arguments": {} }
```

It returns a one-time browser URL tied to the current account and credential. The URL
is valid for **30 minutes** and creates a restricted **deposit-only** session whose
idle timeout is **two hours**, sliding while the user checks the balance or waits for a
cryptocurrency transfer. The restricted page can show the balance and deposit address,
but cannot expose API keys, profile data, generation history or promo-code controls.

Only a SHA-256 hash of each URL and session secret is stored. The raw URL token is not
written to nginx access logs, and redemption immediately redirects to a clean URL. A
used or expired link returns a `410` page that tells the user to ask the agent to call
`top_up` again. Reopening the same link works only in the browser that already owns its
restricted session; another browser cannot reuse it. Issuance is limited to three
links per minute for each credential.

Bearer API-key users receive the normal profile URL from `top_up`, because that path
uses the ordinary web login rather than an OAuth-only restricted session.

## API keys

### Get a key

1. Sign in at <https://bananabanana.pro> (or create an account — new accounts start
   with a small free balance).
2. Open your profile: <https://bananabanana.pro/profile>.
3. In the **API Keys** section, create a new key.
4. Copy the key immediately — it is shown **once** and cannot be retrieved later.

A key looks like:

```
bb_live_…
```

### Use the key

Send it in the `Authorization` header on every request:

```
Authorization: Bearer bb_live_YOUR_KEY
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

A missing or malformed credential returns HTTP `401` with a `WWW-Authenticate: Bearer`
header and a JSON-RPC error. See [troubleshooting.md](./troubleshooting.md).

### How keys work

- **Hashed at rest.** Only a SHA-256 hash of the key is stored. If you lose the key,
  you cannot recover it — create a new one and revoke the old.
- **Scoped to your account.** Every generation is billed to the balance of the
  account that owns the key, and appears in that account's generation history
  (shared with the website).
- **One account, many keys.** Give each client or project its own key so you can
  revoke or cap them independently.

## Spend caps and limits

These apply to API keys and OAuth connections alike — an OAuth connection gets its own
entry in the profile with the same controls.

- **Daily spend cap (optional).** Each credential can carry a daily USD cap. Once it
  has spent that much in a UTC day, further paid calls return `DAILY_CAP_EXCEEDED`
  until the next UTC day. Set or change it in the profile.
- **Rate limits.** Requests may return HTTP `429` or tool error `RATE_LIMITED`.
  Respect `Retry-After` when present and retry with backoff.
- **Usage log.** Every paid tool call is recorded (tool, model, cost, prompt
  preview) and visible in your profile.

See [pricing.md](./pricing.md) for the full cost and limits picture.

## Rotation & revocation

- **Revoke** a key — or disconnect an OAuth app — from the profile at any time; it
  stops working immediately.
- **Rotate** by creating a new key, updating your client config, then revoking the
  old one. Because keys are independent, you can do this with zero downtime.
- If a credential may have leaked, **revoke it first**, then investigate. A leaked key
  can spend your balance up to its daily cap.

## Keeping credentials safe

- Treat a key like a password. Anyone with it can spend your balance.
- **Never commit keys.** This repo's `.gitignore` excludes `.env` and `*.pem`; keep
  real keys out of any config you check in — use placeholders like `bb_live_YOUR_KEY`.
- Prefer client features that store the key securely (e.g. VS Code's encrypted
  `promptString` input, shown in [`examples/vscode.json`](../examples/vscode.json)).
- Where OAuth is available, prefer it: no manually copied API key sits in a config
  file, access tokens expire and capable clients refresh them automatically.
- Use separate credentials per machine/project and set daily caps to bound the blast
  radius.
- Rotate periodically.
