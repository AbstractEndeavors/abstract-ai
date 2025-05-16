from ..dependencies import *
# Initializes the prompt manager with the information needed for querying the GPT AI model
def update_prompt_mgr(self,prompt_data_list:list=None,request_data_list:list=None,chunk_token_distributions:list=None,completion_percentage:(int or str)=None,notation:str=None,chunk_number:(int or str)=None,chunk_type:str="CODE")->(list,list):
    """
    initializes the prompt manager with the information needed for querying the GPT AI model.
    """
    request_data_list,prompt_data_list = self.sanitize_prompt_and_request_data(request_data_list,prompt_data_list)
    self.prompt_mgr.update_request_and_prompt_data(instruction_mgr=self.instruction_mgr,
                               model_mgr=self.model_mgr,
                               role=self.window_mgr.get_from_value('-ROLE-'),
                               completion_percentage=completion_percentage or self.window_mgr.get_from_value('-COMPLETION_PERCENTAGE-'),
                               prompt_data=prompt_data_list,
                               request_data=request_data_list,
                               chunk_type=chunk_type or self.chunk_type)
    self.chunk_text_number_actual = 0
    self.update_query_display()
    chunk_token_distribution_number = self.get_spec_section_number_display('query')
    chunk_number = self.display_number_tracker['chunk_number']
    
    self.chunk_token_distributions=self.prompt_mgr.chunk_token_distributions
    self.update_chunk_info(chunk_token_distribution_number,chunk_number)
    self.prompt_mgr_update_js = {"prompt_data_list":self.prompt_data_list,
                                 "request_data_list":self.request_data_list,
                                 "completion_percentage":None,
                                 "chunk_type":"CODE"}
    
def sanitize_prompt_and_request_data(self,request_data_list:list,prompt_data_list:list)->(list,list):
    request_data_list = request_data_list or self.request_data_list
    prompt_data_list = prompt_data_list or self.prompt_data_list
    for i in range(len(self.prompt_data_list)):
        if prompt_data_list:
            if prompt_data_list[-1] =='' and request_data_list[-1] == '':
                prompt_data_list = prompt_data_list[:-1]
                request_data_list = request_data_list[:-1]
    return request_data_list,prompt_data_list

def get_prompt_data_section_number(self)->int:
    return int(self.window_mgr.get_values()[text_to_key("prompt_data section number")])

def get_chunk_token_distribution_number(self)->int:
    return int(self.window_mgr.get_values()[text_to_key("chunk section number")])

def get_chunk_number(self)->int:
    return int(self.window_mgr.get_values()[text_to_key("chunk number")])

def get_spec_section_number_display(self,variable_header:str)->int:
    value = self.display_number_tracker[variable_header]
    if not is_number(value):
        value = int(self.display_number_tracker[variable_header])
        self.window_mgr.update_value(key=text_to_key(f"{variable_header} section number"),value=value)
    return int(value)

def update_request_data_list(self,data:str=None)->None:
    spec_section_number = self.get_spec_section_number_display(variable_header='request')
    if data == None:
        self.request_data_list[spec_section_number] = self.window_mgr.get_values()[text_to_key('request')]
    else:
        self.request_data_list[spec_section_number] = data
        self.update_request_data_display()

    self.prompt_mgr_update_js['request_data_list']=self.request_data_list
    self.prompt_mgr.update_request_and_prompt_data(request_data = self.request_data_list)
    
def update_request_data_display(self,section_number:int=None)->None:
    if section_number == None:
        section_number = self.get_spec_section_number_display(variable_header='request')
    self.window_mgr.update_value(key=text_to_key('request'),value=self.request_data_list[section_number])
    
def update_prompt_data_list(self,data:str=None)->None:
    spec_section_number = self.get_spec_section_number_display(variable_header='prompt_data')
    if data == None:
        self.prompt_data_list[spec_section_number] = self.window_mgr.get_values()[text_to_key('prompt_data data')]
    else:
        self.prompt_data_list[spec_section_number] = data
        self.update_prompt_data_display()
    self.prompt_mgr_update_js['prompt_data_list']=self.prompt_data_list
    self.prompt_mgr.update_request_and_prompt_data(prompt_data = self.request_data_list,request_data = self.request_data_list)
def update_prompt_data_display(self,section_number:int=None)->None:
    if section_number == None:
        section_number = self.get_spec_section_number_display(variable_header='prompt_data')
    self.window_mgr.update_value(key=text_to_key('prompt_data data'),value=self.prompt_data_list[section_number])
    
def prompt_request_event_check(self)->bool:
    event_triggered = False
    if self.event == text_to_key('request'):
        self.update_request_data_list()
        event_triggered = True
    elif self.event == text_to_key('prompt_data data'):
        self.update_prompt_data_list()
        event_triggered = True
    elif self.event == '-ADD_QUERY-':
        event_triggered = True
    else:
        return False
    self.update_query_display()
    self.fill_lists()
    return True

def get_adjusted_number(self,current_number:int, reference_obj:list)->int:
        return max(0, min(current_number, max(0, len(reference_obj)-1)))
    
def update_prompt_data(self,data:str)->list:
    self.history_mgr.add_to_history(name=self.chunk_history_name,data=self.prompt_data_list)
    self.update_prompt_data_list(data=data)
    return self.prompt_data_list

def update_request_data(self,data:str)->list:
    self.history_mgr.add_to_history(name=self.request_history_name,data=self.request_data_list)
    self.update_request_data_list(data=data)
    return self.request_data_list

