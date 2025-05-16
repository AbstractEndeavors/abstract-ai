from ..dependencies import *
#WindowManagement
def readme_event_check(self)->bool:
    """
    Checks if the Generate README event has been triggered.

    The Generate README event is triggered when a user opts to generate a README file for the prompt.

    Returns:
        bool: True if the Generate README event has been triggered, otherwise False
    """
    if self.event=="-GENERATE_README-":
        prompt_number=self.get_prompt_data_section_number()
        prompt_data = self.prompt_data_list[prompt_number]
        request_data = self.request_data_list[prompt_number]
        
        files_list = self.window['-FILES_LIST_FILES-'].Values
        result,files_list=read_me_window(files_list)

        request_data+='\n\n'+result
        for file_path in files_list:
            if os.path.isfile(file_path):
                file_contents = read_from_file(file_path)
                self.chunk_title= os.path.basename(file_path)
                prompt_data+=self.add_to_chunk(file_contents)
                
        self.chunk_type="CODE"
        
        if prompt_data:
            self.update_prompt_data(prompt_data)
        
        if request_data:
            self.update_request_data(request_data)
    else:
        return False
    return True
def database_event_check(self)->bool:
    """
    Checks if the Generate README event has been triggered.

    The Generate README event is triggered when a user opts to generate a README file for the prompt.

    Returns:
        bool: True if the Generate README event has been triggered, otherwise False
    """
    if self.event=="-GENERATE_DATABASE_QUERY-":
        prompt_number=self.get_prompt_data_section_number()
        prompt_data = self.prompt_data_list[prompt_number]
        request_data = self.request_data_list[prompt_number]
        prompt_data+='\n\n'+get_instruction_from_tableName()
        self.update_prompt_data(prompt_data)
        
        contents = self.read_file_contents(file_path)  # Assuming read_file_contents is defined to handle different file types
        contents = safe_json_loads(contents)


        
        if prompt_data:
            self.update_prompt_data(prompt_data)
        
        if request_data:
            self.update_request_data(request_data)
    else:
        return False
    return True

def perform_event_checks(self)->None:
    """
    Iterates through the different event checks to see if any has been triggered.

    The function stops checking once an event has been triggered.
    """
    for event_check in self.event_check_keys:
        # Use getattr to get the method by name, then call it
        method = getattr(self, event_check)
        self.bool_loop = method()
        
        # If you want to stop checking once bool_loop is True (or some condition), you can break here
        if self.bool_loop or self.event==None:  # Assuming self.bool_loop should stop the loop when True
            break
    

def browser_event_query(self,event:str=None,values:dict=None,window=None):
    values=values or self.window_mgr.get_values()
    event=event or self.window_mgr.get_event()
    window=window or self.window
    self.browser_mgr.handle_event(event,values,window)

    
def while_window(self,event,values,window):
    self.event,self.values,window=event,values,window
    if self.event != None:
        if self.loop_one == False:
            
            self.update_all()
            self.restore_instruction_defaults()
            self.update_instruction_mgr()
            self.window_mgr.update_value(key="-INSTRUCTIONS_TEXT-",value=self.default_instructions)
            for browser_event in ['-SCAN_FILES-',
                                  '-SCAN_RESPONSES-']:
                self.browser_event_query(browser_event,self.values,self.window)
            
        self.next_read_mgr.execute_queue()
        self.script_event_js = get_event_key_js(event = self.event,key_list=self.additions_key_list)
        self.perform_event_checks()
        self.loop_one=True
