from abstract_utilities import (
    convert_to_percentage,
    read_from_file,
    eatAll,
    make_list,is_number
)
from abstract_utilities.parse_utils import (
    num_tokens_from_string,
    chunk_source_code,
    chunk_data_by_type,
)
from abstract_math import divide_it,multiply_it,add_it,subtract_it,floor_divide_it
from ..model_selection.ModelBuilder import ModelManager
from ..instruction_selection import InstructionManager
from ..api_selection.ApiBuilder import ApiManager
import re
from typing import List, Optional
import tiktoken

def get_encoder(model_name: str = "gpt-4", encoding_name: Optional[str] = None):
    """Return a tiktoken encoder for your model or encoding."""
    if encoding_name:
        return tiktoken.get_encoding(encoding_name)
    return tiktoken.encoding_for_model(model_name)

def count_tokens(text: str, encoder) -> int:
    """Count how many tokens `text` encodes to."""
    return len(encoder.encode(text))

def recursive_chunk(
    text: str,
    desired_tokens: int,
    model_name: str = "gpt-4",
    separators: Optional[List[str]] = None,
    overlap: int = 0
) -> List[str]:
    """
    Split `text` into chunks as close to `desired_tokens` tokens as possible,
    preserving contiguous blocks via `separators`, and *only* splitting inside
    a block if it can’t possibly fit otherwise.
    
    Args:
        text: the full string to split
        desired_tokens: target token count per chunk (never exceed)
        encoder: a tiktoken encoder
        separators: list of splitters, from largest to smallest logical unit
        overlap: how many tokens to overlap between adjacent chunks
    """
    encoder = get_encoder(model_name)
    if separators is None:
        # from big (paragraphs) to small (words)
        separators = ["\n\n", "\n", r"(?<=[\.\?\!])\s", ", ", " "]

    # If it already fits, return it whole:
    if count_tokens(text, encoder) <= desired_tokens:
        return [text]

    # Try splitting by each separator in turn
    for sep in separators:
        # use regex split when the separator is a lookbehind pattern
        parts = re.split(sep, text) if sep.startswith("(?") else text.split(sep)
        if len(parts) > 1:
            chunks: List[str] = []
            current = ""
            current_tokens = 0

            for part in parts:
                part = part.strip()
                if not part:
                    continue
                part_tokens = count_tokens(part, encoder)

                # If this block alone is too big, recurse into it with the next-level separators
                if part_tokens > desired_tokens:
                    # flush current
                    if current:
                        chunks.extend(recursive_chunk(
                            current, desired_tokens, model_name, separators[1:], overlap
                        ))
                        current, current_tokens = "", 0
                    # now chunk the oversized block
                    chunks.extend(recursive_chunk(
                        part, desired_tokens, model_name, separators[1:], overlap
                    ))
                else:
                    # can we add it to the current chunk?
                    if current_tokens + part_tokens <= desired_tokens:
                        # include the separator back in
                        current = sep.join([current, part]) if current else part
                        current_tokens += part_tokens
                    else:
                        # flush current, start new
                        chunks.append(current)
                        current, current_tokens = part, part_tokens

            if current:
                chunks.append(current)
            return chunks

    # Fallback: pure token sliding window (the only time we’ll split “inside” a block)
    tokens = encoder.encode(text)
    stride = desired_tokens - overlap
    return [
        encoder.decode(tokens[i : i + desired_tokens])
        for i in range(0, len(tokens), stride)
    ]

def subtract_it_int(*args):
    return int(subtract_it(*args))