def update_query_display(self)->None:
    section_number = self.get_adjusted_number(self.display_number_tracker['request'], self.prompt_mgr.chunk_token_distributions)
    chunk_number = self.get_adjusted_number(self.display_number_tracker['chunk_number'], self.prompt_mgr.chunk_token_distributions[section_number])
    self.display_number_tracker['query']=section_number
    self.display_number_tracker['chunk_number']=chunk_number
    self.window_mgr.update_value(text_to_key(f'query section number'),section_number)
    self.window_mgr.update_value(text_to_key(f'query number'),chunk_number)
    self.window_mgr.update_value(key='-QUERY-',value=self.prompt_mgr.create_prompt(chunk_token_distribution_number=section_number,chunk_number=chunk_number))

def update_chunk_info(self,chunk_token_distribution_number:(str or int)=0,chunk_number:(str or int)=0)->None:
    if self.prompt_mgr.chunk_token_distributions:
        
        chunk_token_distribution_number=self.get_adjusted_number(int(chunk_token_distribution_number),self.prompt_mgr.chunk_token_distributions)
        if int(chunk_token_distribution_number) < len(self.prompt_mgr.chunk_token_distributions) and chunk_token_distribution_number >=0:
            chunk_number=self.get_adjusted_number(int(chunk_number),self.prompt_mgr.chunk_token_distributions[chunk_token_distribution_number])
            self.chunk_token_distribution = self.prompt_mgr.chunk_token_distributions[int(chunk_token_distribution_number)][int(chunk_number)]
            self.window_mgr.update_value(key=self.sectioned_chunk_data_key, value=self.chunk_token_distribution['chunk']['data'])
            for key in self.chunk_display_keys:
                spl = key[1:-1].lower().split('_')
                if spl[0] in self.chunk_token_distribution:
                    if spl[-1] in self.chunk_token_distribution[spl[0]]:
                        self.window_mgr.update_value(key=key,value=self.chunk_token_distribution[spl[0]][spl[-1]])
     
def add_to_chunk(self,content:str)->str:
    """
    adds the user's entered request to the request chunk. It also updates the 'chunk_text_number' in the GUI.
    """
    if self.window_mgr.get_from_value('-AUTO_CHUNK_TITLE-'):
        if self.chunk_title:
            content="# SOURCE #\n"+self.chunk_title+'\n# CONTENT #\n'+content+"\n# END SOURCE #"+self.chunk_title
    prompt_data = self.prompt_data_list[self.get_prompt_data_section_number()]
    if prompt_data:
        content = prompt_data+'\n\n'+content
    content = eatAll(content,['\n'])
    return content

## chunk data keys
def chunk_event_check(self)->bool:
    """
    checks if any events related to the chunk UI elements were triggered and performs the necessary actions.
    """

    if self.event in self.section_navigation_keys+self.sub_navigation_keys:
        nav_type, nav_direction=self.navigation_mgr.parse_navigation_event(self.event)
        nav_data=self.navigation_mgr.get_navigation_data(nav_type)
        sub_section_number = self.navigation_mgr.get_sub_section_number(nav_type)
        refference_object = self.navigation_mgr.get_reference_object(nav_type)
        self.navigation_mgr.update_navigation_counters(nav_data, nav_direction)

    elif self.event in ['-REDO_CHUNKS-',
                        '-ADD_URL_TO_CHUNK-',
                        '-ADD_FILE_TO_CHUNK-',
                        '-ADD_QUERY_TO_CHUNK-',
                        '-COMPLETION_PERCENTAGE-',
                        '-PROMPT_PERCENTAGE-'] or self.script_event_js['found'] in ['-FILE_TEXT-',
                                                                                    '-ADD_FILE_TO_CHUNK-',
                                                                                    '-ADD_QUERY_TO_CHUNK-',
                                                                                    '-ADD_URL_TO_CHUNK-']:
        data=None
        if self.event == '-CLEAR_CHUNKS-':
            """
            clears the currently displayed chunk data from the GUI.
            """
            data = ''
            self.chunk_type = None
        
        elif self.event in self.toke_percentage_dropdowns:
            value = self.window_mgr.get_from_value(self.event)
            key = '-COMPLETION_PERCENTAGE-'
            completion_percentage = 100-value
            if self.event == '-COMPLETION_PERCENTAGE-':
                key = '-PROMPT_PERCENTAGE-'
                completion_percentage = value
            self.window_mgr.update_value(key,value=100-value)
            self.prompt_mgr_update_js['completion_percentage']=completion_percentage
            self.prompt_mgr.update_request_and_prompt_data(completion_percentage = completion_percentage)
        elif self.event == '-UNDO_CHUNKS-':
            data = self.history_mgr.undo(self.chunk_history_name)

        elif self.event == '-REDO_CHUNKS-':
            data = self.history_mgr.redo(self.chunk_history_name)
        elif self.event == '-ADD_URL_TO_CHUNK-':
            self.chunk_title=self.window_mgr.get_values()[text_to_key('-CHUNK_TITLE-',section='url')]
            data = self.add_to_chunk(self.window_mgr.get_values()['-URL_TEXT-'])
            self.chunk_type=self.url_chunk_type
            
        elif self.script_event_js['found']=='-ADD_FILE_TO_CHUNK-':
            self.chunk_title=self.window_mgr.get_values()[text_to_key('-CHUNK_TITLE-',section=self.script_event_js['section'])]
            data = self.add_to_chunk(self.window_mgr.get_values()[text_to_key('-FILE_TEXT-',section=self.script_event_js['section'])])
            if self.script_event_js['section'].lower() == 'database':
                spec_num = self.get_spec_section_number_display('request')
                self.instruction_data_list[spec_num]['bool_values']['database_query']=True
                self.update_bool_instructions()
            self.chunk_type='CODE'
        self.update_prompt_data(data)

    else:
        return False
    self.update_text()
    self.update_query_display()
    return True
           


