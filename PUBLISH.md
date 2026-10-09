# How to publish (for the repo owner)

Draft lives locally until you review. **Do not push secrets.**

## Publish this repo

1. Create or use the public repo `https://github.com/derekwalldevin-wen/freetoken-bots`.
2. Push this folder as the repo root (layout already matches).
3. Push only after review (`git status` must not show `.env`, `*.password`, `report.json`).

## Checklist before push

- [ ] No real passwords / Basic auth values
- [ ] No machineIds
- [ ] No absolute paths like `C:\Users\<you>\...` with credentials
- [ ] `examples/env.example` uses placeholders only
- [ ] Daily scan timer documented for installers

## Suggested commit message

```
feat(FreeToken-Bots): OpenCode Free routing for Grok Bot (LongCat / Ling 3.1 / Space Bunny)
```

## Suggested release note

```
## Summary
OpenCode FreeToken skill: headless `opencode serve` on 127.0.0.1:4096,
radar scan/probe/sync --dry-run, bot diversion rules, never auto-paid.

## Default Free pool
- opencode/longcat-2.5-preview-free (text)
- opencode/ling-3.1-flash-free (text backup)
- opencode/space-bunny-free (multimodal)

## Notes
Windows desktop service is optional backup; Grok Bot 云电脑 is the primary always-on host.
```
