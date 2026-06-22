@echo off
REM 期權每日提示 - Windows 啟動檔
REM Task Scheduler 叫呢個檔就得;%~dp0 = 呢個 .bat 所在資料夾,自動 cd 入去
cd /d "%~dp0"
python daily_alert.py >> alert.log 2>&1
