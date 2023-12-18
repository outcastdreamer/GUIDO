"""
# Dynamic File Explorer For CMD : v0.0.3
    > Fixed Arrow Keys Behaviour (Needs more fine-tuning & optimization)
    > Need to fix sorting logic for folders
"""


# ----------------------------------------------------------------------------------------------------- #
import os
import re
import json
import logging
from sys import exit


import pyperclip
import curses

logging.basicConfig(filename='app.log', filemode='w', 
                    format='%(lineno)d, %(funcName)s=> %(message)s', datefmt='%H:%M:%S',
                    level=logging.DEBUG)

# ----------------------------------------------------------------------------------------------------- #
class FileExplorer:
    def __init__(self, stdscr, path='.'):
        self.stdscr = stdscr
        self.current_path = os.path.abspath(path)
        self.root_path = os.path.abspath(path)
        self.previous_path = ""
        self.selected_index = 0
        self.hidden_folder = 0
        self.exception_check = 0
        self.exception_string = ""
        self.json_dict = {"Recent_Folders":[], "Restore_Folder":""}
        self.recent_check = 0
        self.marked_check = 0
        self.top_position = 0
        self.descendingSort_Flag = False
        self.previous_index = 0
        self.MAX_FILE_DISPLAY_LIMIT = curses.LINES - 3
        logging.debug(" NEW SESSION BEGINS ".center(75, "+"))
        logging.debug(f"self.MAX_FILE_DISPLAY_LIMIT #1 : {self.MAX_FILE_DISPLAY_LIMIT}")
        os.system("clear")
        
        # ----------------------------------------------------------------------------------------------------- #
        self.files = self.get_files(self.current_path)
        self.files_count = len(self.files)
        # ----------------------------------------------------------------------------------------------------- #
        
        curses.start_color() 
        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)  
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_GREEN)  
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_RED) 
        curses.curs_set(0)
        self.stdscr.keypad(True)


    def update_max_file_display_limit(self):
        max_y, max_x = self.stdscr.getmaxyx()

        self.MAX_FILE_DISPLAY_LIMIT = max_y - 3
        logging.debug(f"#2 : self.MAX_FILE_DISPLAY_LIMIT : {self.MAX_FILE_DISPLAY_LIMIT}")
        
    def highlight_current_position(self, i, file):
        if (self.exception_check):
            if (self.current_path != self.root_path):
                self.previous_path = self.current_path[:self.current_path.rfind("\\")]
            else:
                self.previous_path = self.current_path
            self.stdscr.addstr(i + 2, 2, file, curses.color_pair(1))
            self.stdscr.addstr(i + 2, 2 + len(file) + 2, "[ERROR] : %s"%(self.exception_string), curses.color_pair(3))
        else:
            self.stdscr.addstr(i + 2, 2, file, curses.color_pair(1) | curses.A_REVERSE | curses.A_BOLD)

    def draw(self):
        # terminal size change
        if curses.is_term_resized(curses.LINES, curses.COLS):
            curses.resizeterm(curses.LINES, curses.COLS)
            self.update_max_file_display_limit()
            
        self.stdscr.clear()
        # Display current path
        self.stdscr.addstr(0, 0, "CURRENT PATH: ", curses.color_pair(2) | curses.A_BOLD)
        self.stdscr.addstr(0, 15, f"{self.current_path}", curses.A_BOLD)
        self.stdscr.addstr(0, 15 + len(self.current_path) + 2, f"[{self.files_count}]", curses.color_pair(2) | curses.A_BOLD)

        # Display files        
        if (self.selected_index >= self.MAX_FILE_DISPLAY_LIMIT - 3):
            logging.debug(f"\n\n------------ Max Limit : {self.MAX_FILE_DISPLAY_LIMIT}, Dir Len : {len(self.files)}, Files Count : {self.files_count}, Current Path : {self.current_path} ------------\n")
            logging.debug(f"### TP : {self.top_position}, SI : {self.selected_index}, len : {len(self.files)}, FC : {self.files_count}")

        for i, file in enumerate(self.files):
            try: 
                if (i <= self.MAX_FILE_DISPLAY_LIMIT):
                    if ((self.selected_index >= len(self.files) - 1) and (i == self.MAX_FILE_DISPLAY_LIMIT)):
                        if (self.selected_index >= self.MAX_FILE_DISPLAY_LIMIT - 3):
                            logging.debug(f">>> TopPos: {self.top_position}, SI: {self.selected_index}, CI: {i}, FN: {file}, Pos: {self.selected_index - self.top_position} <<<")
                        self.highlight_current_position(i, file)
                    
                    elif ((self.selected_index > self.MAX_FILE_DISPLAY_LIMIT) and (i == self.MAX_FILE_DISPLAY_LIMIT) 
                            and self.selected_index < len(self.files) - 1):
                        if (self.selected_index >= self.MAX_FILE_DISPLAY_LIMIT - 3):
                            logging.debug(f"??? TopPos: {self.top_position}, SI: {self.selected_index}, CI: {i}, FN: {file}, Pos: {self.selected_index - self.top_position} ???")
                        self.highlight_current_position(i, file)

                    elif i == self.selected_index and self.selected_index <= self.MAX_FILE_DISPLAY_LIMIT:
                        if (self.selected_index >= self.MAX_FILE_DISPLAY_LIMIT - 3):
                            logging.debug(f"%%% TopPos: {self.top_position}, SI: {self.selected_index}, CI: {i}, FN: {file}, Pos: {self.selected_index - self.top_position} %%%")
                        self.highlight_current_position(i, file)

                    elif os.path.isdir(os.path.join(self.current_path, file)):
                        self.stdscr.addstr(i + 2, 2, file, curses.color_pair(1))
                        if (self.selected_index >= self.MAX_FILE_DISPLAY_LIMIT - 3):
                            logging.debug(f"TopPos: {self.top_position}, SI: {self.selected_index}, CI: {i}, FN: {file}, Pos: {self.selected_index - self.top_position}")
                        
                    else:
                        self.stdscr.addstr(i + 2, 2, file) 
                        if (self.selected_index >= self.MAX_FILE_DISPLAY_LIMIT - 3):
                            logging.debug(f"  TopPos: {self.top_position}, SI: {self.selected_index}, CI: {i}, FN: {file}, Pos: {self.selected_index - self.top_position}")
                        
            except curses.error:
                pass 

        self.stdscr.refresh()
        
    def sort_directory(self, files, descending=False):
        match = re.search(r'\d+', files)
        numeric_part = int(match.group()) if match else float('inf')
        return -numeric_part if descending else numeric_part

    def get_files(self, path):
        files = os.listdir(path)

        if (self.hidden_folder):
            dirs = [f for f in files if os.path.isdir(os.path.join(self.current_path, f)) if not f.startswith('.') or (f.startswith('.') and f[1] == '_')]  # Exclude hidden folders
            files = [f for f in files if not f.startswith('.') and f not in dirs]
        else:
            dirs = [f for f in files if os.path.isdir(os.path.join(self.current_path, f))]
            files = [f for f in files if f not in dirs]        
        return dirs + files
        # return  sorted(dirs + files, key=lambda x: self.sort_directory(x, descending=self.descendingSort_Flag))

    def get_recent_files(self):
        self.previous_path = self.current_path
        files = self.json_dict["Recent_Folders"]
        dirs = [f for f in files if os.path.isdir(os.path.join(self.current_path, f))]
        files = [f for f in files if f not in dirs]
        return dirs + files
    
    def find_exact_match_index(self, folders, target_folder):
        pattern = re.compile(fr'^{re.escape(target_folder)}$')
        
        for index, folder in enumerate(folders):
            if pattern.match(folder):
                return index
        
        return -1
    
    def json_updater(self):
        if (os.path.exists("files_history.json")):
            with open("files_history.json", "r") as r:
                self.json_dict = json.load(r)
            
            if (len(self.json_dict["Recent_Folders"]) >= 15):
                self.json_dict["Recent_Folders"].pop()
            
            if (len(self.json_dict["Recent_Folders"]) < 15 and self.current_path not in self.json_dict["Recent_Folders"]):
                self.json_dict["Recent_Folders"].append(self.current_path)
            
            if (self.current_path != self.root_path):
                self.json_dict["Restore_Folder"] = self.current_path
            
            json_obj = json.dumps(self.json_dict, indent=4)
            with open("files_history.json", "w") as w:
                w.write(json_obj)
            
        else:
            json_obj = json.dumps(self.json_dict, indent=4)
            with open("files_history.json", "w") as w:
                w.write(json_obj)
                
    
    def navigate(self, key):
        logging.debug(f"<<< key : {str(key)}, TP : {self.top_position}, SI : {self.selected_index}, len : {len(self.files)}, FC : {self.files_count}")
        
        # ------------------------------------------ ARROW KEYS START ----------------------------------------- #
        
        if key in [curses.KEY_UP, ord('w')]:
            if self.selected_index > 0:
                self.selected_index -= 1
                self.json_updater()
                
                if (self.top_position > 0 and self.top_position < self.selected_index):
                    self.top_position -= 1
                    temp_files = self.get_files(self.current_path)
                    self.files_count = len(temp_files)
                    self.files = temp_files[self.top_position:]
            elif self.selected_index == 0:
                self.selected_index = self.files_count - 1
                if (self.files_count > self.MAX_FILE_DISPLAY_LIMIT):
                    self.top_position = self.files_count - 1 - self.MAX_FILE_DISPLAY_LIMIT
                else:
                    self.top_position = 0  
                temp_files = self.get_files(self.current_path)
                self.files_count = len(temp_files)
                self.files = temp_files[self.top_position:]
            
            if (self.exception_check):
                self.current_path = self.previous_path
                self.files = self.get_files(self.current_path)
                self.files_count = len(self.files)
                self.exception_check = 0
                self.exception_string = ""
        
        elif key in [curses.KEY_DOWN, ord('s')]:
            if self.selected_index < self.files_count - 1:
                
                self.selected_index += 1
                self.json_updater()
                logging.debug(f"***  ENTER HERE : {self.top_position}, SI : {self.selected_index}, FC : {self.files_count}")
                
                if (self.selected_index > self.MAX_FILE_DISPLAY_LIMIT):
                    self.top_position += 1
                    logging.debug(f"???  ENTER HERE : {self.top_position}, SI : {self.selected_index}")
                    temp_files = self.get_files(self.current_path)
                    self.files_count = len(temp_files)
                    self.files = temp_files[self.top_position:]
                    # print("\n", self.files, self.selected_index)
                
                logging.debug(f"!!!TP : {self.top_position}, SI : {self.selected_index}, len : {len(self.files)}, FC : {self.files_count}")
            
            
            elif self.selected_index >= self.files_count - 1:
                self.json_updater()
                self.top_position = 0
                self.selected_index = 0
                self.files = self.get_files(self.current_path)
                self.files_count = len(self.files)
                
            if (self.exception_check):
                self.current_path = self.previous_path
                self.files = self.get_files(self.current_path)
                self.files_count = len(self.files)
                self.exception_check = 0
                self.exception_string = ""
            
        
        elif key in [curses.KEY_RIGHT, ord('d'), curses.KEY_ENTER, 10, 13]:
            self.json_updater()
            
            if (self.selected_index < self.MAX_FILE_DISPLAY_LIMIT):
                selected_item = self.files[self.selected_index]  
            else:
                selected_item = self.files[self.selected_index - self.top_position]
            
            selected_path = os.path.join(self.current_path, selected_item)
            previous_index = self.selected_index
            
            logging.debug(f"Files : {self.files}")
            logging.debug(f"SelInd: {self.selected_index}, SelectedItem: {selected_item}, SelectedPath: {selected_path}, CurrentPath: {self.current_path}")
            
            if (self.exception_check):
                self.current_path = self.previous_path
                self.files = self.get_files(self.current_path)
                self.files_count = len(self.files)

                self.exception_check = 0
                self.exception_string = ""
            else:
                try:
                    if os.path.isdir(selected_path):
                        self.current_path = selected_path
                        self.files = self.get_files(self.current_path)
                        self.files_count = len(self.files)
                        self.selected_index = 0
                    else:
                        try:
                            os.startfile(selected_path) 
                        except Exception as e:
                            self.exception_string = e
                            self.exception_check = 1
                            self.selected_index = previous_index
                except Exception as e:
                    self.exception_string = e
                    self.exception_check = 1          
                    self.selected_index = previous_index
        
        elif key in [curses.KEY_LEFT, ord('a'), curses.KEY_BACKSPACE, 8]: 
            self.json_updater()
            
            if (self.recent_check):
                self.current_path = self.previous_path
                self.recent_check = 0
                self.files = self.get_files(self.current_path)
                self.files_count = len(self.files)
                self.selected_index = 0
            else:
                if (self.exception_check):
                    self.current_path = self.previous_path
                    self.files = self.get_files(self.current_path)
                    self.files_count = len(self.files)

                    self.exception_check = 0
                    self.exception_string = ""
                else:
                    previous_folder_name = self.current_path[self.current_path.rfind("\\")+1:]
                    
                    if self.current_path != os.path.abspath(os.sep): 
                        self.current_path = os.path.dirname(self.current_path)
                    # self.files = self.get_files(self.current_path)
                    # self.selected_index = 0
                    
                    self.previous_index = self.find_exact_match_index(self.get_files(self.current_path), previous_folder_name)
                    logging.debug(f"PI: {self.previous_index}, PrevFold: {previous_folder_name}, LEFT HERE: {self.current_path}")
                    temp_files = self.get_files(self.current_path)
                    self.files_count = len(temp_files)
                    if (self.previous_index < self.MAX_FILE_DISPLAY_LIMIT):
                        self.top_position = 0
                    self.files = temp_files[self.top_position:]
                    self.selected_index = self.previous_index
            
        # ------------------------------------------- ARROW KEYS END ------------------------------------------ #
        elif key == ord('A'):
            selected_item = self.files[self.selected_index]
            selected_path = os.path.join(self.current_path, selected_item)

            try:
                if os.path.isdir(selected_path):
                    pass
            except:
                pass
        
        
        elif key == ord('r'):
            self.recent_check = 1
            self.json_updater()
            self.files = self.get_recent_files()
            self.selected_index = 0
            
        elif key == ord('R'):
            self.recent_check = 1
            self.json_updater()
            self.current_path = self.json_dict["Restore_Folder"]
            self.files = self.get_files(self.current_path)
            self.files_count = len(self.files)
            self.selected_index = 0
        
        elif key in [ord('e'), ord('E')]:
            selected_item = self.files[self.selected_index]
            selected_path = os.path.join(self.current_path, selected_item)
            if os.path.isdir(selected_path):
                pyperclip.copy(r'cd "%s"'%self.current_path)
                exit()
        
        elif key in [ord('`'), ord('~')]:
            self.current_path = self.root_path
            self.files = self.get_files(self.current_path)
            self.selected_index = 0
        
        elif key == ord('c'): 
            selected_item = self.files[self.selected_index]
            selected_path = os.path.join(self.current_path, selected_item)
            pyperclip.copy(r"%s"%selected_path)
        
        elif key == ord('C'): 
            pyperclip.copy(self.current_path)
        
        elif key in [ord('h'), ord('H')]:  
            if (self.hidden_folder):
                self.hidden_folder = 0
            else:
                self.hidden_folder = 1
            
            self.files = self.get_files(self.current_path)
            self.selected_index = 0
            
        logging.debug(f">>> key : {str(key)}, TP : {self.top_position}, SI : {self.selected_index}, len : {len(self.files)}, FC : {self.files_count}")
        

    def run(self):
        while True:            
            self.draw()
            key = self.stdscr.getch()

            if key in [27, ord('q'), ord('Q')]:  
                self.files = self.get_files(self.current_path)
                logging.debug(f"\n\n{self.files}")
                exit()
            else:
                self.navigate(key)

def main(stdscr):
    explorer = FileExplorer(stdscr)
    explorer.run()

if __name__ == "__main__":
    curses.wrapper(main)
