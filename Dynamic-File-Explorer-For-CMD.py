"""
# Dynamic File Explorer For CMD : v0.0.1
"""

import os
import curses
import pyperclip
from sys import exit

class FileExplorer:
    def __init__(self, stdscr, path='.'):
        self.stdscr = stdscr
        self.current_path = os.path.abspath(path)
        self.selected_index = 0
        self.hidden_folder = 0
        self.exception_check = 0
        self.exception_string = ""
        self.files = self.get_files()

        # Set up curses
        # curses.start_color()  # Enable color support
        # curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)  # Define a color pair (ID=1) with blue text on a black background
        # curses.curs_set(0)
        # self.stdscr.keypad(True)
        
        curses.start_color()  # Enable color support
        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)  # Define a color pair (ID=1) with blue text on a black background
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_GREEN)  # Define a color pair (ID=1) with white text on a green background
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_RED)  # Define a color pair (ID=2) with green text on a black background
        curses.curs_set(0)
        self.stdscr.keypad(True)

    def get_files(self):
        files = os.listdir(self.current_path)
        
        if (self.hidden_folder):
            dirs = [f for f in files if os.path.isdir(os.path.join(self.current_path, f)) if not f.startswith('.')]  # Exclude hidden folders
            files = [f for f in files if not f.startswith('.') and f not in dirs]  # Exclude hidden files
        else:
            dirs = [f for f in files if os.path.isdir(os.path.join(self.current_path, f))]
            files = [f for f in files if f not in dirs]
        return dirs + files

    def draw(self):
        self.stdscr.clear()

        # Display current path
        self.stdscr.addstr(0, 0, "CURRENT PATH: ", curses.color_pair(2) | curses.A_BOLD)
        self.stdscr.addstr(0, 15, f"{self.current_path}", curses.A_BOLD)

        # Display files
        for i, file in enumerate(self.files):
            try:
                if (self.exception_check):
                    if i == self.selected_index:
                        self.stdscr.addstr(i + 2, 2, file + "\t%s"%(self.exception_string), curses.color_pair(3) | curses.A_REVERSE)
                    elif os.path.isdir(os.path.join(self.current_path, file)):
                        self.stdscr.addstr(i + 2, 2, file + "\t%s"%(self.exception_string), curses.color_pair(3))
                    else:
                        self.stdscr.addstr(i + 2, 2, file + "\t%s"%(self.exception_string), curses.color_pair(3))
                    self.exception_check = 0
                    self.exception_string = ""
                else:
                    if i == self.selected_index:
                        self.stdscr.addstr(i + 2, 2, file, curses.color_pair(1) | curses.A_REVERSE)
                    elif os.path.isdir(os.path.join(self.current_path, file)):
                        self.stdscr.addstr(i + 2, 2, file, curses.color_pair(1))
                    else:
                        self.stdscr.addstr(i + 2, 2, file)
            except curses.error:
                pass  # Ignore errors for wide characters

        self.stdscr.refresh()

    def navigate(self, key):
        if key in [curses.KEY_UP, ord('w')] and self.selected_index > 0:
            self.selected_index -= 1
        elif key in [curses.KEY_DOWN, ord('s')] and self.selected_index < len(self.files) - 1:
            self.selected_index += 1
        elif key in [curses.KEY_RIGHT, ord('d'), curses.KEY_ENTER, 10, 13]:  # Right Arrow or 'd'
            selected_item = self.files[self.selected_index]
            selected_path = os.path.join(self.current_path, selected_item)

            try:
                if os.path.isdir(selected_path):
                    self.current_path = selected_path
                    self.files = self.get_files()
                    self.selected_index = 0
                else:
                    try:
                        os.startfile(selected_path)  # Open the file with the default system application
                    except Exception as e:
                        # print(f"Error opening file: {e}")
                        self.exception_string = e
                        self.exception_check = 1
            except Exception as e:
                # print(f"Error Opening dir/file due to : {e}")
                self.exception_string = e
                self.exception_check = 1          
        
        elif key in [ord('e'), ord('E')]:
            selected_item = self.files[self.selected_index]
            selected_path = os.path.join(self.current_path, selected_item)
            if os.path.isdir(selected_path):
                pyperclip.copy(r'cd "%s"'%self.current_path)
                exit()
        
        elif key in [curses.KEY_BACKSPACE, 8, curses.KEY_LEFT, ord('a')]:  # Backspace key
            if key == curses.KEY_BACKSPACE or key == 8 or curses.KEY_LEFT:
                if self.current_path != os.path.abspath(os.sep):  # Avoid going back from the root
                    self.current_path = os.path.dirname(self.current_path)
            self.files = self.get_files()
            self.selected_index = 0
        
        elif key in [99]: # lowecase 'c' key to copy path with file/folder included to clipboard 
            selected_item = self.files[self.selected_index]
            selected_path = os.path.join(self.current_path, selected_item)
            pyperclip.copy(r"%s"%selected_path)
        
        elif key in [67]: # uppercase 'C' key to copy path of current parent directory to clipboard
            pyperclip.copy(self.current_path)
        
        elif key in [ord('h'), ord('H')]:   #hide or unhide files
            if (self.hidden_folder):
                self.hidden_folder = 0
            else:
                self.hidden_folder = 1
            
            self.files = self.get_files()
            self.selected_index = 0
        
        elif key in [27, ord('q'), ord('Q')]:  # ESC, q or Q for Quitting
            exit()

    def run(self):
        while True:
            self.draw()
            key = self.stdscr.getch()

            if key in [27, ord('q'), ord('Q')]:
                exit()
            else:
                self.navigate(key)

def main(stdscr):
    explorer = FileExplorer(stdscr)
    explorer.run()

if __name__ == "__main__":
    curses.wrapper(main)
