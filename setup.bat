@echo off
chcp 65001
REM Description
echo Installing ESP...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Installing...
    REM Download and install the latest Python
    powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe -OutFile .\python-installer.exe"
    start /wait .\python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    del .\python-installer.exe

    REM Check if Python is installed after installation attempt
    python --version >nul 2>&1
    if errorlevel 1 (
        echo Python installation failed.
        pause
        exit /b
    ) else (
        echo Python installed successfully.
    )
) else (
    echo Python is already installed.
)

REM Create a virtual environment
python -m venv venv

REM Activate the virtual environment
call venv\Scripts\activate

REM Install dependencies
pip install -r requirements.txt

REM Dependency installation complete
echo ESP installation completed...
pause
