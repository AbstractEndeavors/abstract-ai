from ..dependencies import *
# updates instructions manager with environment values from GUI      
def update_instruction_mgr(self)->None:
    """
    updates the Instruction Manager with the environment values from the GUI. If the '-instructions-'
    key in the UI is set, it also updates the Instruction Manager's attributes for each instruction key.
    """
    spec_num = self.get_spec_section_number_display('request')
    self.instruction_data_list[spec_num]['text_values']={"api_response":"place response to prompt here"}
    for key in self.instruction_pre_keys:
        bool_key = text_to_key(text=key,section="BOOL")
        text_key = text_to_key(text=key,section="TEXT")
        self.instruction_data_list[spec_num]['bool_values'][key]=self.window_mgr.get_from_value(bool_key)
        if self.window_mgr.get_from_value(bool_key):
            self.instruction_data_list[spec_num]['text_values'][key]=self.window_mgr.get_from_value(text_key)
    instructions_display_text_value=""
    if self.instruction_data_list[spec_num]['bool_values']["instructions"]:
        instructions_display_text_value = self.instruction_mgr.get_instructions_text(self.instruction_data_list[spec_num]['text_values'])
    self.instruction_data_list[spec_num]['text']=instructions_display_text_value
    self.window_mgr.update_value(key="-INSTRUCTIONS_TEXT-",value=self.instruction_data_list[spec_num]['text'])
    self.prompt_mgr.update_request_and_prompt_data(instruction_data = self.instruction_data_list)
    
def update_bool_instructions(self)->None:
    spec_num = self.get_spec_section_number_display('request')
    self.instruction_data_list[spec_num]['bool_values']['api_response']=True
    for key in self.instruction_pre_keys:
        bool_key = text_to_key(text=key,section="BOOL")
        value=False
        if key in self.instruction_data_list[spec_num]['bool_values']:
            value = self.instruction_data_list[spec_num]['bool_values'][key]
        self.window_mgr.update_value(key=bool_key,value=value)
    self.window_mgr.update_value(key="-INSTRUCTIONS_TEXT-",value=self.instruction_data_list[spec_num]['text'])
    
def restore_instruction_defaults(self)->None:
    defaults = self.instruction_mgr.default_instructions
    for key in self.instruction_pre_keys:
        text_key = text_to_key(text=key,section="TEXT")
        if key in defaults:
            self.window_mgr.update_value(key=text_key,value=defaults[key]['instruction'])

def delegate_instruction_text(self)->None:
    """
    updates the instructions section in the GUI with the values in the latest response. If the instruction
    key isn't in the GUI's value list, it appends the instruction to the '-other-' section of feedback in the GUI.
    """
    for key in self.instruction_pre_keys:
        value = get_any_value(safe_json_loads(self.last_response_content),key)
        setattr(self,'last_'+key,value)
        self.unlist_self(['last_'+key])
        instruction_key = text_to_key(key,section='feedback')
        if instruction_key not in self.window_mgr.get_values():
            if value:
                self.append_output(text_to_key(text='other',section='feedback'),f"{key}: {value}"+'\n')
        else:
            self.window_mgr.update_value(key=instruction_key,value=value)

def instruction_event_check(self)->bool:
    """
    checks if there was an instruction-related event and updates the Instruction Manager if there was one.
    It then updates the Prompt Manager with the latest instructions.
    """
    if self.event in self.instruction_bool_keys:
        self.update_instruction_mgr()

    else:
        return False
    self.update_query_display()
    return True
