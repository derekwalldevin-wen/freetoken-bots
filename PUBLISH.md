# How to publish (for the repo owner)

Draft lives locally until you review. **Do not push secrets.**

## Option A — Fork min-skill (closest to the linked form)

1. On GitHub: fork https://github.com/limin112/min-skill
2. Clone your fork.
3. Replace or add `skills/FreeToken-Bots/` with this folder contents.
   - Upstream already has an OpenRouter/Pi FreeToken-Bots. Prefer renaming this
     edition to `skills/FreeToken-OpenCode/` **or** keep the name and add a clear
     README note that this is the OpenCode edition (coordinate with upstream if PR).
4. Open a PR to limin112/min-skill **or** keep it only on your fork.

## Option B — Your own skill repo (recommended if not contributing upstream)

1. Create a public repo under your GitHub (e.g. `freetoken-bots` or `min-skill`).
2. Layout:

```text
your-repo/
└── skills/
    └── FreeToken-Bots/   ← this folder
```

3. Push only after review (`git status` must not show `.env`, `*.password`, `report.json`).

## Checklist before push

- [ ] No real passwords / Basic auth values
- [ ] No machineIds
- [ ] No absolute paths like `C:\Users\<you>\...` with credentials
- [ ] `examples/env.example` uses placeholders only
- [ ] Daily scan timer documented for installers

## Suggested commit / PR title

```
feat(FreeToken-Bots): OpenCode Free routing for Grok Bot (LongCat / Ling 3.1 / Space Bunny)
```

## Suggested PR body

```
## Summary
OpenCode-edition FreeToken skill: headless `opencode serve` on 127.0.0.1:4096,
radar scan/probe/sync --dry-run, bot diversion rules, never auto-paid.

## Default Free pool
- opencode/longcat-2.5-preview-free (text)
- opencode/ling-3.1-flash-free (text backup)
- opencode/space-bunny-free (multimodal)

## Notes
Distinct from the OpenRouter/Pi FreeToken-Bots in limin112/min-skill.
Windows desktop service is optional backup; Linux box is preferred always-on.
```
