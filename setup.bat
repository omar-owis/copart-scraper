@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

echo ================================
echo Copart Scraper Setup
echo ================================

REM Base directory (where setup.bat lives)
set BASE_DIR=%~dp0
set BASE_DIR=%BASE_DIR:~0,-1%
cd /d "%BASE_DIR%"

REM --------------------------------------------------
REM Find Python robustly
REM --------------------------------------------------

set PYTHON_EXE=

where py >nul 2>&1
if %ERRORLEVEL%==0 (
    for /f "delims=" %%P in ('py -3 -c "import sys; print(sys.executable)"') do (
        set PYTHON_EXE=%%P
    )
)

if "%PYTHON_EXE%"=="" (
    where python >nul 2>&1
    if %ERRORLEVEL%==0 (
        for /f "delims=" %%P in ('python -c "import sys; print(sys.executable)"') do (
            set PYTHON_EXE=%%P
        )
    )
)

if "%PYTHON_EXE%"=="" (
    echo ERROR: Python not found.
    pause
    exit /b 1
)

echo Using Python: %PYTHON_EXE%

REM --------------------------------------------------
REM Install requirements
REM --------------------------------------------------

echo.
"%PYTHON_EXE%" -m pip install -e .

REM --------------------------------------------------
REM Ask interval
REM --------------------------------------------------

echo.
set /p HOURS=Enter how often to run the scraper (in hours): 

for /f "delims=0123456789" %%A in ("%HOURS%") do (
    echo Invalid number.
    pause
    exit /b 1
)

set /a MINUTES=%HOURS% * 60

REM --------------------------------------------------
REM Create scheduled task
REM --------------------------------------------------

set TASK_NAME=CopartScraper

echo.
echo Creating Task Scheduler task "%TASK_NAME%"...

schtasks /create ^
 /tn "%TASK_NAME%" ^
 /tr "\"%PYTHON_EXE%\" -m copartscraper" ^
 /sc minute ^
 /mo %MINUTES% ^
 /f

echo.
echo Task created successfully!
echo Program : %PYTHON_EXE%
echo Args    : -m copartscraper
echo Workdir : %BASE_DIR%
echo.

pause
ENDLOCAL
