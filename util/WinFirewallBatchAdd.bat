@echo off&cd /d %~pd0&setlocal ENABLEDELAYEDEXPANSION

call :addRule AnitApp- "C:\Program Files (x86)\App"

pause
exit /b

:addRule
set prefix=%1
set target=%2

set target=%target:"=%
if "%target%"=="" goto:eof
if not exist "%target%" goto:eof

set i=0

for /r "%target%" %%a in (*.exe) do (
  set id=%prefix%!i!
  echo [^>] !id! : %%a
  netsh advfirewall firewall add rule action=block dir=in name="!id!" program="%%a" protocol=any
  netsh advfirewall firewall add rule action=block dir=out name="!id!" program="%%a" protocol=any
  set /a i+=1
)

goto:eof
