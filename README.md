# Terminal File Explorer (Ranger Replica) with Python Curses

## Overview

This is a simple terminal-based file explorer written in Python using the curses module. It mimics the functionality of the Ranger file manager for the Linux terminal but is designed to run on Windows using Python curses.

## Features

- Navigate through directories and files using arrow keys or 'w', 's', 'a', 'd'.
- Open files and directories using 'Enter' or 'd'.
- Move up to the parent directory using 'Backspace' or 'a'.
- Exit the file explorer and change CMD path using 'e'.
- Copy current file/folder path to clipboard using 'c'.
- Copy the path of the current parent directory to clipboard using 'C'.
- Toggle visibility of hidden files and folders using 'h'.
- Automatically adjusts the number of displayed files based on CMD window size changes.
- Dynamically updates the file display when the CMD window size is changed.

## Usage

1. Run the file explorer script using the following command:

    ```bash
    python file_explorer.py
    ```

2. Navigate through directories using arrow keys or designated keys.
3. Open files or directories using 'Enter' or 'd'.
4. Change CMD path and exit using 'e'.
5. Copy paths to clipboard using 'c' or 'C'.
6. Toggle visibility of hidden files and folders using 'h'.
7. Adjust the displayed files based on CMD window size changes.

## Requirements

- Python 3.x
- curses module (comes pre-installed with Python on Unix-like systems)
- pyperclip

## Notes

- This file explorer is designed to run on Windows using Python curses.
- Ensure that Python is installed and available in the system's PATH.

