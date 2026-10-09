# Setup — Windows desktop (optional backup)

Prefer the Linux / agent box for always-on Free. Use Windows only when the box is down.

## Find CLI

Typical install (placeholders — adjust for your user):

```text
%LOCALAPPDATA%\Programs\@opencodedesktop\resources\opencode-cli.exe
```

Set for radar:

```bat
set OPENCODE_CLI=%LOCALAPPDATA%\Programs\@opencodedesktop\resources\opencode-cli.exe
```

## Autostart service (no GUI)

1. `Win + R` → `shell:startup` → Enter
2. New shortcut → target:

```text
"%LOCALAPPDATA%\Programs\@opencodedesktop\resources\opencode-cli.exe" service start
```

3. Name e.g. `OpenCode服务`
4. Confirm Arguments actually contain `service start` (empty args = no-op)

Quit the GUI (including tray). Service should keep listening so radar / HTTP clients still work while the PC is on.

## Daily scan

Task Scheduler → Daily 08:00 → action:

```bat
path\to\FreeToken-Bots\scripts\scan.cmd
```

`scan.cmd` tries `py -3` / `python` / `python3`, then falls back to `node scripts\radar.mjs`.

## Limits

- PC asleep or off → this host's Free stops.
- Do not copy `service.json` / password files into git or chat.
- Do not point public ingress at the Windows OpenCode port.
