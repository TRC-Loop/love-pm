@echo off
:: love-pm installer - Windows
setlocal enabledelayedexpansion

set BIN=love-pm
set URL=https://raw.githubusercontent.com/TRC-Loop/love-pm/main/src/love-pm.py
set DEST=%ProgramFiles%\love-pm

echo [*] Installing love-pm...

if not exist "%DEST%" mkdir "%DEST%" || (echo [X] Failed to create directory & exit /b 1)

:: Download
powershell -Command "try { Invoke-WebRequest '%URL%' -OutFile '%DEST%\%BIN%.py' -ErrorAction Stop } catch { exit 1 }"
if errorlevel 1 ( echo [X] Download failed. & exit /b 1 )

:: Create wrapper
echo @python "%DEST%\%BIN%.py" %%* > "%DEST%\%BIN%.cmd"

:: Auto add to PATH
set "NEWPATH=%DEST%"
for %%A in ("%PATH:;=";"%") do (
    if /I "%%~A"=="%NEWPATH%" set FOUND=1
)
if not defined FOUND (
    setx PATH "%PATH%;%NEWPATH%"
    echo [i] PATH updated. Restart your terminal.
)

echo [✔] Installed at %DEST%
echo [i] Run with: %BIN%
