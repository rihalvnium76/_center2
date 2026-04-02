@echo off&cd /d %~pd0
:: VERSION 1.0.11
:: --- CONFIG ---
set "BRANCH=dev"
set WAIT_SECOND=5
set FRIST_GIT_LOGIN=0
set EMPTY_LOG=0
set EMPTY_PROFILE_FOLDER=0
set PRESET=1
:: --- END CONFIG ---

echo [D] Target branch: %BRANCH%
echo [D] First git login: %FRIST_GIT_LOGIN%
echo [D] Create empty log file: %EMPTY_LOG%
echo [D] Create empty profile folder: %EMPTY_PROFILE_FOLDER%
echo [D] Preset: %PRESET%
echo.

:: --- Sources ---

if "%PRESET%"=="1" (
  call :update repo1 "http://github.com/user1/repo1.git" %BRANCH%
  call :login_prompt
  call :update repo2 "http://github.com/user1/repo2.git" %BRANCH%
  call :update repo3 "http://github.com/user1/repo3.git" %BRANCH%
)

:: --- Extensions ---

call :create_log_file repo1.console.log

call :create_profile_folder AppProfile
call :create_profile_folder IdeProfile

echo [I] OK
timeout /t %WAIT_SECOND% >nul

exit /b

:create_profile_folder
if "%1"=="" goto:eof
if not "%EMPTY_PROFILE_FOLDER%"=="1" goto:eof
if not exist %1 (
  echo [I] Creating empty profile folder %1
  md %1
)
goto:eof

:create_log_file
if "%1"=="" goto:eof
if not "%EMPTY_LOG%"=="1" goto:eof
if not exist %1 (
  echo [I] Creating empty log file %1
  echo. > %1
)
goto:eof

:login_prompt
if "%FRIST_GIT_LOGIN%"=="1" (
  echo.
  echo ^>^>^> Press any key to continue after completing first git login.
  echo.
  pause>nul
)
goto:eof

:update
if "%1"=="" goto:eof
if exist %1 (
  call :pull %1 %2 %3
) else (
  call :clone %1 %2 %3
)
goto:eof

:clone
if "%2"=="" goto:eof
if "%3"=="" (
  echo [I] Async cloning %2 to %1
  start cmd /c title %1 ^& git clone %2 %1 ^& timeout /t %WAIT_SECOND% ^>nul
) else (
  echo [I] Async cloning %3 of %2 to %1
  start cmd /c title %1 ^& git clone -b %3 %2 %1 ^& timeout /t %WAIT_SECOND% ^>nul
)
goto:eof

:pull
if "%1"=="" goto:eof
echo [I] Async pulling %1
start cmd /c title %1 ^& cd /d %1 ^& git pull ^& git gc ^& timeout /t %WAIT_SECOND% ^>nul
goto:eof
