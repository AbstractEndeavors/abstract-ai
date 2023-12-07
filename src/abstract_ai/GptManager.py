# DEPENDENCIES #
import os
import pyperclip
from . import (get_total_layout,
               instructions_keys,
               all_token_keys,
               test_options_keys,
               read_me_window,
               AbstractNavigationManager,
               ApiManager,
               InstructionManager,
               ResponseManager,
               PromptManager,
               ModelManager,
               FileCollator,
               read_from_file_with_multiple_encodings)

from abstract_webtools import UrlManager, SafeRequest, url_grabber_component
from .gui_components.abstract_browser import AbstractBrowser

from abstract_gui import (
    get_event_key_js,
    text_to_key,
    AbstractWindowManager,
    NextReadManager,
    expandable
    
)
from abstract_utilities import (
    get_any_value,
    create_new_name,
    get_sleep,
    eatAll,
    safe_json_loads,
    read_from_file,
    make_list,
    ThreadManager,
    HistoryManager,
    get_file_create_time,
    safe_read_from_json,
    is_number,
    format_json_key_values
)

class GptManager:
    """
    The GptManager class in the abstract_ai module is a complex management system that uses modules to control AI interactions.
    This class initiates window management, browser management, next read management, threading, history management, model management,
    and instruction management. Various update methods set and manage values for the model, API, and instructions, among others.
    It also handles events related to model and instructions, as well as query submissions.
    
    Methods:

    1) __init__() - Initializes types and states of class attributes.

    2) initialize_keys() - Sets up the required keys for events and values on the GUI.

    3) update_api_mgr() - Updates the API manager with new values from GUI.

    4) update_all() - Update instructions manager, model manager, API manager, and other key parts of GptManager with current GUI values.

    5) update_model_mgr() - Updates model manager with latest model name from GUI.

    6) model_event_check() - Checks for model related event and then updates model manager.

    7) unlist_self() - Helper function to unpack a list and assign its value from keys.

    8) get_output_response() - Helper function to format output of a response for easy readability on GUI.

    9) update_text_with_responses() - Formats and displays the response received from GPT model on the GUI.

    10) update_instruction_mgr() - Updates instructions manager with environment values from GUI.

    11) delegate_instruction_text() - Updates instructions section on GUI with values from response.

    12) instruction_event_check() - Checks for instruction related events and then updates instruction manager.

    13) get_new_api_call_name() - Generates a new unique name for the API call.

    14) check_response_mgr_status() - checks if the Response Manager has completed the query process. It returns a Boolean indicating the status.

    15) submit_query() - manages the process of submitting queries to the GPT AI. It starts by disabling the '-SUBMIT_QUERY-'
                         button and then starts a new thread for the get_query method. The method continues to update the progress bar until a response
                         is received, or until the test mode has started, in which case it updates the UI with the test output. After the response is received,
                         the last response file is updated and the text in the UI is updated with the response. The '-SUBMIT_QUERY-' button is then enabled again.

    16) get_query() - handles the operation of querying the AI model. It continues to query until a response is received or until the API call process is stopped.

    17) update_prompt_mgr() - initializes the prompt manager with the information needed for querying the GPT AI model.

    18) update_chunk_info() - updates necessary fields in the chunk info section of the GUI. It gets the chunk data and number from the Prompt
                              Manager's relevant methods and updates the GUI fields.

    19) adjust_chunk_display() - manages the GUI's chunk navigation buttons 'Back' and 'Forward'. It ensures that the navigation is within the
                                 limits of the total chunks and updates the GUI with the correct chunk.

    20) get_chunk_display_numbers() - This helper method retrieves the number of chunks that need to be displayed on the GUI.

    21) determine_chunk_display() - determines the chunk to be displayed based on the chunk navigation buttons 'Back' or 'Forward'.

    22) add_to_chunk() - adds the user's entered request to the request chunk. It also updates the 'chunk_text_number' in the GUI.

    23) clear_chunks() - clears the currently displayed chunk data from the GUI.

    24) chunk_event_check() - checks if any events related to the chunk UI elements were triggered and performs the necessary actions.

    25) append_output() - appends a line of text to the 'other' section of feedback on the GUI.

    26) get_url() - retrieves the URL entered by the user in the corresponding input field of the UI.

    27) get_url_manager() - returns the processed URL. It uses the UrlManager and SafeRequest classes from the abstract_webtools module to process and safe-proof the URL.

    28) query_event_check() - checks if the '-SUBMIT_QUERY-' event was triggered. If it was, it creates a new API call name, initializes the query
                              submission process, and submits the query using the submit_query method.

    29) get_dots() - This is a helper method used in the update_progress_chunks method. It manages the progress tracking visual indication in the UI.
                     It updates the dots string depending on the current state of the dots. If the dots string is full of dots, it resets it to empty.

    30) update_progress_chunks() - updates the progress bar and text status in the GUI, depending on the amount of chunks processed. If the process
                                   is completed, it updates the UI with a sent status and enables the '-SUBMIT_QUERY-' button again.
                                   uses the helper get_dots method for dynamic visual indication of the processing.

        Overall, this class manages each operation in the process of user interaction, query formation, API calling, and result displaying,
        thereby making customized and complex conversations with the GPT model possible.
    """
    def __init__(self)->None:
        """
        initializes the GptManager. It starts by setting the window manager and defining a new window for the chat GPT console. The manager
        for API events is also initiated and the window starts listening for events. The method also initializes the managers for handling the
        AI's responses, the instruction handling, and the submission of queries to the AI. It finally sets a few more internal state variables
        and kicks off the UI's main loop.
 	"""
        self.window_mgr = AbstractWindowManager()
        self.window_name = self.window_mgr.add_window(window_name="Chat GPT Console",title="Chat GPT Console",layout=get_total_layout(),window_height=0.7,window_width=0.8,**expandable())
        self.window_mgr.set_current_window(self.window_name)
        self.window = self.window_mgr.get_window_method(self.window_name)
        self.api_call_list=[]
        self.instruction_bool_keys=[]
        self.values = None
        self.event = None
        self.chunk_title=None
        self.chunk_number=None
        self.start_query=False
        self.display_number_tracker={'instructions':0,'request':0,'prompt_data':0,'chunk':0,'query':0,'chunk_number':0}
        self.prompt_mgr_update_js = {"prompt_data_list":None,
                                     "request_data_list":None,
                                     "completion_percentage":None,
                                     "chunk_type":"CODE"}
        self.navigation_mgr= AbstractNavigationManager(self,window_mgr=self.window_mgr,)
        self.browser_mgr = AbstractBrowser(window_mgr=self)
        self.next_read_mgr=NextReadManager()
        self.thread_mgr = ThreadManager()
        self.history_mgr = HistoryManager()
        self.model_mgr = ModelManager()
        self.instruction_mgr = InstructionManager()
        self.request_data_list=['']
        self.prompt_data_list=['']
        self.instruction_data_list=[{"bool_values":{'api_response':True},"text_values":{"api_response":"place response to prompt here"},"text":""}]
        self.prompt_mgr = PromptManager(instruction_mgr=self.instruction_mgr,
                                   model_mgr=self.model_mgr,
                                        instruction_data=self.instruction_data_list)
        
        self.response=False
        self.updated_progress = False
        self.test_bool=False
        self.output_list=[]
        self.latest_output=[]
        
        self.new_response_path_list=[]
        self.response_directories_list=[]
        #self.response_path_list = self.aggregate_conversations()
        self.initialize_keys()
        self.loop_one=False
        self.bool_loop=False

        self.window_mgr.while_window(window_name=self.window_name, event_handlers=self.while_window)
        
    @staticmethod
    def get_remainder(num:int) ->int: 
        return 100-int(num)
    
    @staticmethod
    def get_new_line(num:int=1)->str:
        new_line = ''
        for i in range(num):
            new_line +='\n'
        return new_line
    
    #text and bool handling
    @staticmethod
    def get_bool_and_text_keys(key_list:list,sections_list:list=[])->list:
        keys = []
        for text in key_list:
            keys.append(text_to_key(text))
            for section in sections_list:
                keys.append(text_to_key(text,section=section))
        return keys
    
    @staticmethod
    def read_file_contents(file_path:str)->str:
        """
        Reads the contents of the file at the given path.

        Args:
            file_path (str): The path to the file.

        Returns:
            str: The contents of the file.
        """
        if os.path.splitext(file_path)[-1] == '.docx':
            return read_docx(file_path)
        else:
            return read_from_file_with_multiple_encodings(file_path)
        
    def initialize_keys(self)->None:
        """sets up the necessary key definitions for handling events and values from the GUI. It defines the keys
        needed to check the event, the chunk history, the token percentage dropdowns, the instruction keys, and others.
        This is essential for the proper functioning and interaction of the GptManager with the GUI.
 	"""
        self.event_check_keys = ['chunk_event_check',
                                 'response_event_check',
                                 'url_event_check',
                                 'listbox_event_check',
                                 'test_event_check',
                                 'instruction_event_check',
                                 'model_event_check',
                                 'query_event_check',
                                 'readme_event_check',
                                 'browser_event_query',
                                 'prompt_request_event_check']
        self.sub_navigation_keys = [
                          text_to_key("chunk forward"),
                          text_to_key("chunk back"),
                          text_to_key("query forward"),
                          text_to_key("query back"),
                          text_to_key('chunk section forward'),
                          text_to_key('query section forward'),
                          text_to_key('chunk section back'),
                          text_to_key('query section back'),
                          ]
        self.section_navigation_keys = [
                          text_to_key('instructions section back'),
                          text_to_key('instructions section forward'),
                          text_to_key('request section back'),
                          text_to_key('request section forward'),
                          text_to_key('prompt_data section back'),
                          text_to_key('prompt_data section forward'),
                          ]
        self.chunk_history_name = self.history_mgr.add_history_name('chunk')
        self.request_history_name = self.history_mgr.add_history_name('request')
        self.toke_percentage_dropdowns = ['-COMPLETION_PERCENTAGE-',
                                          '-PROMPT_PERCENTAGE-']
        self.additions_key_list = self.browser_mgr.key_list+['-FILE_TEXT-',
                                                             '-ADD_FILE_TO_CHUNK-',
                                                             '-ADD_URL_TO_CHUNK-']
        self.instruction_pre_keys = instructions_keys
        for key in self.instruction_pre_keys:
            self.instruction_bool_keys.append(text_to_key(text=key,section='bool'))
        self.sectioned_chunk_text_number_key= text_to_key('chunk text number')
        self.sectioned_chunk_data_key = text_to_key('chunk sectioned data')
        self.chunk_display_keys=self.get_bool_and_text_keys(
            all_token_keys
            )
        self.default_instructions='''your response is expected to be in JSON format with the keys as follows:

0) api_response - place response to prompt here
1) suggestions - A parameter that allows the module to provide suggestions for improving efficiency in future prompt sequences. These suggestions will be reviewed by the user after the entire prompt sequence is fulfilled.
2) generate_title - A parameter used for title generation of the chat. To maintain continuity, the generated title for a given sequence is shared with subsequent queries.

below is an example of the expected json dictionary response format, with the default inputs:
{"api_response": "", "suggestions": "", "generate_title": ""}'''
    def update_all(self)->None:
        """
        updates all the needed managers. It updates the Model Manager, Instruction Manager, API Manager,
        Prompt Manager, and Response Manager with the values currently entered in the GUI.
        """
        self.update_model_mgr()
        self.update_api_mgr()
        self.update_text()
        self.update_response_mgr()
        self.check_test_bool()

    def update_text(self)->None:
        self.update_prompt_mgr(**self.prompt_mgr_update_js)
        
    def fill_lists(self)->None:
        if self.prompt_data_list[-1] != '' or self.request_data_list[-1] != '':
            self.prompt_data_list.append('')
            self.request_data_list.append('')
            self.instruction_data_list.append(self.instruction_data_list[-1])
            
            
