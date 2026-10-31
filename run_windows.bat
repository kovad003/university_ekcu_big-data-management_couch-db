@echo off
rem same commands as python run.py, for cmd or powershell with docker desktop running
rem inside wsl use python3 run.py instead
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" run.py %*
    goto done
)
where py >nul 2>nul
if errorlevel 1 (
    python run.py %*
) else (
    py -3 run.py %*
)
:done
if errorlevel 1 pause
exit /b %errorlevel%
