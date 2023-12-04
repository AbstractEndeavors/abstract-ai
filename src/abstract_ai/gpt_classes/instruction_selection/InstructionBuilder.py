from abstract_utilities import get_actual_number
from abstract_utilities.type_utils import is_bool

class InstructionManager:
    def __init__(self)->None:
        self.default_instructions = {
            "api_response": {"instruction": "Place response to prompt here.", "example": "This is the reply to your request."},
            "additional_responses": {"instruction": "Marking 'True' initiates a loop which continues to send the current chunk's prompt until the module returns a 'False' value.", "example": "false"},
            "generate_title": {
                "instruction": "Generate a short and concise title for this query, using underscores instead of spaces and avoiding special characters. The title should not exceed 30 characters to ensure compatibility with file systems.",
                "example": "Short_Title_for_Query"
                },
            "notation": {"instruction": "This value allows for communication between modules throughout the query iterations. These notations can be used to preserve relevant information or context for subsequent prompts.", "example": "Selecting additional responses due to insufficient completion tokens."},
            "suggestions": {"instruction": "This parameter allows the module to provide suggestions for improving efficiency in future prompt sequences.", "example": "Consider batching queries to reduce server load"},
            "abort": {"instruction": "If you cannot fulfill the request, respond with this value as 'True'. Leave a detailed reason as to why the query stream was aborted in 'suggestions'", "example": "False"},
            "prompt_as_previous": {"instruction": "This is a user-end declaration. If this is visible, the request portion of the prompt will change to include previous response data, if needed", "example": "True"},
            "request_chunks": {"instruction": "Request to prompt again the previous chunk data. If selected, the query will iterate once more with the previous data chunk included in the prompt.", "example": "False"},
            "token_adjustment": {"instruction": "Suggest percentage adjustments, between -100 up to 100, for the future token allotment. If it will provide better results to increase or decrease the future allotment, place a number.", "example": "0"},

            "context_preservation": {"instruction": "Maintain and reference relevant context from previous iterations. Store context data securely and efficiently for accurate response generation.", "example": "Context from previous iteration stored: User preference for X identified."},
            "error_handling": {"instruction": "Identify and handle errors gracefully. Provide clear error messages and log errors for debugging purposes.", "example": "Error identified: Data format mismatch. Logged for review."},
            "response_validation": {"instruction": "Validate the response for accuracy, relevance, and completeness before finalizing. Implement checks for coherence and pertinence.", "example": "Response validated for accuracy and relevance."},
            "user_feedback": {"instruction": "Incorporate user feedback mechanism post-response or at the end of the sequence. Use feedback to refine future interactions.", "example": "User feedback requested on response clarity."},
            "adaptive_token_adjustment": {"instruction": "Automatically suggest token adjustments based on historical query lengths and complexities. Adjust token size dynamically.", "example": "Token size increased by 10% based on previous complex queries."},
            "documentation": {"instruction": "Provide a detailed example for this instruction as documented in the system's manual.", "example": "Refer to page 42 for 'context_preservation' usage examples."},
            "performance_metrics": {"instruction": "Track and report performance metrics such as response time, accuracy, or relevance for each iteration.", "example": "Response time: 2 seconds, Accuracy: 95%."},
            "dynamic_chunk_management": {"instruction": "Adjust chunk sizes dynamically based on the complexity and nature of incoming data.", "example": "Chunk size increased for complex image processing task."},
            "ui_interaction": {"instruction": "Provide a user-friendly interface for module interactions, displaying progress and allowing adjustments.", "example": "UI updated with query progress and adjustment options."},
            "security_privacy": {"instruction": "Ensure data security and user privacy. Implement features for secure data handling and confidentiality.", "example": "User data encrypted and access logs maintained for privacy compliance."},
            "scalability_resource_management": {"instruction": "Optimize system scalability and efficient resource management for handling larger datasets and increased queries.", "example": "System resources adjusted for 20% increased query load."},
            "multilingual_support": {"instruction": "Provide support for multiple languages in processing and responding to queries.", "example": "Spanish language processing enabled for current query."},
            "customization_flexibility": {"instruction": "Allow customization in response formats and system integration as per user needs.", "example": "Custom response format applied as per user settings."}

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
