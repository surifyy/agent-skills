#!/usr/bin/env node
// scripts/log-bridge.mjs
//
// Web eval log stream — single entry point that:
//   1. Rewrites <workspace>/.env.local with the eval nonce
//   2. Spawns `npm run dev` inside the demo workspace
//   3. Waits for the Vite dev server port to accept TCP
//   4. Launches a headless Chromium via Puppeteer, navigates to the dev URL
//   5. Prints `TRTC_EVAL_NONCE=<nonce>` so runtime_monitor can verify provenance
//   6. Forwards every page console event as a JSON line to stdout (parsed by
//      scripts/lib/log_parsers/puppeteer_parser.py). The event schema carries
//      both the raw text and a best-effort `event` field (first /on[A-Z]\w+/
//      match) so Mode-A (JSON with event) and Mode-B (plain text with on* +
//      trtc keyword) parsers both succeed.
//   7. On SIGTERM: closes the browser, SIGTERMs the vite child (SIGKILL
//      fallback after 200ms), then exits 0.
//
// stdout is piped directly to cases/<id>/runtime.log by log_streamer.py —
// every line here lands in the runtime log untouched.

import { spawn } from "node:child_process";
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { connect as tcpConnect } from "node:net";
import { dirname, join } from "node:path";
import process from "node:process";

// ---------------------------------------------------------------------------
// Argv parsing — `--url <u> --nonce <hex> --workspace <path>`, all required.
// ---------------------------------------------------------------------------
function parseArgv(argv) {
  const out = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--url") out.url = argv[++i];
    else if (a === "--nonce") out.nonce = argv[++i];
    else if (a === "--workspace") out.workspace = argv[++i];
  }
  const missing = ["url", "nonce", "workspace"].filter((k) => !out[k]);
  if (missing.length) {
    process.stderr.write(
      `log-bridge: missing required args: ${missing.join(", ")}\n` +
        `usage: node scripts/log-bridge.mjs --url <u> --nonce <hex> --workspace <path>\n`,
    );
    process.exit(2);
  }
  return out;
}

// ---------------------------------------------------------------------------
// .env.local rewrite — mirrors scripts/lib/platforms/web.py::_inject_web_nonce.
// Strip any existing VITE_EVAL_RUN_NONCE=* line, append the fresh one.
// ---------------------------------------------------------------------------
function injectNonceEnv(workspace, nonce) {
  const envPath = join(workspace, ".env.local");
  let lines = [];
  if (existsSync(envPath)) {
    lines = readFileSync(envPath, "utf8")
      .split("\n")
      .filter((line) => !line.startsWith("VITE_EVAL_RUN_NONCE="));
  }
  lines.push(`VITE_EVAL_RUN_NONCE=${nonce}`);
  writeFileSync(envPath, lines.join("\n") + "\n", "utf8");
}


// ---------------------------------------------------------------------------
// TRTC test credential propagation — reads <case_dir>/.eval-meta/launch.env
// (written by the orchestrator from the skill's config.json / shell env) and
// translates the TRTC_TEST_* keys into the VITE_TRTC_TEST_* keys the frontend
// loadEnv() expects. Without this, Vite's requireEnv() throws and the demo
// crashes before any SDK init can run, which shows up as "JSHandle@error" in
// runtime.log.
//
// launch.env lives at <workspace>/../.eval-meta/launch.env. We resolve it from
// workspace (case_dir = parent of workspace) so log-bridge doesn't need an
// extra CLI flag.
// ---------------------------------------------------------------------------
function injectTrtcCredsEnv(workspace) {
  // <workspace> is "<case_dir>/workspace"; creds live one level up
  const caseDir = dirname(workspace);
  const launchEnvPath = join(caseDir, ".eval-meta", "launch.env");
  if (!existsSync(launchEnvPath)) return;

  const raw = readFileSync(launchEnvPath, "utf8");
  const source = new Map();
  for (const line of raw.split("\n")) {
    const m = line.match(/^([A-Z0-9_]+)=(.*)$/);
    if (m) source.set(m[1], m[2]);
  }

  // Keys the browser bundle needs; Vite only exposes VITE_*-prefixed ones.
  const toVite = {
    TRTC_TEST_SDKAPPID: "VITE_TRTC_TEST_SDKAPPID",
    TRTC_TEST_USERID: "VITE_TRTC_TEST_USERID",
    TRTC_TEST_USERSIG: "VITE_TRTC_TEST_USERSIG",
  };

  const envPath = join(workspace, ".env.local");
  let existing = [];
  if (existsSync(envPath)) {
    existing = readFileSync(envPath, "utf8")
      .split("\n")
      .filter((l) => !/^VITE_TRTC_TEST_/.test(l));
  }
  for (const [src, viteKey] of Object.entries(toVite)) {
    const v = source.get(src);
    if (v !== undefined && v !== "") existing.push(`${viteKey}=${v}`);
  }
  // Remove trailing empty strings before rejoining to avoid double blank lines
  while (existing.length && existing[existing.length - 1] === "") existing.pop();
  writeFileSync(envPath, existing.join("\n") + "\n", "utf8");
}

