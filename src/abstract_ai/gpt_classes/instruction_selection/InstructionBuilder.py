from abstract_utilities import get_actual_number
from abstract_utilities.type_utils import is_bool
class InstructionManager:
    def __init__(self)->None:
        self.default_instructions = {"api_response": {"instruction": "place response to prompt here", "example": ""},
                                "additional_responses": {"instruction": "This parameter, usually set to True when the answer cannot be fully covered within the current token limit, initiates a loop that continues to send the current chunks prompt until the module returns a False value. This option also enables a module to have access to previous notations", "example": "False"},
                                "generate_title": {"instruction": "A parameter used for title generation of the chat. To maintain continuity, the generated title for a given sequence is shared with subsequent queries.", "example": ""},
                                "notation": {"instruction": "A useful parameter that allows a module to retain context and continuity of the prompts. These notations can be used to preserve relevant information or context that should be carried over to subsequent prompts.", "example": ""},
                                "suggestions": {"instruction": "A parameter that allows the module to provide suggestions for improving efficiency in future prompt sequences. These suggestions will be reviewed by the user after the entire prompt sequence is fulfilled.", "example": ""},
                                "abort": {"instruction": "if you cannot fullfil the request,", "example": "False"},
                                "prompt_as_previous": {"instruction": "this is a user end declaration; if this is visible that means that the request portion of the prompt will change such that the previous response data will be available if needed", "example": ""},
                                "request_chunks": {"instruction": "you may request that the previous chunk data be prompted again, if selected, the query itterate once more with the previous chunk included in the prompt.", "example": "False"},
                                "token_adjustment": {"instruction": "generally the token size of incoming queries is going to be static, because of this, if it will provide better results to increase or decrease the future allotment, place a number -100 up to 100 for a percentage adjustment for the remainder of the chunks and data", "example": "0"},
                                }
        self.instructions = []
    def get_instructions(self,instruction_number:int=None)->dict:
        if len(self.instructions)==0:
            self.add_instructions()
        instruction_number = instruction_number or -1
        return self.instructions[instruction_number]
    
    def get_instructions_bools(self,parameters:dict)->dict:
        for parameter,value in parameters.items():
            parameters[parameter] = True if value else False
        return parameters
    
    def get_instructions_text_values(self,instruction_bools:dict,parameters:dict)->dict:
        parameter_text_values = {}
        for parameter,value in instruction_bools.items():
            if value:
                parameter_text_values[parameter] = self.default_instructions[parameter]['instruction'] if is_bool(parameters[parameter]) else  parameters[parameter]
        return parameter_text_values
    def get_instructions_text(self,instructions_js:dict)->dict:
        """
        Retrieves instructions for the conversation.

        Returns:
            None
        """
        instructions = ""
        example_format={}
        if instructions_js:
            instructions = "your response is expected to be in JSON format with the keys as follows:\n\n"
            i=0
            for key in instructions_js.keys():
                if key in self.default_instructions.keys():
                    instructions+=f"{i}) {key} - {instructions_js[key]}\n"
                    example_format[key]=self.default_instructions[key]['example']
                    i+=1
            instructions += '\nbelow is an example of the expected json dictionary response format, with the default inputs:\n' + str(example_format).replace("'",'"')
        return instructions
    def add_instructions(self,all_true:bool=False)->None:
        print('adding instructions')
        if len(self.instructions)==0:
            instruction_display,instruction_bools,instructions_text_values,instructions_text=self.get_instructions_values(all_true=all_true)
            last_instructions = {'instruction_display':instruction_display,'instructions_bools':instruction_bools,"instructions_text_values":instructions_text_values,"instructions_text":instructions_text}
        else:
            last_instructions = self.instructions[-1]
        self.instructions.append(last_instructions)
        
    def get_instructions_values(self,all_true:bool= False,**kwargs)->(bool,dict,dict,str):
        parameters = {}
        for parameter in self.default_instructions.keys():
            value = kwargs.get(parameter,False) if all_true == False else True
            parameters[parameter]=value
        instruction_display=kwargs.get("instruction_display",True)    
        instruction_bools = self.get_instructions_bools(parameters)
        instructions_text_values= self.get_instructions_text_values(instruction_bools,parameters)
        instructions_text = self.get_instructions_text(instructions_js=instructions_text_values)
        return instruction_display,instruction_bools,instructions_text_values,instructions_text
    
    def update_instructions(self,instruction_number:int,**kwargs)->None:
        
        instruction_display,instruction_bools,instructions_text_values,instructions_text=self.get_instructions_values(**kwargs)
        self.instructions[instruction_number]={'instruction_display':instruction_display,'instructions_bools':instruction_bools,"instructions_text_values":instructions_text_values,"instructions_text":instructions_text}
