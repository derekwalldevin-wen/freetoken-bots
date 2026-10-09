#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OpenCode free-model radar (OpenCode Free models only).

Commands:
  scan              Discover free OpenCode models; write report.json
  status            Print short Chinese summary of latest report
  probe --model ID  Plain completion (+ tools probe if CLI supports)
  sync --dry-run    Print proposed config change only; never writes opencode.json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPORT_PATH = Path(
    os.environ.get("FREETOKEN_REPORT", str(ROOT / "report.json"))
).expanduser()


def resolve_cli() -> Path:
    env = os.environ.get("OPENCODE_CLI")
    if env:
        return Path(env)
    which = shutil.which("opencode")
    if which:
        return Path(which)
    home_bin = Path.home() / ".opencode" / "bin" / "opencode"
    if home_bin.exists():
        return home_bin
    # Windows desktop default (placeholder user profile via LOCALAPPDATA)
    local = os.environ.get("LOCALAPPDATA")
    if local:
        win = (
            Path(local)
            / "Programs"
            / "@opencodedesktop"
            / "resources"
            / "opencode-cli.exe"
        )
        if win.exists():
            return win
    return Path("opencode")


CLI = resolve_cli()
SHANGHAI = timezone(timedelta(hours=8))

KNOWN_FREE_IDS = {
    "opencode/exo-free",
    "opencode/ling-3.0-flash-fin-free",
    "opencode/ling-3.1-flash-free",
    "opencode/longcat-2.5-preview-free",
    "opencode/mimo-v2.6-flash-free",
    "opencode/muse-spark-1.3-contributor-free",
    "opencode/nemotron-3-ultra-free",
    "opencode/nemotron-3.5-lightning-free",
    "opencode/space-bunny-free",
    "opencode/step-5-preview-free",
}

FREE_RE = re.compile(r"free", re.IGNORECASE)


def now_shanghai_iso() -> str:
    return datetime.now(SHANGHAI).isoformat(timespec="seconds")


def run_cli(args: list[str], timeout: int = 60) -> subprocess.CompletedProcess:
    cmd = [str(CLI), *args]
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        shell=False,
    )


def cli_version() -> str:
    try:
        p = run_cli(["--version"], timeout=30)
        out = (p.stdout or p.stderr or "").strip()
        return out.splitlines()[0] if out else "unknown"
    except Exception as e:
        return f"error: {e}"


def list_models() -> list[str]:
    """Non-interactive: `opencode models` prints provider/model lines."""
    p = run_cli(["models"], timeout=60)
    if p.returncode != 0:
        raise RuntimeError(
            f"opencode models failed (code={p.returncode}): "
            f"{(p.stderr or p.stdout or '').strip()}"
        )
    models = []
    for line in (p.stdout or "").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "/" not in line:
            continue
        models.append(line.split()[0])
    return models


def is_free_candidate(model_id: str) -> bool:
    if FREE_RE.search(model_id):
        return True
    if model_id in KNOWN_FREE_IDS:
        return True
    return False


def classify(models: list[str]) -> dict:
    candidates = []
    needs_verification = []
    inactive = []
    eligible = []
    notes = [
        "OpenCode Free models only.",
        "eligible[] stays empty until probe verifies plain (+ tools if supported).",
        "IDs matching /free/i under opencode/ are candidates; tool capability unverified at scan.",
        "Paid providers without free marker are ignored.",
        "Never auto-route to paid on failure.",
    ]

    for mid in models:
        if not is_free_candidate(mid):
            continue
        entry = {
            "id": mid,
            "provider": mid.split("/", 1)[0] if "/" in mid else "",
            "free_marker": bool(FREE_RE.search(mid)),
            "tools_verified": False,
            "plain_verified": False,
        }
        candidates.append(entry)
        needs_verification.append(
            {
                "id": mid,
                "reason": "listed as free candidate; plain/tools not probed in this scan",
            }
        )

    return {
        "candidates": candidates,
        "eligible": eligible,
        "needs_verification": needs_verification,
        "inactive": inactive,
        "notes": notes,
    }


