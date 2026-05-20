# MCP UserSig Generation

> Referenced during login code generation in A2-Q3 (when processing a login-auth
> slice) and A1 (when configuring demo credentials).

## When to trigger

Call this protocol when ALL of these are true:

1. **MCP server is available** — detected via `mcp-credential-detection.md` (either
   project-level or global IDE config contains a `tencentcloud-sdk-mcp` or `tencent-rtc`
   server entry), and the `mcp_tool_prefix` is already recorded in conversation context
2. **Credentials are in conversation context** — SDKAppID + SecretKey were already
   collected (via MCP auto-detect or manual input)
3. **Current step involves login/auth** — the slice being processed is
   `{product}/login-auth` or involves `login()` / `LoginStore` / TIM login /
   TRTC `enterRoom` authentication

If ANY condition is false → go to **Fallback (no MCP)** below.

## Generation Protocol

### Step 1: Generate a test userID

Create a test userID in the format `userXXX` where XXX is a zero-padded 3-digit
number. Default: `user001`.

If the user has expressed a preference for a specific userID or naming pattern,
use their chosen format instead.

### Step 2: Call `get_usersig`

Invoke the MCP tool using the **dynamic prefix** from `mcp_tool_prefix`
(recorded during credential detection — see `mcp-credential-detection.md` Step 5):

```
{mcp_tool_prefix}get_usersig(userID: "user001")
```

Examples:
- If prefix is `mcp__tencentcloud-sdk-mcp__` → call `mcp__tencentcloud-sdk-mcp__get_usersig`
- If prefix is `mcp__tencent-rtc__` → call `mcp__tencent-rtc__get_usersig`

This returns a real, time-limited userSig generated from the configured
SDKAppID and SecretKey in the MCP server's environment.

**If the call fails** (tool error, timeout, etc.): fall through to the
**Fallback (no MCP)** section. Do not retry. Do not block the flow.

### Step 3: Embed in generated code

In the login code being generated, use the MCP-returned values as **pre-filled
defaults** while also providing input fields for custom credentials:

```typescript
// ================================================
// Test credentials (auto-generated, development only)
// ================================================
const DEFAULT_SDK_APP_ID = {sdkAppId};       // from MCP config
const DEFAULT_USER_ID = 'user001';           // test user
const DEFAULT_USER_SIG = '{mcp_returned_usersig}';

// ⚠️ This userSig is for development/testing only.
// It expires in ~24 hours. For production, generate userSig on your server.
// See: https://trtc.io/document/34385
```

### Step 4: Provide user-input entry

The generated login page / component MUST also include input fields (or a
configuration mechanism) that allows users to override the defaults at runtime.

**For Web (Vue/React):**
- Input fields for userID and userSig in the login form
- Pre-fill with the default values from Step 3
- Allow the user to type their own values before clicking login

**For Native (iOS/Android/Flutter):**
- A config struct/object with the test defaults
- Clear comments marking where to replace with custom values
- Optionally: text fields on the login screen if the UI supports it

**Template pattern (Web Vue example):**

```vue
<template>
  <div class="login-form">
    <input v-model="userId" placeholder="UserID" />
    <input v-model="userSig" placeholder="UserSig" type="password" />
    <button @click="handleLogin">Login</button>
  </div>
</template>

<script setup>
import { ref } from 'vue';

// Pre-filled test credentials (generated via MCP tool, valid ~24h)
const userId = ref('user001');
const userSig = ref('{mcp_returned_usersig}');

// SDKAppID from MCP configuration
const sdkAppId = {sdkAppId};

async function handleLogin() {
  // login logic using userId.value, userSig.value, sdkAppId
}
</script>
```

### Step 5: Multiple test users (optional enhancement)

If the scenario requires multiple users (e.g., caller + callee in a Call demo,
host + audience in Live), generate userSigs for each:

- `user001` (first participant)
- `user002` (second participant)

Call `get_usersig` for each userID. Present them clearly labeled:

```
// User A (e.g., host / caller)
const USER_A_ID = 'user001';
const USER_A_SIG = '{usersig_for_user001}';

// User B (e.g., audience / callee) — use in a second browser tab or device
const USER_B_ID = 'user002';
const USER_B_SIG = '{usersig_for_user002}';
```

## Fallback (no MCP available)

When the MCP server is NOT configured, or the `get_usersig` call fails:

1. Generate login code with **placeholder values**:
   ```typescript
   const SDK_APP_ID = 0;          // TODO: Replace with your SDKAppID
   const USER_ID = 'YOUR_USER_ID'; // TODO: Replace with your userID
   const USER_SIG = 'YOUR_USER_SIG'; // TODO: Replace with your userSig
   ```

2. Include clear instructions as code comments:
   ```typescript
   // To get these values:
   // 1. Go to https://trtc.io/console
   // 2. Create or select an application
   // 3. Find SDKAppID in the app details
   // 4. Generate a test UserSig from the console's "Quick Start" tool
   //    (for production, generate UserSig on your server)
   ```

3. The login page input fields are still generated (same as Step 4 above),
   but with empty/placeholder default values instead of pre-filled test credentials.

## Never

- Never hardcode a real SecretKey in generated **client-side** code
- Never generate userSig manually (using HMAC-SHA256) in client code — always
  either call the MCP tool or instruct the user to use server-side generation
- Never present the MCP-generated userSig as "production-ready" — always mark
  it as test/development only with an expiry warning
- Never call `get_usersig` for more than 3 users in a single step (performance)
