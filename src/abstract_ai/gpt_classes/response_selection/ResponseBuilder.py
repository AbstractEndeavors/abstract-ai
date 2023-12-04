import os
import requests
import json
from abstract_utilities import (get_date,
                                mkdirs,
                                get_files,
                                unified_json_loader,
                                safe_json_loads,
                                safe_read_from_json,
                                get_file_create_time,
                                get_highest_value_obj,
                                get_any_value,
                                safe_json_loads,
                                safe_dump_to_file,
                                read_from_file,
                                write_to_file,
                                is_number,)
def is_bool(obj,convert=False):
    converted = obj
    is_bool = False
    if obj in [0,False,'false','False','F']:
        converted = bool(obj)
        is_bool = True
    if obj in  [1,True,'true','True','T']:
        converted = bool(obj)
        is_bool = True
    if convert:
        return converted
    return is_bool
        
class SaveManager:
    """
    Manages the saving of data. This class should provide methods to specify where (e.g., what database or file) and how (e.g., in what format) data should be saved.
    """
    def __init__(self, data={},title:str=None,directory:str=None,model:str='default')->None:
        self.title=title
        self.model=model
        self.date = get_date()
        if isinstance(directory,list):
            abs_path = directory[0]
            if not os.path.isabs(directory[0]):
                abs_path = os.path.join(os.getcwd(), directory[0])
                mkdirs(abs_path)
            path = abs_path
            for child in directory[1:]:
                path = os.path.join(path, child)
                mkdirs(path)
            self.directory=path
        else:
            self.directory = mkdirs(directory or os.path.join(os.getcwd(), 'response_data'))
            self.directory = mkdirs(os.path.join(self.directory, self.date))
            self.directory = mkdirs(os.path.join(self.directory, self.model))
        self.file_name = self.create_unique_file_name()
        self.file_path = os.path.join(self.directory, self.file_name)
        if data:
            self.data = safe_json_loads(data)
            self.data['file_path']=self.file_path
            self.data['title']=self.title
            self.data['model']=self.model
            safe_dump_to_file(data = data,file_path = self.file_path)
    def create_unique_file_name(self) -> str:
        # Sanitize and shorten the title
        sanitized_title = self.sanitize_title(self.title)

        # Generate base file name
        base_name = f"{sanitized_title}.json"
        
        # Check for uniqueness and append index if needed
        unique_name = base_name
        index = 1
        while os.path.exists(os.path.join(self.directory, unique_name)):
            unique_name = f"{sanitized_title}_{index}.json"
            index += 1

        return unique_name

    @staticmethod
    def sanitize_title(title: str) -> str:
        if title:
            # Replace spaces and special characters
            title = str(title).replace(" ", "_").replace(":", "_")

            # Limit the length of the title
            max_length = 30
            if len(title) > max_length:
                title = title[:max_length]

            return title
            def save_to_file(self, data:dict, file_path:str)->None:
                # Assuming `data` is already a dictionary, we convert it to a JSON string and save.
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)
        
    @staticmethod
    def read_saved_json(file_path:str)->dict:
        # Use 'safe_read_from_json' which is presumed to handle errors and return JSON
        return safe_read_from_json(file_path)
    