def cmd_scan(_: argparse.Namespace) -> int:
    version = cli_version()
    try:
        models = list_models()
    except Exception as e:
        report = {
            "scanned_at": now_shanghai_iso(),
            "cli_version": version,
            "candidates": [],
            "eligible": [],
            "needs_verification": [],
            "inactive": [],
            "notes": [f"scan failed: {e}"],
        }
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"scan failed: {e}", file=sys.stderr)
        return 1

    parts = classify(models)
    report = {
        "scanned_at": now_shanghai_iso(),
        "cli_version": version,
        "all_models_count": len(models),
        **parts,
        "top_recommendation": (
            parts["candidates"][0]["id"] if parts["candidates"] else None
        ),
    }
    preferred = [
        "opencode/longcat-2.5-preview-free",
        "opencode/ling-3.1-flash-free",
        "opencode/space-bunny-free",
        "opencode/nemotron-3.5-lightning-free",
    ]
    ids = {c["id"] for c in parts["candidates"]}
    for pref in preferred:
        if pref in ids:
            report["top_recommendation"] = pref
            break

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"scan ok: {len(parts['candidates'])} free candidates → {REPORT_PATH}")
    if report["top_recommendation"]:
        print(f"top_recommendation: {report['top_recommendation']}")
    return 0


def cmd_status(_: argparse.Namespace) -> int:
    if not REPORT_PATH.exists():
        print("尚无扫描报告。请先运行: radar.py scan")
        return 0
    data = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    n = len(data.get("candidates") or [])
    el = len(data.get("eligible") or [])
    nv = len(data.get("needs_verification") or [])
    top = data.get("top_recommendation") or "（无）"
    print("【OpenCode 免费模型雷达】")
    print(f"扫描时间: {data.get('scanned_at', '?')}")
    print(f"CLI: {data.get('cli_version', '?')}")
    print(f"免费候选: {n} | 已验证可用: {el} | 待验证: {nv}")
    print(f"推荐: {top}")
    if data.get("notes"):
        print("备注: " + "；".join(data["notes"][:3]))
    return 0


def classify_error(text: str) -> str:
    t = (text or "").lower()
    if "429" in t or "too many requests" in t or "rate limit" in t:
        return "rate_limit_429"
    if any(
        k in t
        for k in (
            "quota",
            "insufficient",
            "billing",
            "payment",
            "out of credits",
            "credit",
            "exceeded your current quota",
        )
    ):
        return "quota_exhausted"
    return "other_error"


def ensure_free_model(model_id: str) -> None:
    if not is_free_candidate(model_id):
        raise SystemExit(
            f"拒绝探测非免费模型: {model_id}"
            "（仅允许含 free/Free 或已知 OpenCode 免费条目；禁止自动改走付费）"
        )


