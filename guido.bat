@echo off

start /b /wait python Dynamic-File-Explorer-For-CMD.py

IF EXIST selected_dir.txt (
    for /f "tokens=* delims=" %%x in (selected_dir.txt) do cd /d %%x
)

IF EXIST explorer_dir.txt (
    for /f "tokens=* delims=" %%x in (explorer_dir.txt) do explorer %%x
)