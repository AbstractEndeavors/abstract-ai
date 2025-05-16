from abstract_utilities import get_actual_number, eatAll
from abstract_utilities.type_utils import is_bool

def get_instructions_list_to_dict(obj) -> dict:
    if not isinstance(obj, dict):
        obj = {key: value[key] for value in obj for key in value}
    return obj

def get_instructions_dict_to_list(obj) -> list:
    if not isinstance(obj, list):
        obj = [{key: value} for key, value in obj.items()]
    return obj

class InstructionManager:
    def __init__(self) -> None:
        self.default_instructions = {
            "api_response": {
                "instruction": "Place response to prompt here.",
                "example": "This is the reply to your request.",
                "default": True},
            "additional_responses": {
                "instruction": "Marking 'True' initiates a loop which continues to send the current chunk's prompt until the module returns a false value.",
                "example": "false",
                "default": False},
            "generate_title": {
                "instruction": "Generate a short and concise title for this query, using underscores instead of spaces and avoiding special characters. The title should not exceed 30 characters to ensure compatibility with file systems.",
                "example": "Short_Title_for_Query",
                "default": True},
            "notation": {
                "instruction": "notation is a module end  functionality that allows the module, you, to to preserve relevant information or context for subsequent prompts; allowing for communication between modules throughout the query iterations. ",
                "example": "Selecting additional responses due to insufficient completion tokens.",
                "default": True},
            "suggestions": {
                "instruction": "This parameter allows the module to provide suggestions for improving efficiency in future prompt sequences.",
                "example": "Consider batching queries to reduce server load",
                "default": True},
            "abort": {
                "instruction": """If you cannot fulfill the request, respond with this value as true. Leave a detailed reason as to why the query stream was aborted in suggestions""",
                "example": "False",
                "default": False},
            "prompt_as_previous": {
                "instruction": "This is a user-end declaration. If this is visible, the request portion of the prompt will change to include previous response data, if needed",
                "example": "true",
                "default": False},
            "request_chunks": {
                "instruction": "Request to prompt again the previous chunk data. If selected, the query will iterate once more with the previous data chunk included in the prompt.",
                "example": "false",
                "default": False},
            "token_adjustment": {
                "instruction": "Suggest percentage adjustments, between -100 up to 100, for the future token allotment. If it will provide better results to increase or decrease the future allotment, place a number.",
                "example": "0",
                "default": False}
        }
        self.instruction_number = 0
        self.instructions = []

    def get_default_instructions(self, instruction_number=None):
        instructions = []
        instructions.append([{key: self.default_instructions.get(key)} for key in self.default_instructions if self.default_instructions.get(key).get("default")])
        self.update_instruction(instructions, instruction_number=instruction_number)
        return get_instructions_dict(self)  # Note: Assuming this typo meant get_instructions_dict

    def get_instructions_list(self):
        return get_instructions_dict_to_list(self.instructions[self.instruction_number])

    def get_instructions_dict(self):
        return get_instructions_list_to_dict(self.instructions[self.instruction_number])

    def update_instruction(self, instruction, instruction_number=None):
        self.instruction_number = instruction_number or self.instruction_number
        while len(self.instructions) <= self.instruction_number:  # Expand list if needed
            self.instructions.append({})
        self.instructions[self.instruction_number] = instruction

    def get_instructions(self, instruction_number: int = None) -> dict:
        if len(self.instructions) == 0:
            self.add_instructions()  # Assuming this exists elsewhere
        instruction_number = instruction_number or -1
        return self.instructions[instruction_number]

    def update_instructions_bools(self, **kwargs) -> dict:
        instructions = self.get_instructions_dict()
        for key, value in instructions.items():
            if value == False and kwargs.get(key):
                del instructions[key]
            else:
                instructions[key] = self.default_instructions.get(key) or value
        self.update_instruction(instructions)
        return instructions

    def update_instructions_text(self, **kwargs) -> dict:
        instructions = self.get_instructions_dict()  # Fixed typo from get_instructions_dict()
        for key, value in instructions.items():
            if key not in instructions:  # Fixed 'instruction' typo
                instructions[key] = self.default_instructions.get(key, {"instruction": "", "example": "", "default": False, "bool": False})
            instructions[key].update(value)
        self.update_instruction(instructions)
        return instructions

    def make_instructions_reference(self):
        instructions = self.default_instructions
        instructions.update(self.get_instructions_dict())
        instructions_bools = {key: False if not self.get_instructions_dict().get(key) else True for key in instructions.keys()}
        instructions_text = self.get_instructions_text()
        return {
            "instructions_bools": instructions_bools,
            "instructions_text_values": instructions_text,
            "instructions_text": self.get_instructions_text(),  # Fixed typo
            "text": instructions_text
        }

    def find_instruction_from_list(self, search_key):
        for key, inst in self.instructions_bool_list.items():  # Assuming instructions_bool_list is defined elsewhere
            if key == search_key:
                return inst

    def update_instructions_text_values(self, **kwargs) -> dict:
        parameter_text_values = {}  # Added missing variable
        for key, value in kwargs.items():
            parameter_text_values[key] = self.default_instructions[key]['instruction'] if is_bool(value) else value
        return parameter_text_values

    def get_instructions_text(self) -> dict:  # Changed return type from string to dict
        """
        Retrieves instructions for the conversation in a JSON-parsable format.

        Returns:
            dict: A structured dictionary with instructions and example response.
        """
        instruction_dict = self.get_instructions_dict()
        return {
            "instructions": {
                key: value.get("instruction")
                for key, value in instruction_dict.items()
            },
            "example_response": {
                key: value.get("example")
                for key, value in instruction_dict.items()
            }
        }

    def update_instructions(self, instruction_number: int, **kwargs) -> None:
        instruction_display, instruction_bools, instructions_text_values, instructions_text = self.get_instructions_values(**kwargs)  # Assuming get_instructions_values exists
        self.instructions[instruction_number] = {
            'instruction_display': instruction_display,
            'instruction_bools': instruction_bools,
            "instructions_text": instructions_text_values,
            "text": instructions_text
        }
