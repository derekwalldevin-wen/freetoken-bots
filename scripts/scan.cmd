@echo off
setlocal EnableExtensions
set "DIR=%~dp0"
REM Prefer env OPENCODE_CLI; else common desktop install under LOCALAPPDATA
if not defined OPENCODE_CLI (
  if defined LOCALAPPDATA (
    set "OPENCODE_CLI=%LOCALAPPDATA%\Programs\@opencodedesktop\resources\opencode-cli.exe"
  )
)

set "PYEXE="
for %%P in (py python python3) do (
  if not defined PYEXE (
    where %%P >nul 2>&1
    if not errorlevel 1 (
      for /f "delims=" %%V in ('%%P -3 --version 2^>nul ^& %%P --version 2^>nul') do (
        echo %%V | findstr /B /C:"Python 3" >nul
        if not errorlevel 1 (
          if /I "%%P"=="py" (set "PYEXE=py -3") else (set "PYEXE=%%P")
        )
      )
    )
  )
)

if defined PYEXE (
  %PYEXE% "%DIR%radar.py" scan
  exit /b %ERRORLEVEL%
)

where node >nul 2>&1
if not errorlevel 1 (
  echo [freetoken] Python not found; falling back to node radar.mjs
  node "%DIR%radar.mjs" scan
  exit /b %ERRORLEVEL%
)

echo [freetoken] BLOCKER: neither working Python nor Node found.
echo Install Python 3 from python.org (not Microsoft Store), or ensure node is on PATH.
exit /b 1
