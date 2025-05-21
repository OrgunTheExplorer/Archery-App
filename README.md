🏹 Archery Tracker
Archery Tracker is a full-screen desktop application built with Python and Tkinter that allows archers to log, track, and analyze their shooting performance across sessions. It features real-time data entry, visual analytics, CSV import/export, and an interactive leaderboard with dynamic sorting.

🚀 Features
📅 Log archery sessions with your name, date, and arrow scores (72 shots)

⌨️ Fast keyboard-based entry — just type scores and hit Enter

📊 Real-time computation of Average Score and Precision (Standard Deviation)

📈 Automatically updated line charts showing performance over time

🏆 Leaderboard with sortable columns (by name, average score, or precision)

📂 Import and append past results from .csv files

💾 Data is saved locally in archery_data.csv

📝 Data Format
The app saves and reads data using the following format:

`Name,Date & Time,Average Score,Precision
John,2025-05-21 15:30:02,8.91,0.87`

📄 License
MIT License — feel free to use, modify, and share.




To transform it into an .exe file

1. Install PyInstaller
Open Command Prompt and run:                     

`python -m pip install pyinstaller`

2. Use the full Python path to run PyInstaller

`python -m PyInstaller --noconsole --onefile archery_app.py`

