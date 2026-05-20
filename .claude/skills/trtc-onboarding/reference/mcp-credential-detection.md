# MCP Credential Detection

> Referenced by A1-Q1 and A2-Q2 before showing the manual credential prompt.
> Run this protocol BEFORE the standard "Do you have SDKAppID/SecretKey?" question.

## Detection Protocol

### Step 1: Locate MCP configuration

Search for MCP server configuration in the following locations, **in priority order**
(first match wins):

**Project-level** (checked first):
- `{project_root}/.mcp.json`

**Global / IDE-level** (checked if project-level has no match):
- **Claude Code**: `~/.claude/settings.json` → `mcpServers` section
- **Cursor**: `~/.cursor/mcp.json`
- **Codex**: `~/.codex/mcp.json`
- **CodeBuddy**: `~/.codebuddy/mcp.json`

In each config file, look for a server entry whose **key name** is one of:
- `tencentcloud-sdk-mcp` (from `@tencentcloud/sdk-mcp`)
- `tencent-rtc` (from `@tencent-rtc/mcp`)

**Record the matched key name** — this determines the MCP tool call prefix used
throughout the session (see Step 5).

If no config file exists or no matching server entry is found → go to **Step 4 (Fallback)**.

### Step 2: Extract credentials from env vars

If a matching server entry is found, inspect its `env` block for:
- `SDKAPPID` (case-insensitive: also match `SDKAppID`, `sdkAppId`) — must be a numeric string
- `SECRETKEY` (case-insensitive: also match `SecretKey`, `secretKey`) — hex or base64 string

If EITHER value is missing or empty → go to **Step 4 (Fallback)**.

### Step 3: Present for confirmation (MCP-detected path)

If BOTH values are found, do NOT show the standard A1-Q1/A2-Q2 manual question.
Instead, present the detected credentials for user confirmation:

> I detected TRTC credentials from your MCP server configuration:
> - **SDKAppID**: `{value}`
> - **SecretKey**: `{first 8 chars}...{last 4 chars}` (masked for security)
>
> Use these credentials for this session?

| # | Option | Next |
|---|--------|------|
| 1 | Yes, use these | Hold both values in conversation context. Set `credentials.sdk_app_id_provided = true`, `credentials.secret_key_provided = true` in session state. Proceed to the next step in the flow. |
| 2 | No, I want to use different ones | Fall through to the standard manual credential prompt (A1-Q1 / A2-Q2 original flow). |
| 3 | Type something | free-text |

**On user confirmation (option 1):**
- Store the full SDKAppID value in conversation context
- Store the full SecretKey value in conversation context
- These are used by downstream steps (login code generation, `get_usersig` calls)
- Update session booleans at the next checkpoint write (do NOT trigger an extra write)

### Step 4: Fallback (no MCP detected)

If ANY of the following is true:
- No MCP config file found (neither project-level nor any global IDE config)
- Config exists but contains no server entry matching `tencentcloud-sdk-mcp` or `tencent-rtc`
- A matching server exists but its `env` block is missing `SDKAPPID` or `SECRETKEY`

→ Fall through to the standard manual credential prompt **without mentioning MCP**.
Do not tell the user "I checked for MCP but didn't find it" — just show the
normal credential question as if this protocol was never run.

### Step 5: Record the MCP tool prefix (critical for downstream calls)

The MCP tool call name depends on the **key name** the user registered in their config:

| Config key name | Tool call prefix |
|-----------------|-----------------|
| `tencentcloud-sdk-mcp` | `mcp__tencentcloud-sdk-mcp__` |
| `tencent-rtc` | `mcp__tencent-rtc__` |

**Record this prefix in conversation context** as `mcp_tool_prefix`. All subsequent
MCP tool calls in this session MUST use this prefix:
- `{mcp_tool_prefix}get_usersig` (e.g., `mcp__tencent-rtc__get_usersig`)
- `{mcp_tool_prefix}record_skill_session` (e.g., `mcp__tencent-rtc__record_skill_session`)

**Never hardcode `mcp__tencentcloud-sdk-mcp__` as the prefix** — if the user
configured `@tencent-rtc/mcp` under the key `tencent-rtc`, the correct prefix
is `mcp__tencent-rtc__`.

## Security notes

- The actual credential values are held in **conversation context ONLY**.
- They are NEVER written to `.trtc-session.yaml` (only booleans `sdk_app_id_provided` / `secret_key_provided`).
- The masked display in Step 3 prevents accidental leakage in screenshots/recordings.
- The full SecretKey is used internally for `get_usersig` MCP calls but never echoed in full to the user.
- `.mcp.json` / global IDE configs are the developer's own files — their security is their responsibility.
