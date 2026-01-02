@echo off
setlocal

REM Sync helper for this repo. Usage: sync_repo.bat "commit message"
REM Defaults to "sync" if no message provided.

set MSG=%~1
if "%MSG%"=="" set MSG=sync

REM Show status first
git status
if errorlevel 1 goto :err

echo.
echo === Staging all tracked/untracked changes ===
git add -A
if errorlevel 1 goto :err

echo.
echo === Committing "%MSG%" ===
git commit -m "%MSG%"
if errorlevel 1 goto :maybe_no_changes

echo.
echo === Pulling latest (rebase) ===
git pull --rebase
if errorlevel 1 goto :err

echo.
echo === Pushing ===
git push
if errorlevel 1 goto :err

echo.
echo Sync completed successfully.
goto :eof

:maybe_no_changes
echo No changes to commit or commit failed.
goto :eof

:err
echo Sync aborted due to an error (see messages above).
exit /b 1
