"""
# Dynamic File Explorer For CMD :
    # v0.0.6
        > Change 'e', "E", and "ALT+E" shortcuts feature to directly change directory to 
            parent cmd shell & explorer.
        > Previously binded "e" and "E" has been move to "c" and "C" keys.
        > Added guido.bat for running the python code
        > Changed sort order from "D" to "O" key
        > TODO: Need to fix recent folders bug still
        > TODO: Need to rename project to GUIDO and need to add guido_settings.json
                for cutsom keymapping & color schemes (maybe)
        > TODO: Try multi-pane implementation
        > TODO: Add Starred or Saved Folders logic
    # v0.0.5
        > Fixed cmd resize issue which was causing cursor to go out of screen
        > Fixed path size bleeding off to next line if the path length was too long than current terminal size

    # v0.0.4
        > Fixed Arrow Keys Behaviour (Needs optimization & cleaning)
        > Added sort logic on capital "D" to change to descending (Toggle Behaviour)
"""


# ----------------------------------------------------------------------------------------------------- #
import os
import re
import json
import time
import logging
from sys import exit


import pyperclip
import curses

logging.basicConfig(filename='app.log', filemode='w', 
                    format='%(lineno)d, %(funcName)s=> %(message)s', datefmt='%H:%M:%S',
                    level=logging.CRITICAL)

version = "0.0.6"

