# Claude Code setup

BananaBanana is a remote (streamable HTTP) MCP server, so Claude Code talks to it
directly — no local process, no `npx`.

## Add the server

```bash
claude mcp add --transport http bananabanana https://bananabanana.pro/api/mcp
```

Run `/mcp` inside Claude Code and choose **Authenticate**. Claude Code opens the
BananaBanana OAuth consent screen; no API key is required.

By default this adds the server to your **local** (per-project) config. To make it
available in every project, add `--scope user`:

```bash
claude mcp add --transport http bananabanana https://bananabanana.pro/api/mcp \
  --scope user
```

## API-key fallback

For CI or another non-interactive environment, create a key at
<https://bananabanana.pro/profile> and add it explicitly:

```bash
claude mcp add --transport http bananabanana https://bananabanana.pro/api/mcp \
  --header "Authorization: Bearer bb_live_YOUR_KEY"
```

## Verify

```bash
claude mcp list
```

You should see `bananabanana` listed. Inside a session you can then ask Claude to,
for example, "list the bananabanana models" (calls `list_models`) or
"generate an image of …".

## Remove

```bash
claude mcp remove bananabanana
```

## Notes

- When using the API-key fallback, the key is stored in Claude Code's MCP config.
  Treat that config like a secret — see
  [`../docs/authentication.md`](../docs/authentication.md).
- Start every session by having the agent call `list_models` / `get_account` — both
  are free and give it live prices and your current balance before it spends anything.