def cmd_probe(ns: argparse.Namespace) -> int:
    model_id = ns.model.strip()
    ensure_free_model(model_id)
    print(f"plain probe: {model_id}")
    try:
        p = run_cli(
            [
                "run",
                "--model",
                model_id,
                "--format",
                "json",
                "--auto",
                "Reply with exactly: PONG",
            ],
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        print("plain: timeout")
        return 2
    except Exception as e:
        print(f"plain: error {e}")
        return 2

    out = (p.stdout or "") + "\n" + (p.stderr or "")
    if p.returncode == 0:
        print("plain: ok")
        plain_ok = True
    else:
        kind = classify_error(out)
        print(f"plain: fail code={p.returncode} kind={kind}")
        plain_ok = False
        if kind in ("rate_limit_429", "quota_exhausted"):
            print(out.strip()[:500])
            print("NEVER auto-paid: stop here; do not switch to Zen/paid providers.")
            return 3 if kind == "rate_limit_429" else 4

    print("tools probe: attempting run with tool-needed prompt (best-effort)")
    tools_ok = False
    tools_note = "no dedicated tools probe API; best-effort prompt only"
    try:
        t = run_cli(
            [
                "run",
                "--model",
                model_id,
                "--format",
                "json",
                "--auto",
                "Call a tool if available to list the current directory; "
                "otherwise reply TOOLS_UNSUPPORTED",
            ],
            timeout=120,
        )
        tout = (t.stdout or "") + "\n" + (t.stderr or "")
        if t.returncode == 0:
            if re.search(r"tool|function.?call|mcp", tout, re.I) and "TOOLS_UNSUPPORTED" not in tout:
                tools_ok = False
                tools_note = "response mentioned tools but not treated as verified"
            else:
                tools_note = "completed without clear tool-call evidence → needs_verification"
        else:
            kind = classify_error(tout)
            tools_note = f"tools attempt failed: {kind}"
            if kind in ("rate_limit_429", "quota_exhausted"):
                print(f"tools: {kind}")
                print("NEVER auto-paid: stop here.")
                return 3 if kind == "rate_limit_429" else 4
    except Exception as e:
        tools_note = f"tools attempt error: {e}"

    print(f"tools_verified: {tools_ok} ({tools_note})")

    if REPORT_PATH.exists():
        data = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        for c in data.get("candidates") or []:
            if c.get("id") == model_id:
                c["plain_verified"] = plain_ok
                c["tools_verified"] = tools_ok
                c["last_probe_at"] = now_shanghai_iso()
                c["tools_note"] = tools_note
        if plain_ok and tools_ok:
            el = data.setdefault("eligible", [])
            if not any(x.get("id") == model_id for x in el):
                el.append({"id": model_id, "plain": True, "tools": True})
            data["needs_verification"] = [
                x for x in data.get("needs_verification") or [] if x.get("id") != model_id
            ]
        elif plain_ok and not tools_ok:
            nv = data.setdefault("needs_verification", [])
            if not any(x.get("id") == model_id for x in nv):
                nv.append({"id": model_id, "reason": tools_note})
        data["notes"] = list(
            dict.fromkeys((data.get("notes") or []) + [f"probed {model_id}"])
        )
        REPORT_PATH.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    return 0 if plain_ok else 1


def cmd_sync(ns: argparse.Namespace) -> int:
    if not ns.dry_run:
        print("拒绝: sync 必须带 --dry-run（不会写入 opencode.json）", file=sys.stderr)
        return 2
    if not REPORT_PATH.exists():
        print("无报告，请先 scan")
        return 1
    data = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    top = data.get("top_recommendation")
    eligible = [x.get("id") for x in (data.get("eligible") or [])]
    print("=== sync --dry-run（仅建议，不写磁盘）===")
    print("不会修改 ~/.config/opencode/opencode.json 或任何付费 provider 配置")
    print("建议操作:")
    if eligible:
        print(f"  1. 在 OpenCode 中切换到已验证: {eligible[0]}")
    elif top:
        print(f"  1. 先 probe 再切换；当前推荐候选: {top}")
    else:
        print("  1. 暂无免费候选")
    print("  2. 保留现有付费 provider 不动")
    print("  3. 失败时禁止自动改走付费模型")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="OpenCode free-model radar")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("scan", help="Scan free OpenCode models")
    s.set_defaults(func=cmd_scan)

    s = sub.add_parser("status", help="Show latest report summary (zh)")
    s.set_defaults(func=cmd_status)

    s = sub.add_parser("probe", help="Probe one free model")
    s.add_argument("--model", required=True, help="provider/model id")
    s.set_defaults(func=cmd_probe)

    s = sub.add_parser("sync", help="Propose config change (dry-run only)")
    s.add_argument("--dry-run", action="store_true", help="Required; never writes")
    s.set_defaults(func=cmd_sync)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    ns = parser.parse_args(argv)
    return int(ns.func(ns))


if __name__ == "__main__":
    sys.exit(main())
