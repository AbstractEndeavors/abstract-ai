# DEPENDENCIES #
from .dependencies import *
from .response_section import *
from .instruction_section import *
from .test_section import *
from .window_section import *
from .url_section import *
from .prompt_section import *
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
        self.logger = logger
        self.loop = asyncio.new_event_loop()
        self.submission_in_progress = False
        #ResponseManagement
        self.load_response_management()
        #InstructionManagement
        self.load_instruction_management()
        #TestManagement
        self.load_test_management()
        #WindowManagement
        self.load_window_management()
        #urlManagement
        self.load_url_management()
        #PromptManagement
        self.load_prompt_management()
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
    def load_prompt_management(self):
        GptManager.update_prompt_mgr=update_prompt_mgr
        GptManager.sanitize_prompt_and_request_data=sanitize_prompt_and_request_data
        GptManager.get_prompt_data_section_number=get_prompt_data_section_number
        GptManager.get_chunk_token_distribution_number=get_chunk_token_distribution_number
        GptManager.get_chunk_number=get_chunk_number
        GptManager.get_spec_section_number_display=get_spec_section_number_display
        GptManager.update_request_data_list=update_request_data_list
        GptManager.update_request_data_display=update_request_data_display
        GptManager.update_prompt_data_list=update_prompt_data_list
        GptManager.update_prompt_data_display=update_prompt_data_display
        GptManager.prompt_request_event_check=prompt_request_event_check
        GptManager.get_adjusted_number=get_adjusted_number
        GptManager.update_prompt_data=update_prompt_data
        GptManager.update_request_data=update_request_data
        GptManager.update_query_display=update_query_display
        GptManager.update_chunk_info=update_chunk_info
        GptManager.add_to_chunk=add_to_chunk
        GptManager.chunk_event_check=chunk_event_check
    def load_url_management(self):
        GptManager.append_output=append_output
        GptManager.get_url=get_url
        GptManager.get_url_manager=get_url_manager
        GptManager.url_event_check=url_event_check
    def load_window_management(self):
        GptManager.readme_event_check=readme_event_check
        GptManager.database_event_check=database_event_check
        GptManager.perform_event_checks=perform_event_checks
        GptManager.browser_event_query=browser_event_query
        GptManager.while_window=while_window
    def load_test_management(self):
        GptManager.check_test_bool=check_test_bool
        GptManager.test_event_check=test_event_check
    def load_instruction_management(self):
        GptManager.update_instruction_mgr=update_instruction_mgr
        GptManager.update_bool_instructions=update_bool_instructions
        GptManager.restore_instruction_defaults=restore_instruction_defaults
        GptManager.delegate_instruction_text=delegate_instruction_text
        GptManager.instruction_event_check=instruction_event_check
    def load_response_management(self):
        GptManager.update_response_mgr=update_response_mgr
        GptManager.get_new_api_call_name=get_new_api_call_name
        GptManager.start_asyncio_loop=start_asyncio_loop
        GptManager.query_event_check=query_event_check
        GptManager.handle_future_result=handle_future_result
        GptManager.submit_event=submit_event
        GptManager.get_dots=get_dots
        GptManager.update_progress_chunks=update_progress_chunks
        GptManager.check_response_mgr_status=check_response_mgr_status
        GptManager.submit_query=submit_query
        GptManager.get_query=get_query
        GptManager.response_event_check=response_event_check
        GptManager.get_output_response=get_output_response
        GptManager.update_text_with_responses=update_text_with_responses
        GptManager.get_current_request_data=get_current_request_data
        GptManager.unlist_self=unlist_self
        GptManager.initialize_output_display=initialize_output_display
        GptManager.get_output_display_numbers=get_output_display_numbers
        GptManager.determine_output_display=determine_output_display
        GptManager.update_output=update_output
        GptManager.adjust_output_display=adjust_output_display
        GptManager.listbox_event_check=listbox_event_check
        GptManager.update_last_response_file=update_last_response_file
        GptManager.update_response_list_box=update_response_list_box
        GptManager.aggregate_conversations=aggregate_conversations
        threading.Thread(target=self.start_asyncio_loop, daemon=True).start()
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
        self.api_mgr = ApiManager(header=self.header,api_env=self.api_env,api_key=self.api_key,endpoint=self.model_mgr.selected_endpoint)

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
 


        

