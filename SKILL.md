---
name: freetoken-bots
description: Discover, verify, and route zero-priced OpenCode Free models for Grok Bot and sibling bots. Use for OpenCode free-model discovery, headless serve on 127.0.0.1, bot diversion rules, daily health checks, and NEVER-auto-paid fallback. OpenCode-only (not OpenRouter/Pi).
version: 0.2.0
---

# FreeToken-Bots (OpenCode edition)

Grok Bot (and sibling bots) may call OpenCode Free models **only** through a local headless `opencode serve` bound to `127.0.0.1`, or via the OpenCode CLI. Do not claim to replace the host product's native model. Do not auto-route to paid Zen / third-party providers.

> Related upstream: [limin112/min-skill FreeToken-Bots](https://github.com/limin112/min-skill/tree/main/skills/FreeToken-Bots) targets OpenRouter + Pi. **This edition** targets OpenCode Free + Grok Bot diversion. Keep them separate; do not mix OpenRouter keys into this stack.

## Principles

- **Free** means an OpenCode model id that contains `free` / `Free`, or is on the known OpenCode Free allowlist below. Free eligibility is dynamic — re-scan daily.
- **Never auto paid.** A 402, quota exhaustion, region block, or rate limit is **not** a reason to call Zen paid, Volcengine paid, or any non-free id. Fail closed; tell the user.
- **Fail-closed model resolution:** refuse any probe/sync id that is not a free candidate. Missing `-free` / `:free` style markers → refuse (do not silently strip and hit paid).
- **Local only.** Bind serve to `127.0.0.1`. Never expose OpenCode HTTP without auth to the public internet.
- **Secrets stay off git.** Password files, Basic auth, API keys, machineIds, and absolute user home paths with credentials must use placeholders in docs and env vars in scripts.
- **Do not rewrite** the user's paid OpenCode / Zen config. `sync` is dry-run proposal only.

## Verified Free pool (default routing)

Probe these before promising other Free ids. Prefer this order for **text**; use Space Bunny for **vision**.

| Role | Model id | Notes |
|------|----------|-------|
| Text default | `opencode/longcat-2.5-preview-free` | Long context, coding, tool-friendly drafts |
| Text backup | `opencode/ling-3.1-flash-free` | Fast extract / short drafts |
| Multimodal | `opencode/space-bunny-free` | Image / video understanding |

Known Free ids that may appear in scans but are **not** default-routed until re-probed:

`opencode/exo-free`, `opencode/ling-3.0-flash-fin-free`, `opencode/mimo-v2.6-flash-free`, `opencode/muse-spark-1.3-contributor-free`, `opencode/nemotron-3-ultra-free`, `opencode/nemotron-3.5-lightning-free`, `opencode/step-5-preview-free`

Observed caveats (re-check on your host): Muse Spark may be region-blocked; MiMo Free may require in-app OpenCode client only; Ling 3.0 Flash Fin may be unavailable upstream — prefer Ling 3.1.

## Usage

From this skill directory:

```bash
# Linux / macOS / agent box
export OPENCODE_CLI="$(command -v opencode || echo "$HOME/.opencode/bin/opencode")"
python3 scripts/radar.py scan
python3 scripts/radar.py status
python3 scripts/radar.py probe --model 'opencode/longcat-2.5-preview-free'
python3 scripts/radar.py sync --dry-run

# Headless serve (cloud / agent box)
./scripts/start-serve.sh   # listens 127.0.0.1:4096

# Windows (optional backup host)
scripts\scan.cmd
```

`scan` writes a private report next to the scripts (default `scripts/report.json`, overridable via `FREETOKEN_REPORT`). Pattern for agents: `~/.config/freetoken-bots/report.json` or skill-local `report.json` — **never commit** live reports.

HTTP call pattern against a running serve:

1. `POST http://127.0.0.1:4096/session` (Basic auth user `opencode`, password from env / password file)
2. `POST http://127.0.0.1:4096/session/:id/message` with body:

```json
{
  "model": { "providerID": "opencode", "modelID": "longcat-2.5-preview-free" },
  "parts": [{ "type": "text", "text": "Reply with exactly: PONG" }]
}
```

## Install workflow (agent)

1. Confirm `opencode` CLI (`opencode --version`). Install: `curl -fsSL https://opencode.ai/install | bash` → usually `$HOME/.opencode/bin/opencode`.
2. Start headless serve with `scripts/start-serve.sh` (creates password file with mode `0600` if missing). Confirm `127.0.0.1:4096` only.
3. Run `scan`, then `probe` for LongCat / Ling 3.1 / Space Bunny. Record pass/fail + cost (must be 0) in the report.
4. Apply **bot diversion** from `references/bot-diversion.md`. Publish / money / brand finals stay on the host bot's native model.
5. Schedule daily `scan` (see Scheduling). On install, tell the user in Chinese:「这个 skill 需要每天早上 8 点跑一次扫描，不配的话免费名单会过期，它自己不会动。」

## Scheduling (required)

This skill does **not** scan by itself.

- Run `python3 /absolute/path/to/scripts/radar.py scan` **every day at 08:00 local** on the machine running OpenCode.
- Cron example: `0 8 * * * /usr/bin/python3 /path/to/scripts/radar.py scan`
- Windows: Task Scheduler → daily 08:00 → `scripts\scan.cmd`
- Compare against previous report; surface newly listed, delisted, and broken Free models.

## Windows optional backup

Cloud / agent-box serve is preferred so the desktop can sleep. Windows desktop is optional backup:

1. Install OpenCode Desktop.
2. Startup folder shortcut target (placeholders only):

```text
"%LOCALAPPDATA%\Programs\@opencodedesktop\resources\opencode-cli.exe" service start
```

3. Point `OPENCODE_CLI` at that `opencode-cli.exe` when running radar on Windows.
4. Desktop powered off → Free via that host stops. Prefer the always-on box.

Details: `references/setup-windows.md`, `references/setup-linux-box.md`.

## Bot diversion (summary)

| Workload | Free? | Model hint |
|----------|-------|------------|
| Daily digests / trend monitors | Strong yes | LongCat → Ling 3.1 |
| Social drafts (X / Weibo / Xiaohongshu) | Draft yes; publish no | LongCat; vision → Space Bunny |
| Vision aesthetics analysis | Vision yes; public copy no | Space Bunny |
| Knowledge-base draft Q&A | Draft yes; formal write no | LongCat / Ling |
| Finance classify | Assist yes; ledger final no | Ling → host review |
| Motion / code tryouts | Tryouts yes; design final no | LongCat + host |
| FreeToken manager itself | Minimal | Prefer orchestration over burning Free |

Full table: `references/bot-diversion.md`.
