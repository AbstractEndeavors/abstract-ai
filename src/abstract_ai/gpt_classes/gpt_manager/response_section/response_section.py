from ..dependencies import *
#ResponseManagement
def update_response_mgr(self)->None:
    self.response_mgr = ResponseManager(prompt_mgr=self.prompt_mgr,api_mgr=self.api_mgr)
    
def get_new_api_call_name(self)->None:
    """
    A helper method that generates and appends a new unique API call name to the api_call_list.
    """
    self.logger.info(f"get_new_api_call_name..")
    call_name = create_new_name(name='api_call',names_list=self.api_call_list)
    if call_name not in self.api_call_list:
        self.api_call_list.append(call_name)

def start_asyncio_loop(self):
    asyncio.set_event_loop(self.loop)
    self.loop.run_forever()    
        
# checks if the Response Manager has completed the query process.         
def check_response_mgr_status(self)->bool:
    """
    checks if the Response Manager has completed the query process. It returns a Boolean indicating the status.
    """
    self.logger.info(f"check_response_mgr_status..")
    if not self.test_bool:
        return self.response_mgr.query_done
    return self.start_query
def response_event_check(self)->bool:
    """
    Checks if a response event has been triggered.

    A response event is triggered when a user interacts with the response management interface.

    Returns:
        bool: True if a response event has been triggered, otherwise False
    """
    if self.event == "-COLLATE_RESPONSES_BOOL-":
        if self.window_mgr.get_values()["-COLLATE_RESPONSES_BOOL-"]:
            files_list = self.window['-FILES_LIST_RESPONSES-'].Values
            if len(files_list)>0:
                collator = FileCollator(files_list)
                collated_responses=collator.get_gollated_responses(files_list,key_value = 'response')
                self.window_mgr.update_value('-FILE_TEXT_RESPONSES-',collated_responses)
                
    elif self.event in ['-RESPONSE_TEXT_BACK-','-RESPONSE_TEXT_FORWARD-']:
        self.determine_output_display(self.event)
        
    elif self.event == 'Copy Response':
        active_tab_key = self.window_mgr.get_values()['-TABS-']  # get active tab key
        # Construct the key for multiline text box
        multiline_key = active_tab_key.replace('TAB','TEXT')
        if multiline_key in self.window_mgr.get_values():
            text_to_copy = self.window_mgr.get_values()['-FILE_TEXT-']
            pyperclip.copy(text_to_copy)
    else:
        return False
    return True

def get_current_request_data(self)->int:
    self.logger.info(f"get_current_request_data..")
    num=0
    for i,data in enumerate(self.prompt_data_list):
        num+=len(data)
        if self.response_text_number_actual<=num:
            if i>len(self.request_data_list):
                return len(request_data_list)-1
            return i
    return len(self.request_data_list)-1
def unlist_self(self,keys:list):
    """
    A helper method that takes a list of keys as a parameter, iterates over each key, and checks if
    the value of the corresponding key in the class is a non-empty list. If it is, it updates the class's attribute with the last element in the list.
    """
    for key in keys:
        value = getattr(self,key)
        if isinstance(value,list) and value:
            value = value[-1]
        setattr(self,key,value)


