#!/usr/bin/env node
/**
 * OpenCode free-model radar (Node fallback when Python is missing).
 * Same behavior as radar.py: scan | status | probe --model | sync --dry-run
 * OpenCode Free only; never writes opencode.json; never prints secrets.
 */
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = __dirname;
const REPORT_PATH = process.env.FREETOKEN_REPORT
  ? path.resolve(process.env.FREETOKEN_REPORT)
  : path.join(ROOT, "report.json");

function resolveCli() {
  if (process.env.OPENCODE_CLI) return process.env.OPENCODE_CLI;
  const homeBin = path.join(os.homedir(), ".opencode", "bin", "opencode");
  if (fs.existsSync(homeBin)) return homeBin;
  const local = process.env.LOCALAPPDATA;
  if (local) {
    const win = path.join(
      local,
      "Programs",
      "@opencodedesktop",
      "resources",
      "opencode-cli.exe"
    );
    if (fs.existsSync(win)) return win;
  }
  return "opencode";
}

const CLI = resolveCli();

const KNOWN_FREE_IDS = new Set([
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
]);

const FREE_RE = /free/i;

function nowShanghaiIso() {
  const d = new Date();
  const fmt = new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Shanghai",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
  const parts = Object.fromEntries(
    fmt.formatToParts(d).filter((p) => p.type !== "literal").map((p) => [p.type, p.value])
  );
  return `${parts.year}-${parts.month}-${parts.day}T${parts.hour}:${parts.minute}:${parts.second}+08:00`;
}

function runCli(args, timeoutMs = 60000) {
  return spawnSync(CLI, args, {
    encoding: "utf8",
    timeout: timeoutMs,
    windowsHide: true,
  });
}

function cliVersion() {
  try {
    const p = runCli(["--version"], 30000);
    const out = ((p.stdout || p.stderr || "") + "").trim();
    return out.split(/\r?\n/)[0] || "unknown";
  } catch (e) {
    return `error: ${e}`;
  }
}

function listModels() {
  const p = runCli(["models"], 60000);
  if (p.status !== 0) {
    throw new Error(
      `opencode models failed (code=${p.status}): ${((p.stderr || p.stdout || "") + "").trim()}`
    );
  }
  const models = [];
  for (const line of ((p.stdout || "") + "").split(/\r?\n/)) {
    const s = line.trim();
    if (!s || s.startsWith("#") || !s.includes("/")) continue;
    models.push(s.split(/\s+/)[0]);
  }
  return models;
}

function isFreeCandidate(id) {
  return FREE_RE.test(id) || KNOWN_FREE_IDS.has(id);
}

function classify(models) {
  const candidates = [];
  const needs_verification = [];
  const notes = [
    "OpenCode Free models only.",
    "eligible[] stays empty until probe verifies plain (+ tools if supported).",
    "IDs matching /free/i under opencode/ are candidates; tool capability unverified at scan.",
    "Paid providers without free marker are ignored.",
    "Never auto-route to paid on failure.",
    "Runner: node radar.mjs",
  ];
  for (const mid of models) {
    if (!isFreeCandidate(mid)) continue;
    candidates.push({
      id: mid,
      provider: mid.includes("/") ? mid.split("/", 1)[0] : "",
      free_marker: FREE_RE.test(mid),
      tools_verified: false,
      plain_verified: false,
    });
    needs_verification.push({
      id: mid,
      reason: "listed as free candidate; plain/tools not probed in this scan",
    });
  }
  return { candidates, eligible: [], needs_verification, inactive: [], notes };
}

function writeReport(data) {
  fs.mkdirSync(path.dirname(REPORT_PATH), { recursive: true });
  fs.writeFileSync(REPORT_PATH, JSON.stringify(data, null, 2) + "\n", "utf8");
}

