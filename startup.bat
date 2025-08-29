@echo off
chcp 65001 > NUL
cd /d "%~dp0"

if "%1" == "" (
    call :check_for_dependencies
    start /high "LyPay Launcher" cmd /c python launcher.py
    exit /b 0
)

:launching_loop
if not "%1" == "" (
    if "%1" == "-core" (
        if "%2" == "" ( goto :bad_parsing )
        if "%3" == "" ( goto :bad_parsing )
        if "%4" == "" ( goto :bad_parsing )
        call :launch "p", "%2", "%3", "%4"
        shift & shift & shift
    ) else ( if "%1" == "-beat" (
        if "%2" == "" ( goto :bad_parsing )
        call :launch "b", "%2"
        shift
    ))
    shift
    goto :launching_loop
)
exit

:bad_parsing
echo parsing went wrong, press 'enter' to exit
pause > NUL
exit /b 1

:launch
if "%~1" == "p" (
    start "LyPay: %~3" cmd /c python "%~2" "%~4"
) else ( if "%~1" == "b" (
    start /min "LyPay: heartbeat" cmd /c bokeh serve --show "%~2"
))
exit /b 0

:check_for_dependencies
if not exist ".req" (
    echo can't find '.req' file in current directory, press 'enter' to exit
    pause > NUL
    exit /b 1
)
echo checking for dependencies...
timeout 1 > NUL
python -m pip install -r .req
echo done
exit /b 0