// ---------------------------------------------------------------------------
// TCP port probe — poll 127.0.0.1:<port> until it accepts a connection.
// ---------------------------------------------------------------------------
function parsePort(url) {
  const m = url.match(/:(\d+)(?:\/|$)/);
  return m ? Number.parseInt(m[1], 10) : 80;
}

function probeTcp(host, port, timeoutMs) {
  return new Promise((resolve) => {
    const socket = tcpConnect({ host, port });
    let done = false;
    const finish = (ok) => {
      if (done) return;
      done = true;
      socket.destroy();
      resolve(ok);
    };
    socket.once("connect", () => finish(true));
    socket.once("error", () => finish(false));
    setTimeout(() => finish(false), timeoutMs);
  });
}

async function waitForPort(host, port, attempts, intervalMs) {
  for (let i = 0; i < attempts; i++) {
    if (await probeTcp(host, port, intervalMs)) return true;
    await new Promise((r) => setTimeout(r, intervalMs));
  }
  return false;
}

// ---------------------------------------------------------------------------
// JSON log emitter — one line per event, parseable by puppeteer_parser.py.
// ---------------------------------------------------------------------------
function emit(payload) {
  process.stdout.write(JSON.stringify(payload) + "\n");
}

function extractEvent(text) {
  const m = text && text.match(/\bon[A-Z]\w+\b/);
  return m ? m[0] : undefined;
}

