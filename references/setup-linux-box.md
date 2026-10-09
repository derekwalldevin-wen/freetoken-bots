# Setup — Grok Bot 云电脑（主路径）

> **主安装目标**：Grok Bot 的云电脑（Linux agent box）。常开、可装 CLI、可跑 headless serve、可配 cron。  
> Windows 桌面见 `setup-windows.md`，仅作可选备用。

云电脑 = 和你对话的 Grok Bot / 助手们共用的那台 Linux 机器（box）。装一次，热点纪要、运营助手、视觉美学都可以共用 Free 线路；你自己的 Windows 休眠不会把线路掐断。

## 1. 克隆仓库

```bash
git clone https://github.com/derekwalldevin-wen/freetoken-bots.git ~/freetoken-bots
cd ~/freetoken-bots
```

（路径可改；后面 cron 要用**绝对路径**。）

## 2. 安装 OpenCode CLI

```bash
curl -fsSL https://opencode.ai/install | bash
export PATH="$HOME/.opencode/bin:$PATH"
opencode --version
```

把 `export PATH=...` 写进 `~/.bashrc`（或云电脑启动钩子），避免新会话找不到命令。

## 3. 密码文件（仅本机）

```bash
PASS_FILE="${OPENCODE_SERVER_PASSWORD_FILE:-$HOME/.opencode/server.password}"
mkdir -p "$(dirname "$PASS_FILE")"
openssl rand -hex 16 > "$PASS_FILE"
chmod 600 "$PASS_FILE"
```

不要提交这个文件。不要把内容贴进聊天或 git。

## 4. 启动无头 serve（只绑 127.0.0.1）

```bash
cd ~/freetoken-bots
./scripts/start-serve.sh
# → http://127.0.0.1:4096  Basic auth user: opencode
```

或手动：

```bash
export OPENCODE_SERVER_PASSWORD="$(cat "$PASS_FILE")"
opencode serve --port 4096 --hostname 127.0.0.1
```

**硬边界**：hostname 必须是 `127.0.0.1`。不要对公网裸奔。

## 5. 雷达：扫名单 → 探针

```bash
export OPENCODE_CLI="$HOME/.opencode/bin/opencode"
python3 scripts/radar.py scan
python3 scripts/radar.py status
python3 scripts/radar.py probe --model 'opencode/longcat-2.5-preview-free'
python3 scripts/radar.py probe --model 'opencode/ling-3.1-flash-free'
python3 scripts/radar.py probe --model 'opencode/space-bunny-free'
python3 scripts/radar.py sync --dry-run   # 只预览，不改写付费配置
```

HTTP 探针概念（Basic auth）：

```bash
# POST /session 然后 POST /session/:id/message
# model.providerID = "opencode"
# model.modelID    = "longcat-2.5-preview-free"   # HTTP body 里不要带 "opencode/" 前缀
```

## 6. 每天 8:00 扫描（必配）

这个 skill **自己不会扫描**。免费名单会变，必须定时跑：

```cron
0 8 * * * /usr/bin/python3 /home/box/freetoken-bots/scripts/radar.py scan >> /tmp/freetoken-radar.log 2>&1
```

把 `/home/box/freetoken-bots` 换成你的绝对路径。时区按云电脑本地（Grok Bot box 一般为 Asia/Shanghai）。

装完请用中文告诉使用者：「这个 skill 需要每天早上 8 点跑一次扫描，不配的话免费名单会过期，它自己不会动。」

## 7. 开机自启 serve（可选但推荐）

用 systemd user service、supervisord，或云电脑 / agent-box 的 start hook 跑 `start-serve.sh`。  
Built-in `opencode` provider 的 Free 模型通常**不需要** Zen 登录；付费 Zen 另配 —— 本 skill 默认路径不要开付费。

## 8. 助手 diversion

谁可以用 Free、谁必须留在宿主模型：见 `bot-diversion.md`。  
发帖 / 回复 / 私信 / 花钱 / 品牌终稿 → 仍由宿主确认，**绝不自动发**。

## 硬边界速查

| 规则 | 说明 |
|------|------|
| 不自动切付费 | 402 / 额度尽 / 地区拦 / 限流 → 失败关闭 |
| 不自动发帖 | 分流只写草稿 |
| 只绑 127.0.0.1 | 不对公网暴露 |
| 密钥不进 git | `.env`、password 文件已 gitignore |
| sync 默认 dry-run | 防止手滑改写付费配置 |
