from abstract_utilities import get_actual_number, eatAll
from abstract_utilities.type_utils import is_bool
import json

def get_dict_from_instruction(instructions):
    new_instructions = {}
    if instructions:
        count = 0
        if isinstance(instructions, str):
            new_instructions[f"additional_instructions_{count}"] = {
                "instruction": instructions,
                "example": "",
                "default": True
            }
        elif isinstance(instructions, list):
            for instruction in instructions:
                if isinstance(instruction, str):
                    new_instructions[f"additional_instructions_{count}"] = {
                        "instruction": instruction,
                        "example": "",
                        "default": True
                    }
                    count += 1
                if isinstance(instruction, dict):
                    new_instruction = {"instruction": "", "example": "", "default": True}
                    new_instruction.update(instruction)
                    new_instructions[f"additional_instructions_{count}"] = new_instruction
                    count += 1
        elif isinstance(instructions, dict):
            for key, value in instructions.items():
                new_instruction = {"instruction": "", "example": "", "default": True}
                new_instruction.update(instructions[key])
                new_instructions[key] = new_instruction
    return new_instructions

class InstructionManager:
    def __init__(self, instructions=None, instruction_bools=None) -> None:
        instruction_bools = instruction_bools or {}
        self.default_instructions = {
            "api_response": {
                "instruction": "Place response to prompt here.",
                "example": "This is the reply to your request.",
                "default": True
            },
            "additional_responses": {
                "instruction": "Marking 'True' initiates a loop which continues to send the current chunk's prompt until the module returns a 'False' value.",
                "example": False,  # Use Python boolean for consistency
                "default": False
            },
            "generate_title": {
                "instruction": "Generate a short and concise title for this query, using underscores instead of spaces and avoiding special characters. The title should not exceed 200 characters to ensure compatibility with file systems.",
                "example": "Short_Title_for_Query",
                "default": True
            },
            "database_query": {
                "instruction": "The given database schema, variables, values, and function are provided in the prompt data; please derive the most appropriate inputs for a database query from the context and assertions of the request. Place all inputs for the function within this response key.",
                "example": {"query": """SELECT dnc_data FROM dncdata WHERE dnc_data ->> 'Data_Subscriber_First_Name' = 'Karen';"""},
                "default": False
            },
            "notation": {
                "instruction": "Notation is a module-end functionality that allows the module to preserve relevant information or context for subsequent prompts, enabling communication between modules throughout the query iterations.",
                "example": "Selecting additional responses due to insufficient completion tokens.",
                "default": False
            },
            "suggestions": {
                "instruction": "This parameter allows the module to provide suggestions for improving efficiency in future prompt sequences.",
                "example": "Consider batching queries to reduce server load",
                "default": False
            },
            "abort": {
                "instruction": "If you cannot fulfill the request, respond with this value as 'True'. Leave a detailed reason as to why the query stream was aborted in 'suggestions'.",
                "example": False,  # Use Python boolean
                "default": False
            },
            "prompt_as_previous": {
                "instruction": "This is a user-end declaration. If this is visible, the request portion of the prompt will change to include previous response data, if needed.",
                "example": False,  # Use Python boolean
                "default": False
            },
            "request_chunks": {
                "instruction": "Request to prompt again the previous chunk data. If selected, the query will iterate once more with the previous data chunk included in the prompt.",
                "example": False,  # Use Python boolean
                "default": False
            },
            "token_adjustment": {
                "instruction": "Suggest percentage adjustments, between -100 up to 100, for the future token allotment. If it will provide better results to increase or decrease the future allotment, place a number.",
                "example": 0,
                "default": False
            },
        }
        self.instructions = [[]]
        self.default_instructions.update(get_dict_from_instruction(instructions))
        for key, value in instruction_bools.items():
            if key in self.default_instructions:
                self.default_instructions[key]["default"] = value
        self.update_instructions(0, **{
            key: self.default_instructions[key]
            for key in self.default_instructions
            if self.default_instructions[key].get("default")
        })

    def get_instructions(self, instruction_number: int = None) -> dict:
        if not self.instructions or self.instructions == [[]]:
            self.add_instructions()
        instruction_number = instruction_number if instruction_number is not None else -1
        return self.instructions[instruction_number]

    def update_default_instructions(self, data):
        self.default_instructions.update(get_dict_from_instruction(data))
        self.update_instructions(0, **{
            key: self.default_instructions[key]
            for key in self.default_instructions
            if self.default_instructions[key].get("default")
        })

    def get_instructions_bools(self, parameters: dict) -> dict:
        return {parameter: bool(value) for parameter, value in parameters.items()}

    def get_instructions_text_values(self, instruction_bools: dict, parameters: dict) -> dict:
        parameter_text_values = {}
        for parameter, value in instruction_bools.items():
            if value and parameter in self.default_instructions:
                parameter_text_values[parameter] = (
                    self.default_instructions[parameter]["instruction"]
                    if is_bool(parameters[parameter])
                    else parameters[parameter]
                )
        return parameter_text_values

    def get_instructions_text(self, instructions_js: dict) -> tuple[str, dict]:
        """
        Retrieves instructions and example dictionary for the conversation.

        Args:
            instructions_js: Dictionary of instruction text values.

        Returns:
            Tuple of (instructions string, example dictionary).
        """
        instructions = ""
        example_format = {}
        if instructions_js:
            instructions = (
                "Your response is expected to be in JSON format, with boolean responses as lowercase unquoted values (true/false), "
                "using the following keys:\n\n"
            )
            for i, key in enumerate(instructions_js.keys()):
                if key in self.default_instructions:
                    instructions += f'{i}) {key} - """{eatAll(instructions_js[key], ["\'"])}"""\n'
                    example_value = self.default_instructions[key]["example"]
                    # Ensure JSON-compliant booleans
                    if isinstance(example_value, bool):
                        example_value = str(example_value).lower()
                    example_format[key] = example_value
            instructions += (
                "\nBelow is an example of the expected JSON dictionary response format, with default inputs. "
                "This response MUST be a dict:\n" + json.dumps(example_format, indent=2)
            )
        return instructions, example_format

    def add_instructions(self, all_true: bool = False, **kwargs) -> None:
        if not self.instructions or self.instructions == [[]]:
            instruction_display, instruction_bools, instructions_text_values, instructions_text, example_format = (
                self.get_instructions_values(all_true, **kwargs)
            )
            last_instructions = {
                "instruction_display": instruction_display,
                "instructions_bools": instruction_bools,
                "instructions_text_values": instructions_text_values,
                "instructions_text": instructions_text,
                "example_format": example_format,
                "text": instructions_text
            }
        else:
            last_instructions = self.instructions[-1]
        self.instructions.append(last_instructions)

    def get_instructions_values(self, all_true: bool = False, **kwargs) -> tuple[bool, dict, dict, str, dict]:
        parameters = {}
        for parameter in self.default_instructions.keys():
            parameters[parameter] = kwargs.get(parameter, False) if not all_true else True
        instruction_display = kwargs.get("instruction_display", True)
        instruction_bools = self.get_instructions_bools(parameters)
        instructions_text_values = self.get_instructions_text_values(instruction_bools, parameters)
        if not instructions_text_values:
            # Ensure at least one instruction is included to avoid empty prompt
            instructions_text_values["api_response"] = self.default_instructions["api_response"]["instruction"]
            instruction_bools["api_response"] = True
        instructions_text, example_format = self.get_instructions_text(instructions_js=instructions_text_values)
        return instruction_display, instruction_bools, instructions_text_values, instructions_text, example_format

    def update_instructions(self, instruction_number: int = 0, **kwargs) -> None:
        instruction_display, instruction_bools, instructions_text_values, instructions_text, example_format = (
            self.get_instructions_values(**kwargs)
        )
        while len(self.instructions) <= instruction_number:
            self.instructions.append({})
        self.instructions[instruction_number] = {
            "instruction_display": instruction_display,
            "instructions_bools": instruction_bools,
            "instructions_text_values": instructions_text_values,
            "instructions_text": instructions_text,
            "example_format": example_format,
            "text": instructions_text
        }

    def parse_model_response(self, response: str) -> dict:
        """
        Parses a model response string into a dictionary.

        Args:
            response: The model's response string (expected to be JSON-formatted).

        Returns:
            Dictionary containing the parsed response, or an error message if parsing fails.
        """
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            return {
                "error": f"Failed to parse JSON response: {str(e)}",
                "raw_response": response
            }
