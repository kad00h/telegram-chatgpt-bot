@echo off
echo Starting Telegram + ChatGPT Bot...
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install requirements if needed
pip install -r requirements.txt

REM Start the bot
echo.
echo Starting bot...
python telegram_chatgpt_bot.py

pause
