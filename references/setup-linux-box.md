# Setup — Linux / agent box (preferred always-on)

## Install CLI

```bash
curl -fsSL https://opencode.ai/install | bash
export PATH="$HOME/.opencode/bin:$PATH"
opencode --version
```

## Password file (local only)

```bash
PASS_FILE="${OPENCODE_SERVER_PASSWORD_FILE:-$HOME/.opencode/server.password}"
mkdir -p "$(dirname "$PASS_FILE")"
openssl rand -hex 16 > "$PASS_FILE"
chmod 600 "$PASS_FILE"
```

Do not commit this file. Do not paste contents into chat or git.

## Start headless serve

```bash
./scripts/start-serve.sh
# → http://127.0.0.1:4096  Basic auth user: opencode
```

Or manually:

```bash
export OPENCODE_SERVER_PASSWORD="$(cat "$PASS_FILE")"
opencode serve --port 4096 --hostname 127.0.0.1
```

## Probe via HTTP (concept)

```bash
# POST /session then POST /session/:id/message
# model.providerID = "opencode"
# model.modelID    = "longcat-2.5-preview-free"   # note: no "opencode/" prefix in HTTP body
```

CLI probe alternative:

```bash
export OPENCODE_CLI="$HOME/.opencode/bin/opencode"
python3 scripts/radar.py probe --model 'opencode/longcat-2.5-preview-free'
```

## Persist across reboot

Use systemd user service, supervisord, or your agent-box start hook to run `start-serve.sh`. Free models from the built-in `opencode` provider often work **without** Zen login; paid Zen needs separate auth — do not enable for this skill's default path.

## Daily scan

```cron
0 8 * * * /usr/bin/python3 /absolute/path/to/FreeToken-Bots/scripts/radar.py scan
```