#ApiManagement:
    # Updates the API manager with new values from GUI    
    def update_api_mgr(self)->None:
        """
        updates the API manager with new values from the GUI. The values include the API content type,
        header, environment, and key.
 	"""
        self.header=self.window_mgr.get_from_value(text_to_key("header"),delim='')
        self.api_env=self.window_mgr.get_from_value(text_to_key("api_env"),delim='')
        self.api_key=self.window_mgr.get_from_value(text_to_key("api_key"),delim='')
        self.api_mgr = ApiManager(header=self.header,api_env=self.api_env,api_key=self.api_key)

#ModelManagement
# Updates model manager with latest model name from GUI
    def update_model_mgr(self)->None:
        """
        updates the Model Manager with the latest model name from the GUI.
        """
        self.model_mgr = ModelManager(input_model_name=self.window_mgr.get_from_value(text_to_key('model')))
        self.window_mgr.update_value(key=text_to_key('model'),value=self.model_mgr.selected_model_name)
        self.window_mgr.update_value(key=text_to_key('endpoint'),value=self.model_mgr.selected_endpoint)
        self.window_mgr.update_value(key=text_to_key('max_tokens'),value=self.model_mgr.selected_max_tokens)
        
    # Checks for model related event and then updates model manager
    def model_event_check(self)->None:
        """
        checks if there was a model-related event and, if there was, updates the Model Manager.
        """
        if self.event in "-MODEL-":
            self.update_model_mgr()
            self.update_prompt_mgr()
        else:
            return False
        return True
 
