# FreeToken-Bots (OpenCode edition)

Route **zero-priced OpenCode Free** models for Grok Bot and sibling agents — headless `opencode serve` on `127.0.0.1:4096`, daily radar, bot diversion rules, **never** auto-paid failover.

> ⚠️ **安装要求：这个 skill 自己不会扫描。** 必须配每天早上 8 点（本地时间）跑 `scripts/radar.py scan` 的定时任务（cron / launchd / systemd / Windows 任务计划程序 任选），否则免费名单会过期。装完第一件事就是把定时任务建起来。

## Relationship to upstream

| Edition | Repo path | Stack |
|---------|-----------|-------|
| OpenRouter + Pi | [limin112/min-skill `skills/FreeToken-Bots`](https://github.com/limin112/min-skill/tree/main/skills/FreeToken-Bots) | OpenRouter catalog, Pi child agents |
| **This (OpenCode)** | `skills/FreeToken-Bots` in your fork / skill repo | OpenCode Free, Grok Bot diversion |

Do not put OpenRouter API keys into this edition. Do not expect Pi `models.json` sync here.

## Default Free pool

| Role | Model |
|------|-------|
| Text default | `opencode/longcat-2.5-preview-free` |
| Text backup | `opencode/ling-3.1-flash-free` |
| Multimodal | `opencode/space-bunny-free` |

## Quick start

```bash
# 1) Install OpenCode CLI (Linux / agent box)
curl -fsSL https://opencode.ai/install | bash
export PATH="$HOME/.opencode/bin:$PATH"

# 2) Headless serve (localhost only)
cp examples/env.example .env   # edit placeholders; never commit real secrets
./scripts/start-serve.sh

# 3) Radar
export OPENCODE_CLI="$HOME/.opencode/bin/opencode"
python3 scripts/radar.py scan
python3 scripts/radar.py status
python3 scripts/radar.py probe --model 'opencode/longcat-2.5-preview-free'
python3 scripts/radar.py sync --dry-run
```

Windows optional backup: see `references/setup-windows.md` and `scripts/scan.cmd`.

## Layout

```
FreeToken-Bots/
├── SKILL.md                 # agent entry (YAML name + description)
├── README.md                # human install
├── .gitignore
├── scripts/
│   ├── radar.py             # scan | status | probe | sync --dry-run
│   ├── radar.mjs            # Node fallback when Python missing
│   ├── start-serve.sh       # Linux headless serve helper
│   └── scan.cmd             # Windows daily entry
├── references/
│   ├── bot-diversion.md     # which bots may burn Free
│   ├── setup-linux-box.md
│   └── setup-windows.md
├── examples/
│   ├── env.example
│   └── report.example.json
└── tests/
    └── test_radar.py
```

## Report path

- Default: `scripts/report.json` (alongside radar)
- Override: `FREETOKEN_REPORT=/path/to/report.json`
- Recommended private home path: `~/.config/freetoken-bots/report.json`
- Live reports are gitignored — commit only `examples/report.example.json`

## Safety

- Never auto-route to paid models.
- Never commit passwords, Basic auth secrets, machineIds, or real absolute home paths with credentials.
- `sync` refuses to write without `--dry-run`, and even then only prints a proposal.
- Bind to `127.0.0.1` only unless you know what you are doing (and still require auth).

## License note

Document your own license when you publish. Upstream min-skill terms apply if you fork that repo.
