#!/usr/bin/env bash
# Start headless OpenCode serve on 127.0.0.1 (never bind public by default).
set -euo pipefail

export PATH="${HOME}/.opencode/bin:${PATH}"
PORT="${OPENCODE_PORT:-4096}"
HOST="${OPENCODE_HOSTNAME:-127.0.0.1}"
PASS_FILE="${OPENCODE_SERVER_PASSWORD_FILE:-${HOME}/.opencode/server.password}"

if ! command -v opencode >/dev/null 2>&1; then
  echo "opencode not found. Install: curl -fsSL https://opencode.ai/install | bash" >&2
  exit 1
fi

mkdir -p "$(dirname "$PASS_FILE")"
if [[ ! -f "$PASS_FILE" ]]; then
  if command -v openssl >/dev/null 2>&1; then
    openssl rand -hex 16 > "$PASS_FILE"
  else
    head -c 32 /dev/urandom | xxd -p -c 32 > "$PASS_FILE"
  fi
  chmod 600 "$PASS_FILE"
  echo "created password file: $PASS_FILE (mode 0600)"
fi

if command -v ss >/dev/null 2>&1; then
  if ss -ltn 2>/dev/null | awk '{print $4}' | grep -q ":${PORT}$"; then
    echo "Port $PORT already in use; not starting another serve."
    exit 0
  fi
fi

if [[ -n "${OPENCODE_SERVER_PASSWORD:-}" ]]; then
  PASS="$OPENCODE_SERVER_PASSWORD"
else
  PASS="$(cat "$PASS_FILE")"
fi
export OPENCODE_SERVER_PASSWORD="$PASS"

LOG="${OPENCODE_SERVE_LOG:-/tmp/opencode-serve.log}"
nohup opencode serve --port "$PORT" --hostname "$HOST" --print-logs --log-level INFO \
  > "$LOG" 2>&1 &
echo "started pid=$! host=$HOST port=$PORT password_file=$PASS_FILE log=$LOG"
echo "Basic auth user: opencode  (password in file; never commit)"