class ResponseManager:
    """
    The `ResponseManager` class handles the communication process with AI models by managing the sending of queries and storage of responses. It ensures that responses are correctly interpreted, errors are managed, and that responses are saved in a structured way, facilitating easy retrieval and analysis.

    It leverages various utilities from the `abstract_utilities` module for processing and organizing the data and interacts closely with the `SaveManager` for persisting responses.

    Attributes:
        prompt_mgr (Any): An instance of the prompt manager that is responsible for creating the prompts that will be sent to the AI model.
        api_mgr (Any): An instance that manages the communication with the API endpoint for sending queries and receiving responses.
        title (str, optional): The title for the session or the saved file. Defaults to None.
        directory (str, optional): The path to the directory where responses will be saved. Defaults to the 'response_data' folder in the current working directory.
        bot_notation (Any, optional): A notation used by the bot for managing responses. Defaults to None.
        token_dist (List[Any]): A list that contains information about the distribution of tokens or elements related to the response.
        output (List[Any]): A list to store output data after processing.
        content (Dict[Any, Any]): A dictionary to hold the content of the response.
        query_js (Dict[Any, Any]): A dictionary that holds the complete query and response data.
        chunk_descriptions (List[str]): A list to hold descriptions of different chunks of the response if applicable.
        i_query (int): An index to keep track of the query being processed.
        original_title (str): The original title for the session or saved file.
        query_done (bool): A flag to indicate if the query process is complete.
        response_keys (List[str]): A list of keys that are expected or relevant in the responses.

    Methods:
        re_initialize_query: Resets query-related attributes to their default state for a new query cycle.
        post_request: Sends a POST request with the current prompt and headers to the AI model and handles the response.
        get_response: Extracts and formats the response from the API call.
        try_load_response: Attempts to load the response content into a structured format.
        extract_response: Processes the response and manages the creation of a save point through `SaveManager`.
        get_last_response: Retrieves the last response from the save location.
        get_response_bools: Checks and sets boolean flags based on the content of the latest response.
        send_query: Prepares and sends a new query to the AI model, then processes the response.
        test_query: Simulates sending a query for testing purposes.
        prepare_response: Handles the response after a query has been sent.
        initial_query: Manages the initial sequence of sending queries and processing responses.
    """

    def __init__(self, prompt_mgr=None, api_mgr=None, title=None, directory=None):
        self.prompt_mgr = prompt_mgr
        self.model_mgr=self.prompt_mgr.model_mgr
        self.instruction_mgr = self.prompt_mgr.instruction_mgr
        self.api_mgr = api_mgr
        self.title = title
        self.directory = directory or os.path.join(os.getcwd(), 'response_data')
        self.save_manager = SaveManager()
        self.re_initialize_query()
        self.response_keys = ["api_response", "abort", "additional_responses", "suggestions", "notation", "generate_title", "request_chunks", "token_adjustment", "prompt_as_previous", "created", "model", "error", "content"]

    def re_initialize_query(self):
        self.i_query = 0
        self.generate_title = None
        self.query_done = False
        self.api_response = {}
        self.abort_js = {"abort": None, "additional_responses": None, "request_chunks": None}
        self.output = []
        self.current_content = {}
        self.query_js = {}
        self.chunk_token_distributions = self.prompt_mgr.chunk_token_distributions if self.prompt_mgr else []

    def post_request(self):
        """
        Sends a POST request with the current prompt to the AI model and handles the response.

        Returns:
            dict or str: Processed response received from the server.
        """
        self.query_js["prompt"]=safe_json_loads(self.prompt)
        self.endpoint = self.prompt_mgr.model_mgr.selected_endpoint
        self.header = self.api_mgr.header

        response = requests.post(url=self.endpoint, json=self.prompt, headers=self.header)

        if response.status_code != 200:
            raise Exception(f"Request failed with status code {response.status_code}\n{response.text}\n\n")

        return self.process_response(response)

    def create_save_directory(self,response_json,query_js=None,title=None):
        self.error_response = response_json.get('error')
        self.model = response_json.get('model', 'default')
        self.created = response_json.get('created')
        self.model=self.model or self.error_response
        self.title= title or self.generate_title or self.title or self.created
        folder = 'response_data'
        os.makedirs(folder,exist_ok=True)
        folder = os.path.join(folder,f'{get_date()}')
        os.makedirs(folder,exist_ok=True)
        folder=os.path.join(folder,f'{self.model}')
        if self.query_js:
            SaveManager(data=self.query_js, title=self.title, directory=folder, model=self.model)
        else:
            os.makedirs(folder,exist_ok=True)
            folder=os.path.join(folder,'raw_response')
            SaveManager(data=response_json, title=self.title, directory=folder, model=self.model)
        
    def process_response(self, response):
        """
        Processes the API response, extracting relevant data and handling errors.

        Args:
            response (Response): The response object from the API request.

        Returns:
            dict: The processed and structured response data.
        """
        response_json=response
        try:
            if not isinstance(response,dict):
                response_json = response.json()
        except ValueError:
            # If the response is not in JSON format, handle it accordingly
             response_json = {"error": "Response is not in JSON format", "data": response.text}
        
        self.extract_data_from_response(response_json)
        self.title= self.generate_title or self.title or self.created 
        self.query_js['response'] = response_json
        self.response_choices = safe_json_loads(get_any_value(response_json,'choices'))
        if isinstance(self.response_choices,list):
            self.response_choices=safe_json_loads(safe_json_loads(self.response_choices)[0])
        self.response_message=safe_json_loads(get_any_value(self.response_choices,'message'))
        self.response_content=safe_json_loads(get_any_value(self.response_message,'content'))
        self.generate_title=safe_json_loads(get_any_value(self.response_content,'generate_title'))
        self.create_save_directory(response_json=response_json)
        return response_json


    def extract_data_from_response(self, response_json):
        """
        Extracts and processes various components from the response JSON.

        Args:
            response_json (dict): The JSON response from the API.

        This method updates the class attributes based on the response content.
        """
        # Process and update the class attributes based on response content
        # Example: Extract 'error', 'model', 'created', etc., from response_json
        self.error_response = response_json.get('error')
        self.model = response_json.get('model', 'default')
        self.created = response_json.get('created')
        
        # Further processing based on response content
        self.get_all_instruction(data=response_json)

    def get_abort(self):
        self.abort_js = {"abort":None,"additional_responses":None,"request_chunks":None}

        
    def prep_instructions_values(self,distribution_number=None):
        self.prompt_as_previous_clone=None
        default_instructions = self.instruction_mgr.default_instructions
        self.expected_instructions_js={}
        for key in default_instructions.keys():
            setattr(self,key,None)
        if len(self.instruction_mgr.instructions) >0:
            self.distribution_number=distribution_number or self.chunk_token_distribution_number
            self.instructions_js = self.instruction_mgr.instructions[self.distribution_number]
            
            for key,value in instructions_js['instructions_bools'].items():
                if value == True:
                    example = default_instructions[key]['example']
                    if is_bool(example):
                        value = is_bool(value,convert=True)
                    elif is_number(value):
                        value = int(value)
                    else:
                        value = None
                    setattr(self,key,value)
                    self.expected_instructions_js[key]=value
    def get_all_instruction(self, data: dict) -> None:
        """
        Processes all instructions from the response data and updates the relevant attributes.

        Args:
            data (dict): The response data from which instructions are extracted.
        """
        self.current_api_response = data.get('api_response', '')
        self.instruction_mgr = self.prompt_mgr.instruction_mgr
        self.prompt_as_previous_clone=None
        self.get_abort()        

        # Extract and process each instruction
        for response_key, value in data.items():
            if response_key in self.expected_instructions_js:
                self.expected_instructions_js[response_key]
                if is_bool(value):
                    value = is_bool(value,convert=True)
                elif is_number(value):
                    value = int(value)
                elif value == '':
                    value = None
                setattr(self, response_key, value)
                if response_key in ["prompt_as_previous", "additional_responses", "request_chunks", "abort"] and value:
                    self.break_current = True
                if response_key in self.abort_js:
                    self.abort_js[response_key] = bool(value)
                if response_key == "prompt_as_previous" and bool_value:
                    self.prompt_as_previous_clone = self.current_api_response
        
    def send_query(self):
        """
        Prepares and sends a new query to the AI model, then processes the response.
        """
        self.query_js = {}  # Resetting the query JSON
        
        # Create a prompt using the PromptManager
        self.prompt = self.prompt_mgr.create_prompt(
            chunk_token_distribution_number=self.chunk_token_distribution_number,
            chunk_number=self.chunk_number,
            notation=self.notation,
            generate_title=self.generate_title,
            request_chunks=self.request_chunks,
            token_adjustment=self.token_adjustment,
            prompt_as_previous=self.prompt_as_previous_clone
        )
        self.prep_instructions_values()
        # Check for a blank prompt to avoid unnecessary requests
        if not self.prompt.get('blank_prompt'):
            self.query_js["prompt"] = self.prompt
            response = self.post_request()  # Send the request and get the response
            self.process_response(response)  # Process the received response
        
        self.title= self.generate_title or self.title or self.created 
        # Handling the break condition based on the 'abort' instruction
        self.create_save_directory(response_json=self.query_js['response'],query_js=self.query_js,title=self.title)
        self.output.append(self.query_js)
    def get_loop_current(self):
        return True if True in [getattr(self, "additional_responses"),getattr(self, "request_chunks")] else False
    def initial_query(self):
        """
        Manages the initial sequence of sending queries and processing responses.

        Returns:
            list[dict]: List of output data after processing.
        """
        self.query_done = False
        self.i_query = 0
        self.chunk_token_distribution_number=0
        self.total_dists = sum(len(dist) for dist in self.chunk_token_distributions)
        self.prep_instructions_values(self.i_query)
        self.loop_current=True
        for chunk_token_distribution_number, distributions in enumerate(self.chunk_token_distributions):
            for chunk_number, _ in enumerate(distributions):
                self.chunk_token_distribution_number = chunk_token_distribution_number
                self.chunk_number = chunk_number
                while True:
                    self.send_query()
                    if self.get_loop_current() != True or getattr(self, "abort") == True:
                        break
                self.i_query += 1
                if getattr(self, "abort"):
                    break
        self.query_done = True
        self.i_query = 0
        return self.output

