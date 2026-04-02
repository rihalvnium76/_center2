@echo off
set "PREV_PATH=%~dp0"
set "REPO_PATH=%~d0\page"
set "GIT_AUTHOR_DATE=1970-01-01T08:00:00 +0000"
set "GIT_COMMITTER_DATE=%GIT_AUTHOR_DATE%"

cd /d %REPO_PATH%
git commit --amend --no-edit --date="%GIT_AUTHOR_DATE%"
echo.
git log -1 --pretty=fuller
cd /d %PREV_PATH%

timeout /t 5 >nul
