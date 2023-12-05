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
from abstract_gui import sg,get_event_key_js,make_component,text_to_key
from abstract_utilities import eatAll
def capitalize(text):
    if text:
        text=text[0].upper()+text[1:]
    return text
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
        self.mode_tracker={}
        self.scan_mode = "all"
        self.history = [os.getcwd()]
        self.modes = ['-SCAN_MODE_FILES-','-SCAN_MODE_FOLDERS-','-SCAN_MODE_ALL-']
        self.key_list = ['-BROWSER_LIST-','-CLEAR_LIST-','-ADD_TO_LIST-',"-FILES_BROWSER-","-DIR-","-DIRECTORY_BROWSER-","-FILES_LIST-","-SCAN_MODE_ALL-","-SELECT_HIGHLIGHTED-","-SCAN-", "-SELECT_HIGHLIGHTED-", "-MODE-", "-BROWSE_BACKWARDS-", "-BROWSE_FORWARDS-"]+self.modes

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
        checkboxes_layout = [
            [sg.Checkbox('All', default=True, key=text_to_key(text='scan mode all',section=section)),sg.Checkbox('Files', key=text_to_key(text='file browser',section=section))],
            [sg.Checkbox('Folders', key=text_to_key(text='scan mode folders',section=section))]
        ]

        browser_buttons_layout = [
            sg.FolderBrowse('Folders', key=text_to_key(text='directory browser',section=section)),
            sg.FileBrowse('Files', key=text_to_key(text='file browser',section=section)),
            
        ]
        listboxes_layout=[]
        listboxes_layout.append(sg.Listbox(values=[], size=(50, 10), key=text_to_key(text='browser list',section=section), enable_events=True))
        listboxes_layout.append(sg.Listbox(values=[], size=(50, 10), key=text_to_key(text='files list',section=section), enable_events=True))
        control_buttons_layout = [
            sg.Button('Scan', key=text_to_key(text='scan',section=section)),
            sg.Button('<-', key=text_to_key(text='browse backwards',section=section)),
            sg.Button('All Scan Mode', key=text_to_key(text='mode',section=section)),
            sg.Button('->', key=text_to_key(text='browse forwards',section=section)),
            sg.Button('Add', key=text_to_key(text='add_to_list',section=section)),
            sg.Button('Clear', key=text_to_key(text='clear list',section=section))
        ] + extra_buttons

        return [[sg.Text('Directory to scan:'), sg.InputText(os.getcwd(),key=text_to_key(text='dir',section=section))],
            [sg.Column([listboxes_layout,browser_buttons_layout])],
            [sg.Column(checkboxes_layout)],
            control_buttons_layout
        ]

    def while_static(self,event_key_js,values,window):
        self.event_key_js,self.values,self.window=event_key_js,values,window
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
        if self.event_key_js['found'] == '-ADD_TO_LIST-':
            file_list = self.values[self.event_key_js['-BROWSER_LIST-']]
            files_list = self.values[self.event_key_js['-FILES_LIST-']] or []
            if file_list:
                files_list.append(file_list[0])
            path_dir = self.values[self.event_key_js['-DIR-']].split(';')
            for path in path_dir:
                if path not in files_list:
                    files_list.append(path)
            self.window[self.event_key_js['-FILES_LIST-']].update(files_list)
        if self.event_key_js['found'] == '-CLEAR_LIST-':
            self.window[self.event_key_js['-FILES_LIST-']].update([])
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