#PromptManagement
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
                            '-COMPLETION_PERCENTAGE-',
                            '-PROMPT_PERCENTAGE-'] or self.script_event_js['found'] in ['-FILE_TEXT-',
                                                                                        '-ADD_FILE_TO_CHUNK-',
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
                self.chunk_title=self.window_mgr.get_values()[text_to_key('-CHUNK_TITLE-',section='files')]
                data = self.add_to_chunk(self.window_mgr.get_values()[self.script_event_js['-FILE_TEXT-']])
                self.chunk_type='CODE'
            self.update_prompt_data(data)

        else:
            return False
        self.update_text()
        self.update_query_display()
        return True
        
#InstructionManagement
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
            value = get_any_value(safe_json_loads(self.last_content),key)
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
            
#urlManagement
    def append_output(self,key:str,new_content:str)->None:
        """
        appends a line of text to the 'other' section of feedback on the GUI.
 	"""
        self.window_mgr.update_value(key=key,value=self.window_mgr.get_from_value(key)+'\n\n'+new_content)
        
    def get_url(self)->None:
        """
        retrieves the URL entered by the user in the corresponding input field of the UI.
 	"""
        url = self.window_mgr.get_values()['-URL-']
        if url==None:
            url_list =self.window_mgr.get_values()['-URL_LIST-']
            url = safe_list_return(url_list)
        return url
    
    def get_url_manager(self,url:str=None)->str:
        """
        returns the processed URL. It uses the UrlManager and SafeRequest classes from the abstract_webtools
        module to process and safe-proof the URL.
 	"""
        url = url or self.get_url()
        url_manager = UrlManager(url=url)    
        return url_manager

    def url_event_check(self)->bool:
        """
        Checks if a URL event has been triggered.

        An event is triggered when a user interacts with the URL management interface.
        This function prompts the SafeRequest module to return the HTML content or the
        BeautifulSoup object of the specified URL.

        Returns:
            bool: True if a URL event has been triggered, otherwise False
        """
        if self.event in ['-GET_SOUP-',
                          '-GET_SOURCE_CODE-',
                          '-ADD_URL-']:
            url_manager = self.get_url_manager()
            if self.event in ['-GET_SOUP-',
                              '-GET_SOURCE_CODE-']:
                self.chunk_title=None
                data=self.window_mgr.get_values()['-URL_TEXT-']
                url=None
                if url_manager.url:
                    url = url_manager.url
                if self.event=='-GET_SOUP-':
                    self.url_chunk_type='SOUP'
                    data = url_grabber_component(url=url)
                    self.window_mgr.update_value(key='-URL_TEXT-',value=data)
                elif url_manager.url and self.event=='-GET_SOURCE_CODE-':
                    url_list =self.window_mgr.get_values()['-URL_LIST-']
                    if url_list:
                        url = UrlManager(url=self.window_mgr.get_values()['-URL_LIST-'][0]).url
                        self.chunk_title=url
                        self.window_mgr.update_value(key=text_to_key('-CHUNK_TITLE-',section='url'),value=url)
                    request_manager = SafeRequest(url_manager=url_manager)
                    if self.event == '-GET_SOURCE_CODE-':
                        self.url_chunk_type='URL'
                        data = request_manager.source_code
                else:
                    print(f'url {url} is malformed... aborting...')
            elif self.event == '-ADD_URL-':
                url = url_manager.url
                url_list = make_list(self.window_mgr.get_values()['-URL_LIST-']) or make_list(url)
                if url_list:
                    if url not in url_list:
                        url_list.append(url)
                self.window_mgr.update_value(key='-URL_LIST-',args={"values":url_list})
        else:
            return False
        return True
    
#ResponseManagement
    def update_response_mgr(self)->None:
        self.response_mgr = ResponseManager(prompt_mgr=self.prompt_mgr,api_mgr=self.api_mgr)
        
    def get_new_api_call_name(self)->None:
        """
        A helper method that generates and appends a new unique API call name to the api_call_list.
 	"""
        call_name = create_new_name(name='api_call',names_list=self.api_call_list)
        if call_name not in self.api_call_list:
            self.api_call_list.append(call_name)
    
    def query_event_check(self)->bool:
        """
        checks if the '-SUBMIT_QUERY-' event was triggered. If it was, it creates a new API call name, initializes
        the query submission process, and submits the query using the submit_query method.
	"""
        if self.event == "-SUBMIT_QUERY-":
            self.get_new_api_call_name()
            self.start_query= False
            self.updated_progress=False
            self.response_mgr.re_initialize_query()
            self.submit_query()
        else:
            return False
        return True
    
    def get_dots(self)->None:
        """
        This is a helper method used in the update_progress_chunks method. It manages the progress tracking visual
        indication in the UI. It updates the dots string depending on the current state of the dots. If the dots string
        is full of dots, it resets it to empty.
        """
        count = 0
        stop = False
        dots = ''
        for each in self.dots: 
            if each == ' ' and stop == False:
                dots+='.'
                stop = True
            else:
                dots+=each
        self.dots = dots
        if stop == False:
            self.dots = '   '
        get_sleep(1)
        status='Testing'
        if self.test_bool == False:
            status = "Updating Content" if not self.updated_progress else "Sending"
        self.window_mgr.update_value(key='-PROGRESS_TEXT-', value=f'{status}{self.dots}')
        
    def update_progress_chunks(self,done:bool=False)->None:
        """
        updates the progress bar and text status in the GUI, depending on the amount of chunks processed. If the
        process is completed, it updates the UI with a sent status and enables the '-SUBMIT_QUERY-' button again.
        uses the helper get_dots method for dynamic visual indication of the processing.
	"""
        self.total_dists=0
        for dist in self.chunk_token_distributions:
            self.total_dists +=len(dist)
        i_query = int(self.response_mgr.i_query)
        if done == True:
            self.window['-PROGRESS-'].update_bar(100, 100)
            self.window_mgr.update_value(key='-QUERY_COUNT-', value=f"a total of {self.total_dists} chunks have been sent")
            self.window_mgr.update_value(key='-PROGRESS_TEXT-', value='SENT')
            self.updated_progress = True
        else:
            self.get_dots()
            self.window['-PROGRESS-'].update_bar(i_query, self.total_dists)
            if i_query == 0 and self.total_dists!= 0 :
                i_query = 1
            self.window_mgr.update_value(key='-QUERY_COUNT-', value=f"chunk {i_query} of {self.total_dists} being sent")
            
    # checks if the Response Manager has completed the query process.         
    def check_response_mgr_status(self)->bool:
        """
        checks if the Response Manager has completed the query process. It returns a Boolean indicating the status.
	"""
        if not self.test_bool:
            return self.response_mgr.query_done
        return self.start_query
    
    # Manages the process of submitting queries to the GPT AI
    def submit_query(self)->None:
        """
        manages the process of submitting queries to the GPT AI. It starts by disabling the '-SUBMIT_QUERY-'
        button and then starts a new thread for the get_query method. The method continues to update the progress
        bar until a response is received, or until the test mode has started, in which case it updates the UI with the
        test output. After the response is received, the last response file is updated and the text in the UI is updated
        with the response. The '-SUBMIT_QUERY-' button is then enabled again.
	"""
        self.window["-SUBMIT_QUERY-"].update(disabled=True)
        self.dots = '...'
        self.start_query=False
        while self.check_response_mgr_status() == False or self.start_query == False:
            self.update_progress_chunks()
            if not self.updated_progress:
                
                self.update_all()
                
                if self.test_bool == False:
                    self.thread_mgr.add_thread(name=self.api_call_list[-1],target_function=self.get_query,overwrite=True)
                    self.thread_mgr.start(self.api_call_list[-1])
                else:
                    self.latest_output=[safe_read_from_json(self.test_file_path)]
                self.start_query=True    
                self.updated_progress = True
        if not self.test_bool:
            self.latest_output=self.thread_mgr.get_last_result(self.api_call_list[-1])
        self.latest_output=self.latest_output or []
        self.output_list.append(self.latest_output)
  
        self.update_progress_chunks(done=True)
        self.update_last_response_file()
        self.update_text_with_responses()
        self.window["-SUBMIT_QUERY-"].update(disabled=False)
        if not self.window_mgr.get_values()['-REUSE_CHUNK_DATA-']:
            self.update_prompt_data('')
        self.response=False
        
    def get_query(self)->None:
        """
        handles the operation of querying the AI model. It continues to query until a response is
        received or until the API call process is stopped.
	"""
        while not self.response_mgr.query_done:
            if self.response:
                self.thread_mgr.stop(self.api_call_list[-1])
            self.response = self.response_mgr.initial_query()
            if self.response_mgr.query_done:
                print('Response Recieved')
        self.thread_mgr.stop(self.api_call_list[-1],result=self.response)

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
    
    def get_output_response(self,model:str="None",title:str="None",request:str="None",response:str="None")->str:
        """
        A helper method that formats the output string of a response in a clear and readable manner.
        It includes information about the model, title, user request, and AI response.
 	"""
        model = f"#MODEL#{self.get_new_line(1)}{self.last_model}{self.get_new_line(2)}"
        title = f"#TITLE#{self.get_new_line(1)}{str(title)}{self.get_new_line(2)}"
        request = f"#USER REQUEST#{self.get_new_line(1)}{str(request)}{self.get_new_line(2)}"
        response = f"#RESPONSE#{self.get_new_line(2)}{str(response)}{self.get_new_line(2)}"
        return f"{model}{title}{request}{response}"
    
    def update_text_with_responses(self)->None:
        """
        gets the latest response from the AI, formats it using the get_output_response helper method,
        and updates the GUI's '-RESPONSE-' key with the formatted string.
 	"""
        output_keys = []
        self.last_prompt= get_any_value(safe_json_loads(self.current_output),'prompt')
        self.last_response = get_any_value(safe_json_loads(self.current_output),'response')
        self.last_file_path= get_any_value(safe_json_loads(self.current_output),'file_path')
        self.last_title= get_any_value(safe_json_loads(self.current_output),'title')
        self.unlist_self(["last_prompt","last_title","last_file_path","last_prompt"])
        self.last_content = get_any_value(safe_json_loads(self.last_response),'content')
        self.last_api_response = get_any_value(safe_json_loads(self.last_response),'api_response')
        self.last_model =get_any_value(safe_json_loads(self.last_response),'model')
        self.unlist_self(["last_model","last_api_response","last_content"])
        self.window_mgr.update_value(key=text_to_key('title input'),value=self.last_title)
        response_content = self.last_content
        if self.last_api_response:
            response_content=self.last_api_response
            self.delegate_instruction_text()
        self.window_mgr.update_value('-RESPONSE-',self.get_output_response(model=self.last_model,
                                                                           title=self.last_title,
                                                                           request=self.request_data_list[self.get_current_request_data()],
                                                                           response=response_content))
    def get_current_request_data(self)->int:
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
    def initialize_output_display(self)->None:
        """
        Initializes the display of the latest output in the GUI.
        """
        if len(self.latest_output)>0:
            self.current_output=self.latest_output[-1]
        else:
            self.current_output=[]
        self.response_text_number_actual=0
        self.response_text_number_display=1
        self.window_mgr.update_value(key='-RESPONSE_TEXT_NUMBER-',value=self.response_text_number_display)
        self.update_output(output_iteration=0)
        
    def get_output_display_numbers(self)->None:
        """
        Retrieves the actual and display numbers of the current output for navigation purposes.
        """
        self.response_text_number_display = int(self.window_mgr.get_from_value('-RESPONSE_TEXT_NUMBER-'))
        self.response_text_number_actual = self.response_text_number_display-1
        
    def determine_output_display(self,event):
        """
        Determines the output to display based on the navigation event.

        Args:
            event: The navigation event that occurred
        """
        self.get_output_display_numbers()
        if self.event == '-RESPONSE_TEXT_BACK-':
            if self.response_text_number_actual >0:
                self.adjust_output_display(-1)
        elif self.event == '-RESPONSE_TEXT_FORWARD-':
            if self.response_text_number_display < len(self.latest_output):
                self.adjust_output_display(1)
                
    def update_output(self,output_iteration:int):
        """
        Updates the displayed output based on the given iteration.

        Args:
            output_iteration (int): The index of the output to display.
        """
        if output_iteration < len(self.latest_output) and output_iteration >=0:
            self.current_output = self.latest_output[output_iteration]
            self.update_text_with_responses()
            
    def adjust_output_display(self,num:int):
        self.response_text_number_actual+=num
        self.response_text_number_display+=num
        self.update_output(output_iteration=self.response_text_number_actual)
        self.window_mgr.update_value(key='-RESPONSE_TEXT_NUMBER-',value=self.response_text_number_display)
        
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
        
        if file_path:
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
        
#TestManagement
    def check_test_bool(self)->None:
        """
        Checks the status of the `self.test_bool` attribute.

        `self.test_bool` is updated based on the user interaction with the testing tools interface.
        """
        if self.window_mgr.get_values():
            self.test_file_path = self.window_mgr.get_values()['-TEST_FILE_INPUT-']
            self.window_mgr.update_value('-TEST_FILE-',self.test_file_path)
            if self.event=='-TEST_RUN-':
                self.test_bool=self.window_mgr.get_values()['-TEST_RUN-']
                if self.test_bool:
                    status_color = "green"
                    value = 'TESTING'
                    if self.test_file_path:
                        self.test_bool=os.path.isfile(self.test_file_path)
                else:
                    status_color = "light blue"
                    value = 'Awaiting Prompt'
                self.window_mgr.update_value(key='-PROGRESS_TEXT-', args={"value":value,"background_color":status_color})
                
    def test_event_check(self)->bool:
        """
        Checks if a testing event has been triggered.

        A testing event is triggered when a user interacts with the testing features within the module.

        Returns:
            bool: True if a testing event has been triggered, otherwise False
        """
        if self.event in ['-TEST_RUN-','-TEST_FILES-']:
            self.check_test_bool()
        else:
            return False
        return True
