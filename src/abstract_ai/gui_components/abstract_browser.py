"""
abstract_browser
=================

The `abstract_browser` module is part of the `abstract_gui` module of the `abstract_essentials` package. 
It provides an abstracted mechanism for creating and managing a file/folder browser using PySimpleGUI.

Classes and Functions:
----------------------
- get_scan_browser_layout: Returns the layout for the file/folder scanner window.
- browse_update: Updates values in the browse window.
- return_directory: Returns the current directory or parent directory if a file is selected.
- scan_window: Handles events for the file/folder scanner window.
- forward_dir: Navigate to the given directory.
- scan_directory: Returns the files or folders present in the given directory based on the selected mode.
- get_browse_scan: Initializes the scanner with default settings and runs it.

"""
import os
from abstract_gui import sg,get_event_key_js,make_component,text_to_key,ensure_nested_list
from abstract_utilities import eatAll
def capitalize(text):
    if text:
        text=text[0].upper()+text[1:]
    return text
class filesListManager:
    def __init__(self):
        self.files_list_dict={}
    def check_files_list_key(self,key):
        if key not in self.files_list_dict:
            self.files_list_dict[key]=[]
        return self.files_list_dict[key]
    def clear_list(self,key):
        self.files_list_dict[key]=[]
        return []
    def revise_display_names(self,key):
        file_names_dict={}
        for i,file_refference in enumerate(self.files_list_dict[key]):
            file_name = file_refference['filename']
            if file_name not in file_names_dict:
                file_names_dict[file_name]=0
            else:
                file_names_dict[file_name]+=1
            display_name = file_refference['filename'] if file_names_dict[file_name] == 0 else f"{file_refference['filename']} ({file_names_dict[file_name]})"
            self.files_list_dict[key][i]['display_name'] = display_name
    def is_display_name(self,key,display_name):
        for i,file_refference in enumerate(self.check_files_list_key(key)):
            if display_name == file_refference['display_name']:
                return i
        return display_name
    
    def add_to_files_list_dict(self,key,file_path):
        directory = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        for i,file_refference in enumerate(self.check_files_list_key(key)):
            if file_refference['filepath'] == file_path:
                return
        self.files_list_dict[key].append({"dirname":directory,"filename":filename,"filepath":file_path,"display_name":filename})
        self.revise_display_names(key)
    def return_display_names(self,key):
        display_names = []
        for file_refference in self.files_list_dict[key]:
            display_names.append(file_refference['display_name'])
        return display_names
    def re_arrange_display(self,key,position_numbers):
        current_positions = [self.files_list_dict[key][position_numbers[0]],self.files_list_dict[key][position_numbers[1]]]
        new_poisitions = [current_positions[1],current_positions[0]]
        self.files_list_dict[key][position_numbers[0]]=new_poisitions[0]
        self.files_list_dict[key][position_numbers[1]]=new_poisitions[1]
    def remove_item(self,key,display_number):
        new_key_refference = []
        display_number = self.is_display_name(key,display_number)
        for i,file_refference in enumerate(self.files_list_dict[key]):
            if i != display_number:
                new_key_refference.append(self.files_list_dict[key][i])
        self.files_list_dict[key]=new_key_refference
        return self.return_display_names(key)
    def move_up(self,key,display_number):
        display_number = self.is_display_name(key,display_number)
        if display_number >0:
            position_numbers = display_number-1,display_number
            self.re_arrange_display(key,position_numbers)
        return self.return_display_names(key)
    def move_down(self,key,display_number):
        display_number = self.is_display_name(key,display_number)
        if display_number < len(self.files_list_dict[key])-1:
            position_numbers = display_number,display_number+1
            self.re_arrange_display(key,position_numbers)
        return self.return_display_names(key)
    def get_file_path(self,key,display_number):
        display_number = self.is_display_name(key,display_number)
        return self.files_list_dict[key][display_number]['filepath']
    def get_file_path_list(self,key):
        path_list = []
        for file_refference in self.check_files_list_key(key):
            path_list.append(file_refference['filepath'])
        return path_list
