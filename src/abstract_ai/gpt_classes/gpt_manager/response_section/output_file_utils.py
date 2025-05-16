from ..dependencies import *
def listbox_event_check(self)->bool:
    """
    Checks if a listbox event has been triggered and updates the GUI accordingly.

    Returns:
        bool: True if a listbox event has been triggered, otherwise False
    """
    event_triggered = False
    values = self.window_mgr.get_values()
    file_path = None

    if self.script_event_js['found'] == '-FILES_LIST-':
        selected_files = values[self.event]
        if selected_files:
            file_path = selected_files[0]
            event_triggered = True
    elif self.script_event_js['found'] == '-BROWSER_LIST-':
        directory = values[self.script_event_js['-DIR-']]
        selected_files = values[self.script_event_js['-BROWSER_LIST-']]
        if selected_files:
            file_path = os.path.join(directory, selected_files[0])
            event_triggered = True
    if self.window_mgr.get_from_value(text_to_key('database query bool', section='database')):
            contents = get_instruction_from_tableName(self.window_mgr.get_from_value(text_to_key('table configuration', section='database')))
            self.window_mgr.update_value(key=text_to_key('-FILE_TEXT-', section='database'), value=contents)
            self.window_mgr.update_value(key=text_to_key('-CHUNK_TITLE-', section='database'), value=self.chunk_title)
    if file_path:
        if isinstance(file_path,list):
            file_path = file_path[0]
        if os.path.isfile(file_path):
            try:
                contents = self.read_file_contents(file_path)  # Assuming read_file_contents is defined to handle different file types
                contents = safe_json_loads(contents)
                
                if isinstance(contents,dict) and self.window_mgr.get_from_value(text_to_key('format json to string', section='responses')):
                    contents = format_json_key_values(contents)
                self.window_mgr.update_value(key=self.script_event_js['-FILE_TEXT-'], value=contents)
                self.chunk_title = os.path.basename(file_path)
                self.window_mgr.update_value(key=text_to_key('-CHUNK_TITLE-', section='files'), value=self.chunk_title)
            except Exception as e:
                print(f"Cannot read from path {file_path}. Error: {e}")
        else:
            file_path = self.window_mgr.get_values()[self.script_event_js['-DIR-']]
            files_list = self.window_mgr.get_values()[self.script_event_js['-BROWSER_LIST-']]
            if file_path:
                file_path = os.path.join(file_path,files_list[0])
                if not os.path.isfile(file_path):
                    self.browser_mgr.handle_event(self.event,self.window_mgr.get_values(),self.window)
    return event_triggered


def update_last_response_file(self)->None:
    """
    Updates the path to the last file that recorded a response.

    This function also updates the GUI with the contents of the new file.
    """
    self.logger.info(f"update_last_response_file..")
    if self.test_bool:
        self.last_response_file=self.test_file_path
    else:
        self.last_response_file = self.response_mgr.save_manager.file_path
    self.last_directory=os.path.dirname(self.last_response_file)
    self.window_mgr.update_value(key='-DIR_RESPONSES-',value=self.last_directory)
    self.update_response_list_box()
    self.window["-DIRECTORY_BROWSER_RESPONSES-"].InitialFolder=self.last_directory
    self.window["-FILE_BROWSER_RESPONSES-"].InitialFolder=self.last_directory
    self.initialize_output_display()
    
def update_response_list_box(self)->None:
    """
    Update the List Box component that displays saved responses.

    This function is often called after a new API response has been received and saved.
    """
    self.logger.info(f"update_response_list_box..")
    if self.latest_output:
        for data in self.latest_output:
            file_path = get_any_value(data,'file_path')
            if file_path in self.new_response_path_list:
                self.new_response_path_list.remove(file_path)
            self.new_response_path_list.append(file_path)
        files_list = self.window['-FILES_LIST_RESPONSES-'].Values
        if file_path in self.new_response_path_list:
            if file_path in files_list:
                files_list.remove(file_path)
        files_list=self.new_response_path_list+files_list
        self.window_mgr.update_value('-FILES_LIST_RESPONSES-',args={"values":files_list})

def aggregate_conversations(self,directory:str=None)->list:
    """
    Aggregates conversations from JSON files in the specified directory.

    Args:
        directory (str): The directory containing the JSON files. If none, it will take the current working directory.

    Returns:
        list: A list of aggregated conversations.
    """
    self.logger.info(f"aggregate_conversations..")
    if directory == None:
        directory = os.getcwd()
    json_files, lsAll = [], []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                file = os.path.join(root, file)
                json_files.append((get_file_create_time(file), file))
    sorted_json_files = sorted(json_files, key=lambda x: x[0])
    aggregated_conversations = []
    chat_log_file = open("chat_log.txt", "w")
    model = 'gpt'
    for file in sorted_json_files:
        file = file[1]
        data = safe_read_from_json(file)
        if data:
            relevant_values={}
            relevant_keys = ['id', 'object', 'created', 'model']
            for key in relevant_keys:
                value = get_any_value(data,key)
                if value:
                    relevant_values[key]=value
            if len(relevant_values.keys())==len(relevant_keys):
                if file not in aggregated_conversations:
                    aggregated_conversations.append(file)
                dir_name=os.path.dirname(file)
                if dir_name not in self.response_directories_list:
                    self.response_directories_list.append(dir_name)
       
    #self.next_read_mgr.add_to_queue(self.window_mgr.update_value,'-FILES_LIST_RESPONSES-',args={"values":aggregated_conversations})
    return aggregated_conversations