class PromptManager:
    """
    Manages the generation and management of prompts. This includes creating prompts based on user input or predefined conditions, formatting prompts, and handling errors or special cases.
    """
    def __init__(self,
                 instruction_mgr=None,
                 model_mgr=None,
                 prompt_data:(str or list)=None,
                 request_data:(str or list)=None,
                 instruction_data:(str or list)= None,
                 role:str='assistant',
                 completion_percentage:int=40,
                 notation:str=None,
                 chunk_token_distribution_number:int=None,
                 chunk_number:int=None,
                 chunk_type:str=None)->None:
        """
        Initialize the PromptManager.

        Args:
            instruction_mgr: The instruction manager.
            model_mgr: The model manager.
            role (str, optional): The role of the issuer (e.g., user, assistant). Defaults to 'assistant'.
            completion_percentage (int, optional): The completion percentage. Defaults to 40.
            prompt_data: The preliminary data variable that gets converted to chunks.
            request: The prompt request.
            token_dist: Token distribution information.
            bot_notation: Additional notation for the bot.
            chunk: The current chunk.
            chunk_type: The type of chunk (e.g., URL, SOUP, DOCUMENT, CODE, TEXT).
        """
        self.notation_text = ''
        self.prompt_as_previous_text = ''
        self.chunk_type = chunk_type
        
        self.instruction_mgr = instruction_mgr or InstructionManager()
        
        self.model_mgr=model_mgr or ModelManager()
        
        self.role=role
        
        self.completion_percentage=completion_percentage
        
        self.instruction_data = instruction_data or self.instruction_mgr.instructions
        if not isinstance(self.instruction_data,list):
            self.instruction_data = [self.instruction_data]
        
        self.request_data=request_data or ['']
        if not isinstance(self.request_data,list):
            self.request_data = [self.request_data]
        #this data is what the prompt request will be reffering to, it is also the preliminary data variable that gets converted to chunks
        self.prompt_data=prompt_data or ['']
        if not isinstance(self.prompt_data,list):
            self.prompt_data = [self.prompt_data]
        #will initialize as '', this 
        self.notation=notation or ''
        #if None it will initialize such that the prompt creation will initially intake the entirety of the prompt_data, otherwise it will utilize its cunk info
        self.chunk_number=chunk_number or 0
        self.chunk_token_distribution_number=chunk_token_distribution_number or chunk_token_distribution_number
        self.total_chunks =10
        self.chunk_token_distributions=self.calculate_token_distribution(request_data=self.request_data,
                                                                         notation=self.notation,
                                                                         max_tokens=self.model_mgr.selected_max_tokens,
                                                                         completion_percentage=self.completion_percentage,
                                                                         prompt_data=self.prompt_data)
        
    def update_managers(self,instruction_mgr=None,model_mgr=None)->None:
        self.instruction_mgr = instruction_mgr or self.instruction_mgr
        self.model_mgr=model_mgr or self.model_mgr
    def update_request_and_prompt_data(self,model_mgr=None,
                                       instruction_mgr=None,
                                       prompt_data:(str or list)=None,
                                       request_data:(str or list)=None,
                                       instruction_data:(str or list)=None,
                                       completion_percentage:int=None,
                                       notation:str=None,
                                       chunk_type:str=None,
                                       role:str=None,
                                       reprocess_chunks:bool=True)->None:
        previous_completion_percentage = self.completion_percentage
        previous_prompt_data = self.prompt_data
        previous_request_data = self.request_data
        previous_max_tokens = self.model_mgr.selected_max_tokens
        if model_mgr:
            self.model_mgr=model_mgr
        self.update_managers(instruction_mgr=None,model_mgr=None)
        self.prompt_data=prompt_data or self.prompt_data
        self.role=role or self.role
        self.completion_percentage = completion_percentage or self.completion_percentage
        if not isinstance(self.prompt_data,list):
            self.prompt_data = [self.prompt_data]
        self.request_data=request_data or self.request_data
        if not isinstance(self.request_data,list):
            self.request_data = [self.request_data]
        self.instruction_data = instruction_data or self.instruction_data
        if not isinstance(self.instruction_data,list):
            self.instruction_data = [self.instruction_data]
        
        if reprocess_chunks:
            if (previous_prompt_data != self.prompt_data) or (previous_completion_percentage != self.completion_percentage) or (previous_max_tokens != self.model_mgr.selected_max_tokens):
                self.chunk_token_distributions=self.calculate_token_distribution(request_data=self.request_data,
                                                                                 prompt_data=self.prompt_data,
                                                                                 notation=self.notation,
                                                                                 max_tokens=self.model_mgr.selected_max_tokens,
                                                                                 completion_percentage=self.completion_percentage,
                                                                                 )
    def calculate_token_distribution(self,
                                     request_data:(str or list)=None,
                                     prompt_data:(str or list)=None,
                                     instruction_data:(str or list)=None,
                                     notation:str=None,
                                     max_tokens:int=None,
                                     completion_percentage:int=None,
                                     prompt_guide:str=None,
                                     assume_bot_notation:bool=True)->list[dict]:
        
        def get_token_calcs(i,
                            chunk_data:str,
                            total_chunks:int,
                            initial_prompt_token_length:int,
                            prompt_token_desired:int,
                            initial_completion_token_length:int,
                            completion_token_desired:int)->dict:
            """
            Calculates token usage statistics for a given chunk of data.

            Args:
                i (int): The index of the current chunk.
                chunk_data (str): The data within the current chunk.
                total_chunks (int): The total number of chunks.
                initial_prompt_token_length (int): The initial token length of the prompt.
                prompt_token_desired (int): The desired token length for the prompt.
                initial_completion_token_length (int): The initial token length of the completion.
                completion_token_desired (int): The desired token length for the completion.

            Returns:
                dict: A dictionary containing calculated token statistics for prompt and completion, as well as chunk details.
            """
            current_chunk_token_length = num_tokens_from_string(str(chunk_data))

            prompt_token_used = add_it(initial_prompt_token_length,current_chunk_token_length)
            prompt_token_available = subtract_it_int(prompt_token_desired,prompt_token_used)

            completion_token_used = initial_completion_token_length
            completion_token_available = subtract_it_int(completion_token_desired,completion_token_used)
            if prompt_token_available <0:
                completion_token_available+=prompt_token_available
            chunk_js = {
                    "completion": {
                        "desired": completion_token_desired,
                        "available": completion_token_available,
                        "used": completion_token_used
                    },
                    "prompt": {
                        "desired": prompt_token_desired,
                        "available": prompt_token_available,
                        "used": prompt_token_used
                    },
                    "chunk": {
                        "number": i,
                        "total": total_chunks,
                        "length": current_chunk_token_length,
                        "data": chunk_data
                    }
                }
            return chunk_js

        def get_token_distributions(prompt_token_desired:int,
                                    initial_prompt_token_length:int,
                                    total_chunk_data:str,
                                    fictitious_chunk_token_length:int,
                                    completion_token_desired:int,
                                    initial_completion_token_length:int,
                                    chunk_type:str)->list[dict]:
            """
            Computes token distributions for all chunks of data given the desired token allocations for prompts and completions.

            Args:
                prompt_token_desired (int): The desired number of tokens for the prompt.
                initial_prompt_token_length (int): The initial number of tokens used in the prompt.
                total_chunk_data (str): All the chunk data combined.
                fictitious_chunk_token_length (int): A hypothetical chunk token length used for chunking data.
                completion_token_desired (int): The desired number of tokens for the completion.
                initial_completion_token_length (int): The initial number of tokens used in the completion.
                chunk_type (str): The type of chunking to apply to the data.

            Returns:
                list of dict: A list where each dictionary contains the token distribution for a chunk.
            """
            # Function implementation ...
            get_token_distributions = []
            data_chunks_list = recursive_chunk(text=total_chunk_data, desired_tokens=fictitious_chunk_token_length)
            while '' in data_chunks_list:
                data_chunks_list.remove('')
            total_chunks = len(data_chunks_list)

            for i, chunk_data in enumerate(data_chunks_list):
                chunk_js = get_token_calcs(i=i,
                                           chunk_data=chunk_data,
                                           total_chunks=total_chunks,
                                           initial_prompt_token_length=initial_prompt_token_length,
                                           prompt_token_desired=prompt_token_desired,
                                           initial_completion_token_length=initial_completion_token_length,
                                           completion_token_desired=completion_token_desired)
                
                get_token_distributions.append(chunk_js)

            if total_chunks == 0:
                # Handle the case where there are no chunks
                chunk_js = get_token_calcs(i=0,
                                           chunk_data='',
                                           total_chunks=total_chunks,
                                           initial_prompt_token_length=initial_prompt_token_length,
                                           prompt_token_desired=prompt_token_desired,
                                           initial_completion_token_length=initial_completion_token_length,
                                           completion_token_desired=completion_token_desired)
                get_token_distributions.append(chunk_js)

            return get_token_distributions
        token_distributions=[]
        for i,chunk_prompt in enumerate(prompt_data):
            tokenize_js={"notation":notation,
                "max_tokens":max_tokens,
                "completion_percentage":completion_percentage,
                "prompt_guide":self.create_prompt_guide(request=request_data[i],chunk_token_distribution_number=i),
                "chunk_prompt":chunk_prompt}
            total_prompt = ''
            for each in tokenize_js.keys():
                if each != "chunk_prompt":
                    total_prompt+=str(tokenize_js[each])
                    
            max_tokens = int(tokenize_js["max_tokens"])
            
            completion_percent = convert_to_percentage(tokenize_js["completion_percentage"])
            completion_token_desired = int(multiply_it(max_tokens,completion_percent))
            
            
            prompt_percent = convert_to_percentage(100-tokenize_js["completion_percentage"])
            prompt_token_desired = int(multiply_it(max_tokens,prompt_percent))
            bot_notation_token_count= num_tokens_from_string(str(self.notation_text))
            prompt_as_previous_token_count = num_tokens_from_string(str(self.prompt_as_previous_text))
            total_prompt_length = num_tokens_from_string(str(total_prompt))
            initial_prompt_token_length = add_it(total_prompt_length,max(200,bot_notation_token_count),max(200,prompt_as_previous_token_count))

            initial_completion_token_length=bot_notation_token_count
            
            total_chunk_data = tokenize_js["chunk_prompt"] or ''
        
            total_chunk_token_length = num_tokens_from_string(str(total_chunk_data))
            ficticious_chunk_token_length = subtract_it_int(prompt_token_desired,initial_prompt_token_length)
            num_chunks = floor_divide_it(total_chunk_token_length,ficticious_chunk_token_length)      
            instruction_token_size = 0
            
            token_distributions.append(get_token_distributions(prompt_token_desired=prompt_token_desired,
                                                         initial_prompt_token_length=initial_prompt_token_length,
                                                         total_chunk_data=total_chunk_data,
                                                         fictitious_chunk_token_length=ficticious_chunk_token_length,
                                                         completion_token_desired=completion_token_desired,
                                                         initial_completion_token_length=initial_completion_token_length,
                                                         chunk_type=self.chunk_type))
        
        return token_distributions
           
    def create_prompt_guide(self,
                            pre_process:bool=False,
                            chunk_data:str=None,
                            request:str=None,
                            instructions:str=None,
                            chunk_token_distribution_number:int=None,
                            chunk_number:int=None,
                            total_chunks:int=None,
                            notation:str=None,
                            generate_title:str=None,
                            request_chunks:str=None,
                            prompt_as_previous:str=None)->str:
        """
        This method encapsulates the process of creating formatted communication for the current data chunk,
        which includes forming the prompt, notation, and other required fields for personalized bot communication.
        This is returned as a formatted string.

        Args:
            token_dist_prompt: Token distribution information for the prompt.
            notation (str, optional): Additional notation for the bot.
            data_chunk (str, optional): The data chunk.
            generate_title: Previously generated title.
            chunk_descriptions: Descriptions of the chunks.
            request_chunks: Previous chunk data requested.
            select_data: Selected data.

        Returns:
            str: A formatted communication guide.
        """
        def get_delimeters()->str:
            return '\n-----------------------------------------------------------------------------\n'
        def get_for_prompt(title:str,data:str)->str:
            if data:
                return f'#{title}#'+'\n\n'+f'{data}'
            return ''
        def get_chunk_header(current_chunk:int,total_chunks:int,chunk_data:str)->(None or str):
            if total_chunks in [0,'0'] or chunk_data in ['',None]:
                return None
            current_chunk = current_chunk or 0
            try:
                current_chunk=int(current_chunk)+1
            except:
                pass
            return f'this is chunk {current_chunk} of {total_chunks}'+'\n\n'+f'{chunk_data}'
        
        
        if pre_process:
            chunk_number=0
            total_chunks =10
            chunk_data= ''
            
        request = request or self.request_data[chunk_token_distribution_number]
        self.notation_text = notation
        self.prompt_as_previous_text=prompt_as_previous
        values_js = {'instructions':{'display':'instructions','data':instructions},
                     'prompt':{'display':'prompt','data':request},
                     'notation':{'display':'notation from the previous response','data':notation},
                     'chunk_data':{'display':'chunk_data','data':get_chunk_header(chunk_number,total_chunks,chunk_data)},
                     'prompt_as_previous':{'display':'previous module response','data':prompt_as_previous},
                     'generate_title':{'display':'previously generated_title','data':generate_title}
                     }
        prompt_data_source = ''
        self.key_check=[]
        for key,value in values_js.items():
            title = value['display']
            data = value['data']
            if data:
                self.key_check.append(key)
                prompt_data_source+=f"{get_delimeters()}{get_for_prompt(title,data)}"
        return prompt_data_source

    def create_prompt(self,
                      chunk_token_distribution_number:int=0,
                      chunk_number:int=0,
                      chunk_token_distribution_data:dict=None,
                      notation:str=None,
                      instructions:str=None,
                      generate_title:str=None,
                      request_chunks:str=None,
                      prompt_as_previous:str=None,
                      token_adjustment:int=None)->dict:
        """
        This method forms a dictionary embodying the prompt for the chatbot. This includes the model name,
        the role of the issuer, the content, and other variables. The method also takes an optional distribution number
        and bot notation for more personalized prompts.

        Args:
            dist_number (int, optional): The distribution number for the prompt.
            bot_notation (str, optional): Additional notation for the bot.
            generate_title: Previously generated title.
            chunk_descriptions: Descriptions of the chunks.
            request_chunks: Previous chunk data requested.

        Returns:
            dict: A dictionary representing the prompt for the chatbot.
        """
        self.prompt_as_previous=prompt_as_previous
        self.notation_text = notation
        self.prompt_as_previous_text=prompt_as_previous
        if prompt_as_previous and isinstance(prompt_as_previous,str):
            previous_request_data = self.request_data[chunk_token_distribution_number][:chunk_number]
            remaining_request_data = self.request_data[chunk_token_distribution_number][chunk_number:]
            previous_prompt_data = self.prompt_data[chunk_token_distribution_number][:chunk_number]
            remaining_prompt_data = self.prompt_data[chunk_token_distribution_number][chunk_number:]
            collated_remaining_prompt_data = '\n'.join(remaining_prompt_data)
            if chunk_number == 0:
                previous_chunks = make_list(self.chunk_token_distributions[chunk_token_distribution_number][0])
                remaining_chunks = make_list(self.chunk_token_distributions[chunk_token_distribution_number][1:])
            elif chunk_number == len(self.chunk_token_distributions[chunk_token_distribution_number]):
                previous_chunks = make_list(self.chunk_token_distributions[chunk_token_distribution_number][:-1])
                remaining_chunks = make_list(self.chunk_token_distributions[chunk_token_distribution_number][-1])
            else:
                previous_chunks = make_list(self.chunk_token_distributions[chunk_token_distribution_number][:chunk_number])
                remaining_chunks = make_list(self.chunk_token_distributions[chunk_token_distribution_number][chunk_number:])
            collated_chunks = ['\n'.join([chunk.get('chunk',{}).get('data','') for chunk in remaining_chunks])]
            new_chunk_distributions=self.calculate_token_distribution(
                 request_data=remaining_request_data,
                 prompt_data=collated_chunks,
                 instruction_data=self.instruction_data[chunk_token_distribution_number].get('text') or [],
                 notation=self.notation,
                 max_tokens=self.model_mgr.selected_max_tokens,
                 completion_percentage=self.completion_percentage,
                 assume_bot_notation=self.notation_text)
            self.chunk_token_distributions[chunk_token_distribution_number]=previous_chunks +new_chunk_distributions[0]
            for chunk_token_distribution_number_count,chunk_distribution in enumerate(self.chunk_token_distributions):
                for chunk_number_count,chunk in enumerate(chunk_distribution):
                    self.chunk_token_distributions[chunk_token_distribution_number_count][chunk_number_count]["number"]= chunk_number_count
                    self.chunk_token_distributions[chunk_token_distribution_number_count][chunk_number_count]["total"]= len(chunk_distribution)
        
        self.prompt =""
        total_chunks =0
        
        for each in self.chunk_token_distributions:
            total_chunks+=len(each)
        chunk_token_distribution_data=self.chunk_token_distributions[chunk_token_distribution_number][chunk_number]
        
        self.prompt =self.create_prompt_guide(request=self.request_data[chunk_token_distribution_number].replace('n**n','\n'),
                                              instructions=instructions or self.instruction_data[chunk_token_distribution_number]['text'],
                                              chunk_token_distribution_number=chunk_token_distribution_number,
                                              chunk_number=chunk_number,
                                              chunk_data=chunk_token_distribution_data['chunk']['data'],
                                              total_chunks=len(self.chunk_token_distributions[chunk_token_distribution_number]),
                                              notation=notation,
                                              generate_title=generate_title,
                                              request_chunks=request_chunks,
                                              prompt_as_previous=prompt_as_previous)

        role = self.role or "user"
        init_message = {"role": role, "content":self.prompt}
        init_message_ls = [init_message]
        init_prompt = {"model": self.model_mgr.selected_model_name, "messages": init_message_ls}
        init_prompt_str = str(init_prompt)
        init_prompt_str_tokens = num_tokens_from_string(init_prompt_str)
        max_tokens = subtract_it_int(self.model_mgr.selected_max_tokens,init_prompt_str_tokens)
        self.prompt ={"model": self.model_mgr.selected_model_name, "messages": [{"role": self.role or "user", "content":self.prompt }],"max_tokens": max_tokens}
        blank = True
        for key in self.key_check:
            if key not in ['instructions']:
                blank=False
        if blank:
            self.prompt['blank_prompt']=True
        
        return self.prompt