# ----------------------------------------------------------------------------------------------------- #
class FileExplorer:
    def __init__(self, stdscr, path='.'):
        self.stdscr = stdscr
        self.exe_path = os.getcwd()
        self.current_path = os.path.abspath(path)
        self.root_path = self.current_path
        self.display_path = self.current_path
        self.previous_path = ""
        self.selected_index = 0
        self.hidden_folder = 0
        self.exception_check = 0
        self.exception_string = ""
        self.json_dict = {"Recent_Folders":[], "Restore_Folder":"", "shortcuts":{}}
        self.recent_check = 0
        self.marked_check = 0
        self.top_position = 0
        self.descendingSort_Flag = False
        self.previous_index = 0
        self.active_pane_index = 0
        self.dir_mode_flag = False
        self.rightSide_files = []
        self.enter_once = True
        self.temp_values = []
        self.MAX_FILE_DISPLAY_LIMIT = curses.LINES - 3
        logging.debug(" NEW SESSION BEGINS ".center(75, "+"))
        logging.debug(f"Version: {version}")
        logging.debug(f"self.MAX_FILE_DISPLAY_LIMIT #1 : {self.MAX_FILE_DISPLAY_LIMIT}, curses.LINES : {curses.LINES}")
        logging.debug(f"self.MAX_FILE_DISPLAY_LIMIT #1 : {self.MAX_FILE_DISPLAY_LIMIT}, curses.LINES : {curses.LINES}")
        logging.debug(f"exe path: {self.exe_path}")
        os.system("cls")
        
        # ----------------------------------------------------------------------------------------------------- #
        self.files = self.get_files(self.current_path)
        self.files_count = len(self.files)
        # ----------------------------------------------------------------------------------------------------- #
        
        curses.start_color() 
        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)  
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_GREEN)  
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_RED) 
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
        self.stdscr.bkgd(' ', curses.color_pair(4))
        
        curses.curs_set(0)
        self.stdscr.keypad(True)
        self.stdscr.nodelay(True)
        self.stdscr.refresh()
    
    def set_display_path(self, width):
        current_len = len("CURRENT PATH: ") + len(self.current_path) + 2 + len(f"[{self.files_count}]")
        if (current_len > width):
            prev_dir = self.current_path[0:self.current_path.rfind("\\")]
            self.display_path = "...\\" + prev_dir[prev_dir.rfind("\\")+1:] + "\\" + self.current_path[self.current_path.rfind("\\")+1:]
            if (len(self.display_path) > width):
                self.display_path = "...\\" + self.display_path[self.display_path.rfind("\\") + 1:]
        else:
            self.display_path = self.current_path
        
    def highlight_current_position(self, i, file, pos_y):
        try:
            if (self.exception_check):
                if (self.current_path != self.root_path):
                    self.previous_path = self.current_path[:self.current_path.rfind("\\")]
                    if (self.previous_path.find("\\") == -1):
                        self.previous_path = self.previous_path + "\\"
                    logging.debug(f"EXCEPTION: PrevPath : {self.previous_path}, CurrentPath: {self.current_path}")
                else:
                    self.previous_path = self.current_path
                self.stdscr.addstr(i + 2, pos_y, file, curses.color_pair(1))
                self.stdscr.addstr(i + 2, pos_y + len(file) + 2, "[ERROR] : %s"%(self.exception_string), curses.color_pair(3))
            else:
                self.stdscr.addstr(i + 2, pos_y, file, curses.color_pair(1) | curses.A_REVERSE | curses.A_BOLD)
        except curses.error:
            pass 

    def draw(self):
        self.height, self.width = self.stdscr.getmaxyx()
        self.MAX_FILE_DISPLAY_LIMIT = self.height - 3
        if (self.active_pane_index):
            self.both_pane_draw()
        elif (self.dir_mode_flag):
            self.right_pane_view()
        else:    
            self.pane_display(True, True, self.current_path, self.get_files(self.current_path), 2)
            
    def right_pane_view(self):
        try:
            if (self.enter_once):
                self.files = self.get_files(self.current_path)
                self.enter_once = False
                fileName_size = (self.width // 2) - 5
                trimmed_left_files_list = [i[:fileName_size-5] + "..." if len(i) > fileName_size else i for i in self.get_files(self.current_path)]
                self.active_pane_index = 0
                self.pane_display(True, True, self.current_path, trimmed_left_files_list, 2, 0)
                
                iSplit_size = (self.width // 2) + 5
                selected_item = self.files[self.selected_index]
                # print(selected_item)
                
                selected_path = os.path.join(self.current_path, selected_item)
                
                    
                
                if os.path.isdir(selected_path):
                    for i in range(2, self.height):
                        self.stdscr.addch(i, self.width // 2, '|')
                    self.active_pane_index = 0
                    self.rightSide_files = self.get_files(selected_path)
                    trimmed_rightFiles_list = [i[:fileName_size-5] + "..." if len(i) > fileName_size else i for i in self.rightSide_files]
                    self.pane_display(False, False, selected_path, trimmed_rightFiles_list, iSplit_size, 1)
                    
            
        except curses.error():
            pass 
            
    def both_pane_draw(self):
        try:
            self.set_display_path(self.width)
            
            self.stdscr.clear()
            iSplit_size = (self.width // 2) - 4
            
        except curses.error():
            pass
            
    def pane_display(self, showCurrentPathFlag, clearScreenFlag, current_path, files, pos_y, rs=0):
        try: 
            if (clearScreenFlag):
                self.stdscr.clear()
                
            if (showCurrentPathFlag):
                self.set_display_path(self.width)
                if (len(self.display_path) < self.width):
                    self.stdscr.addstr(0, 0, "CURRENT PATH: ", curses.color_pair(2) | curses.A_BOLD)
                    self.stdscr.addstr(0, 15, f"{self.display_path}", curses.A_BOLD)
                    self.stdscr.addstr(0, 15 + len(self.display_path) + 2, f"[{self.files_count}]", curses.color_pair(2) | curses.A_BOLD)
                else:
                    self.stdscr.addstr(0, 0, "./  " + f"[{self.files_count}]", curses.color_pair(2) | curses.A_BOLD)
            
            
            # if (self.selected_index >= self.MAX_FILE_DISPLAY_LIMIT - 3):
            #     logging.debug(f"\n\n------------ Max Limit : {self.MAX_FILE_DISPLAY_LIMIT}, Dir Len : {len(self.files)}, Files Count : {self.files_count}, Current Path : {self.current_path} ------------\n")
            #     logging.debug(f"### TP : {self.top_position}, SI : {self.selected_index}, len : {len(self.files)}, FC : {self.files_count}")

            if files == []:
                self.stdscr.addstr(2, pos_y , "CURRENT DIRECTORY IS EMPTY!", curses.color_pair(3))
            else:
                if (self.dir_mode_flag):
                    n = os.path.abspath(current_path).strip().rfind("\\") 
                    fs =  "..." + current_path[n:] if len("..." + current_path[n:]) < self.width//2 - 5 else current_path[self.width//2 - 5]
                    self.stdscr.addstr(1, pos_y + 2, "..." + current_path[n:])

                for i, file in enumerate(files):
                    if (i <= self.MAX_FILE_DISPLAY_LIMIT):
                        if ((self.selected_index >= len(files) - 1) and (i == self.MAX_FILE_DISPLAY_LIMIT)):
                            # if (self.selected_index >= self.MAX_FILE_DISPLAY_LIMIT - 3):
                            #     logging.debug(f">>> TopPos: {self.top_position}, SI: {self.selected_index}, CI: {i}, FN: {file}, Pos: {self.selected_index - self.top_position} <<<")
                            if (not self.dir_mode_flag and not self.active_pane_index):
                                self.highlight_current_position(i, file, pos_y)
                                if (self.temp_values != []):
                                    self.temp_values = []
                                self.temp_values.append([i, file, pos_y])
                            elif (self.dir_mode_flag and not self.active_pane_index):
                                self.highlight_current_position(self.temp_values[0][0], self.temp_values[0][1], self.temp_values[0][2])
                                if (rs and os.path.isdir(os.path.join(current_path, file))):
                                    self.stdscr.addstr(i + 2, pos_y, file, curses.color_pair(1))
                                elif (rs):
                                    self.stdscr.addstr(i + 2, pos_y, file)
                                    
                            elif os.path.isdir(os.path.join(current_path, file)):
                                self.stdscr.addstr(i + 2, pos_y, file, curses.color_pair(1))
                            else:
                                self.stdscr.addstr(i + 2, pos_y, file) 
                        elif ((self.selected_index > self.MAX_FILE_DISPLAY_LIMIT) and (i == self.MAX_FILE_DISPLAY_LIMIT) 
                                and self.selected_index < len(files) - 1):
                            # if (self.selected_index >= self.MAX_FILE_DISPLAY_LIMIT - 3):
                            #     logging.debug(f"??? TopPos: {self.top_position}, SI: {self.selected_index}, CI: {i}, FN: {file}, Pos: {self.selected_index - self.top_position} ???")
                            if (not self.dir_mode_flag and not self.active_pane_index):
                                self.highlight_current_position(i, file, pos_y)
                                if (self.temp_values != []):
                                    self.temp_values = []
                                self.temp_values.append([i, file, pos_y])
                            elif (self.dir_mode_flag and not self.active_pane_index):
                                self.highlight_current_position(self.temp_values[0][0], self.temp_values[0][1], self.temp_values[0][2])
                                if (rs and os.path.isdir(os.path.join(current_path, file))):
                                    self.stdscr.addstr(i + 2, pos_y, file, curses.color_pair(1))
                                elif (rs):
                                    self.stdscr.addstr(i + 2, pos_y, file) 
                                    
                            elif os.path.isdir(os.path.join(current_path, file)):
                                self.stdscr.addstr(i + 2, pos_y, file, curses.color_pair(1))
                            else:
                                self.stdscr.addstr(i + 2, pos_y, file) 

                        elif i == self.selected_index and self.selected_index <= self.MAX_FILE_DISPLAY_LIMIT:
                            # if (self.selected_index >= self.MAX_FILE_DISPLAY_LIMIT - 3):
                            #     logging.debug(f"%%% TopPos: {self.top_position}, SI: {self.selected_index}, CI: {i}, FN: {file}, Pos: {self.selected_index - self.top_position} %%%")
                            if (not self.dir_mode_flag and not self.active_pane_index):
                                self.highlight_current_position(i, file, pos_y)
                                if (self.temp_values != []):
                                    self.temp_values = []
                                self.temp_values.append([i, file, pos_y])
                            elif (self.dir_mode_flag and not self.active_pane_index):
                                self.highlight_current_position(self.temp_values[0][0], self.temp_values[0][1], self.temp_values[0][2])
                                if (rs and os.path.isdir(os.path.join(current_path, file))):
                                    self.stdscr.addstr(i + 2, pos_y, file, curses.color_pair(1))
                                elif (rs):
                                    self.stdscr.addstr(i + 2, pos_y, file) 
                                    
                            elif os.path.isdir(os.path.join(current_path, file)):
                                self.stdscr.addstr(i + 2, pos_y, file, curses.color_pair(1))
                            else:
                                self.stdscr.addstr(i + 2, pos_y, file) 
                        elif os.path.isdir(os.path.join(current_path, file)):
                            self.stdscr.addstr(i + 2, pos_y, file, curses.color_pair(1))
                            # if (self.selected_index >= self.MAX_FILE_DISPLAY_LIMIT - 3):
                            #     logging.debug(f"TopPos: {self.top_position}, SI: {self.selected_index}, CI: {i}, FN: {file}, Pos: {self.selected_index - self.top_position}")
                        else:
                            self.stdscr.addstr(i + 2, pos_y, file) 
                            # if (self.selected_index >= self.MAX_FILE_DISPLAY_LIMIT - 3):
                            #     logging.debug(f"  TopPos: {self.top_position}, SI: {self.selected_index}, CI: {i}, FN: {file}, Pos: {self.selected_index - self.top_position}")
                            
            self.stdscr.refresh()
        except curses.error:
            pass 

        
    def sort_num_directory(self, files, descending=False):
        match = re.search(r'\d+', files)
        numeric_part = int(match.group()) if match else float('inf')
        return -numeric_part if descending else numeric_part
    
    def list_and_sort_folders(self, path, items=[], descending=False):
        folders = [item for item in items if os.path.isdir(os.path.join(path, item))]
        files = [item for item in items if os.path.isfile(os.path.join(path, item))]

        symbol_folders = sorted([i for i in folders if not i[0].isalnum()], reverse=descending)
        num_folders = [i for i in folders if i[0].isdigit()]
        num_folders = sorted(num_folders, key=lambda x:self.sort_num_directory(x, descending))
        alpha_folders = sorted([i for i in folders if i[0].isalpha()], key=lambda x:x.casefold(), reverse=descending)

        symbol_files = sorted([i for i in files if not i[0].isalnum()], reverse=descending)
        num_files = [i for i in files if i[0].isdigit()]
        num_files = sorted(num_files, key=lambda x:self.sort_num_directory(x, descending))
        alpha_files = sorted([i for i in files if i[0].isalpha()], key=lambda x:x.casefold(), reverse=descending)
        

        if (descending):
            sorted_folders = alpha_folders + num_folders + symbol_folders
            sorted_files = alpha_files + num_files + symbol_files
        else:
            sorted_folders = symbol_folders + num_folders + alpha_folders
            sorted_files = symbol_files + num_files + alpha_files

        sorted_items = sorted_folders + sorted_files

        return sorted_items

    def get_files(self, path):
        try:
            files = os.listdir(path)

            if (self.hidden_folder):
                dirs = [f for f in files if os.path.isdir(os.path.join(path, f)) if not f.startswith('.') or (f.startswith('.') and f[1] == '_')]  # Exclude hidden folders
                files = [f for f in files if not f.startswith('.') and f not in dirs]
            else:
                dirs = [f for f in files if os.path.isdir(os.path.join(path, f))]
                files = [f for f in files if f not in dirs]        
            return self.list_and_sort_folders(path, dirs + files, self.descendingSort_Flag)
        except Exception as e:
            self.exception_string = e
            self.exception_check = 1
            self.previous_path = self.current_path

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
            
            if (len(self.json_dict["Recent_Folders"]) >= 10):
                self.json_dict["Recent_Folders"].pop()
            
            if (len(self.json_dict["Recent_Folders"]) < 10 and 
            os.path.abspath(self.current_path.strip()) not in self.json_dict["Recent_Folders"]):
                self.json_dict["Recent_Folders"].append(os.path.abspath(self.current_path.strip()))
            
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
        logging.debug(f"BEGUN key : {str(key)}, TP : {self.top_position}, SI : {self.selected_index}, len : {len(self.files)}, FC : {self.files_count}, curses.LINES: {curses.LINES}")
        
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
                logging.debug(f"***  ENTER HERE : {self.top_position}, SI : {self.selected_index}, FC : {self.files_count}, CP: {self.current_path}")
                
                if (self.selected_index > self.MAX_FILE_DISPLAY_LIMIT):
                    self.top_position += 1
                    logging.debug(f"???  ENTER HERE : {self.top_position}, SI : {self.selected_index}")
                    temp_files = self.get_files(self.current_path)
                    self.files_count = len(temp_files)
                    self.files = temp_files[self.top_position:]
                
                logging.debug(f"!!!TP : {self.top_position}, SI : {self.selected_index}, len : {len(self.files)}, FC : {self.files_count}")
            
            
            elif self.selected_index >= self.files_count - 1:
                self.json_updater()
                self.top_position = 0
                self.selected_index = 0
                self.files = self.get_files(self.current_path)
                self.files_count = len(self.files)
                
            if (self.exception_check):
                self.current_path = self.previous_path
                logging.debug(f"DOWN Exception : PrevPath : {self.previous_path}, CP: {self.current_path}")
                self.files = self.get_files(self.current_path)
                self.files_count = len(self.files)
                self.exception_check = 0
                self.exception_string = ""
            
        
        elif key in [curses.KEY_RIGHT, ord('d'), curses.KEY_ENTER, 10, 13]:
            if (self.files == []):
                return
            
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
            self.json_updater()
        
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
                    
                    self.previous_index = self.find_exact_match_index(self.get_files(self.current_path), previous_folder_name)
                    if (self.previous_index == -1):
                        return
                    
                    logging.debug(f"PI: {self.previous_index}, PrevFold: {previous_folder_name}, LEFT HERE: {self.current_path}")
                    temp_files = self.get_files(self.current_path)
                    self.files_count = len(temp_files)
                    if (self.previous_index < self.MAX_FILE_DISPLAY_LIMIT):
                        self.top_position = 0
                    self.files = temp_files[self.top_position:]
                    self.selected_index = self.previous_index
            self.json_updater()  
        logging.debug(f"END key : {str(key)}, TP : {self.top_position}, SI : {self.selected_index}, len : {len(self.files)}, FC : {self.files_count}, CP: {self.current_path}")
        

    def function_keys(self, key):        
        if key in [ord('o'), ord('O')]:  # Sort Order Shortcut
            if (self.descendingSort_Flag):
                self.descendingSort_Flag = 0
            else:
                self.descendingSort_Flag = 1
                
            self.files = self.get_files(self.current_path)
            self.selected_index = 0
            self.top_position = 0
            self.json_updater()
        
        elif key == ord('r'):  # Recent Files
            self.recent_check = 1
            self.json_updater()
            self.files = self.get_recent_files()
            self.selected_index = 0
            
        elif key == ord('R'):  # Restore Last Location
            self.recent_check = 1
            self.json_updater()
            self.current_path = self.json_dict["Restore_Folder"]
            self.files = self.get_files(self.current_path)
            self.files_count = len(self.files)
            self.selected_index = 0
        
        elif key == ord('e'):  # Exit to Parent shell and change directory to active folder
            if os.path.isdir(self.current_path):
                with open("selected_dir.txt", "w") as f:
                    f.write(self.current_path)
                    try:
                        os.remove("explorer_dir.txt")
                    except FileNotFoundError:
                        pass
                    exit()
        
        elif key == ord('E'):  # Exit to Parent shell and change directory to selected folder
            selected_item = self.files[self.selected_index]
            selected_path = os.path.join(self.current_path, selected_item)
            if os.path.isdir(selected_path):
                with open("selected_dir.txt", "w") as f:
                    f.write(selected_path)
                    try:
                        os.remove("explorer_dir.txt")
                    except FileNotFoundError:
                        pass
                    exit()
                    
        elif key == curses.ALT_E:  # Open current folder in explorer
            if os.path.isdir(self.current_path):
                with open("explorer_dir.txt", "w") as f:
                    f.write(self.current_path)
                    try:
                        os.remove("selected_dir.txt")
                    except FileNotFoundError:
                        pass
                    exit()
                    
        elif key == ord('D'):
            selected_item = self.files[self.selected_index]
            selected_path = os.path.join(self.current_path, selected_item)
            if os.path.isdir(selected_path):
                self.dir_mode_flag = not self.dir_mode_flag
                self.enter_once = True
                    
        elif key in [ord('`'), ord('~'), ord('.'), ord('>')]:  # Go back to Root Path
            self.current_path = self.root_path
            self.files = self.get_files(self.current_path)
            self.selected_index = 0
        
        elif key == ord('c'):   # Copy selected file with folder path to clipboard
            selected_item = self.files[self.selected_index]
            selected_path = os.path.join(self.current_path, selected_item)
            pyperclip.copy(r"%s"%selected_path)
        
        elif key == ord('C'):  # Copy selected folder path to clipboard
            pyperclip.copy(self.current_path)
        
        elif key in [ord('h')]:
            self.current_path = os.path.expanduser('~')
            self.files = self.get_files(self.current_path)
            self.selected_index = 0
        
        elif key in [ord('H')]:   # So hidden or unhidden folders
            if (self.hidden_folder):
                self.hidden_folder = 0
            else:
                self.hidden_folder = 1
            
            self.files = self.get_files(self.current_path)
            self.selected_index = 0
            
        elif key == ord('\t'):
            self.active_pane_index = not self.active_pane_index

    def run(self):
        try:
            os.remove("selected_dir.txt")
        except FileNotFoundError:
            pass
        
        try:
            os.remove("explorer_dir.txt")
        except FileNotFoundError:
            pass        

        navigation_list = [curses.KEY_LEFT, ord('a'), curses.KEY_BACKSPACE, 8, curses.KEY_RIGHT, curses.KEY_DOWN, ord('s'), curses.KEY_UP, ord('w')]
        up_down_keys = [curses.KEY_DOWN, ord('s'), curses.KEY_UP, ord('w')]
        
        key = None
        self.draw()
        while True:
            key = self.stdscr.getch()
            # if (key not in [ord('D')] and key not in navigation_list and not self.enter_once):
                
                
            if key in [27, ord('q'), ord('Q')]:  
                self.files = self.get_files(self.current_path)
                logging.debug(f"\n\n{self.files}")
                exit()
            else:
                if key in navigation_list:
                    if (not self.enter_once):
                        self.dir_mode_flag = not self.dir_mode_flag
                        self.enter_once = True
                    # else:
                    self.navigate(key)
                else:
                    self.function_keys(key)
                self.draw()  
                
def main(stdscr):
    explorer = FileExplorer(stdscr)
    explorer.run()

if __name__ == "__main__":
    curses.wrapper(main)
