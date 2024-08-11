:: v1.0.1

@echo off

cd %~dp0

start /b /wait python "%~dp0\Dynamic-File-Explorer-For-CMD.py"

IF EXIST "%~dp0\selected_dir.txt" (
    :: echo Reading "%~dp0\selected_dir.txt"...
    for /f "usebackq tokens=* delims=" %%x in ("%~dp0\selected_dir.txt") do (
        echo Changing directory to "%%x"
        cd /d "%%x"
    )
)

IF EXIST "%~dp0\explorer_dir.txt" (
    :: echo Reading "%~dp0\explorer_dir.txt"...
    for /f "usebackq tokens=* delims=" %%x in ("%~dp0\explorer_dir.txt") do (
        :: echo Changing directory to "%%x"
        cd /d "%%x"
    )
)