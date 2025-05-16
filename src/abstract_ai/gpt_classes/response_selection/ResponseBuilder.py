from ..prompt_selection import *
from ..model_selection import *
from ..instruction_selection import *
from ..api_selection import *
from ..nogui_selection import *
from .tokenBucket import TokenBucket
from .saveBuilder import SaveManager
from ...specializations.responseContentParser import *
import aiohttp
import asyncio
import logging
import time
from typing import List, Dict, Any
from abstract_apis import asyncPostRequest
# Configure logging
logging.basicConfig(level=logging.INFO)
class ResponseManager:
    def __init__(self, prompt_mgr=None, api_mgr=None, title: str = None, directory: str = None, rate_limit_per_minute: int = 80000):
        self.query_js = {}
        self.prompt_mgr = prompt_mgr or PromptManager()
        self.model_mgr = self.prompt_mgr.model_mgr
        self.model = self.model_mgr.selected_model_name
        self.api_mgr = api_mgr or ApiManager()
        self.title = title
        self.directory=directory or os.path.join(os.getcwd(),'response_data')
        self.save_manager = SaveManager(directory=self.directory)
        os.makedirs(self.directory,exist_ok=True)
        self.chunk_token_distributions = self.prompt_mgr.chunk_token_distributions
        self.output = []
        self.token_bucket = TokenBucket(capacity=rate_limit_per_minute, refill_rate=rate_limit_per_minute / 60)
        self.logger = logging.getLogger(__name__)
        self.re_initialize_query()
        self.total_tokens_list = []
        self.response_keys = [
            "api_response", "abort", "additional_responses", "suggestions", "notation",
            "generate_title", "request_chunks", "token_adjustment", "prompt_as_previous",
            "created", "model", "error", 'content'
        ]
        # Initialize abort_js to prevent KeyError
        self.abort_js = {
            "abort": None,
            "additional_responses": False,
            "request_chunks": None,
            "blank_prompt": None
        }

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
    def get_response(self):
        # Convert the response to JSON directly within this method
        self.current_response = safe_json_loads(self.response) or {}
        self.current_created = self.current_response.get("created") or time.time()
        self.current_title = get_title(self.current_response) or get_any_value(self.current_response,'generate_title') or self.current_created or 'response'
        self.current_model = get_model(self.current_response) or get_any_value(self.current_response,'model') or self.model or 'default'
        self.current_usage = get_any_value(self.response,"usage")
        self.current_total_tokens = get_any_value(self.current_usage,"total_tokens")
        self.current_content = get_any_value(self.response,"content")
        if not isinstance(self.current_content,dict):
            try:
                self.current_content = safe_json_loads(self.current_content)
                self.current_response['choices'][0]['message']['content'] = self.current_content
            except:
                pass

        self.total_tokens_list.append({"time":self.current_created,"tokens":self.current_usage})
        self.get_all_instruction(self.current_content)
        self.query_js["response"]=self.current_response
        self.save_manager = SaveManager(data=self.query_js, title=self.current_title, directory=self.directory, model=self.current_model)
        self.output.append(self.save_manager.data)
    def get_all_instruction(self,data:dict)->None:
        self.prompt_as_previous_clone=False
        if data:
            self.abort_js = {"abort":None,"additional_responses":False,"request_chunks":None,"blank_prompt":self.prompt.get('blank_prompt')}
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
            self.model = self.current_model
            self.title = self.current_title
            self.get_abort()

    async def send_query(self) -> None:
        """
        Asynchronously sends a query to the AI model and processes the response.
        """
        self.query_js = {}
        self.prompt = self.prompt_mgr.create_prompt(
            chunk_token_distribution_number=self.chunk_token_distribution_number,
            chunk_number=self.chunk_number,
            notation=self.notation,
            generate_title=self.generate_title,
            request_chunks=self.request_chunks,
            token_adjustment=self.token_adjustment,
            prompt_as_previous=self.prompt_as_previous_clone
        )
        if self.prompt.get('blank_prompt') is None:
            self.query_js["prompt"] = safe_json_loads(self.prompt)
            self.endpoint = self.model_mgr.selected_endpoint
            self.header = self.api_mgr.header
            self.response = await asyncPostRequest(url=self.endpoint,data=self.prompt,headers=self.header)
            json_api_response = safe_json_loads(self.response)
            self.save_manager = SaveManager(data=json_api_response, title=get_any_value(json_api_response,'created') or str(time.time()).split('.')[0], directory=['response_data','raw_response'], model=get_any_value(json_api_response,'model'))
            self.get_response()
        else:
            self.logger.info("Blank prompt detected, skipping send_query")
            # Update abort_js to prevent infinite loop
            self.abort_js["abort"] = True

    async def initial_query(self) -> List[dict]:
        """
        Manages the initial sequence of sending queries and processing responses.

        Returns:
            List[dict]: List of output data after processing.
        """
        self.query_done = False
        self.i_query = 0
        self.total_dists = sum(len(dist) for dist in self.chunk_token_distributions)
        self.chunk_token_distribution_number = 0
        self.chunk_number = -1
        for chunk_token_distribution_number, distributions in enumerate(self.chunk_token_distributions):
            for chunk_number, distribution in enumerate(distributions):
                self.chunk_token_distribution_number = chunk_token_distribution_number
                self.chunk_number = chunk_number
                self.total_current_dist = len(distributions)
                response_loop = True
                while response_loop:
                    # Wait for tokens to be available according to rate limit
                    tokens_needed = self.model_mgr.selected_max_tokens
                    await self.token_bucket.wait_for_token(tokens_needed)

                    # Send the query
                    await self.send_query()

                    # Add logging to see the state
                    self.logger.info(f"In loop. get_abort(): {self.get_abort()}, abort_js['abort']: {self.abort_js.get('abort')}, additional_responses: {self.abort_js.get('additional_responses')}")

                    if self.get_abort() or self.abort_js.get("abort"):
                        response_loop = False
                        break
                    else:
                        # If additional responses are requested, handle them here
                        if self.abort_js.get('additional_responses'):
                            # Handle additional responses if necessary
                            self.logger.info("Handling additional responses")
                            # Implement logic to handle additional responses
                            # For now, we'll just break to prevent infinite loop
                            response_loop = False
                        else:
                            # No additional responses requested, break the loop
                            response_loop = False
                self.logger.info(f"Completed query {self.i_query}")
                if self.abort_js.get("abort"):
                    self.logger.info('Query aborted.')
                    break

                self.i_query += 1
                self.chunk_number += 1

        self.query_done = True
        self.i_query = 0
        return self.output

    def get_abort(self) -> bool:
        """
        Determines whether to abort the current query based on response data.
        """
        abort = False
        if self.abort_js.get("abort"):
            abort = True
        elif self.abort_js.get("blank_prompt"):
            abort = True
        elif not self.abort_js.get("request_chunks") and not self.abort_js.get("additional_responses"):
            abort = True
        else:
            abort = False
        return abort
