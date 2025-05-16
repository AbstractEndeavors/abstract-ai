def text_to_key(text, section):
    """ Converts a text description to a GUI key based on the section """
    return f"{section}_{text}".replace(" ", "_").upper()

class InstructionManager_nogui:
    def __init__(self, instructions):
        self.default_instructions = {
            "api_response": {
                "instruction": "Place response to prompt here.",
                "example": "This is the reply to your request.",
                "default": True},
            "additional_responses": {
                "instruction": "Marking 'True' initiates a loop which continues to send the current chunk's prompt until the module returns a false value.",
                "example": "false",
                "default": False},
            # Add other instruction definitions here...
            }
        self.instructions = []
        self.default_instructions.update({key:{"instruction":instructions[key] if not isinstance(instructions[key],dict) else instructions[key].get('instruction',instructions[key]),"example":instructions[key] if not isinstance(instructions[key],dict) else instructions.get("example",""),"default":True} for key in instructions})
        self.get_default_instructions()
        self.make_instructions_reference()
        
    def get_default_instructions(self):
        """ Loads the default instructions based on what's set as default """
        self.instructions = [{key: self.default_instructions[key]} for key in self.default_instructions if self.default_instructions[key]["default"]]
        return self.instructions

    def update_instructions(self):
        """ Updates the instructions dynamically from the GUI values """
        bools = {}
        instructions = {}
        for key, value in self.default_instructions.items():
            bools[key] = self.window_mgr.get_values().get(text_to_key(text=key, section="BOOL"))
            instructions[key] = self.window_mgr.get_values().get(text_to_key(text=key, section="TEXT"))
        self.update_instructions_bools(**bools)
        self.update_instructions_text_values(**instructions)

    def update_instructions_bools(self, **bools):
        """ Updates boolean settings for instructions based on GUI input """
        for key, value in bools.items():
            if value is not None:
                self.instructions[key]["default"] = bool(value)

    def update_instructions_text_values(self, **text_values):
        """ Updates text settings for instructions based on GUI input """
        for key, value in text_values.items():
            if value is not None:
                self.instructions[key]["instruction"] = value

    def make_instructions_reference(self):
        """ Constructs a reference dictionary for the GUI to use """
        instructions_bools = {key: instr["default"] for key, instr in self.instructions[0].items()}
        instructions_text = {key: instr["instruction"] for key, instr in self.instructions[0].items()}
        self.instructions={
            "instructions_bools": instructions_bools,
            "instructions_text_values": instructions_text,
            "text": self.get_instructions_text(),
        }

    def get_instructions_text(self):
        """ Formats the instructions for display in the GUI """
        instructions = "your response is expected to be in JSON format with the keys as follows:\n\n"
        i = 0
        for key, value in self.instructions[0].items():
            instructions += f"{i}) {key} - {value.get('instruction')}\n"
            i += 1
        return instructions
