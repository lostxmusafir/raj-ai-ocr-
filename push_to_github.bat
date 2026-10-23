@echo off
title Push to GitHub: lostxmusafir/raj-ai-ocr-
echo ============================================================
echo Pushing commits to https://github.com/lostxmusafir/raj-ai-ocr-.git
echo ============================================================
echo.

set "PATH=%PATH%;C:\Program Files\Git\cmd;C:\Program Files\Git\bin;%LOCALAPPDATA%\Programs\Git\cmd"

git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git command not found in PATH.
    pause
    exit /b 1
)

echo Authenticating and pushing to main branch...
git push -u origin main
echo.
echo ============================================================
if %errorlevel% equ 0 (
    echo [SUCCESS] Successfully pushed all commits to GitHub!
) else (
    echo [NOTE] GitHub authentication required.
    echo Please sign in via the browser popup or enter your GitHub Personal Access Token (PAT).
)
echo ============================================================
pause
