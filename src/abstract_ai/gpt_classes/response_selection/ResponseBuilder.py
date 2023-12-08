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
                                write_to_file)
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
            self.save_to_file(data = data,file_path = self.file_path)
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
    def __init__(self,prompt_mgr=None,api_mgr=None,title:str=None,directory:str=None)->None:
        self.prompt_mgr=prompt_mgr
        self.model_mgr=self.prompt_mgr.model_mgr
        self.api_mgr=api_mgr
        self.title=title
        self.save_manager = SaveManager()
        self.directory=mkdirs(directory or os.path.join(os.getcwd(),'response_data'))
        self.chunk_token_distributions=prompt_mgr.chunk_token_distributions
        self.output=[]
        self.content={}
        self.query_js={}
        self.bool_test=False
        self.chunk_descriptions=[]
        self.original_title=self.title
        self.re_initialize_query()
        self.response_keys = ["api_response","abort","additional_responses","suggestions","notation","generate_title","request_chunks","token_adjustment","prompt_as_previous","created","model","error",'content']
    def re_initialize_query(self)->None:
        self.i_query=0
        self.generate_title=None
        self.query_done=False
        self.abort_js = {"abort":None,"additional_responses":None,"request_chunks":None}
        self.suggestions=False
        self.notation=False
        self.api_response={}
        self.request_chunks=None
        self.token_adjustment=None
        self.prompt_as_previous_clone=None
    def post_request(self)->(str or dict):
        """
        Sends a POST request to the specified endpoint with the provided prompt and headers.
        
        Args:
            endpoint (str): URL endpoint to which the request is sent.
            prompt (str or dict): Prompt or data to be sent in the request.
            content_type (str): Type of the content being sent in the request.
            api_key (str): The API key for authorization.
            header (dict): Optional custom headers. If not provided, default headers will be used.
            
        Returns:
            dict: Response received from the server.
        """

        if self.response.status_code == 200:
            print(f'Request successful with status code {self.api_response.status_code}')
        else:
            raise Exception(f'Request failed with status code {self.api_response.status_code}\n{self.api_response.text}\n\n')
        return self.get_response()
    def get_response(self):
        # Convert the response to JSON directly within this method
        try:
            self.api_response = self.response.json()
        except ValueError:
            # Handle the case where the response is not JSON
            self.api_response = {"error": "Response is not in JSON format", "data": self.response.text}
        # Save the response using SaveManager
        json_api_response = safe_json_loads(self.api_response)
        self.save_manager = SaveManager(data=self.query_js, title=json_api_response.get('created','response'), directory=['response_data','raw_response'], model=json_api_response.get('model','default'))
        self.get_all_instruction(json_api_response)
        self.query_js["response"]=json_api_response
        self.save_manager = SaveManager(data=self.query_js, title=self.generate_title or self.title or 'response', directory=self.directory, model=self.model)
        self.output.append(self.save_manager.data)
    def try_load_response(self)->None:
        """
        Attempts to load the response content into a structured format.
        """
        self.api_response = safe_json_loads(self.get_response())
    def extract_response(self)->dict:
        """
        Processes the response and manages the creation of a save point through `SaveManager`.
        """
        return self.query_js
    def get_abort(self)->bool:
       if self.abort_js["abort"] or self.abort_js["blank_prompt"]:
            return True
       if self.abort_js["request_chunks"] or self.abort_js["additional_responses"]:
           return False
       else:
           return True
    def get_all_instruction(self,data:dict)->None:
        self.prompt_as_previous_clone
        if data:
            self.abort_js = {"abort":None,"additional_responses":None,"request_chunks":None,"blank_prompt":self.prompt.get('blank_prompt')}
            for i,key in enumerate(self.response_keys):
                value = get_any_value(data,key)
                self.abort_js[key]=value
                if isinstance(value,list) and value:
                    value=value[-1]
                setattr(self,key,value)
                if key == 'prompt_as_previous' and value:
                    self.prompt_as_previous_clone=self.api_response
            error_response = get_any_value(data,'error')
            if error_response:
                self.error = 'error'
            self.model = self.model or self.error or 'default'
            self.title = self.generate_title or self.original_title or self.created
            self.get_abort()
    def send_query(self)->None:
        """
        Handles the response after a query has been sent.
        """
        self.query_js={}
        self.prompt = self.prompt_mgr.create_prompt(chunk_token_distribution_number=self.chunk_token_distribution_number,
                                                    chunk_number = self.chunk_number,
                                                    notation=self.notation,
                                                    generate_title=self.generate_title,
                                                    request_chunks=self.request_chunks,
                                                    token_adjustment=self.token_adjustment,
                                                    prompt_as_previous=self.prompt_as_previous_clone)
        if self.prompt.get('blank_prompt')==None:
            self.query_js["prompt"]=safe_json_loads(self.prompt)
            self.endpoint = self.model_mgr.selected_endpoint
            self.header = self.api_mgr.header
            self.response = requests.post(url=self.endpoint, json=self.prompt, headers=self.header)
            safe_json_loads(self.get_response())
    def initial_query(self)->list[dict]:
        """
        Manages the initial sequence of sending queries and processing responses.

        Returns:
            list: List of output data after processing.
        """
        self.query_done=False
        self.i_query = 0
        self.total_dists = 0
        for dist in self.chunk_token_distributions:
            self.total_dists +=len(dist)
        for chunk_token_distribution_number,distributions in enumerate(self.chunk_token_distributions):
            for chunk_number,distribution in enumerate(distributions):
                self.chunk_token_distribution_number=chunk_token_distribution_number
                self.chunk_number=chunk_number
                self.total_current_dist = len(distributions)
                response_loop=True
                abort_it=False
                while response_loop:
                    self.send_query()
                    if self.get_abort() or self.abort_js["abort"]:
                        response_loop=False
                        break
                print(f'in while {self.i_query}')
                if self.abort_js["abort"]:
                    break
                self.i_query+=1
        self.query_done=True
        self.i_query=0
        return self.output