class AbstractBrowser:
    """
    This class aims to provide a unified way of browsing through different sources.
    It could be used as the base class for browsing through different APIs, files, databases, etc.
    The actual implementation of how to retrieve or navigate through the data should be done in the derived classes.
    """
    def __init__(self, window_mgr=None,window_name=None,window=None):
        self.window_mgr = window_mgr
        if window_mgr:
            if hasattr(window_mgr, 'window'):
                self.window = window_mgr.window
        elif window_name:
            if hasattr(window_mgr, 'get_window'):
                self.window=window_mgr.get_window(window_name=window_name)
        else:
            self.window = make_component('Window','File/Folder Scanner', layout=self.get_scan_browser_layout())
        self.event = None
        self.values = None
        self.files_list_mgr = filesListManager()
        self.mode_tracker={}
        self.scan_mode = "all"
        self.history = [os.getcwd()]
        self.modes = ['-SCAN_MODE_FILES-','-SCAN_MODE_FOLDERS-','-SCAN_MODE_ALL-']
        self.key_list = ['-BROWSER_LIST-','-CLEAR_LIST-','-REMOVE_FROM_LIST-','-MOVE_UP_LIST-','-MOVE_DOWN_LIST-','-ADD_TO_LIST-',"-FILES_BROWSER-","-DIR-","-DIRECTORY_BROWSER-","-FILES_LIST-","-SCAN_MODE_ALL-","-SELECT_HIGHLIGHTED-","-SCAN-", "-SELECT_HIGHLIGHTED-", "-MODE-", "-BROWSE_BACKWARDS-", "-BROWSE_FORWARDS-"]+self.modes

    def handle_event(self,event,values,window):
          
        self.event,self.values,self.window=event,values,window
        if event not in self.key_list:
            try:
                self.event_key_js = get_event_key_js(self.event,key_list=self.key_list)
            except:
                self.event_key_js={"found":event,"section":'',"event":event}
        if self.event_key_js['found']:
            return self.while_static(event_key_js=self.event_key_js, values=self.values,window=self.window)
        else:
            return self.event, self.values
    def scan_it(self,directory):
        if os.path.isdir(self.values[self.event_key_js['-DIR-']]):
            self.scan_results = self.scan_directory(directory, self.scan_mode)
            self.browse_update(key=self.event_key_js['-BROWSER_LIST-'],args={"values":self.scan_results})
    @staticmethod
    def get_scan_browser_layout(section=None, extra_buttons=[]):
        """
        Generate the layout for the file/folder scanning window.

        Returns:
            --------
            list:
                A list of list of PySimpleGUI elements defining the window layout.
            """
            
        # More complex layout with additional elements
        browser_buttons_layout = [
            sg.Button('All Scan Mode', key=text_to_key(text='mode',section=section)),sg.Checkbox('All', default=True, key=text_to_key(text='scan mode all',section=section)),sg.Checkbox('Files', key=text_to_key(text='file browser',section=section)),sg.Checkbox('Folders', key=text_to_key(text='scan mode folders',section=section))
        ]
        listboxes_layout=[]
        listboxes_layout.append(sg.Frame('browser',layout=ensure_nested_list([[sg.Listbox(values=[], size=(50, 10), key=text_to_key(text='browser list',section=section), enable_events=True)],
                                                                             [sg.Push(),sg.Button('<-', key=text_to_key(text='browse backwards',section=section)),
                                                                              sg.Button('Scan', key=text_to_key(text='scan',section=section)),
                                                                              sg.Button('->', key=text_to_key(text='browse forwards',section=section)),sg.Button('ADD', key=text_to_key(text='add_to_list',section=section)),sg.Push()]])))

        listboxes_layout.append(sg.Frame('files',layout=ensure_nested_list([[sg.Listbox(values=[], size=(50, 10), key=text_to_key(text='files list',section=section), enable_events=True)],
                                                                             [sg.Push(),sg.Button('UP', key=text_to_key(text='move up list',section=section)),sg.Button('DOWN', key=text_to_key(text='move down list',section=section)),
                                                                              sg.Button('REMOVE', key=text_to_key(text='remove from list',section=section)),
                                                                              sg.Button('Clear', key=text_to_key(text='clear list',section=section)),sg.Push()]])))


        layout = [[sg.Text('Directory to scan:'), sg.InputText(os.getcwd(),key=text_to_key(text='dir',section=section)),sg.FolderBrowse('Folders', key=text_to_key(text='directory browser',section=section)),sg.FileBrowse('Files', key=text_to_key(text='file browser',section=section))],
            [sg.Column([listboxes_layout,browser_buttons_layout])]]
        if extra_buttons:
            layout.append(extra_buttons)         
        return layout
    def while_static(self,event_key_js,values,window):
        self.event_key_js,self.values,self.window=event_key_js,values,window
        self.section_key = key = self.event_key_js['section']
        if self.event_key_js['found'] == "-FILES_BROWSER-":
            self.browse_update(key=self.event_key_js['-DIR-'],args={"value":self.values[self.event_key_js["-FILES_BROWSER-"]]})
        if self.event_key_js['found'] == "-DIRECTORY_BROWSER-":
            self.browse_update(key=self.event_key_js['-DIR-'],args={"value":self.values[self.event_key_js["-DIRECTORY_BROWSER-"]]})
        if self.event_key_js['found'] == '-SCAN-':
            self.scan_it(self.return_directory())
        if self.event_key_js['found'] == "-SELECT_HIGHLIGHTED-":
            if len(self.values[self.event_key_js['-BROWSER_LIST-']])>0:
                self.browse_update(key=self.event_key_js['-DIR-'],args={"value":os.path.join(self.return_directory(), self.values[self.event_key_js['-BROWSER_LIST-']][0])})
        if self.event_key_js['found'] in self.modes:
            for mode in self.modes:
                if self.event_key_js['found'] == mode:
                    if self.values[self.event_key_js[mode]]:
                        self.scan_mode = eatAll(mode[1:-1].split('_')[-1].lower(),['s'])
                        self.window.Element(self.event_key_js['-MODE-']).update(text=f"{capitalize(self.scan_mode)} Scan Mode")
                        for each_mode in self.modes:
                            if each_mode != mode:
                                self.window[self.event_key_js[each_mode]].update(False)
        if self.event_key_js['found'] == '-MODE-':
            if self.event_key_js['-MODE-'] not in self.mode_tracker:
                self.mode_tracker[self.event_key_js['-MODE-']]=[self.scan_mode,self.scan_mode]
            if self.values[self.event_key_js['-SCAN_MODE_FILES-']]:
                self.scan_mode = 'file'
            elif self.values[self.event_key_js['-SCAN_MODE_FOLDERS-']]:
                self.scan_mode = 'folder'
            elif self.values[self.event_key_js['-SCAN_MODE_ALL-']]:
                self.scan_mode='all'
            else:
                modes = ['all','file','folder']
                for mode in modes:
                    if mode not in self.mode_tracker[self.event_key_js['-MODE-']]:
                        self.scan_mode=mode
                        break
            if self.scan_mode != self.mode_tracker[self.event_key_js['-MODE-']][-1]:
                self.mode_tracker[self.event_key_js['-MODE-']].append(self.scan_mode)
                self.mode_tracker[self.event_key_js['-MODE-']]=self.mode_tracker[self.event_key_js['-MODE-']][1:]
            self.window.Element(self.event_key_js['-MODE-']).update(text=f"{capitalize(self.scan_mode)} Scan Mode")
            self.scan_it(self.return_directory())
        if self.event_key_js['found'] in ['-MOVE_UP_LIST-','-MOVE_DOWN_LIST-','-REMOVE_FROM_LIST-']:
            list_value = self.values[self.event_key_js['-FILES_LIST-']]
            if list_value:
                display_number=list_value[0]
                if self.event_key_js['found'] == '-MOVE_UP_LIST-':
                    display_values = self.files_list_mgr.move_up(self.section_key,display_number)
                elif self.event_key_js['found'] == '-MOVE_DOWN_LIST-':
                    display_values = self.files_list_mgr.move_down(self.section_key,display_number)
                elif self.event_key_js['found'] == '-REMOVE_FROM_LIST-':
                    display_values = self.files_list_mgr.remove_item(self.section_key,display_number)
                self.window[self.event_key_js['-FILES_LIST-']].update(display_values)
        if self.event_key_js['found'] == '-ADD_TO_LIST-':
            
            self.files_list_mgr.check_files_list_key(self.section_key)
            file_list = self.values[self.event_key_js['-BROWSER_LIST-']]
            path_dir = self.values[self.event_key_js['-DIR-']]
            filename = file_list[0]
            if file_list:
                file_path = os.path.join(path_dir,filename)
                self.files_list_mgr.add_to_files_list_dict(self.section_key,file_path)
                self.window[self.event_key_js['-FILES_LIST-']].update(self.files_list_mgr.return_display_names(self.section_key))
        if self.event_key_js['found'] == '-CLEAR_LIST-':
            self.window[self.event_key_js['-FILES_LIST-']].update(self.files_list_mgr.clear_list(key))
        if self.event_key_js['found'] == "-BROWSE_BACKWARDS-":
            # Navigate up to the parent directory
            if self.return_directory() not in self.history:
                self.history.append(self.return_directory())
            directory = os.path.dirname(self.return_directory())  # This will give the parent directory
            self.browse_update(key=self.event_key_js['-DIR-'],args={"value":directory})
            self.browse_update(key=self.event_key_js['-BROWSER_LIST-'],args={"values":self.scan_directory(directory, self.scan_mode)})
            self.scan_it(directory)
        if self.event_key_js['found'] in ["-BROWSE_FORWARDS-",'-BROWSER_LIST-']:
            directory=None
            try:
                # Navigate down into the selected directory or move to the next history path
                if self.values[self.event_key_js['-BROWSER_LIST-']]:  # If there's a selected folder in the listbox
                    directory = os.path.join(self.return_directory(), self.values[self.event_key_js['-BROWSER_LIST-']][0])
                    if os.path.isdir(directory):
                        self.forward_dir(directory)
                        self.scan_it(directory)
                elif self.history:  # If there's a directory in the history stack
                    directory = self.history.pop()
                    self.browse_update(key=self.event_key_js['-DIR-'],args={"value":directory})
                    self.browse_update(key=self.event_key_js['-BROWSER_LIST-'],args={"values":self.scan_directory(directory, self.scan_mode)})
            except:
                print(f'could not scan directory {directory}')
        return self.event,self.values
    def return_directory(self):
        """
        Return the current directory or parent directory if a file path is provided.

        Returns:
        --------
        str:
            Directory path.
        """
        directory = self.values[self.event_key_js['-DIR-']]
        if os.path.isfile(self.values[self.event_key_js['-DIR-']]):
            directory = os.path.dirname(self.values[self.event_key_js['-DIR-']])
        if directory == '':
            directory = os.getcwd()
        return directory
    def browse_update(self,key: str = None, args: dict = {}):
        """
        Update specific elements in the browse window.

        Parameters:
        -----------
        window : PySimpleGUI.Window
            The window to be updated. Default is the global `browse_window`.
        key : str, optional
            The key of the window element to update.
        args : dict, optional
            Arguments to be passed for the update operation.
        """
        self.window[key](**args)
    def read_window(self):
        self.event,self.values=self.window.read()
        return self.event,self.values
    def get_values(self):
        if self.values==None:
            self.read_window()
        return self.vaues
    def get_event(self):
        if self.values==None:
            self.read_window()
        return self.event
    def scan_window(self):
        """
        Event handler function for the file/folder scanning window.

        Parameters:
        -----------
        event : str
            Name of the event triggered in the window.
        """
        while True:
            self.read_window()
            if self.event == None:
                break
            while_static(event)
        self.window.close()

    def forward_dir(self,directory):
        """
        Navigate and update the scanner to display contents of the given directory.

        Parameters:
        -----------
        directory : str
            Path to the directory to navigate to.
        """
        if os.path.isdir(directory):
            self.browse_update(key=self.event_key_js['-DIR-'],args={"value":directory})
            self.browse_update(key=self.event_key_js['-BROWSER_LIST-'],args={"values":self.scan_directory(directory, self.scan_mode)})
    def scan_directory(self,directory_path, mode):
        """
        List files or folders in the given directory based on the provided mode.

        Parameters:
        -----------
        directory_path : str
            Path to the directory to scan.
        mode : str
            Either 'file' or 'folder' to specify what to list.

        Returns:
        --------
        list:
            List of file/folder names present in the directory.
        """
        if mode == 'file':
            return [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
        elif mode == 'folder':
            return [d for d in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, d))]
        return [d for d in os.listdir(directory_path)]
  
    @staticmethod
    def popup_T_F(title:str="popup window",text:str="popup window text"):
        answer = get_yes_no(title=title,text=text)
        if answer == "Yes":
            return True
        return False
    @staticmethod
    def create_new_entity(event:str=None, entity_type:str="Folder"):
        # Retrieve values from the GUI
        if "-ENTITY_TYPE-" in self.values:
            entity_type = self.values["-ENTITY_TYPE-"]
        if event in ["-FOLDER_BROWSE-",'-ENTITY_NAME-']:
            if os.path.isfile(self.values['-ENTITY_NAME-']):
                self.browse_update("-PARENT_DIR-",args={"value":self.get_directory(self.values['-ENTITY_NAME-'])})
                file_name = os.path.basename(self.values['-ENTITY_NAME-'])
                self.browse_update('-ENTITY_NAME-',args={"value":file_name})
        if event == "Create":
            exists =False
            if values['-ENTITY_NAME-'] and self.values['-PARENT_DIR-']:
                entity_path = os.path.join(self.values['-PARENT_DIR-'],self.values['-ENTITY_NAME-'])
                if entity_type == "Folder":
                    exists = os.path.exists(entity_path)  # changed from os.path.dir_exists(entity_path)
                if entity_type == "File":
                    exists = os.path.exists(entity_path)
                if exists:
                    if not popup_T_F(title=f"Override the {entity_type}?",text=f"looks like the {entity_type} path {entity_path} already exists\n did you want to overwrite it?"):
                        return False
                if entity_type == "Folder" and not exists:
                    os.makedirs(entity_path, exist_ok=True)
                elif entity_type == "File":
                    with open(entity_path, 'w') as f:
                        if "save_data" in js_browse_bridge:
                            f.write(self.save_data)  # writes the save_data to the file
                        else:
                            pass  # creates an empty file, or you can handle this differently
                self.browse_update("-FINAL_OUTPUT-",args={"value":entity_path})
                self.browse_update("-SAVE_PROMPT-",args={"visible":True})
                self.window.Element("Cancel").update(text="Exit")

                return "Cancel"
