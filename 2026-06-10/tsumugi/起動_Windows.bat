@echo off
rem TSUMUGI 起動用(Windows)。ダブルクリックで起動し、ブラウザが自動で開きます。
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
    py -m tsumugi.app
) else (
    python -m tsumugi.app
)
echo.
echo アプリを終了しました。このウィンドウは閉じて構いません。
pause