function cmdScan() {
  const version = cliVersion();
  let models;
  try {
    models = listModels();
  } catch (e) {
    writeReport({
      scanned_at: nowShanghaiIso(),
      cli_version: version,
      candidates: [],
      eligible: [],
      needs_verification: [],
      inactive: [],
      notes: [`scan failed: ${e}`],
    });
    console.error(`scan failed: ${e}`);
    return 1;
  }
  const parts = classify(models);
  const report = {
    scanned_at: nowShanghaiIso(),
    cli_version: version,
    all_models_count: models.length,
    ...parts,
    top_recommendation: parts.candidates[0]?.id || null,
  };
  const preferred = [
    "opencode/longcat-2.5-preview-free",
    "opencode/ling-3.1-flash-free",
    "opencode/space-bunny-free",
    "opencode/nemotron-3.5-lightning-free",
  ];
  const ids = new Set(parts.candidates.map((c) => c.id));
  for (const pref of preferred) {
    if (ids.has(pref)) {
      report.top_recommendation = pref;
      break;
    }
  }
  writeReport(report);
  console.log(`scan ok: ${parts.candidates.length} free candidates → ${REPORT_PATH}`);
  if (report.top_recommendation) console.log(`top_recommendation: ${report.top_recommendation}`);
  return 0;
}

function cmdStatus() {
  if (!fs.existsSync(REPORT_PATH)) {
    console.log("尚无扫描报告。请先运行: radar.mjs scan");
    return 0;
  }
  const data = JSON.parse(fs.readFileSync(REPORT_PATH, "utf8"));
  console.log("【OpenCode 免费模型雷达】");
  console.log(`扫描时间: ${data.scanned_at || "?"}`);
  console.log(`CLI: ${data.cli_version || "?"}`);
  console.log(
    `免费候选: ${(data.candidates || []).length} | 已验证可用: ${(data.eligible || []).length} | 待验证: ${(data.needs_verification || []).length}`
  );
  console.log(`推荐: ${data.top_recommendation || "（无）"}`);
  return 0;
}

function ensureFree(modelId) {
  if (!isFreeCandidate(modelId)) {
    console.error(
      `拒绝探测非免费模型: ${modelId}（禁止自动改走付费）`
    );
    process.exit(2);
  }
}

function classifyError(text) {
  const t = (text || "").toLowerCase();
  if (t.includes("429") || t.includes("rate limit") || t.includes("too many requests"))
    return "rate_limit_429";
  if (/(quota|insufficient|billing|payment|out of credits|credit)/.test(t))
    return "quota_exhausted";
  return "other_error";
}

function cmdProbe(modelId) {
  ensureFree(modelId);
  console.log(`plain probe: ${modelId}`);
  const p = runCli(
    ["run", "--model", modelId, "--format", "json", "--auto", "Reply with exactly: PONG"],
    120000
  );
  const out = (p.stdout || "") + "\n" + (p.stderr || "");
  let plainOk = false;
  if (p.status === 0) {
    console.log("plain: ok");
    plainOk = true;
  } else {
    const kind = classifyError(out);
    console.log(`plain: fail code=${p.status} kind=${kind}`);
    if (kind === "rate_limit_429" || kind === "quota_exhausted") {
      console.log(out.trim().slice(0, 500));
      console.log("NEVER auto-paid: stop here; do not switch to Zen/paid providers.");
      return kind === "rate_limit_429" ? 3 : 4;
    }
  }
  console.log(`tools_verified: false (best-effort only on node path)`);
  return plainOk ? 0 : 1;
}

function cmdSync(dryRun) {
  if (!dryRun) {
    console.error("拒绝: sync 必须带 --dry-run（不会写入 opencode.json）");
    return 2;
  }
  if (!fs.existsSync(REPORT_PATH)) {
    console.log("无报告，请先 scan");
    return 1;
  }
  const data = JSON.parse(fs.readFileSync(REPORT_PATH, "utf8"));
  console.log("=== sync --dry-run（仅建议，不写磁盘）===");
  console.log("不会修改 ~/.config/opencode/opencode.json 或任何付费 provider 配置");
  console.log(`推荐候选: ${data.top_recommendation || "（无）"}`);
  console.log("失败时禁止自动改走付费模型");
  return 0;
}

const [, , cmd, ...rest] = process.argv;
let code = 1;
if (cmd === "scan") code = cmdScan();
else if (cmd === "status") code = cmdStatus();
else if (cmd === "probe") {
  const i = rest.indexOf("--model");
  const model = i >= 0 ? rest[i + 1] : null;
  if (!model) {
    console.error("probe requires --model");
    code = 2;
  } else code = cmdProbe(model);
} else if (cmd === "sync") {
  code = cmdSync(rest.includes("--dry-run"));
} else {
  console.error("Usage: radar.mjs scan|status|probe --model ID|sync --dry-run");
  code = 2;
}
process.exit(code);