function nowIso() {
  return new Date().toISOString();
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------
async function main() {
  const { url, nonce, workspace } = parseArgv(process.argv.slice(2));

  // Step 1: write .env.local so Vite picks up VITE_EVAL_RUN_NONCE on dev start
  try {
    injectNonceEnv(workspace, nonce);
  } catch (e) {
    emit({
      ts: nowIso(),
      level: "error",
      text: `log-bridge: failed to write .env.local: ${e.message}`,
      ok: false,
    });
    process.exit(1);
  }

  // Step 1b: propagate TRTC test creds from <case_dir>/.eval-meta/launch.env
  // into .env.local so the frontend's loadEnv() finds VITE_TRTC_TEST_*. Missing
  // launch.env is intentionally non-fatal — a case without creds will fail with
  // a much clearer "Missing required env" from the frontend than from log-bridge.
  try {
    injectTrtcCredsEnv(workspace);
  } catch (e) {
    emit({
      ts: nowIso(),
      level: "warn",
      text: `log-bridge: failed to inject TRTC creds: ${e.message}`,
      ok: false,
    });
  }

  // Step 2: spawn `npm run dev` inside the workspace
  const viteEnv = { ...process.env, EVAL_RUN_NONCE: nonce };
  const vite = spawn("npm", ["run", "dev"], {
    cwd: workspace,
    env: viteEnv,
    stdio: ["ignore", "ignore", "pipe"],
  });
  let viteExited = false;
  vite.on("exit", (code, signal) => {
    viteExited = true;
    emit({
      ts: nowIso(),
      level: code === 0 ? "info" : "warn",
      text: `log-bridge: vite child exited code=${code} signal=${signal || ""}`,
      ok: code === 0,
    });
  });
  // Surface vite stderr into runtime.log so build failures are visible
  vite.stderr.on("data", (chunk) => {
    const text = chunk.toString("utf8").trimEnd();
    if (text) {
      emit({ ts: nowIso(), level: "warn", text: `[vite] ${text}`, ok: true });
    }
  });

  // Step 3: wait for the dev server to listen
  const host = "127.0.0.1";
  const port = parsePort(url);
  const ready = await waitForPort(host, port, 30, 500);
  if (!ready || viteExited) {
    emit({
      ts: nowIso(),
      level: "error",
      text: `log-bridge: vite-not-ready host=${host} port=${port}`,
      ok: false,
    });
    try {
      vite.kill("SIGTERM");
    } catch {}
    process.exit(1);
  }

  // Step 4: launch Puppeteer and attach console listeners
  let puppeteer;
  try {
    puppeteer = (await import("puppeteer")).default;
  } catch (e) {
    emit({
      ts: nowIso(),
      level: "error",
      text: `log-bridge: puppeteer import failed: ${e.message}. Run \`cd scripts && npm install\`.`,
      ok: false,
    });
    try {
      vite.kill("SIGTERM");
    } catch {}
    process.exit(1);
  }

  let browser;
  try {
    browser = await puppeteer.launch({
      headless: "new",
      args: ["--no-sandbox", "--disable-dev-shm-usage"],
    });
  } catch (e) {
    emit({
      ts: nowIso(),
      level: "error",
      text: `log-bridge: chromium launch failed: ${e.message}`,
      ok: false,
    });
    try {
      vite.kill("SIGTERM");
    } catch {}
    process.exit(1);
  }

  const page = await browser.newPage();

  // Step 5: print the nonce marker BEFORE any console events so runtime_monitor
  // always finds it even if the page hangs. Must be the exact literal string
  // `TRTC_EVAL_NONCE=<nonce>` (see scripts/runtime_monitor.py:88-89).
  process.stdout.write(`TRTC_EVAL_NONCE=${nonce}\n`);

  page.on("console", (msg) => {
    let text;
    try {
      text = msg.text();
    } catch {
      text = String(msg);
    }
    const payload = {
      ts: nowIso(),
      level: msg.type(),
      text,
      ok: msg.type() !== "error",
    };
    const ev = extractEvent(text);
    if (ev) payload.event = ev;
    emit(payload);
  });
  page.on("pageerror", (err) => {
    emit({
      ts: nowIso(),
      level: "error",
      text: `[pageerror] ${err && err.message ? err.message : String(err)}`,
      ok: false,
    });
  });
  page.on("requestfailed", (req) => {
    const failure = req.failure();
    emit({
      ts: nowIso(),
      level: "warn",
      text: `[requestfailed] ${req.url()} :: ${failure ? failure.errorText : "unknown"}`,
      ok: false,
    });
  });

  try {
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: 30_000 });
  } catch (e) {
    emit({
      ts: nowIso(),
      level: "error",
      text: `log-bridge: page.goto failed url=${url} err=${e.message}`,
      ok: false,
    });
    // Do not exit — runtime.log already has the nonce marker and the error.
    // Let orchestrator's 60s timer run its course, SIGTERM will clean up.
  }

  // Step 6: SIGTERM cascade — close browser, then kill vite (SIGKILL fallback
  // after 200ms), then exit 0. log_streamer.py sends SIGTERM via PID file.
  let shuttingDown = false;
  const shutdown = async () => {
    if (shuttingDown) return;
    shuttingDown = true;
    try {
      await browser.close();
    } catch {}
    try {
      vite.kill("SIGTERM");
    } catch {}
    setTimeout(() => {
      try {
        if (!viteExited) vite.kill("SIGKILL");
      } catch {}
      process.exit(0);
    }, 200).unref();
  };
  process.on("SIGTERM", shutdown);
  process.on("SIGINT", shutdown);

  // Keep the event loop alive; shutdown is driven by SIGTERM from log_streamer.
  // Puppeteer's internal handles normally suffice, but add a no-op interval as
  // a safety net against premature exit on pages that idle quickly.
  setInterval(() => {}, 60_000).unref();
}

main().catch((e) => {
  emit({
    ts: nowIso(),
    level: "error",
    text: `log-bridge: fatal ${e && e.stack ? e.stack : e}`,
    ok: false,
  });
  process.exit(1);
});
