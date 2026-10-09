# FreeToken-Bots (OpenCode edition)

把 **OpenCode Free 零价模型** 接到 **Grok Bot 云电脑（agent box）** 上：本机 `opencode serve`（`127.0.0.1:4096`）、每天雷达扫描、助手 diversion。**绝不**自动切付费。

> 主安装路径 = **Grok Bot 的云电脑**（常开 Linux box）。你自己的 Windows 桌面只是可选备用（休眠就断）。
>
> ⚠️ **安装要求：这个 skill 自己不会扫描。** 必须在云电脑上配每天早上 8 点（上海时区 / 本地时间）跑 `scripts/radar.py scan`，否则免费名单会过期。装完第一件事就是把 cron 建起来。

## Relationship to upstream

| Edition | Repo path | Stack |
|---------|-----------|-------|
| OpenRouter + Pi | [limin112/min-skill `skills/FreeToken-Bots`](https://github.com/limin112/min-skill/tree/main/skills/FreeToken-Bots) | OpenRouter catalog, Pi child agents |
| **This (OpenCode)** | 本仓库 | OpenCode Free + **Grok Bot 云电脑** diversion |

Do not put OpenRouter API keys into this edition. Do not expect Pi `models.json` sync here.

## Default Free pool

| Role | Model |
|------|-------|
| Text default | `opencode/longcat-2.5-preview-free` |
| Text backup | `opencode/ling-3.1-flash-free` |
| Multimodal | `opencode/space-bunny-free` |

## Quick start — Grok Bot 云电脑（主路径）

在 Grok Bot 的云电脑（Linux agent box）终端里：

```bash
# 0) 克隆本仓库（示例路径）
git clone https://github.com/derekwalldevin-wen/freetoken-bots.git ~/freetoken-bots
cd ~/freetoken-bots

# 1) 安装 OpenCode CLI
curl -fsSL https://opencode.ai/install | bash
export PATH="$HOME/.opencode/bin:$PATH"
opencode --version

# 2) 无头 serve（只绑本机，不上公网）
cp examples/env.example .env   # 改占位符；永远不要提交真实密钥
./scripts/start-serve.sh       # → http://127.0.0.1:4096

# 3) 雷达：扫名单 → 看状态 → 探针 → 只预览 sync
export OPENCODE_CLI="$HOME/.opencode/bin/opencode"
python3 scripts/radar.py scan
python3 scripts/radar.py status
python3 scripts/radar.py probe --model 'opencode/longcat-2.5-preview-free'
python3 scripts/radar.py sync --dry-run

# 4) 每天 8:00 扫描（上海时区 cron；路径改成你的绝对路径）
# crontab -e
# 0 8 * * * /usr/bin/python3 /home/box/freetoken-bots/scripts/radar.py scan >> /tmp/freetoken-radar.log 2>&1
```

完整步骤与 persist：`references/setup-linux-box.md`（标题就是 Grok Bot 云电脑）。

助手 diversion（谁可以用 Free、谁必须留在宿主模型）：`references/bot-diversion.md`。

### Windows 桌面（可选备用）

云电脑挂了才用。见 `references/setup-windows.md` 与 `scripts/scan.cmd`。PC 休眠 = 这条 Free 线路断。

## Layout

```
FreeToken-Bots/
├── SKILL.md                 # agent entry (YAML name + description)
├── README.md                # human install — 云电脑主路径
├── .gitignore
├── scripts/
│   ├── radar.py             # scan | status | probe | sync --dry-run
│   ├── radar.mjs            # Node fallback when Python missing
│   ├── start-serve.sh       # 云电脑 headless serve
│   └── scan.cmd             # Windows 可选备用
├── references/
│   ├── bot-diversion.md     # which bots may burn Free
│   ├── setup-linux-box.md   # ★ Grok Bot 云电脑主安装
│   └── setup-windows.md     # 可选备用
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

## Safety（硬边界）

- Never auto-route to paid models.（绝不自动切付费）
- Never auto-post / auto-reply on social.（绝不自动发帖）
- Never commit passwords, Basic auth secrets, machineIds, or real absolute home paths with credentials.
- `sync` refuses to write without `--dry-run`, and even then only prints a proposal.
- Bind to `127.0.0.1` only unless you know what you are doing (and still require auth).

## License note

Document your own license when you publish. Upstream min-skill terms apply if you fork that repo.
